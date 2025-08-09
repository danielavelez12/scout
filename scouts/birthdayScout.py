import os
from typing import List, Dict, Any, Optional
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
from vapi_call import VapiCaller
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BirthdayScout:
    """
    A scout class for fetching birthday data from Google Sheets using gspread.
    """

    def __init__(
        self, service_account_file: str, spreadsheet_id: str, sheet_name: str = "Sheet1"
    ):
        """
        Initialize the BirthdayScout.

        Args:
            service_account_file (str): Path to the service account JSON file
            spreadsheet_id (str): The ID of the Google Spreadsheet
            sheet_name (str): The name of the sheet to fetch data from
        """
        self.service_account_file = service_account_file
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.gc = None
        self.worksheet = None
        self.results = []
        self.status = "idle"
        self.error_message = None
        self.subscribers = [{"name": "Daniela", "phone": "9549559235"}]
        # Vapi configuration from environment variables
        self.vapi_private_api_key = os.getenv("PRIVATE_API_KEY")
        self.vapi_assistant_id = os.getenv("ASSISTANT_ID")

    def _initialize_gspread(self):
        """
        Initialize gspread client and worksheet.
        """
        try:
            # Set up credentials
            SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
            creds = Credentials.from_service_account_file(
                self.service_account_file,
                scopes=SCOPES,
            )

            # Authorize gspread
            self.gc = gspread.authorize(creds)

            # Open spreadsheet by ID
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)

            # Get worksheet
            self.worksheet = spreadsheet.worksheet(self.sheet_name)

        except Exception as e:
            self.error_message = f"Initialization error: {str(e)}"
            self.status = "error"
            raise

    def fetch_birthdays(self) -> List[Dict[str, Any]]:
        """
        Fetch birthday data from the Google Spreadsheet using gspread.

        Returns:
            List[Dict[str, Any]]: List of birthday records
        """
        try:
            self.status = "fetching"

            # Initialize gspread if not already done
            if self.gc is None:
                self._initialize_gspread()

            # Get all values from the worksheet
            values = self.worksheet.get_all_values()

            if not values:
                self.status = "completed"
                return []

            # Process the data
            birthdays = []
            headers = values[0] if values else ["", "Name", "Year", "Month", "Day"]

            for row in values[1:]:  # Skip header row
                if len(row) >= 4:  # At least empty, name, month, day
                    # Handle the actual structure: [empty, name, year, month, day]
                    birthday_record = {
                        "name": row[1] if len(row) > 1 and row[1] else "",
                        "year": (
                            row[2]
                            if len(row) > 2
                            and row[2]
                            and row[2].isdigit()
                            and row[2] != "null"
                            else None
                        ),
                        "month": (
                            int(row[3])
                            if len(row) > 3 and row[3] and row[3].isdigit()
                            else None
                        ),
                        "day": (
                            int(row[4])
                            if len(row) > 4 and row[4] and row[4].isdigit()
                            else None
                        ),
                    }
                    # Only add if we have at least a name and date
                    if (
                        birthday_record["name"]
                        and birthday_record["month"]
                        and birthday_record["day"]
                    ):
                        birthdays.append(birthday_record)

            self.results = birthdays
            self.status = "completed"
            return birthdays

        except Exception as e:
            self.error_message = f"Fetch error: {str(e)}"
            self.status = "error"
            return []

    def get_todays_birthdays(self) -> List[Dict[str, Any]]:
        """
        Get birthdays for today from the results.

        Returns:
            List[Dict[str, Any]]: List of today's birthdays
        """
        if not self.results:
            return []

        today = datetime.now()
        todays_birthdays = []

        for birthday in self.results:
            if (
                birthday.get("month") == today.month
                and birthday.get("day") == today.day
            ):
                todays_birthdays.append(birthday)

        return todays_birthdays

    def check_vapi_config(self) -> bool:
        """
        Check if Vapi is properly configured with environment variables.

        Returns:
            bool: True if Vapi is configured, False otherwise
        """
        if not self.vapi_private_api_key:
            self.error_message = "PRIVATE_API_KEY environment variable not set"
            return False
        if not self.vapi_assistant_id:
            self.error_message = "ASSISTANT_ID environment variable not set"
            return False
        return True

    def format_birthdays_for_prompt(self, birthdays: List[Dict[str, Any]]) -> str:
        """
        Format birthdays data as a readable string for the Vapi prompt.

        Args:
            birthdays: List of birthday dictionaries

        Returns:
            str: Formatted birthday string for the prompt
        """
        if not birthdays:
            return "No birthdays today"

        formatted_birthdays = []
        for birthday in birthdays:
            name = birthday.get("name", "")
            month = birthday.get("month", "")
            day = birthday.get("day", "")

            if name and month and day:
                formatted_birthdays.append(f"{name} ({month}/{day})")

        if formatted_birthdays:
            return ", ".join(formatted_birthdays)
        else:
            return "No birthdays today"

    def report_results(self) -> bool:
        """
        Report birthday results to all subscribers using Vapi calls.

        Returns:
            bool: True if reporting was successful, False otherwise
        """
        try:
            self.status = "reporting"

            if not self.check_vapi_config():
                self.status = "error"
                return False

            if not self.subscribers:
                self.error_message = "No subscribers to report to"
                self.status = "error"
                return False

            # Get today's birthdays
            todays_birthdays = self.get_todays_birthdays()

            if not todays_birthdays:
                print("No birthdays today to report")
                self.status = "completed"
                return True

            # Format birthdays for the prompt
            birthdays_text = self.format_birthdays_for_prompt(todays_birthdays)
            print(f"Today's birthdays: {birthdays_text}")

            # Initialize Vapi caller
            vapi_caller = VapiCaller(self.vapi_private_api_key, self.vapi_assistant_id)

            # Report to each subscriber
            for subscriber in self.subscribers:
                subscriber_name = subscriber.get("name", "")
                subscriber_phone = subscriber.get("phone", "")

                if not subscriber_phone:
                    print(f"Warning: No phone number for subscriber {subscriber_name}")
                    continue

                # Prepare variable values for the call using the new prompt format
                variable_values = {
                    "userFirstName": subscriber_name,
                    "birthdays": birthdays_text,
                }

                print(
                    f"Calling {subscriber_name} at {subscriber_phone} about today's birthdays"
                )
                print(f"Birthdays to report: {birthdays_text}")

                # Make the call
                call_result = vapi_caller.make_call_with_variables(
                    phone_number=subscriber_phone,
                    variable_values=variable_values,
                    call_name=f"Birthday Alert: {len(todays_birthdays)} birthdays today",
                )

                if call_result.get("error"):
                    print(
                        f"Error calling {subscriber_name}: {call_result.get('message')}"
                    )
                else:
                    print(
                        f"Successfully called {subscriber_name} about today's birthdays"
                    )
                    print(f"Call ID: {call_result.get('id', 'N/A')}")

            self.status = "completed"
            return True

        except Exception as e:
            self.error_message = f"Report error: {str(e)}"
            self.status = "error"
            return False


def fetch_birthdays_from_sheet(
    service_account_file: str, spreadsheet_url: str
) -> Dict[str, Any]:
    """
    Helper function to fetch birthdays from a Google Spreadsheet using gspread.

    Args:
        service_account_file (str): Path to the service account JSON file
        spreadsheet_url (str): The URL of the Google Spreadsheet

    Returns:
        Dict[str, Any]: Dictionary containing status and birthday data
    """
    try:
        # Extract spreadsheet ID from URL
        # URL format: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit...
        if "/spreadsheets/d/" in spreadsheet_url:
            spreadsheet_id = spreadsheet_url.split("/spreadsheets/d/")[1].split("/")[0]
        else:
            return {
                "success": False,
                "error": "Invalid spreadsheet URL format",
                "birthdays": [],
            }

        # Create scout instance
        scout = BirthdayScout(service_account_file, spreadsheet_id)

        # Fetch birthdays
        birthdays = scout.fetch_birthdays()

        return {
            "success": scout.status == "completed",
            "error": scout.error_message,
            "birthdays": birthdays,
            "total_count": len(birthdays),
        }

    except Exception as e:
        return {"success": False, "error": str(e), "birthdays": [], "total_count": 0}
