import os
from datetime import datetime
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from urllib.parse import urlencode
import json
from collections import defaultdict

from helpers import *

# Declare global variables
outlookAuthURL = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
outlookTokenURL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
outlookCalendarViewURL = 'https://outlook.office.com/api/v2.0/me/calendarview'
outlookClientID = '3b25d750-9b21-4793-91cf-298e839932bf'
outlook_redirect_uri = 'https://meetingscheduler-api-heroku.herokuapp.com/auth/outlook/redirect'
outlookClientSecret = 'b8XmFm=heopQaW/O=mwCz8xJ[RbDMs58'
# outlookClientID = '51cd3d07-6ee7-4b99-a30d-8279cfd4c085' #dev
# outlook_redirect_uri = 'http://localhost:5000/auth/outlook/redirect' #dev
# outlookClientSecret = 'D28.UvsM29Yb/?TNXTx[t-u6FEmJt61E' #dev
googleAuthURL = 'https://accounts.google.com/o/oauth2/v2/auth'
googleTokenURL = 'https://oauth2.googleapis.com/token'
googleCalendarViewURL = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
googleClientID = '577148182452-id7orf0jisg8dt756c6venquse331thn.apps.googleusercontent.com'
googleClientSecret = 'nqLtrVMkcu6rkTy-uDGLY6KD'
google_redirect_uri = 'https://meetingscheduler-api-heroku.herokuapp.com/auth/google/redirect'
googleAPIKey = 'AIzaSyAz8L0MDA-1VBpcsBijScmBKMVr8N56i3E'

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
# app.jinja_env.filters["currencify"] = currencify

# Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():
    return redirect("/index")

