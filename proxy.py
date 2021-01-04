#!/usr/bin/env python3
"""
Proxy Module
============

The proxy module is a Flask server which works as the core 
of the VQA By Joana application, by establishing a bridge 
between the user and the back-end of the app.

The proxy module provides endpoints for the app's web pages 
that are used as the interface of the app.
It also provides REST API endpoints to interact with the other
Flask servers that manage the app's databases. These endpoints 
are called within the JavaScript code embedded in the front-end 
web pages. 
This organization of the app allows the separation between the
user and the back-end of the app, by making the user go throough 
the proxy to access the databases.
"""

import os
import signal
import requests
import json
import yaml
import threading
import time
from datetime import datetime

from flask import Flask
from flask import redirect
from flask import render_template
from flask import url_for
from flask import abort
from flask import session
from flask import request
from flask_dance.consumer import OAuth2ConsumerBlueprint
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

import nmap3

from aux import ServerConfig
from aux import EventType
from aux import log2term

SCAN_PERIOD = 10

app = Flask(__name__)

########################################################
#                        OAUTH                         #
########################################################
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = "asintisfun"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
fenix_blueprint = OAuth2ConsumerBlueprint(
    "fenix-example",
    __name__,
    client_id="1132965128044796",
    client_secret=
    "HwdRWx6wP7rJkb2UKmxbVoYkjrok4xD/tDlcwom+0qnJLDMrwT3aavKo9OXaQC5gMc+uy7CfbcU6XJL6qASy+w==",
    base_url="https://fenix.tecnico.ulisboa.pt/",
    token_url="https://fenix.tecnico.ulisboa.pt/oauth/access_token",
    authorization_url="https://fenix.tecnico.ulisboa.pt/oauth/userdialog",
)
app.register_blueprint(fenix_blueprint)


########################################################
#                      FUNCTIONS                       #
########################################################
def UserExists(username) -> bool:
    response = requests.get(
        f"http://{flask_users.addr}:{flask_users.port}/API/users/{username}/")
    if response.json() == {}:
        log2term('W', f"There's no user with username {username}")
        return False

    # Log the request to the users flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_USER.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "{username}"\n}}'
    requests.post(url, headers=headers, data=body)

    log2term('D', f"User {username} exists in the database")
    return True


def AdminExists(username) -> bool:
    response = requests.get(
        f"http://{flask_users.addr}:{flask_users.port}/API/admins/{username}/")
    if response.json() == {}:
        log2term('W', f"User with username {username} is not an admin")
        return False

    # Log the request to the users flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_ADMIN.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "{username}"\n}}'
    requests.post(url, headers=headers, data=body)

    log2term('D', f"User {username} is an admin")
    return True


def VideoExists(video_id) -> bool:
    response = requests.get(
        f"http://{flask_videos.addr}:{flask_videos.port}/API/videos/{video_id}/"
    )
    if response.json() == {}:
        log2term('W', f"There's no video with ID {video_id}")
        return False

    # Log the request to the videos flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_VIDEO.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_videos.addr}",\n"dest_port": "{flask_videos.port}",\n"content": "{video_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    log2term('D', f"Video with ID {video_id} exists in the database")
    return True


def QuestionExists(question_id) -> bool:
    response = requests.get(
        f"http://{flask_QAs.addr}:{flask_QAs.port}/API/questions/{question_id}/"
    )
    if response.json() == {}:
        log2term('W', f"There's no question with ID {question_id}")
        return False

    # Log the request to the QAs flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_QAS.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_QAs.addr}",\n"dest_port": "{flask_QAs.port}",\n"content": "{question_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    log2term('D', f"Question with ID {question_id} exists in the database")
    return True


def NewUser(username, email, name):
    if UserExists(username) == True:
        log2term(
            'E',
            f"Can't add user {username} to users databse since it already exists"
        )
        return {}

    url = f"http://{flask_users.addr}:{flask_users.port}/API/new_user/{username}/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"name": "{name}",\n"email": "{email}"\n}}'
    response = requests.post(url, headers=headers, data=body)

    if response.json() == {}:
        log2term('E', f"Failed to add user {username} to the database")
        return {}

    # Log the request to the users flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.POST_NEW_USER.value}",\n"username": "{username}",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "{username}"\n}}'
    requests.post(url, headers=headers, data=body)

    log2term(
        'D',
        f"New user with username {username} was successfully added to the database"
    )
    return response.json()


