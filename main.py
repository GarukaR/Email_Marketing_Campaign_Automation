import os
import base64
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.message import EmailMessage
import time

while True:
    # Get input from user for LIMIT and ACTION_MODE
    LIMIT = int(input("Enter the number of rows to process (e.g., 50): "))
    ACTION_MODE = input("Type 'draft' to save emails as drafts, or 'send' to send them directly: ").strip().lower()

    # Fallback to draft if the user types something invalid
    if ACTION_MODE not in ['draft', 'send']:
        print("Invalid input. Defaulting to 'draft' mode for safety.")
        ACTION_MODE = 'draft'

    # SCOPES: Now including both Gmail and Sheets
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/spreadsheets'
    ]

    # --- SETTINGS ---
    time_delay_between_emails = 15  # seconds
    test_email_filter = []  # Add specific emails here for testing, e.g., ['test@example.com']
    LOGO_URL = "XXXXXXXXXX"
    SPREADSHEET_ID = 'XXXXXXXXXXXXXXXX' 
    SHEET_NAME = 'XXXXXXXXXXX'  # Adjust if your sheet name is different
    RANGE_NAME = f'{SHEET_NAME}!A2:G' # Adjust if your sheet name is different
    TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cold Email Template - Data Automation</title>
        <style>
            /* Notice the double braces here so Python ignores them */
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                background-color: #f4f7f6;
                margin: 0;
                padding: 20px;
            }}

            .email-container {{
                background-color: #ffffff;
                max-width: 600px;
                width: 100%;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                box-sizing: border-box;
                margin: 0 auto;
            }}

            p {{
                margin-bottom: 16px;
            }}

            p:last-child {{
                margin-bottom: 0;
            }}

            @media (max-width: 480px) {{
                .email-container {{
                    padding: 20px;
                }}
                body {{
                    padding: 10px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <p>Hi {first_name},</p>
        
            <p>I noticed your {company} lorem ipsum <b>lorem ipsum</b></p>
            
            <p>lorem ipsum <b>Sales Strategy and Data Automation</b>.
            Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
            
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
            <p>Do you have a reporting blockers that’s currently slowing you down?</p>
            
            <p>Cheers,<br>Garuka.</p>
        </div>

    </body>
    </html>
    """

    def get_services():
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                
        return build('gmail', 'v1', credentials=creds), build('sheets', 'v4', credentials=creds)

    def main():
        gmail, sheets = get_services()
        
        # 1. Fetch data from Google Sheets
        result = sheets.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        rows = result.get('values', [])
        processed_count = 0

        if not rows:
            print("No data found.")
            return

        # 2. Process each row
        for i, row in enumerate(rows):
            # Helper function to safely get column data or return empty string
            def get_col(idx, default=""):
                return row[idx] if len(row) > idx else default

            try:
                name = get_col(0)
                email = get_col(1)
                company = get_col(4)
                sent_status = get_col(5)
                # Logic: Use Col G, if empty use split name, if still empty use "there"
                first_name = get_col(6) or (name.split()[0] if name else "there")
                
            except Exception as e:
                print(f"Skipping row {i+2} due to data error: {e}")
                continue
            
            #Clean email and company fields
            # Convert to string and remove whitespace
            clean_email = str(email).strip() if email is not None else ""

            # Check if it's empty or a 'nan' placeholder
            if not clean_email or clean_email.lower() == 'nan':
                print(f"Skipped - Invalid or missing email: '{name}' at row {i+2}")
                continue
            
            # Filter Logic
            if sent_status.lower() == 'yes':
                continue
            
            if i >= LIMIT:  # Limit to first LIMIT rows for testing
                print(f"Reached {LIMIT} rows, stopping execution.")
                break
            
            if i >= rows.index(rows[-1]) + 1:  # Stop if we go beyond available rows
                print("Reached the end of available rows, stopping execution.")
                break
            
            # # Only process if email is in the test_email_filter list TEST CASE
            # if clean_email not in test_email_filter:
            #     continue

            try:
                # Create Gmail Message
                msg = EmailMessage()
                msg['Subject'] = f"Subject at {company}"
                msg['To'] = clean_email
                
                # Add HTML body
                msg.add_alternative(
                    TEMPLATE.format(first_name=first_name, company=company, LOGO_URL=LOGO_URL),
                    subtype='html'
                )
                
                raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode()
                
                # Check user preference: Send or Draft
                if ACTION_MODE == 'send':
                    time.sleep(time_delay_between_emails)
                    gmail.users().messages().send(userId='me', body={'raw': raw_msg}).execute()
                    action_logged = "Email Sent"
                else:
                    gmail.users().drafts().create(userId='me', body={'message': {'raw': raw_msg}}).execute()
                    action_logged = "Draft Created"

                # 3. Update the Google Sheet (Column F = column 6)
                cell_range = f'{SHEET_NAME}!F{i+2}'
                sheets.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID, 
                    range=cell_range,
                    valueInputOption='USER_ENTERED',
                    body={'values': [['yes']]}
                ).execute()

                print(f"{action_logged} and Sheet updated for {name}")
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing {clean_email}: {e}")

        print(f"Total rows processed: {processed_count}")

    if __name__ == '__main__':
        main()