@app.route("/index", methods=["GET", "POST"])
@login_required
def main():
    if request.method == "GET":
        return render_template('index.html')

    if request.method == "POST":
        accessToken = session["access_token"]
        source = session["calendar_source"]
        events_dict = defaultdict()
        
        # get user-specified parameters
        TimeZone = request.form.get('TimeZone')
        TimeZoneOffset = datetime.now(pytz.timezone(TimeZone)).strftime('%z')
        TimeZoneOffset = TimeZoneOffset[:3] + ':' + TimeZoneOffset[3:]
        StartDate = request.form.get('StartingDate')
        StartTime = request.form.get('StartingTime') + ':00'
        session['StartDate'] = StartDate
        session['StartTime'] = StartTime
        StartDateTime = StartDate + 'T' + StartTime + TimeZoneOffset #ISO 8601 with TimeZone information
        EndDate = request.form.get('EndingDate')
        EndTime = request.form.get('EndingTime') + ':00'
        session['EndDate'] = EndDate
        session['EndTime'] = EndTime
        EndDateTime = EndDate + 'T' + EndTime + TimeZoneOffset #ISO 8601 with TimeZone information
        session['StartOfDay'] = request.form.get('TimeWindowStart') + ':00'
        session['EndOfDay'] = request.form.get('TimeWindowEnd') + ':00'
        session['TimeInterval'] = request.form.get('TimeInterval')
        
        # Record which days of the week the user has indicated to check
        DayOfTheWeek_list = []
        if request.form.get('MondayCheck') is None:
            DayOfTheWeek_list.append(0)
        else:
            DayOfTheWeek_list.append(1)
        if request.form.get('TuesdayCheck') is None:
            DayOfTheWeek_list.append(0)
        else:
            DayOfTheWeek_list.append(1)
        if request.form.get('WednesdayCheck') is None:
            DayOfTheWeek_list.append(0)
        else:
            DayOfTheWeek_list.append(1)
        if request.form.get('ThursdayCheck') is None:
            DayOfTheWeek_list.append(0)
        else:
            DayOfTheWeek_list.append(1)
        if request.form.get('FridayCheck') is None:
            DayOfTheWeek_list.append(0)
        else:
            DayOfTheWeek_list.append(1)
        if request.form.get('SaturdayCheck') is None:
            DayOfTheWeek_list.append(0)
        else:
            DayOfTheWeek_list.append(1)
        if request.form.get('SundayCheck') is None:
            DayOfTheWeek_list.append(0)
        else:
            DayOfTheWeek_list.append(1)
        session['DayOfTheWeek'] = DayOfTheWeek_list

        if source == 'outlook':
            #make API GET request to Outlook
            headers = {
                'Authorization': 'Bearer ' + accessToken,
                'Prefer': 'outlook.timezone="' + TimeZone + '"',
                'content-type' : 'application/json'
            }
            params = {
                'startDateTime': StartDateTime,
                'endDateTime': EndDateTime,
                '$Select': 'Subject, Start, End, IsCancelled, ShowAs, IsAllDay',
                '$Top': 1000
            }
            response = requests.get(outlookCalendarViewURL, headers=headers, params=params)
            #check to make sure request was successful
            if response.status_code != 200:
                return apology('Unable to retrieve calendar information', response.status_code)
                        
            for item in response.json().get('value'):
                if (item.get('ShowAs') == 'Busy' or item.get('ShowAs') == 'Oof') and item.get('IsCancelled') != 1:
                    #check that event is not cancelled or marked as free or working elsewhere
                    EventSubject = item.get('Subject')
                    StartDateTime_response = item.get('Start').get('DateTime')
                    EndDateTime_response = item.get('End').get('DateTime')
                    StartDate_response, StartTime_response = str(StartDateTime_response).split("T")
                    EndDate_response, EndTime_response = str(EndDateTime_response).split("T")
                    if item.get('IsAllDay') == 1:
                        #check if event is an all day event
                        StartTime_response = '00:00:00'
                        EndTime_response = '23:59:59'
                    else:
                        StartTime_response = StartTime_response[0:8]
                        EndTime_response = EndTime_response[0:8]
                    if StartDate_response == EndDate_response:
                        #Check event date is already in dictionary
                        if StartDate_response in events_dict:
                            events_dict[StartDate_response].append((EventSubject, StartTime_response, EndTime_response))
                        else:
                            events_dict[StartDate_response] = [(EventSubject, StartTime_response, EndTime_response)]
                    else:
                        rangeLength, dateRange = daterange(StartDate_response, EndDate_response)
                        for i in range(rangeLength + 1):
                            #iterate through dates in range
                            if i == 0:
                                #the first date's starting time will be the event's starting time while ending time will be 23:59
                                if dateRange[i] in events_dict:
                                    events_dict[dateRange[i]].append((EventSubject, StartTime_response, '23:59:59'))
                                else:
                                    events_dict[dateRange[i]] = [(EventSubject, StartTime_response, '23:59:59')]
                            elif i == rangeLength:
                                #add the final day's event time as starting time equal to start of day and ending time as the event end time
                                if EndDate_response in events_dict:
                                    events_dict[EndDate_response].append((EventSubject, '00:00:00', EndTime_response))
                                else:
                                    events_dict[EndDate_response] = [(EventSubject, '00:00:00', EndTime_response)]
                            else:
                                #subsequent dates will default to the entire day
                                if dateRange[i] in events_dict:
                                    events_dict[dateRange[i]].append((EventSubject, '00:00:00', '23:59:59'))
                                else:
                                    events_dict[dateRange[i]] = [(EventSubject, '00:00:00', '23:59:59')]
            session['calendar_schedule'] = events_dict
            print(events_dict)
        elif source == 'google':
            #make API GET request to Google
            headers = {
                'Authorization': 'Bearer ' + accessToken,
                'Accept' : 'application/json'
            }
            params = {
                'timeMin': StartDateTime,
                'timeMax': EndDateTime,
                'maxResults': 1000,
                'timezone': TimeZone,
                'key': googleAPIKey
            }
            response = requests.get(googleCalendarViewURL, headers=headers, params=params)
            #print(response.json())
            #check to make sure request was successful
            if response.status_code != 200:
                return apology('Unable to retrieve calendar information', response.status_code)

            for item in response.json().get('items'):
                EventSubject = item.get('summary')
                StartDateTime_response = item.get('start').get('dateTime')
                EndDateTime_response = item.get('end').get('dateTime')
                StartDate_response, StartTime_response = str(StartDateTime_response).split("T")
                EndDate_response, EndTime_response = str(EndDateTime_response).split("T")

                #format response times to only display HH:MM:SS
                StartTime_response = StartTime_response[0:8]
                EndTime_response = EndTime_response[0:8]

                if StartDate_response == EndDate_response:
                    #Check event date is already in dictionary
                    if StartDate_response in events_dict:
                        events_dict[StartDate_response].append((EventSubject, StartTime_response, EndTime_response))
                    else:
                        events_dict[StartDate_response] = [(EventSubject, StartTime_response, EndTime_response)]
                else:
                    rangeLength, dateRange = daterange(StartDate_response, EndDate_response)
                    for i in range(rangeLength + 1):
                        #iterate through dates in range
                        if i == 0:
                            #the first date's starting time will be the event's starting time while ending time will be 23:59
                            if dateRange[i] in events_dict:
                                events_dict[dateRange[i]].append((EventSubject, StartTime_response, '23:59:59'))
                            else:
                                events_dict[dateRange[i]] = [(EventSubject, StartTime_response, '23:59:59')]
                        elif i == rangeLength:
                            #add the final day's event time as starting time equal to start of day and ending time as the event end time
                            if EndDate_response in events_dict:
                                events_dict[EndDate_response].append((EventSubject, '00:00:00', EndTime_response))
                            else:
                                events_dict[EndDate_response] = [(EventSubject, '00:00:00', EndTime_response)]
                        else:
                            #subsequent dates will default to the entire day
                            if dateRange[i] in events_dict:
                                events_dict[dateRange[i]].append((EventSubject, '00:00:00', '23:59:59'))
                            else:
                                events_dict[dateRange[i]] = [(EventSubject, '00:00:00', '23:59:59')]
            session['calendar_schedule'] = events_dict
        return redirect("/scheduleoutput")