########################################################
#                 FLASK API ENDPOINTS                  #
########################################################
@app.route("/API/videos/<int:video_id>/", methods=['GET'])
def GetVideo(video_id):
    # Log the request to the proxy
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_VIDEO.value}",\n"username": "-",\n"origin_addr": "-",\n"origin_port": "-",\n"dest_addr": "{me.addr}",\n"dest_port": "{me.port}",\n"content": "{video_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    if VideoExists(video_id) == False:
        return {}

    response = requests.get(
        f"http://{flask_videos.addr}:{flask_videos.port}/API/videos/{video_id}/"
    )

    # Log the request to the videos flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_VIDEO.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_videos.addr}",\n"dest_port": "{flask_videos.port}",\n"content": "{video_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    return response.json()


@app.route("/API/<string:username>/videos/", methods=['GET'])
def GetVideos(username):
    # Log the request to the proxy
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_VIDEO.value}",\n"username": "-",\n"origin_addr": "-",\n"origin_port": "-",\n"dest_addr": "{me.addr}",\n"dest_port": "{me.port}",\n"content": "all"\n}}'
    requests.post(url, headers=headers, data=body)

    if UserExists(username) == False:
        return {}

    response = requests.get(
        f"http://{flask_videos.addr}:{flask_videos.port}/API/{username}/videos/"
    )
    # Log the request to the flask videos server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_VIDEO.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_videos.addr}",\n"dest_port": "{flask_videos.port}",\n"content": "all"\n}}'
    requests.post(url, headers=headers, data=body)

    return response.json()


@app.route("/API/new_admin/<string:username>/", methods=['POST'])
def NewAdmin(username):
    data = request.get_json()
    author = data["author"]  # Post request's author

    # Log the request to the proxy
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.POST_NEW_ADMIN.value}",\n"username": "{author}",\n"origin_addr": "-",\n"origin_port": "-",\n"dest_addr": "{me.addr}",\n"dest_port": "{me.port}",\n"content": "{username}"\n}}'
    requests.post(url, headers=headers, data=body)

    if UserExists(username) == False:
        log2term(
            'E',
            f"Can't promote user {username} to admin since it doesn't exist in the users database"
        )
        return {}

    # Check if admin is already registered to the database
    if AdminExists(username) == True:
        log2term(
            'E',
            f"Can't promote user {username} to admin since that user is already an admin"
        )
        return {}

    response = requests.post(
        f"http://{flask_users.addr}:{flask_users.port}/API/new_admin/{username}/"
    )

    if response == None:
        log2term('E',
                 f"Failed to add user {username} as admin to the database")
        return {}
    log2term('I',
             f"Successfully added user {username} as admin to the database")

    # Log the request to the users flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.POST_NEW_ADMIN.value}",\n"username": "{author}",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "{username}"\n}}'
    requests.post(url, headers=headers, data=body)

    return response.json()


@app.route("/API/<string:username>/videos/", methods=['POST'])
def NewVideo(username):
    data = request.get_json()

    # Log the request to the proxy
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.POST_NEW_VIDEO.value}",\n"username": "{username}",\n"origin_addr": "-",\n"origin_port": "-",\n"dest_addr": "{me.addr}",\n"dest_port": "{me.port}",\n"content": "-"\n}}'
    requests.post(url, headers=headers, data=body)

    if UserExists(username) == False:
        return {}

    response = requests.post(
        f"http://{flask_videos.addr}:{flask_videos.port}/API/{username}/videos/",
        json=data)

    if response.json() == {}:
        log2term('E', f"Failed to add new video to the database")
        return {}

    video_id = response.json()
    video_id = video_id["video_id"]
    log2term('D', f"Video with ID {video_id} was added to the database")

    # Log the request to the videos flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.POST_NEW_VIDEO.value}",\n"username": "{username}",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_videos.addr}",\n"dest_port": "{flask_videos.port}",\n"content": "New video with ID {video_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    requests.put(
        f"http://{flask_users.addr}:{flask_users.port}/API/{username}/stats/videos<Z/"
    )

    # Log the request to the users flask server (to iterate the videos counter un the user's stats)
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.PUT_USERSTATS_VIDEO.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "For user {username} regarding video {video_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    return response.json()


