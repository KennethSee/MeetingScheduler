import os
from datetime import datetime
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import base64
from bs4 import BeautifulSoup

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
def index():
    return redirect("/index")

@app.route("/index", methods=["GET", "POST"])
def main():
    if request.method == "GET":
        conn = 'https://login.microsoftonline.com'
        connRequest = '/common/oauth2/v2.0/authorize'

        clientID = '3b25d750-9b21-4793-91cf-298e839932bf'
        clientSecret = 'b8XmFm=heopQaW/O=mwCz8xJ[RbDMs58'
        redirect_uri = 'http://localhost:5000/'
        scope='openID'
        payload = {'client_id': clientID,
                    'redirect_uri': redirect_uri,
                    'response_type': 'code',
                    'scope': scope
                    }
        from urllib.parse import urlencode
        #response = requests.get(conn + connRequest,params=payload)
        response = '%s?%s' % (conn+connRequest, urlencode(payload))
        return render_template('index.html', response=response)

    if request.method == "POST":
        return redirect("/")

if __name__ == "__main__":
    app.run()
