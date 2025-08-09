# BirthdayScout with gspread

This is an updated implementation of the BirthdayScout that uses the `gspread` library to fetch birthday data from Google Sheets.

## Features

- ✅ Fetches birthday data from Google Sheets using gspread
- ✅ Handles service account authentication
- ✅ Supports multiple worksheets
- ✅ Robust error handling
- ✅ Easy-to-use API

## Installation

1. Install the required dependencies:

```bash
pip install gspread google-auth
```

2. Make sure you have a Google Service Account JSON file (e.g., `personal-web-350101-bf5dd9e830b5.json`)

## Usage

### Method 1: Using the helper function (recommended)

```python
from scouts.birthdayScout import fetch_birthdays_from_sheet

# Configuration
service_account_file = "personal-web-350101-bf5dd9e830b5.json"
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1a1c8uaxhThngwduuha4wxmtXhU3sIEq7hGVyxfPHeFU/edit"

# Fetch birthdays
result = fetch_birthdays_from_sheet(service_account_file, spreadsheet_url)

if result["success"]:
    print(f"Found {result['total_count']} birthdays")
    for birthday in result["birthdays"]:
        print(f"- {birthday['name']}: {birthday['month']}/{birthday['day']}")
else:
    print(f"Error: {result['error']}")
```

### Method 2: Using the BirthdayScout class directly

```python
from scouts.birthdayScout import BirthdayScout

# Extract spreadsheet ID from URL
spreadsheet_id = "1a1c8uaxhThngwduuha4wxmtXhU3sIEq7hGVyxfPHeFU"

# Create scout instance
scout = BirthdayScout("personal-web-350101-bf5dd9e830b5.json", spreadsheet_id, "Sheet1")

# Fetch birthdays
birthdays = scout.fetch_birthdays()

# Get summary
summary = scout.get_summary()
print(f"Status: {summary['status']}")
print(f"Total birthdays: {summary['total_birthdays']}")
```

## Data Structure

The BirthdayScout expects the spreadsheet to have the following structure:

| Column | Index | Description   |
| ------ | ----- | ------------- |
| A      | 0     | Empty (index) |
| B      | 1     | Name          |
| C      | 2     | Year          |
| D      | 3     | Month         |
| E      | 4     | Day           |

### Example data:

```
|   | Name              | Year | Month | Day |
|---|-------------------|------|-------|-----|
|   | Alejandro Velazquez | 2001 | 1     | 1   |
|   | Anson Hu          | 2001 | 1     | 1   |
|   | Burhan Azeem      | null | 1     | 1   |
```

## Configuration

### Service Account Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create a Service Account
5. Download the JSON key file
6. Share your Google Sheet with the service account email (e.g., `daniela@personal-web-350101.iam.gserviceaccount.com`)

### Spreadsheet Permissions

Make sure your Google Sheet is shared with the service account email with at least "Viewer" permissions.

## Error Handling

The BirthdayScout includes comprehensive error handling:

- Invalid spreadsheet URL format
- Authentication errors
- Permission denied errors
- Network connectivity issues
- Data parsing errors

## Examples

See the following files for complete examples:

- `example_usage.py` - Basic usage examples
- `test_birthday_scout.py` - Test script
- `debug_spreadsheet.py` - Debug script for examining spreadsheet structure

## Dependencies

- `gspread==6.0.0` - Google Sheets API wrapper
- `google-auth==2.23.4` - Google authentication library

## Migration from googleapiclient

This implementation replaces the previous `googleapiclient` approach with `gspread` for:

- **Simpler API**: More intuitive and easier to use
- **Better error handling**: More descriptive error messages
- **Automatic retry logic**: Built-in retry mechanisms
- **Cleaner code**: Less boilerplate code required

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'gspread'**

   - Run: `pip install gspread google-auth`

2. **Authentication error**

   - Check that your service account JSON file is correct
   - Ensure the Google Sheets API is enabled in your project
   - Verify the service account has access to the spreadsheet

3. **Permission denied**

   - Share the spreadsheet with the service account email
   - Check that the service account has at least "Viewer" permissions

4. **Invalid spreadsheet URL**
   - Make sure the URL follows the format: `https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit`

### Debug Mode

Use the `debug_spreadsheet.py` script to examine the actual structure of your spreadsheet:

```bash
python debug_spreadsheet.py
```

This will show you:

- Available worksheets
- Column structure
- Sample data rows
- Headers