@app.route("/API/stats/views/<string:username>/<int:video_id>/",
           methods=['PUT', 'PATCH'])
def AddView(username, video_id):
    # Log the request to the proxy
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.PUT_VIEW.value}",\n"username": "-",\n"origin_addr": "-",\n"origin_port": "-",\n"dest_addr": "{me.addr}",\n"dest_port": "{me.port}",\n"content": "For user {username} and for videos {video_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    if UserExists(username) == False:
        return {}
    if VideoExists(video_id) == False:
        return {}

    # Add view to user
    response = requests.put(
        f"http://{flask_users.addr}:{flask_users.port}/API/{username}/stats/views/"
    )
    user_views = response.json()

    # Log the request to the users flask server (to iterate the views counter un the user's stats)
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.PUT_USERSTATS_VIEW.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "For user {username} regarding video {video_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    # Add view to video
    response = requests.put(
        f"http://{flask_videos.addr}:{flask_videos.port}/API/{video_id}/views/"
    )
    video_views = response.json()

    # Log the request to the users flask server (to iterate the views counter un the user's stats)
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.PUT_VIDEO_VIEW.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_videos.addr}",\n"dest_port": "{flask_videos.port}",\n"content": "For video {video_id} regarding user {username}"\n}}'
    requests.post(url, headers=headers, data=body)

    return {
        'user_views': user_views["user_views"],
        'video_views': video_views["video_views"]
    }


@app.route("/API/<string:username>/stats/", methods=['GET'])
def GetUserStats(username):
    # Log the request to the proxy
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_USERSTATS.value}",\n"username": "-",\n"origin_addr": "-",\n"origin_port": "-",\n"dest_addr": "{me.addr}",\n"dest_port": "{me.port}",\n"content": "{username}"\n}}'
    requests.post(url, headers=headers, data=body)

    if UserExists(username) == False:
        return {}

    response = requests.get(
        f"http://{flask_users.addr}:{flask_users.port}/API/{username}/stats/")
    if (response == None):
        log2term('W', f'There were no stats found for user {username}')
        return {}

    # Log the request to the users flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_USERSTATS.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "{username}"\n}}'
    requests.post(url, headers=headers, data=body)

    return response.json()


@app.route("/API/users/", methods=['GET'])
def GetAllUsers():
    # Log the request to the proxy
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_USERS_ADMINS.value}",\n"username": "-",\n"origin_addr": "-",\n"origin_port": "-",\n"dest_addr": "{me.addr}",\n"dest_port": "{me.port}",\n"content": "all"\n}}'
    requests.post(url, headers=headers, data=body)

    response = requests.get(
        f"http://{flask_users.addr}:{flask_users.port}/API/users/")
    users = response.json()
    users = users["users"]

    # Log the request to the users flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_USER.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "all"\n}}'
    requests.post(url, headers=headers, data=body)

    response = requests.get(
        f"http://{flask_users.addr}:{flask_users.port}/API/admins/")
    admins = response.json()
    admins = admins["admins"]

    # Log the request to the users flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_ADMIN.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "all"\n}}'
    requests.post(url, headers=headers, data=body)

    return {"users": users, "admins": admins}


@app.route("/API/logs/", methods=['GET'])
def GetAllLogs():
    # Log the request to the proxy
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_ALL_LOGS.value}",\n"username": "-",\n"origin_addr": "-",\n"origin_port": "-",\n"dest_addr": "{me.addr}",\n"dest_port": "{me.port}",\n"content": "-"\n}}'
    requests.post(url, headers=headers, data=body)

    response = requests.get(
        f"http://{flask_logs.addr}:{flask_logs.port}/API/logs/")
    logs = response.json()
    logs = logs["logs"]

    # Log the request to the users flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_ALL_LOGS.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_logs.addr}",\n"dest_port": "{flask_logs.port}",\n"content": "-"\n}}'
    requests.post(url, headers=headers, data=body)

    return {"logs": logs}


