#!/usr/bin/env python3
"""
Flask Users Alt Module
======================

The Flask Users Module Alt is a Flask server which provides
API REST endpoints to interact directly with the users 
database. This server is a copy of the Flask Users Module
and is a secondary server in case of failure by the former.
The usage of this server ig managed by the Proxy Module.
"""

import os
import signal
import json
import yaml

from flask import Flask
from flask import redirect
from flask import render_template
from flask import url_for
from flask import abort
from flask import session
from flask import request
from flask_dance.consumer import OAuth2ConsumerBlueprint
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

from aux import ServerConfig
from aux import log2term
import db_users as db

app = Flask(__name__)

########################################################
#                   SERVER CONFIGS                     #
########################################################
me = ServerConfig('', 0)


########################################################
#                      FUNCTIONS                       #
########################################################
def readYAML(filename=str):
    try:
        stream = open("config.yaml", 'r')
        config = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        log2term('F', f'While opening config file: {e}')
        os.kill(pid, signal.SIGINT)  # Kill server

    flask_users_dict = config["flask_users"]

    me.set(flask_users_dict["alt_address"], flask_users_dict["alt_port"])


########################################################
#                 FLASK API ENDPOINTS                  #
########################################################
@app.route("/API/users/<string:username>/", methods=['GET'])
def GetUser(username):
    user = db.GetUser(username)

    if (user == None):
        log2term(
            'W',
            f"There's no user with username {username} registered in the database"
        )
        return {}

    log2term('I', f"Fetched information for user {username} from the database")
    return user.to_dictionary()


@app.route("/API/admins/<string:username>/", methods=['GET'])
def GetAdmin(username):
    admin = db.GetAdmin(username)

    if (admin == None):
        log2term(
            'W',
            f"There's no admin with username {username} registered in the database"
        )
        return {}

    log2term('I', f"User with username {username} is an admin")
    return admin.to_dictionary()


@app.route("/API/users/", methods=['GET'])
def GetUsers():
    # Get entire list of users (including users who are admins)
    all_users = db.ListAllUsers()
    if (all_users == None):
        log2term('W', f"There are no users registered in the database")
        return {"users": None}

    users = []
    for user in all_users:
        user_dict = user.to_dictionary()
        users.append(user_dict)

    log2term('I', f"Fetched entire list of users from the database")
    return {"users": users}


@app.route("/API/admins/", methods=['GET'])
def GetAdmins():
    # Get entire lis of admins
    all_admins = db.ListAllAdmins()
    if (all_admins == None):
        log2term('W', f"There are no admins registered in the database")
        return {"admins": None}

    admins = []
    for admin in all_admins:
        admin_dict = admin.to_dictionary()
        admins.append(admin_dict)

    log2term('I', f"Fetched entire list of admins from the database")
    return {"admins": admins}


@app.route("/API/<string:username>/stats/", methods=['GET'])
def GetUserStats(username):
    user_stats = db.GetUserStats(username)

    if (user_stats == None):
        log2term(
            'E',
            f'Failed to fetch stats for user {username} from the database')
        return {}

    log2term('I', f"Fetched stats for user {username} from the database")
    return user_stats.to_dictionary()


@app.route("/API/new_admin/<string:username>/", methods=['POST'])
def NewAdmin(username):
    new_admin = db.NewAdmin(username)

    if new_admin == None:
        log2term('E',
                 f"Failed to add user {username} as admin to the database")
        return {}

    log2term(
        'I',
        f"User with username {username} was successfully promoted to admin")
    return {"username": new_admin}


@app.route("/API/new_user/<string:username>/", methods=['POST'])
def NewUser(username):
    user_data = request.get_json()
    email = user_data["email"]
    name = user_data["name"]

    new_user = db.NewUser(username, email, name)

    # Check if user was added to de DB
    if new_user == None:
        log2term('E', f"Failed to add user {username} to the database")
        return {}

    log2term(
        'I',
        f"New user with username {username} was successfully added to the database"
    )
    return {"username": new_user}


@app.route("/API/<string:username>/stats/videos/", methods=['PUT', 'PATCH'])
def AddVideo(username):
    user_videos = db.Add2VideosPosted(username)
    log2term('I',
             f"The videos counter was iterated in user {user_videos}'s stats")
    return {"user_videos": user_videos}


@app.route("/API/<string:username>/stats/views/", methods=['PUT', 'PATCH'])
def AddView(username):
    user_views = db.AddView2User(username)
    log2term('I', f"The views counter was iterated in user {username}'s stats")
    return {"user_views": user_views}


@app.route("/API/<string:username>/stats/questions/", methods=['PUT', 'PATCH'])
def AddQuestion(username):
    user_questions = db.Add2Questions(username)
    log2term('I',
             f"The questions counter was iterated in user {username}'s stats")
    return {"user_questions": user_questions}


@app.route("/API/<string:username>/stats/answers/", methods=['PUT', 'PATCH'])
def AddAnswer(username):
    user_answers = db.Add2Answers(username)
    log2term('I',
             f"The answers counter was iterated in user {username}'s stats")
    return {"user_answers": user_answers}


########################################################
#                        MAIN                          #
########################################################
if __name__ == "__main__":
    global pid
    pid = os.getpid()

    readYAML('config.yaml')
    app.run(host=me.addr, port=me.port, debug=True)