@app.route("/scheduleoutput", methods=["GET"])
@login_required
def output():
    calendar_schedule = session['calendar_schedule']
    StartDate = session['StartDate']
    StartTime = session['StartTime']
    EndDate = session['EndDate']
    EndTime = session['EndTime']
    StartOfDay = session['StartOfDay']
    EndOfDay = session['EndOfDay']
    DayOfTheWeek = session['DayOfTheWeek']

    #format dates to display Month_Name DD YYYY
    StartDate_formatted = dateFormat(StartDate)
    EndDate_formatted = dateFormat(EndDate)

    #logic to get free times for each day
    output = []
    rangeLength, dateRange = daterange(StartDate, EndDate)
    for i in range(rangeLength + 1):
        #check that date is part of checked day of the week
        weekday_num = datetime.strptime(dateRange[i], '%Y-%m-%d').weekday() #get day of the week where Monday = 0 and Sunday = 7
        #print('weekday:', weekday_num)
        if DayOfTheWeek[weekday_num] == 0:
            #skip over the day
            pass
        else:
            #assign temporal start and end times of the day
            if StartDate == dateRange[i] and StartTime > StartOfDay:
                StartOfDay_temporal = StartTime
            else:
                StartOfDay_temporal = StartOfDay
            if EndDate == dateRange[i] and EndTime < EndOfDay:
                EndOfDay_temporal = EndTime
            else:
                EndOfDay_temporal = EndOfDay

            if dateRange[i] in calendar_schedule:
                events = calendar_schedule.get(dateRange[i])
                schedule = []
                for event in events:
                    eventStartTime = event[1]
                    eventEndTime = event[2]
                    schedule.append((eventStartTime,eventEndTime))
                schedule.sort(key=lambda x:x[0])
                #merge overlapping events
                mergeCount = 1
                while mergeCount > 0:
                    mergeCount, schedule = scheduleMerge(schedule)

                #remove any events that do not fall within user-defined time window
                schedule_clean = []
                for event in schedule:
                    if event[1] > StartOfDay_temporal and event[0] < EndOfDay_temporal:
                        schedule_clean.append(event)
                if len(schedule_clean) == 0:
                    pass
                else:
                    #adjust start and end of days if necessary
                    if schedule_clean[0][0] <= StartOfDay_temporal:
                        #set start of day to end of first event
                        StartOfDay_temporal = schedule_clean[0][1]
                        schedule_clean.pop(0)
                    if len(schedule_clean) > 0:
                        if schedule_clean[-1][1] >= EndOfDay_temporal:
                            #set end of day to start of first event
                            EndOfDay_temporal = schedule_clean[-1][0]
                            schedule_clean.pop(-1)
                    if EndOfDay_temporal < StartOfDay_temporal:
                        #if adjusted start and end of day times result in no time windows available, mark entire day as busy
                        pass
                    else:
                        #get free time windows
                        StartTimes = []
                        EndTimes = []
                        if len(schedule_clean) == 0:
                            output.append([dateFormat(dateRange[i]), [StartOfDay_temporal], [EndOfDay_temporal]])
                        else:
                            for j in range(len(schedule_clean) + 1):
                                if j == 0:
                                    StartTimes.append(StartOfDay_temporal)
                                    EndTimes.append(schedule_clean[j][0])
                                elif j == len(schedule_clean):
                                    StartTimes.append(schedule_clean[len(schedule_clean) - 1][1])
                                    EndTimes.append(EndOfDay_temporal)
                                else:
                                    StartTimes.append(schedule_clean[j-1][1])
                                    EndTimes.append(schedule_clean[j][0])
                            output.append([dateFormat(dateRange[i]), StartTimes, EndTimes])
            else:
                #the entire day is free if date is not in calendar_schedule
                output.append([dateFormat(dateRange[i]), [StartOfDay_temporal], [EndOfDay_temporal]])

    output_formatted = []
    timeInterval = session['TimeInterval']
    for item in output:
        date = item[0]
        timeWindows = []
        for k in range(len(item[1])):
            if int((datetime.strptime(item[2][k], '%H:%M:%S') - datetime.strptime(item[1][k], '%H:%M:%S')).seconds / 60) >= int(timeInterval):
                #only add in time window if it is greater than the minimum time interval
                timeWindows.append(item[1][k] + ' - ' + item[2][k])
        output_formatted.append([date, timeWindows])
    return render_template('scheduleoutput.html', StartDate=StartDate_formatted, EndDate=EndDate_formatted, output=output_formatted)