@app.route("/API/<int:video_id>/questions/answers/", methods=['GET'])
def GetVideoQuestionsAndAnswers(video_id):
    # Log the request to the proxy
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_QAS.value}",\n"username": "-",\n"origin_addr": "-",\n"origin_port": "-",\n"dest_addr": "{me.addr}",\n"dest_port": "{me.port}",\n"content": "For video {video_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    if VideoExists(video_id) == False:
        return {}

    response = requests.get(
        f"http://{flask_QAs.addr}:{flask_QAs.port}/API/{video_id}/questions/answers/"
    )
    questions = response.json()
    questions = questions["video_questions"]

    # Log the request to the QAs flask server
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.GET_QAS.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_QAs.addr}",\n"dest_port": "{flask_QAs.port}",\n"content": "For video {video_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    # For each question and answer find the author's name
    for question in questions:
        # Find the author of the question
        username = question["username"]
        response = requests.get(
            f"http://{flask_users.addr}:{flask_users.port}/API/users/{username}/"
        )
        user = response.json()
        question["user_name"] = user["name"]

        # Log the request to the users flask server
        url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
        headers = {'Content-Type': 'application/json'}
        body = f'{{\n"event_type": "{EventType.GET_USER.value}",\n"username": "-",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "{username}"\n}}'
        requests.post(url, headers=headers, data=body)

        # Go through the question's answers
        answers = question["answers"]
        for answer in answers:
            # Find the author of the answer
            response = requests.get(
                f"http://{flask_users.addr}:{flask_users.port}/API/users/{answer['username']}/"
            )
            user = response.json()
            answer["user_name"] = user["name"]

    return {"video_questions": questions}


@app.route("/API/videos/<int:video_id>/new_question/", methods=['POST'])
def NewQuestion(video_id):
    question_data = request.get_json()
    username = question_data["username"]

    # Log the request to the proxy
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.POST_NEW_QUESTION.value}",\n"username": "{username}",\n"origin_addr": "-",\n"origin_port": "-",\n"dest_addr": "{me.addr}",\n"dest_port": "{me.port}",\n"content": "For video {video_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    if VideoExists(video_id) == False:
        log2term(
            'E',
            f"Can't create a question about video {video_id} since the video doesn't exist in the database"
        )
        return {}

    if UserExists(username) == False:
        log2term(
            'E',
            f"Can't create the question submitted by user {username} since this user doesn't exist in the database"
        )
        return {}

    response = requests.post(
        f"http://{flask_QAs.addr}:{flask_QAs.port}//API/videos/{video_id}/new_question/",
        json=question_data)

    if response != None:
        question_id = response.json()
        question_id = question_id["question_id"]
        # Log the request to the QAs flask server
        url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
        headers = {'Content-Type': 'application/json'}
        body = f'{{\n"event_type": "{EventType.POST_NEW_QUESTION.value}",\n"username": "{username}",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_QAs.addr}",\n"dest_port": "{flask_QAs.port}",\n"content": "New question with ID {question_id} for video {video_id}"\n}}'
        requests.post(url, headers=headers, data=body)

        requests.put(
            f"http://{flask_users.addr}:{flask_users.port}/API/{username}/stats/questions/"
        )

        # Log the request to the users flask server
        url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
        headers = {'Content-Type': 'application/json'}
        body = f'{{\n"event_type": "{EventType.PUT_USERSTATS_QUESTION.value}",\n"username": "{username}",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "For user {username}, regarding question {question_id}"\n}}'
        requests.post(url, headers=headers, data=body)

    return response.json()


@app.route("/API/questions/<int:question_id>/new_answer/", methods=['POST'])
def NewAnswer(question_id):
    answer_data = request.get_json()
    username = answer_data["username"]

    # Log the request to the proxy
    url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
    headers = {'Content-Type': 'application/json'}
    body = f'{{\n"event_type": "{EventType.POST_NEW_ANSWER.value}",\n"username": "{username}",\n"origin_addr": "-",\n"origin_port": "-",\n"dest_addr": "{me.addr}",\n"dest_port": "{me.port}",\n"content": "For question {question_id}"\n}}'
    requests.post(url, headers=headers, data=body)

    if QuestionExists(question_id) == False:
        log2term(
            'E',
            f"Can't create an answer to question {question_id} since it doesn't exist in the database"
        )
        return {}

    if UserExists(username) == False:
        log2term(
            'E',
            f"Can't create an answer submitted by user {username} since this user doesn't exist in the database"
        )
        return {}

    response = requests.post(
        f"http://{flask_QAs.addr}:{flask_QAs.port}/API/questions/{question_id}/new_answer/",
        json=answer_data)
    response_json = response.json()

    if response != None:
        # Log the request to the QAs flask server
        url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
        headers = {'Content-Type': 'application/json'}
        body = f'{{\n"event_type": "{EventType.POST_NEW_ANSWER.value}",\n"username": "{username}",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_QAs.addr}",\n"dest_port": "{flask_QAs.port}",\n"content": "For question {question_id}. New answer with ID {response_json["answer_id"]}"\n}}'
        requests.post(url, headers=headers, data=body)

        requests.put(
            f"http://{flask_users.addr}:{flask_users.port}/API/{username}/stats/answers/"
        )

        # Log the request to the users flask server
        url = f"http://{flask_logs.addr}:{flask_logs.port}/API/new_log/"
        headers = {'Content-Type': 'application/json'}
        body = f'{{\n"event_type": "{EventType.PUT_USERSTATS_ANSWER.value}",\n"username": "{username}",\n"origin_addr": "{me.addr}",\n"origin_port": "{me.port}",\n"dest_addr": "{flask_users.addr}",\n"dest_port": "{flask_users.port}",\n"content": "For user {username}, regarding answer {response_json["answer_id"]}"\n}}'
        requests.post(url, headers=headers, data=body)

    return response_json


########################################################
#               FLASK WEBPAGE ENDPOINTS                #
########################################################
@app.route("/")
def Index():
    return render_template("welcome.html",
                           logged_in=fenix_blueprint.session.authorized)


@app.route('/logout')
def LogOut():
    session.clear()
    return redirect(url_for("Index"))


@app.route("/dashboard")
def Dashboard():
    # Check if user is loggen in
    if fenix_blueprint.session.authorized == False:
        return redirect(url_for("fenix-example.login"))
    else:
        try:
            user_data = (
                fenix_blueprint.session.get("/api/fenix/v1/person/")).json()
        except TokenExpiredError as e:
            log2term('E', f'{e.__class__.__name__}. Logging out...')
            return redirect(url_for("LogOut"))

        # Extract user information
        username = user_data['username']
        email = user_data['email']
        name = user_data['name']

        # Check if user already exists in DB
        is_admin = False
        if UserExists(username) == False:
            NewUser(username=username, email=email, name=name)
            log2term('I', f'New user {username} registered to the database')
        else:
            log2term('I',
                     f'User {username} is already registered to the database')

            # Checking if user, that already exists, is an admin
            if AdminExists(username) == True:
                is_admin = True
                log2term('I', f'User {username} is an admin')
            else:
                log2term('I', f'User {username} is not an admin')

        return render_template("dashboard.html",
                               username=username,
                               is_admin=is_admin)


@app.route('/videos/<int:video_id>')
def Video(video_id):
    # Check if user is loggen in
    if fenix_blueprint.session.authorized == False:
        return redirect(url_for("fenix-example.login"))
    else:
        try:
            user_data = (
                fenix_blueprint.session.get("/api/fenix/v1/person/")).json()
        except TokenExpiredError as e:
            log2term('E', f'{e.__class__.__name__}. Logging out...')
            return redirect(url_for("LogOut"))

        # Extract user information
        username = user_data['username']

        # Check if video is registered to the database
        if VideoExists(video_id) == False:
            log2term('E', f"Video {video_id} doesn't exist in the database")
            return abort(404)

        # Get video information needed for the html template
        video_info = GetVideo(video_id)

        # Find the author's name through its username
        response = requests.get(
            f'http://{flask_users.addr}:{flask_users.port}/API/users/{video_info["posted_by"]}/'
        )
        user = response.json()
        user_name = user["name"]

        return render_template("video.html",
                               video_id=video_id,
                               video_url=video_info["url"],
                               video_desc=video_info["desc"],
                               video_posted_by=video_info["posted_by"],
                               video_posted_by_name=user_name,
                               video_views=video_info["views"],
                               username=username)


########################################################
#                        MAIN                          #
########################################################
def readYAML(filename=str):
    try:
        stream = open("config.yaml", 'r')
        config = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        log2term('F', f'While opening config file: {e}')
        os.kill(pid, signal.SIGINT)  # Kill server

    proxy_dict = config["proxy"]
    flask_users_dict = config["flask_users"]
    flask_videos_dict = config["flask_videos"]
    flask_QAs_dict = config["flask_QAs"]
    flask_logs_dict = config["flask_logs"]

    global me
    me = ServerConfig(proxy_dict["address"], proxy_dict["port"])

    global flask_users
    flask_users = ServerConfig(flask_users_dict["address"],
                               flask_users_dict["port"])

    global flask_videos
    flask_videos = ServerConfig(flask_videos_dict["address"],
                                flask_videos_dict["port"])

    global flask_QAs
    flask_QAs = ServerConfig(flask_QAs_dict["address"], flask_QAs_dict["port"])

    global flask_logs
    flask_logs = ServerConfig(flask_logs_dict["address"],
                              flask_logs_dict["port"])

    global flask_users_alt
    flask_users_alt = ServerConfig(flask_users_dict["alt_address"],
                                   flask_users_dict["alt_port"])


def server_check(addr: str, port: int) -> str:
    nm = nmap3.Nmap()
    res = nm.scan_top_ports(f"{addr}", args=f"-p {port}")
    state = res[f"{addr}"]["ports"][0]["state"]
    return state


def servers_check() -> bool:
    if server_check(flask_users.addr, flask_users.port) == 'closed':
        return False

    if server_check(flask_users_alt.addr, flask_users_alt.port) == 'closed':
        return False

    if server_check(flask_videos.addr, flask_videos.port) == 'closed':
        return False

    if server_check(flask_QAs.addr, flask_QAs.port) == 'closed':
        return False

    if server_check(flask_logs.addr, flask_logs.port) == 'closed':
        return False

    return True


def users_server_check():
    original = ServerConfig(flask_users.addr, flask_users.port)
    alt = ServerConfig(flask_users_alt.addr, flask_users_alt.port)

    nm = nmap3.Nmap()
    while True:
        before_scan = datetime.now()
        res = nm.scan_top_ports(f"{original.addr}", args=f"-p {original.port}")
        state = res[f"{original.addr}"]["ports"][0]["state"]
        #print(f"{original.addr}:{original.port}->{state}")
        after_scan = datetime.now()

        # Change to the back-up server if the original is down
        if state == 'closed' and (flask_users.addr != alt.addr
                                  or flask_users.port != alt.port):
            flask_users.set(alt.addr, alt.port)
            log2term('D', 'Users server set to be the alternative server')

        # Change to the original server if it's back up
        if state == 'open' and (flask_users.addr == alt.addr
                                and flask_users.port == alt.port):
            flask_users.set(original.addr, original.port)
            log2term('D', 'Users server set to be the default server')

        time.sleep(SCAN_PERIOD - (after_scan - before_scan).total_seconds())


if __name__ == "__main__":
    global pid
    pid = os.getpid()

    readYAML('config.yaml')

    if servers_check() == False:
        log2term("F", "At least one of the database access servers is down")
        os.kill(pid, signal.SIGINT)  # Kill server

    thread = threading.Thread(target=users_server_check)
    thread.start()

    app.run(host=me.addr, port=me.port, debug=True)
