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
import requests
import json

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
    response = requests.get(f"http://127.0.0.1:6000/API/users/{username}/")
    if response == None:
        log2term('W', f"There's no user with username {username}")
        return False
    return True


def AdminExists(username) -> bool:
    response = requests.get(f"http://127.0.0.1:6000/API/admins/{username}/")
    if response == None:
        log2term('W', f"There's no user with username {username}")
        return False
    return True


def VideoExists(video_id) -> bool:
    response = requests.get(f"http://127.0.0.1:7000/API/videos/{video_id}/")
    if response == None:
        log2term('W', f"There's no video with ID {video_id}")
        return False
    return True


def QuestionExists(question_id) -> bool:
    response = requests.get(f"http://127.0.0.1:8000/API/videos/{question_id}/")
    if response == None:
        log2term('W', f"There's no question with ID {question_id}")
        return False
    return True


def NewUser(username, email, name):
    if UserExists(username) == True:
        log2term(
            'E',
            f"Can't add user {username} to users databse since it already exists"
        )
        return None

    user_data = {"email": email, "name": name}
    user_data = json.dumps(user_data)

    response = requests.put(f"http://127.0.0.1:6000/API/new_user/{username}/",
                            json=user_data)
    return response.json()


########################################################
#                 FLASK API ENDPOINTS                  #
########################################################
@app.route("/API/videos/<int:video_id>/", methods=['GET'])
def GetVideo(video_id):
    if VideoExists(video_id) == False:
        return None

    response = requests.get(f"http://127.0.0.1:7000/API/videos/{video_id}/")
    return response.json()


@app.route("/API/<string:username>/videos/", methods=['GET'])
def GetVideos(username):
    if UserExists(username) == False:
        return None

    response = requests.get(f"http://127.0.0.1:7000/API/{username}/videos/")
    return response.json()


@app.route("/API/<string:username>/videos/", methods=['POST'])
def AddVideo(username):
    video_data = request.get_json()

    if UserExists(username) == False:
        return None

    response = requests.post(f"http://127.0.0.1:7000/API/{username}/videos/",
                             json=video_data)
    return response.json()


@app.route("/API/stats/views/<string:username>/<int:video_id>/",
           methods=['PUT', 'PATCH'])
def AddView(username, video_id):
    if UserExists(username) == False:
        return None
    if VideoExists(video_id) == False:
        return None

    # Add view to user
    response = requests.put(
        f"http://127.0.0.1:6000/API/{username}/stats/views/")
    user_views = response.json()

    # Add view to video
    response = requests.put(f"http://127.0.0.1:7000/API/{video_id}/views/")
    video_views = response.json()

    return {
        'user_views': user_views["user_views"],
        'video_views': video_views["video_views"]
    }


@app.route("/API/<string:username>/stats/", methods=['GET'])
def GetUserStats(username):
    if UserExists(username) == False:
        return None

    response = requests.get(f"http://127.0.0.1:6000/API/{username}/stats/")
    if (response == None):
        log2term('W', f'There were no stats found for user {username}')
        return None

    return response.json()


@app.route("/API/users/", methods=['GET'])
def GetAllUsers():
    response = requests.get(f"http://127.0.0.1:6000/API/users/")
    users = response.json()

    response = requests.get(f"http://127.0.0.1:6000/API/admins/")
    admins = response.json()

    return {"users": users["users"], "admins": admins["admins"]}


@app.route("/API/new_admin/<string:username>/", methods=['PUT', 'PATCH'])
def NewAdmin(username):
    if UserExists(username) == False:
        log2term(
            'E',
            f"Can't promote user {username} to admin since it doesn't exist in the users database"
        )
        return None

    # Check if admin is already registered to the database
    if AdminExists(username) == True:
        log2term(
            'E',
            f"Can't promote user {username} to admin since that user is already an admin"
        )
        return None

    response = requests.post(
        f"http://127.0.0.1:6000/API/new_admin/{username}/")
    return response.json()


@app.route("/API/<int:video_id>/questions/answers/", methods=['GET'])
def GetVideoQuestionsAndAnswers(video_id):
    if VideoExists(video_id) == False:
        return None

    response = requests.get(
        f"http://127.0.0.1:8000/API/{video_id}/questions/answers/")
    questions = response.json()
    questions = questions["video_questions"]

    # For each question and answer find the author's name
    for question in questions:
        # Find the author of the question
        username = question["username"]
        response = requests.get(f"http://127.0.0.1:6000/API/users/{username}/")
        user = response.json()
        question["user_name"] = user["name"]

        # Go through the question's answers
        answers = question["answers"]
        for answer in answers:
            # Find the author of the answer
            response = requests.get(
                f"http://127.0.0.1:6000/API/users/{answer['username']}/")
            user = response.json()
            answer["user_name"] = user["name"]

    return {"video_questions": questions}


@app.route("/API/videos/<int:video_id>/new_question/", methods=['POST'])
def NewQuestion(video_id):
    question_data = request.get_json()
    username = question_data["username"]

    if VideoExists(video_id) == False:
        log2term(
            'E',
            f"Can't create a question about video {video_id} since the video doesn't exist in the database"
        )
        return None

    if UserExists(username) == False:
        log2term(
            'E',
            f"Can't create the question submitted by user {username} since this user doesn't exist in the database"
        )
        return None

    response = requests.post(
        f"http://127.0.0.1:8000//API/videos/{video_id}/new_question/",
        json=question_data)

    if response != None:
        requests.put(f"http://127.0.0.1:6000/API/{username}/stats/questions/")

    return response.json()


@app.route("/API/questions/<int:question_id>/new_answer/", methods=['POST'])
def NewAnswer(question_id):
    answer_data = request.get_json()
    username = answer_data["username"]

    if QuestionExists(question_id) == False:
        log2term(
            'E',
            f"Can't create an answer to question {question_id} since it doesn't exist in the database"
        )
        return None

    if UserExists(username) == False:
        log2term(
            'E',
            f"Can't create an answer submitted by user {username} since this user doesn't exist in the database"
        )
        return None

    response = requests.post(
        f"http://127.0.0.1:8000//API/questions/{question_id}/new_answer/",
        json=answer_data)

    if response != None:
        requests.put(f"http://127.0.0.1:6000/API/{username}/stats/answers/")

    return response.json()


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
            f'http://127.0.0.1:6000/API/users/{video_info["posted_by"]}/')
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
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
