import os
import pickle
import datetime
from datetime import timedelta
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Set up the Google Calendar API
def authenticate_google_account():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('client_secret_521081729714-c2h5djouqkmsv00iru4fq3ntnf9mulv6.apps.googleusercontent.com.json'):
                    raise FileNotFoundError("credentials.json not found. Please download it from Google Cloud Console.")
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    'client_secret_521081729714-c2h5djouqkmsv00iru4fq3ntnf9mulv6.apps.googleusercontent.com.json', 
                    scopes=['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/gmail.modify'],
                    redirect_uri='http://localhost:8080/'  # No trailing slash
                )
                creds = flow.run_local_server(port=8080)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return None

    return build('calendar', 'v3', credentials=creds)

def get_events_for_day(target_date):
    service = authenticate_google_account()

    start = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + 'Z'
    end = datetime.datetime.combine(target_date + timedelta(days=1), datetime.time.min).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    event_list = []

    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No Title')
        event_list.append(f"{summary} at {start_time}")

    return event_list if event_list else ["No events found for this day."]


def add_event_to_calendar(description, start_time):
    service = authenticate_google_account()
    if not service:
        print("Authentication failed.")
        return

    event = {
        'summary': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': (start_time + timedelta(hours=1)).isoformat(),
            'timeZone': 'America/New_York',
        },
    }

    try:
        event_result = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event_result.get('htmlLink')}")
    except Exception as e:
        print(f"Error creating event: {e}")


def get_events_between(start_date, end_date):
    service = authenticate_google_account()
    start = datetime.datetime.combine(start_date, datetime.time.min).isoformat() + 'Z'
    end = datetime.datetime.combine(end_date, datetime.time.min).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    event_list = []

    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No Title')
        event_list.append(f"{summary} at {start_time}")

    return event_list if event_list else ["No events found in this range."]


def delete_event_by_summary(search_summary, start_date, end_date):
    service = authenticate_google_account()
    if not service:
        return "Authentication failed."

    start = datetime.datetime.combine(start_date, datetime.time.min).isoformat() + 'Z'
    end = datetime.datetime.combine(end_date, datetime.time.max).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    deleted = False

    for event in events:
        summary = event.get('summary', '').lower()
        if search_summary.lower() in summary:
            try:
                service.events().delete(calendarId='primary', eventId=event['id']).execute()
                deleted = True
                print(f"Deleted event: {event['summary']}")
            except Exception as e:
                print(f"Failed to delete event: {e}")
                return "Failed to delete the event."

    return "Reminder deleted." if deleted else "No matching reminder found."

