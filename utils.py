#!/usr/bin/env python2
# coding: utf-8
from models import Users
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, flash, request
import requests
from sqlalchemy.orm import exc

CLIENT_ID = {
    "google": json.loads(
        open("client_secrets.json", "r").read())["web"]["client_id"],
}


def doGoogleSignIn(app, db_session):

    # Validate state token
    if request.args.get("state") != app.config["SECRET_KEY"]:
        response = make_response(json.dumps("Invalid state parameter."), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets("client_secrets.json", scope="")
        oauth_flow.redirect_uri = "postmessage"
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("Failed to upgrade the authorization code."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s"
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, "GET")[1])
    # If there was an error in the access token info, abort.
    if result.get("error") is not None:
        response = make_response(json.dumps(result.get("error")), 500)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token["sub"]
    if result["user_id"] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify that the access token is valid for this app.
    if result["issued_to"] != CLIENT_ID["google"]:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers["Content-Type"] = "application/json"
        return login_session, response

    stored_access_token = login_session.get("access_token")
    stored_gplus_id = login_session.get("gplus_id")
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps("Current user is already connected."), 200)
        response.headers["Content-Type"] = "application/json"
        return response

    # Store the access token in the session for later use.
    login_session["access_token"] = credentials.access_token
    login_session["gplus_id"] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {"access_token": credentials.access_token, "alt": "json"}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session["username"] = data["name"]
    login_session["picture"] = data["picture"]
    login_session["email"] = data["email"]
    # ADD PROVIDER TO LOGIN SESSION
    login_session["provider"] = "google"

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"], db_session)
    if not user_id:
        user_id = createUser(login_session, db_session)
    login_session["user_id"] = user_id

    output = ""
    output += "<h2>Welcome, "
    output += login_session["username"]
    output += "!</h2>"
    output += "<img src='"
    output += login_session["picture"]
    output += """' style = 'width: 80px; height: 80px;border-radius: 150px;
        -webkit-border-radius: 150px;-moz-border-radius: 150px;'>"""

    flash("you are now logged in as %s" % login_session["username"])
    return output


def doGoogleSignOut():

    # Only disconnect a connected user.
    access_token = login_session.get("access_token")
    if access_token is None:
        response = make_response(
            json.dumps("Current user not connected."), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % access_token
    h = httplib2.Http()
    result = h.request(url, "GET")[0]
    if result["status"] == "200":
        response = make_response(json.dumps("Successfully disconnected."), 200)
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        response = make_response(
            json.dumps("Failed to revoke token for given user.", 400))
        response.headers["Content-Type"] = "application/json"
        return response


def doFacebookSignIn(app, db_session):

    if request.args.get("state") != app.config["SECRET_KEY"]:
        response = make_response(json.dumps("Invalid state parameter."), 401)
        response.headers["Content-Type"] = "application/json"
        return response
    access_token = request.data
    print "access token received %s " % access_token

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/me"

    url = "%s?access_token=%s&fields=name,id,email,picture" % \
        (userinfo_url, access_token)
    h = httplib2.Http()
    result = h.request(url, "GET")[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session["provider"] = "facebook"
    login_session["username"] = data["name"]
    login_session["email"] = data["email"]
    login_session["facebook_id"] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session["access_token"] = access_token

    # Get user picture
    login_session["picture"] = data["picture"]["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session["email"], db_session)
    if not user_id:
        user_id = createUser(login_session, db_session)
    login_session["user_id"] = user_id

    output = ""
    output += "<h2>Welcome, "
    output += login_session["username"]

    output += "!</h2>"
    output += "<img src='"
    output += login_session["picture"]
    output += """' style = 'width: 80px; height: 80px;border-radius: 150px;
        -webkit-border-radius: 150px;-moz-border-radius: 150px;'>"""

    flash("Now logged in as %s" % login_session["username"])
    return output


def doFacebookSignOut():

    facebook_id = login_session["facebook_id"]
    # The access token must me included to successfully logout
    access_token = login_session["access_token"]
    url = "https://graph.facebook.com/%s/permissions?access_token=%s" % \
        (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, "DELETE")[1]
    return "you have been logged out"


def doDisconnect(url_redirect):

    if "provider" in login_session:
        if login_session["provider"] == "google":
            doGoogleSignOut()
            del login_session["gplus_id"]
            del login_session["access_token"]
        if login_session["provider"] == "facebook":
            doFacebookSignOut()
            del login_session["facebook_id"]
        del login_session["username"]
        del login_session["email"]
        del login_session["picture"]
        del login_session["user_id"]
        del login_session["provider"]
        flash("You have successfully been logged out.")
    else:
        flash("You were not logged in")
    return url_redirect


def createUser(login_session, db_session):

    newUser = Users(name=login_session["username"], email=login_session[
                   "email"], picture=login_session["picture"])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(Users) \
                     .filter_by(email=login_session["email"]).one()
    return user.id


def getUserInfo(user_id, db_session):

    user = db_session.query(Users).filter_by(id=user_id).one()
    return user


def getUserID(email, db_session):

    try:
        user = db_session.query(Users).filter_by(email=email).one()
        return user.id
    except exc.NoResultFound, exc.MultipleResultsFound:
        return None


def getSecretKey():

    return "".join(random.choice(string.ascii_uppercase + string.digits)
                   for x in xrange(32))
