import json
import gspread
from google.oauth2 import service_account
import streamlit as st
import os
from datetime import datetime, date # <--- Add this line
import toml # You'll need this if you don't have it already for loading secrets.toml

# --- Configuration (matching your app's needs) ---
RECORDS_FILE = "freediving_records.json"
USER_PROFILES_FILE = "user_profiles.json"
TRAINING_LOG_FILE = "training_log.json"
INSTRUCTOR_FEEDBACK_FILE = "instructor_feedback.json"

# --- Google Sheets Connection setup ---
# This part is similar to your Streamlit app's get_gsheets_client
def get_gsheets_client_for_migration():
    try:
        # Load secrets directly from .streamlit/secrets.toml for a standalone script
        # This requires the script to be run from the root of your Streamlit project,
        # or you manually provide the path to secrets.toml
        # For simplicity, we'll mimic st.secrets structure.
        # In a real standalone script, you might load a config file differently.
        
        # --- IMPORTANT: Replace this placeholder with how you actually load secrets in a standalone script ---
        # Option 1: If running from the Streamlit project root, you can read it like this:
        secrets_path = os.path.join(".streamlit", "secrets.toml")
        if not os.path.exists(secrets_path):
            raise FileNotFoundError(f"secrets.toml not found at {secrets_path}. Please create it or adjust the path.")
        
        # This is a simplified way to parse TOML, for production, use a proper TOML parser like `toml`
        import toml
        secrets_data = toml.load(secrets_path)
        
        gsheets_creds = secrets_data.get("gsheets", {})

        creds = service_account.Credentials.from_service_account_info(
            gsheets_creds,
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
        )
        return gspread.authorize(creds), gsheets_creds
    except Exception as e:
        print(f"Error connecting to Google Sheets for migration: {e}")
        print("Please ensure your .streamlit/secrets.toml is correctly configured with Google service account credentials and sheet URLs.")
        exit(1) # Exit if connection fails

def get_worksheet(client, url_key, worksheet_name):
    # Use a dummy Streamlit app to access st.secrets during migration, or pass secrets_data directly.
    # For a true standalone script, you'd load secrets differently.
    try:
        if not hasattr(st, 'secrets') or not st.secrets.get("gsheets"):
             # This block is for running outside a Streamlit context where st.secrets isn't populated
            secrets_path = os.path.join(".streamlit", "secrets.toml")
            if not os.path.exists(secrets_path):
                raise FileNotFoundError(f"secrets.toml not found at {secrets_path}. Please ensure it's in your project root or provide the full path.")
            import toml
            secrets_data = toml.load(secrets_path)
            spreadsheet_url = secrets_data["gsheets"][url_key]
        else:
            spreadsheet_url = st.secrets["gsheets"][url_key]

        spreadsheet = client.open_by_url(spreadsheet_url)
        return spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        print(f"Error: Worksheet '{worksheet_name}' not found in the Google Sheet for {url_key}.")
        print(f"Please ensure the worksheet exists and its name is correct in your Google Sheet.")
        exit(1)
    except Exception as e:
        print(f"Error getting worksheet for {url_key} ({worksheet_name}): {e}")
        exit(1)


def migrate_data(json_file_path, sheet_url_key, worksheet_name):
    print(f"\n--- Migrating {json_file_path} to Google Sheet '{worksheet_name}' ---")
    
    if not os.path.exists(json_file_path):
        print(f"Skipping {json_file_path}: File not found.")
        return

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {json_file_path}: {e}")
        return
    except Exception as e:
        print(f"Error reading {json_file_path}: {e}")
        return

    if not data:
        print(f"No data found in {json_file_path}. Skipping migration for this file.")
        return

    # Special handling for user_profiles which is a dict, not a list of dicts
    if json_file_path == USER_PROFILES_FILE:
        # Convert user_profiles dictionary to a list of dictionaries
        # Each dictionary represents a row, with 'user_name' as a column
        processed_data = []
        for user_name, profile_data in data.items():
            row = profile_data.copy()
            row['user_name'] = user_name # Ensure user_name is a column
            processed_data.append(row)
        data = processed_data # Now `data` is a list of dicts suitable for gspread
        if not data: # After processing, might become empty if source was empty dict
            print(f"No valid user profiles to migrate from {json_file_path}.")
            return
            
    # For other files, ensure they are lists of dictionaries
    if not isinstance(data, list) or (data and not isinstance(data[0], dict)):
        print(f"Skipping {json_file_path}: Expected data to be a list of dictionaries. Found unexpected format.")
        print(f"First element type: {type(data[0]) if data else 'N/A'}")
        return

    client, _ = get_gsheets_client_for_migration() # Get client
    worksheet = get_worksheet(client, sheet_url_key, worksheet_name)

    # Clear existing content in the sheet
    worksheet.clear()
    print(f"Cleared existing data in Google Sheet '{worksheet_name}'.")

    # Get headers from the first data item (assuming consistent keys)
    # Ensure all columns expected by the app are present in the headers,
    # or gspread will just write the keys present in the first dict.
    # It's safest to define an explicit set of headers if your schema might vary slightly.
    headers = list(data[0].keys())

    # Prepare data for batch update: first row is headers, subsequent rows are data
    rows_to_write = [headers]
    for item in data:
        row_values = []
        for header in headers:
            # Handle potential missing keys by providing None or default value
            value = item.get(header)
            # Convert non-string types to string for GSheets, especially dates
            if isinstance(value, (date, datetime)):
                value = value.isoformat()
            elif value is None:
                value = "" # Gspread often prefers empty string to None
            row_values.append(value)
        rows_to_write.append(row_values)

    try:
        # Update all cells in one go for efficiency
        worksheet.update(rows_to_write)
        print(f"Successfully migrated data from {json_file_path} to Google Sheet '{worksheet_name}'.")
    except Exception as e:
        print(f"Failed to write data to Google Sheet '{worksheet_name}': {e}")


if __name__ == "__main__":
    # You might need to set up a dummy st.secrets if running this as a completely standalone script
    # and not importing it into your Streamlit app itself.
    # For simplicity, the `get_gsheets_client_for_migration` function now attempts to load secrets.toml.
    
    # You MUST specify the correct worksheet names here for your Google Sheets!
    migrate_data(RECORDS_FILE, "records_sheet_url", 'freediving_records')
    migrate_data(USER_PROFILES_FILE, "user_profiles_sheet_url", 'user_profiles')
    migrate_data(TRAINING_LOG_FILE, "training_log_sheet_url", 'training_log')
    migrate_data(INSTRUCTOR_FEEDBACK_FILE, "instructor_feedback_sheet_url", 'instructor_feedback')

    print("\nMigration process complete. Please check your Google Sheets.")