from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from models.scout import Scout
from typing import Dict, Any, Optional
from pydantic import BaseModel
from scouts.birthdayScout import BirthdayScout

app = FastAPI(
    title="API Service", description="A basic API service with Scout functionality"
)

# Google Sheets configuration
GOOGLE_SHEETS_SERVICE_KEY = "credentials.json"
BIRTHDAY_SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1a1c8uaxhThngwduuha4wxmtXhU3sIEq7hGVyxfPHeFU/edit?gid=1822428729#gid=1822428729"


class ScoutCreateRequest(BaseModel):
    name: str
    target_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ScoutRunRequest(BaseModel):
    target_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello")
async def hello():
    return {"message": "Hello"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/birthday-scout/run")
async def run_birthday_scout():
    """
    Run the BirthdayScout to check for today's birthdays and report to subscribers.

    Returns:
        Dict containing scout execution results and status
    """
    try:
        # Extract spreadsheet ID from URL
        spreadsheet_id = BIRTHDAY_SPREADSHEET_URL.split("/spreadsheets/d/")[1].split(
            "/"
        )[0]

        # Create and run the BirthdayScout
        scout = BirthdayScout(GOOGLE_SHEETS_SERVICE_KEY, spreadsheet_id)

        # Check if Vapi is configured
        if not scout.check_vapi_config():
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Vapi not configured. Check environment variables.",
                },
            )

        # Fetch birthdays
        birthdays = scout.fetch_birthdays()
        if not birthdays:
            return {
                "success": False,
                "message": "No birthdays found in spreadsheet",
            }

        # Check for today's birthdays
        todays_birthdays = scout.get_todays_birthdays()
        if not todays_birthdays:
            return {
                "success": True,
                "message": "No birthdays today",
                "todays_birthdays": [],
            }

        # Report results (make Vapi calls)
        report_success = scout.report_results()

        return {
            "success": report_success,
            "message": f"Birthday scout completed. Found {len(todays_birthdays)} birthdays today.",
            "todays_birthdays": todays_birthdays,
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Internal server error: {str(e)}",
            },
        )
