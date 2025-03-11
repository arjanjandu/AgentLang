# gmail_helper.py
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Define the scope for read-only access to Gmail.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_most_recent_email():
    """Get the subject and snippet of the most recent email."""
    creds = None
    # token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This will open a browser window for authentication.
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Build the Gmail service.
    service = build('gmail', 'v1', credentials=creds)
    
    # List messages with maxResults=1 to get the most recent email.
    results = service.users().messages().list(userId='me', maxResults=1).execute()
    messages = results.get('messages', [])
    if not messages:
        return "No messages found."
        
    # Get the ID of the most recent message.
    message_id = messages[0]['id']
    # Retrieve the message details.
    message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    
    # Extract some useful details: snippet and subject.
    snippet = message.get('snippet', 'No snippet available')
    
    subject = "No subject found"
    headers = message.get('payload', {}).get('headers', [])
    for header in headers:
        if header.get('name') == 'Subject':
            subject = header.get('value')
            break
    
    # Return the formatted result
    return f"Most Recent Email:\nSubject: {subject}\nSnippet: {snippet}"

if __name__ == '__main__':
    print(get_most_recent_email())