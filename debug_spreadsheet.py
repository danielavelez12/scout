#!/usr/bin/env python3
"""
Debug script to examine the actual structure of the spreadsheet data.
"""

import gspread
from google.oauth2.service_account import Credentials


def debug_spreadsheet():
    """
    Debug function to examine the spreadsheet structure.
    """

    # Configuration
    service_account_file = "personal-web-350101-bf5dd9e830b5.json"
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1a1c8uaxhThngwduuha4wxmtXhU3sIEq7hGVyxfPHeFU/edit?gid=1822428729#gid=1822428729"

    try:
        # Set up credentials
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        creds = Credentials.from_service_account_file(
            service_account_file,
            scopes=SCOPES,
        )

        # Authorize gspread
        gc = gspread.authorize(creds)

        # Extract spreadsheet ID from URL
        spreadsheet_id = spreadsheet_url.split("/spreadsheets/d/")[1].split("/")[0]

        # Open spreadsheet by ID
        spreadsheet = gc.open_by_key(spreadsheet_id)

        # List all worksheets
        print("Available worksheets:")
        for worksheet in spreadsheet.worksheets():
            print(f"  - {worksheet.title}")

        print("\n" + "=" * 50)

        # Get the first worksheet
        worksheet = spreadsheet.worksheet("Sheet1")

        # Get all values
        values = worksheet.get_all_values()

        print(f"Total rows: {len(values)}")
        print(f"Columns in first row: {len(values[0]) if values else 0}")

        if values:
            print("\nFirst 5 rows:")
            for i, row in enumerate(values[:5]):
                print(f"Row {i+1}: {row}")

        print("\n" + "=" * 50)

        # Check for headers
        if values:
            print("Headers (first row):")
            for i, header in enumerate(values[0]):
                print(f"  Column {i}: '{header}'")

        print("\n" + "=" * 50)

        # Look for birthday-related data
        print("Sample data rows (rows 2-6):")
        for i, row in enumerate(values[1:6], 2):
            print(f"Row {i}: {row}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    debug_spreadsheet()
