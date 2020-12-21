#!/usr/bin/env python3
import os

from flask import Flask
from flask import redirect
from flask import render_template
from flask import url_for
from flask import abort
from flask import session
from flask import request
from flask_dance.consumer import OAuth2ConsumerBlueprint
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

from aux.logs import log2term
import db_users as db

app = Flask(__name__)


########################################################
#                 FLASK API ENDPOINTS                  #
########################################################
@app.route("/API/users/<string:username>/", methods=['GET'])
def GetUser(username):
    user = db.GetUser(username)
    if (user == None):
        return None
    else:
        return user.to_dictionary()


@app.route("/API/admins/<string:username>/", methods=['GET'])
def GetAdmin(username):
    admin = db.GetAdmin(username)
    if (admin == None):
        return None
    else:
        return admin.to_dictionary()


@app.route("/API/users/", methods=['GET'])
def GetUsers():
    # Get entire list of users (including users who are admins)
    all_users = db.ListAllUsers()
    if (all_users == None):
        return {"users": None}

    users = []
    for user in all_users:
        user_dict = user.to_dictionary()
        users.append(user_dict)
    return {"users": users}


@app.route("/API/admins/", methods=['GET'])
def GetAdmins():
    # Get entire lis of admins
    all_admins = db.ListAllAdmins()
    if (all_admins == None):
        return {"admins": None}

    admins = []
    for admin in all_admins:
        admin_dict = admin.to_dictionary()
        admins.append(admin_dict)

    return {"admins": admins}


@app.route("/API/<string:username>/stats/", methods=['GET'])
def GetUserStats(username):
    user_stats = db.GetUserStats(username)
    if (user_stats == None):
        return None
    else:
        return user_stats.to_dictionary()


@app.route("/API/new_admin/<string:username>/", methods=['POST'])
def NewAdmin(username):
    new_admin = db.NewAdmin(username)
    return {"username": new_admin}


@app.route("/API/new_user/<string:username>/", methods=['PUT', 'PATCH'])
def NewUser(username):
    user_data = request.get_json()
    email = user_data["email"]
    name = user_data["name"]

    new_user = db.NewUser(username, email, name)
    return {"username": new_user}


@app.route("/API/<string:username>/stats/views/", methods=['PUT', 'PATCH'])
def AddView(username):
    user_views = db.AddView2User(username)
    return {"user_views": user_views}


@app.route("/API/<string:username>/stats/questions/", methods=['PUT', 'PATCH'])
def AddQuestion(username):
    user_questions = db.Add2Questions(username)
    return {"user_questions": user_questions}


@app.route("/API/<string:username>/stats/answers/", methods=['PUT', 'PATCH'])
def AddAnswer(username):
    user_answers = db.Add2Answers(username)
    return {"user_answers": user_answers}


########################################################
#                        MAIN                          #
########################################################
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=6000, debug=True)
