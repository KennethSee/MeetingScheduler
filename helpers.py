import os
import requests
import urllib.parse
import json

from flask import redirect, render_template, request, session
from functools import wraps
from datetime import timedelta, date, datetime
import pytz

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

from datetime import timedelta, date

def daterange(start_date, end_date):
    dates = []
    dayCount = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days
    for n in range(dayCount + 1):
        date_unformatted = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(n)
        date_formatted = date_unformatted.strftime('%Y-%m-%d')
        dates.append(date_formatted)
    return dayCount, dates

def dateFormat(date):
    '''
    Transforms strings of dates from the format of YYYY-MM-DD to Month_Name DD YYYY
    '''
    date_unformatted = datetime.strptime(date, '%Y-%m-%d')
    date_formatted = date_unformatted.strftime('%b %d %Y')
    return date_formatted

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                        ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", code=code, message=message), code

def scheduleMerge(schedule):
    schedule_merged = []
    mergeCount = 0
    HasMerged = 0
    if len(schedule) == 1:
        return mergeCount, schedule
    for i in range(len(schedule)):
        if i == 0:
            if schedule[i][1] >= schedule[i+1][0]: #check if ending time of current event is equal or greater than starting time of next event
                #merge with next event
                schedule_merged.append((schedule[i][0], max(schedule[i][1], schedule[i+1][1])))
                mergeCount = mergeCount + 1
                HasMerged = 1
            else:
                schedule_merged.append(schedule[i])
        elif i == len(schedule) - 1:
            if HasMerged == 1:
                #merge action should have already been performed when iterating through previous event
                HasMerged = 0
                pass
            else:
                schedule_merged.append(schedule[i])
        else:
            if HasMerged == 1:
                #merge action should have already been performed when iterating through previous event
                HasMerged = 0
                pass
            elif schedule[i][1] >= schedule[i+1][0]: #check if ending time of current event is equal or greater than starting time of next event
                #merge with next event
                schedule_merged.append((schedule[i][0], max(schedule[i][1], schedule[i+1][1])))
                mergeCount = mergeCount + 1
                HasMerged = 1
            else:
                schedule_merged.append(schedule[i])
    return mergeCount, schedule_merged
