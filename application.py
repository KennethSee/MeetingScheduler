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

from helpers import *

# Declare global variables
outlookAuthURL = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
outlookTokenURL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
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
        return redirect("/")

@app.route("/login", methods=["GET"])
def login(outlookClientID = outlookClientID, outlookAuthURL = outlookAuthURL, outlook_redirect_uri = outlook_redirect_uri):
    """Log user in"""

    # Forget any user_id
    session.clear()

    #Set up OAuth for Outlook
    outlookScope='openID https://outlook.office.com/calendars.read'
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
    print(accessToken)
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