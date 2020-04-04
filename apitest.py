import os
import requests
import json
from urllib.parse import urlencode

url = 'https://outlook.office.com/api/v2.0/me/calendarview'
#url = 'https://outlook.office.com/api/v2.0/me/events'
token = 'Bearer eyJ0eXAiOiJKV1QiLCJub25jZSI6InRHX1ZUZnNTMldDYklLSE1vdElkYWM2M1JTY25YQjBxRHAyTzF6YUg3RzgiLCJhbGciOiJSUzI1NiIsIng1dCI6IllNRUxIVDBndmIwbXhvU0RvWWZvbWpxZmpZVSIsImtpZCI6IllNRUxIVDBndmIwbXhvU0RvWWZvbWpxZmpZVSJ9.eyJhdWQiOiJodHRwczovL291dGxvb2sub2ZmaWNlLmNvbSIsImlzcyI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzgzMjlhMzFhLTk5MzgtNDU3Mi1hYTZhLWI4MjU5YmY5MWE1NC8iLCJpYXQiOjE1ODU4ODk1NTIsIm5iZiI6MTU4NTg4OTU1MiwiZXhwIjoxNTg1ODkzNDUyLCJhY2N0IjowLCJhY3IiOiIxIiwiYWlvIjoiQVRRQXkvOFBBQUFBUW9sYUhLdW83eG1TSnJTRlZxNEZ6TkFCN1NhbDZLYml3WS9aMDBnb3Uyb3JHY0RBQ1RWTzN3WUU3OW1LV1VFQSIsImFtciI6WyJwd2QiXSwiYXBwX2Rpc3BsYXluYW1lIjoiTWVldGluZ1NjaGVkdWxlciIsImFwcGlkIjoiM2IyNWQ3NTAtOWIyMS00NzkzLTkxY2YtMjk4ZTgzOTkzMmJmIiwiYXBwaWRhY3IiOiIxIiwiZW5mcG9saWRzIjpbXSwiZmFtaWx5X25hbWUiOiJTZWUiLCJnaXZlbl9uYW1lIjoiS2VubmV0aCIsImlwYWRkciI6IjE2Mi4xOTMuODMuMjQxIiwibmFtZSI6Iktlbm5ldGggU2VlIiwib2lkIjoiYzFlNGNmOTAtMWNlZi00MTJiLTg1ZDQtMTMyZDcxM2Q0ZjZlIiwicHVpZCI6IjEwMDMyMDAwNzA4MzZGQTUiLCJzY3AiOiJDYWxlbmRhcnMuUmVhZCBDYWxlbmRhcnMuUmVhZC5TaGFyZWQiLCJzaWQiOiI4ODY5NTk3Ni1hNTdkLTQzN2QtOWI0Ny02OTQxNjM3MmI1MTMiLCJzaWduaW5fc3RhdGUiOlsia21zaSJdLCJzdWIiOiJXc3RaZ3ZWZEJOSzY1MnR0cERlR3p5VUJXRTduQWo1b3hTUTdVSDRSSnJ3IiwidGlkIjoiODMyOWEzMWEtOTkzOC00NTcyLWFhNmEtYjgyNTliZjkxYTU0IiwidW5pcXVlX25hbWUiOiJrc2VlQGFsbHZ1ZXN5c3RlbXMuY29tIiwidXBuIjoia3NlZUBhbGx2dWVzeXN0ZW1zLmNvbSIsInV0aSI6IjVrUTR4X2dhdUVTRU4tYlpjX2dUQUEiLCJ2ZXIiOiIxLjAifQ.jQyqJ81iS1jBp0EaKZbwslHgE1UWMalHYsjOUtB-wwE_qAePK0Skd_NnBkdypK58NYOWW9QysVoUUu7rJUtSNUZalRJzDsv_Wp28Za2mDb0x4YHYXaklAXRFMGaMqz6jSSnIU7JldWkE8xaoVAvhiEoz1vP59_QAfN55Iy6MvH_gRIniecstTfIym-Pgqwj6MJ7XkA2RkQEARSAhk-up_mytKTN9xMhf7xgshVPcKm0OPhOkujx_DuTs69r_Qak85ZP9CcS7Rrg9frzXpbXuUtOn8XTIT-YjEW7TR6JNAQ43d_TE92Fyy17-yYsjRGROBIOXZNcJvbMYUQcuaXJvrg'


headers = {
    'Authorization': token,
    'Prefer': 'outlook.timezone="Pacific Standard Time"',
    'content-type' : 'application/json',
}
payload = {
    'startDateTime': '2020-04-02T08:00:00-08:00',
    'endDateTime': '2020-04-02T20:00:00-08:00',
    '$Select': 'Subject, Start, End'
}

response = requests.get(url, headers=headers, params=payload)
print(response.status_code)
#print(response.json())
for item in response.json().get('value'):
    print(item.get('Subject'))
    StartDateTime = item.get('Start').get('DateTime')
    EndDateTime = item.get('End').get('DateTime')
    StartDate, StartTime = str(StartDateTime).split("T")
    EndDate, EndTime = str(EndDateTime).split("T")
    print(StartDate, StartTime, EndDate, EndTime)