@app.route("/login", methods=["GET"])
def login(outlookClientID = outlookClientID, outlookAuthURL = outlookAuthURL, outlook_redirect_uri = outlook_redirect_uri):
    """Log user in"""

    # Forget any user_id
    session.clear()

    #Set up OAuth for Outlook
    outlookScope= 'openID https://outlook.office.com/calendars.read.shared https://outlook.office.com/calendars.read'
    outlookPayload = {'client_id': outlookClientID,
                'redirect_uri': outlook_redirect_uri,
                'response_type': 'code',
                'scope': outlookScope
                }
    outlookResponse = '%s?%s' % (outlookAuthURL, urlencode(outlookPayload))

    #Set up OAuth for Google
    googleScope = 'openid https://www.googleapis.com/auth/calendar.readonly'
    googlePayload = {'client_id': googleClientID,
                'redirect_uri': google_redirect_uri,
                'response_type': 'code',
                'scope': googleScope
    }
    googleResponse = '%s?%s' % (googleAuthURL, urlencode(googlePayload))
    return render_template("login.html", outlookResponse = outlookResponse, googleResponse = googleResponse)

@app.route("/auth/outlook/redirect")
def outlookAuth(ClientID = outlookClientID, ClientSecret = outlookClientSecret, RedirectURI = outlook_redirect_uri, url = outlookTokenURL):
    #obtain authorization code
    authorizationCode = request.args.get('code')
    
    #get access token
    payload = {'client_id': ClientID,
                'client_secret': ClientSecret,
                'code': authorizationCode,
                'redirect_uri': RedirectURI,
                'grant_type': 'authorization_code'
                }
    headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'accept': 'application/json'
                }
    response = requests.post(url, data=payload, headers=headers)
    responseJSON = response.json()
    accessToken = responseJSON.get('access_token')

    # store accessToken and calendar source
    session["access_token"] = accessToken
    session["calendar_source"] = 'outlook'

    # tell the server that login was successful
    session["user_id"] = 1
    return redirect("/")

@app.route("/auth/google/redirect")
def googleAuth(ClientID = googleClientID, ClientSecret = googleClientSecret, RedirectURI = google_redirect_uri, url = googleTokenURL):
    #obtain authorization code
    authorizationCode = request.args.get('code')
    
    #get access token
    payload = {'client_id': ClientID,
                'client_secret': ClientSecret,
                'code': authorizationCode,
                'redirect_uri': RedirectURI,
                'grant_type': 'authorization_code'
                }
    headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'accept': 'application/json'
                }
    response = requests.post(url, data=payload, headers=headers)
    responseJSON = response.json()
    accessToken = responseJSON.get('access_token')

    # store accessToken and calendar source
    session["access_token"] = accessToken
    session["calendar_source"] = 'google'

    # tell the server that login was successful
    session["user_id"] = 1
    return redirect("/")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/privacy")
def privacy():
    return render_template('privacy.html')

if __name__ == "__main__":
    app.run()

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)