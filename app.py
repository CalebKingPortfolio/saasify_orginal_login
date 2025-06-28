import os
import pathlib
import requests
from flask import Flask, render_template, session, redirect, request, abort
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from datetime import timedelta
import logging
from datetime import datetime

app = Flask("SaaSify Google Login")
app.secret_key = "esc70wegQpJ9jTBia4eWEdpqy9r49cAU"
app.permanent_session_lifetime = timedelta(minutes=15)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

logging.basicConfig(
    filename='login_events.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

GOOGLE_CLIENT_ID = (
    "362632682751-mn02ajnfa960bh48d20e3afb3rke00ea.apps.googleusercontent.com"
)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json"
)

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_uri="http://127.0.0.1:5000/callback"  
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if session.get("state") != request.args.get("state"):
        return abort(400)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session.permanent = True
    session["user_email"] = id_info.get("email")
    session["user_name"] = id_info.get("name")


    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    logging.info(f"User {session['user_email']} ({session['user_name']}) logged in from IP {user_ip}")

    return redirect("/protected_area")


@app.route("/protected_area")
def protected_area():
    if "user_email" not in session:
        return redirect("/")
    return render_template("protected_area.html", user_name=session["user_name"])


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  
