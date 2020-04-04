import os
import requests
import urllib.parse
import json

from flask import redirect, render_template, request, session
from functools import wraps
from datetime import timedelta, date, datetime

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
    for n in range(dayCount):
        date_unformatted = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(n)
        date_formatted = date_unformatted.strftime('%Y-%m-%d')
        dates.append(date_formatted)
    return n, dates

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

print(min(datetime.strptime('16:00:00','%H:%M:%S').time(), datetime.strptime('23:00:00','%H:%M:%S').time()))