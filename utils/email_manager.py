import os
import base64
import pickle
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import google_auth_oauthlib.flow

def authenticate_gmail():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                'client_secret_521081729714-dldvp13tso3qih43hbqkdq1dve08a0ts.apps.googleusercontent.com.json',
                scopes=['https://www.googleapis.com/auth/gmail.modify']
            )
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def read_latest_emails(max_results=5):
    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
    messages = results.get('messages', [])

    if not messages:
        return ["No new messages."]

    email_summaries = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        subject = sender = "Unknown"
        for h in headers:
            if h['name'] == 'Subject':
                subject = h['value']
            elif h['name'] == 'From':
                sender = h['value']
        email_summaries.append(f"From {sender}, Subject: {subject}")

    return email_summaries
