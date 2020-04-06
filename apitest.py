from __future__ import print_function
import os
import requests
import json
from urllib.parse import urlencode
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# url = 'https://outlook.office.com/api/v2.0/me/calendarview'
# #url = 'https://outlook.office.com/api/v2.0/me/events'
# token = 'Bearer eyJ0eXAiOiJKV1QiLCJub25jZSI6InRHX1ZUZnNTMldDYklLSE1vdElkYWM2M1JTY25YQjBxRHAyTzF6YUg3RzgiLCJhbGciOiJSUzI1NiIsIng1dCI6IllNRUxIVDBndmIwbXhvU0RvWWZvbWpxZmpZVSIsImtpZCI6IllNRUxIVDBndmIwbXhvU0RvWWZvbWpxZmpZVSJ9.eyJhdWQiOiJodHRwczovL291dGxvb2sub2ZmaWNlLmNvbSIsImlzcyI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzgzMjlhMzFhLTk5MzgtNDU3Mi1hYTZhLWI4MjU5YmY5MWE1NC8iLCJpYXQiOjE1ODU4ODk1NTIsIm5iZiI6MTU4NTg4OTU1MiwiZXhwIjoxNTg1ODkzNDUyLCJhY2N0IjowLCJhY3IiOiIxIiwiYWlvIjoiQVRRQXkvOFBBQUFBUW9sYUhLdW83eG1TSnJTRlZxNEZ6TkFCN1NhbDZLYml3WS9aMDBnb3Uyb3JHY0RBQ1RWTzN3WUU3OW1LV1VFQSIsImFtciI6WyJwd2QiXSwiYXBwX2Rpc3BsYXluYW1lIjoiTWVldGluZ1NjaGVkdWxlciIsImFwcGlkIjoiM2IyNWQ3NTAtOWIyMS00NzkzLTkxY2YtMjk4ZTgzOTkzMmJmIiwiYXBwaWRhY3IiOiIxIiwiZW5mcG9saWRzIjpbXSwiZmFtaWx5X25hbWUiOiJTZWUiLCJnaXZlbl9uYW1lIjoiS2VubmV0aCIsImlwYWRkciI6IjE2Mi4xOTMuODMuMjQxIiwibmFtZSI6Iktlbm5ldGggU2VlIiwib2lkIjoiYzFlNGNmOTAtMWNlZi00MTJiLTg1ZDQtMTMyZDcxM2Q0ZjZlIiwicHVpZCI6IjEwMDMyMDAwNzA4MzZGQTUiLCJzY3AiOiJDYWxlbmRhcnMuUmVhZCBDYWxlbmRhcnMuUmVhZC5TaGFyZWQiLCJzaWQiOiI4ODY5NTk3Ni1hNTdkLTQzN2QtOWI0Ny02OTQxNjM3MmI1MTMiLCJzaWduaW5fc3RhdGUiOlsia21zaSJdLCJzdWIiOiJXc3RaZ3ZWZEJOSzY1MnR0cERlR3p5VUJXRTduQWo1b3hTUTdVSDRSSnJ3IiwidGlkIjoiODMyOWEzMWEtOTkzOC00NTcyLWFhNmEtYjgyNTliZjkxYTU0IiwidW5pcXVlX25hbWUiOiJrc2VlQGFsbHZ1ZXN5c3RlbXMuY29tIiwidXBuIjoia3NlZUBhbGx2dWVzeXN0ZW1zLmNvbSIsInV0aSI6IjVrUTR4X2dhdUVTRU4tYlpjX2dUQUEiLCJ2ZXIiOiIxLjAifQ.jQyqJ81iS1jBp0EaKZbwslHgE1UWMalHYsjOUtB-wwE_qAePK0Skd_NnBkdypK58NYOWW9QysVoUUu7rJUtSNUZalRJzDsv_Wp28Za2mDb0x4YHYXaklAXRFMGaMqz6jSSnIU7JldWkE8xaoVAvhiEoz1vP59_QAfN55Iy6MvH_gRIniecstTfIym-Pgqwj6MJ7XkA2RkQEARSAhk-up_mytKTN9xMhf7xgshVPcKm0OPhOkujx_DuTs69r_Qak85ZP9CcS7Rrg9frzXpbXuUtOn8XTIT-YjEW7TR6JNAQ43d_TE92Fyy17-yYsjRGROBIOXZNcJvbMYUQcuaXJvrg'


# headers = {
#     'Authorization': token,
#     'Prefer': 'outlook.timezone="Pacific Standard Time"',
#     'content-type' : 'application/json',
# }
# payload = {
#     'startDateTime': '2020-04-02T08:00:00-08:00',
#     'endDateTime': '2020-04-02T20:00:00-08:00',
#     '$Select': 'Subject, Start, End'
# }

# response = requests.get(url, headers=headers, params=payload)
# print(response.status_code)
# #print(response.json())
# for item in response.json().get('value'):
#     print(item.get('Subject'))
#     StartDateTime = item.get('Start').get('DateTime')
#     EndDateTime = item.get('End').get('DateTime')
#     StartDate, StartTime = str(StartDateTime).split("T")
#     EndDate, EndTime = str(EndDateTime).split("T")
#     print(StartDate, StartTime, EndDate, EndTime)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'googleCredentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


if __name__ == '__main__':
    main()