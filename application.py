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
outlook_redirect_uri = 'http://localhost:5000/auth/outlook/redirect'
outlookClientSecret = 'b8XmFm=heopQaW/O=mwCz8xJ[RbDMs58'

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
app.config["SESSION_FILE_DIR"] = mkdtemp()
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
        TimeZone = 'America/Los_Angeles' #hardcode placeholder
        StartDate = request.form.get('StartingDate')
        StartTime = request.form.get('StartingTime') + ':00'
        StartDateTime = StartDate + 'T' + StartTime + '-07:00' #ISO 8601 with TimeZone information (hardcoded as PST for now)
        EndDate = request.form.get('EndingDate')
        EndTime = request.form.get('EndingTime') + ':00'
        EndDateTime = EndDate + 'T' + EndTime + '-07:00' #ISO 8601 with TimeZone information (hardcoded as PST for now)
        session['StartOfDay'] = '08:00:00' #placeholder
        session['EndOfDay'] = '17:00:00' #placeholder

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
            print(response.json())
            #print(response.status_code)
            for item in response.json().get('value'):
                print('subject:', item.get('Subject'))
                print('StartDateTime:', item.get('Start').get('DateTime'))
                print('EndDateTime', item.get('End').get('DateTime'))
                print('EndDateTime', item.get('End').get('TimeZone'))

                print('IsCancelled:', item.get('IsCancelled'))
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
                        for i in range(rangeLength):
                            #iterate through dates in range
                            if i == 0:
                                #the first date's starting time will be the event's starting time while ending time will be 23:59
                                if dateRange[i] in events_dict:
                                    events_dict[dateRange[i]].append((EventSubject, StartTime_response, '23:59:59'))
                                else:
                                    events_dict[dateRange[i]] = [(EventSubject, StartTime_response, '23:59:59')]
                            else:
                                #subsequent dates will default to the entire day
                                if dateRange[i] in events_dict:
                                    events_dict[dateRange[i]].append((EventSubject, '00:00:00', '23:59:59'))
                                else:
                                    events_dict[dateRange[i]] = [(EventSubject, '00:00:00', '23:59:59')]
                        #add the final day's event time as starting time equal to start of day and ending time as the event end time
                        if EndDate_response in events_dict:
                            events_dict[EndDate_response].append((EventSubject, '00:00:00', EndTime_response))
                        else:
                            events_dict[EndDate_response] = [(EventSubject, '00:00:00', EndTime_response)]
                        
            print(events_dict)
        return redirect("/")

@app.route("/login", methods=["GET"])
def login(outlookClientID = outlookClientID, outlookAuthURL = outlookAuthURL, outlook_redirect_uri = outlook_redirect_uri):
    """Log user in"""

    # Forget any user_id
    session.clear()

    #Set up OAuth for Outlook
    outlookScope='openID https://outlook.office.com/calendars.read.shared https://outlook.office.com/calendars.read'
    payload = {'client_id': outlookClientID,
                'redirect_uri': outlook_redirect_uri,
                'response_type': 'code',
                'scope': outlookScope
                }
    from urllib.parse import urlencode
    outlookResponse = '%s?%s' % (outlookAuthURL, urlencode(payload))
    return render_template("login.html", outlookResponse = outlookResponse)

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

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

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