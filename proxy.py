#!/usr/bin/env python3
"""
Proxy Module
============

The proxy module is the core of the VQA By Joana app. 
It establishes the bridge between front-end and back-end 
of the application.
"""

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
import db_videos
import db_users

app = Flask(__name__)

######################## OAUTH ########################
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


######################## FLASK ########################
@app.route("/API/<string:username>/videos/", methods=['GET'])
def GetVideos(username):
    """Fetches all the videos from the database, divided
    in the user's videos and other users' videos. 
    
    The function checks if the user exists in the database before 
    fetching the videos.

    Parameters
    ----------
    username : str
        Username of the user who's made the REST API call.

    Returns
    -------
    dict or None
        Dictionary containing all of the database's videos divided 
        in 'user_videos' and 'other_users_videos'. 
        Each of these keys' values is a list of dictiionaries. 
        Each dictionary is a single video's information.
        The keys' values can be None if :
            1) There are no videos in the database posted by the user;
            2) If no other users posted video to the database.
        Returns None in case of an unexpected error:
            1) The user doesn't exist in the database.
    """

    # Check if user is registered to the database
    if (db_users.UserExists(username) == False):
        log2term('E', f"User {username} doesn't exist in the database")
        return None

    # Fetch videos according to username
    user_videos = []
    other_users_videos = []

    my_videos = db_videos.GetUserVideos(username)
    other_videos = db_videos.GetOtherUsersVideos(username)

    if (my_videos == None):
        log2term('W', f'There were no videos found for user {username}')
    else:
        for video in my_videos:
            video_dict = video.to_dictionary()
            user_videos.append(video_dict)  # This is a list

    # Create a list with all of the videos from other users
    if (other_videos == None):
        log2term('W',
                 f'There were no videos found for other users ({username})')
    else:
        for video in other_videos:
            video_dict = video.to_dictionary()
            other_users_videos.append(video_dict)  # This is a list

    return {
        'user_videos': user_videos,
        "other_users_videos": other_users_videos
    }  # A dict must be returned


@app.route("/API/<string:username>/videos/", methods=['POST'])
def AddVideo(username):
    """Adds a video to the database.

    The function checks if the user exists in the database before 
    adding the video. 

    Parameters
    ----------
    username : str
        Username of the user who's made the REST API call, who's 
        adding the video to the database.

    Returns
    -------
    dict or None
        Dictionary with a single key whose value is the created
        video's ID in the database.
        Returns None in case of an unexpected error:
            1) The user doesn't exist in the database.
    """
    video_data = request.get_json()

    # Check if user is registered to the database
    if (db_users.UserExists(username) == False):
        log2term('E', f"User {username} doesn't exist in the database")
        return None

    url = video_data["url"]
    desc = video_data["desc"]
    video_id = db_videos.NewVideo(url, desc, username)

    return {"video_id": video_id}


@app.route("/API/<string:username>/stats/", methods=['PUT', 'PATCH'])
def AddView(username):
    """Iterates the view counter in the user's and the video's
    information in the database.

    The function checks if both the user and the video exist in the 
    database before itterating both views counters. 

    Parameters
    ----------
    username : str
        Username of the user who's made the REST API call, whose views
        counter is being iterated.

    Returns
    -------
    dict or None
        Dictionary containing both views counters after the
        ieration.
        Returns None in case of an unexpected error:
            1) The user doesn't exist in the database;
            2) The video doesn't exist in the database
    """

    video_data = request.get_json()
    video_id = video_data["id"]

    # Check if user is registered to the database
    if (db_users.UserExists(username) == True):
        log2term('E', f"User {username} doesn't exist in the database")
        return None

    # Check if vidro is registered to the database
    if (db_videos.VideoExists(video_id) == False):
        log2term('E', f"Video {video_id} doesn't exist in the database")
        return None

    user_views = db_users.AddView2User(username)
    video_views = db_videos.AddView2Video(video_id)

    return {"user_views": user_views, "video_views": video_views}


@app.route("/API/<string:username>/stats/", methods=['GET'])
def GetUserStats(username):
    """Fetches a user's stats from the database
    and returns a dictionary with the information.

    The function checks if the user exists in the database. 

    Parameters
    ----------
    username : str
        Username of the user who's made the REST API call, whose
        stats are being fetched.

    Returns
    -------
    dict or None
        A dictionary with the user's stats. 
        Returns None in case of an unexpected error:
            1) The user doesn't exist in the database;
            2) There are no stats for that user.
    """

    # Check if user is registered to the database
    if (db_users.UserExists(username) == False):
        log2term('E', f"User {username} doesn't exist in the database")
        return None

    user_stats = db_users.GetUserStats(username)

    if (user_stats == None):
        log2term('W', f'There were no stats found for user {username}')
        return None
    else:
        return user_stats.to_dictionary()


@app.route("/API/users/", methods=['GET'])
def GetUsers():
    """Fetches and returns a dictionary with all the
    users and admins registered to the database.

    Returns
    -------
    dict or None
        Returns a dictionary with all the users registered to
        the database. The key 'users' has listed all the users
        in the database (admins or not). The key 'admins'
        contains all the users who are admins.
        Returns None if:
            1) There are no users registered to the database;
            2) There are no admins registered to the database.
    """

    # Get entire lis of users (including users who are admins)
    all_users = db_users.ListAllUsers()

    if (all_users == None):
        log2term('W', f'There were no users found')
        return None
    else:
        users = []
        for user in all_users:
            user_dict = user.to_dictionary()
            users.append(user_dict)

    # Get list of admins
    all_admins = db_users.ListAllAdmins()

    if (all_admins == None):
        log2term('W', f'There were no admins found')
        return None
    else:
        admins = []
        for admin in all_admins:
            admin_dict = admin.to_dictionary()
            admins.append(admin_dict)

    return {"users": users, "admins": admins}


@app.route("/API/new_admin/<string:username>/", methods=['PUT', 'PATCH'])
def AddAdmin(username):
    """Adds a user that already exists in the 'users' table to
    the 'admins' table.

    The function checks if the user that is being promoted to admin
    exists in the database. It also checks if the user is alredy an
    admmin, before adding it to de 'admins' table.

    Parameters
    ----------
    username : str
        The username of the user that is being promoted to admin.

    Returns
    -------
    dict or None
        Dictionary with the new admin's username, if it was 
        successfully added to the 'admins' table. 
        Returns None if:
            1) The user doesn't exist in the 'users' table of
            the database;
            2) The user is already an admin.
    """

    # Check if user is registered to the database
    if (db_users.UserExists(username) == False):
        log2term('E', f"User {username} doesn't exist in the database")
        return None

    # Check if admin is already registered to the database
    if (db_users.AdminExists(username) == True):
        log2term('E', f"User {username} is already an admin")
        return None

    new_admin = db_users.NewAdmin(username)

    return {"username": new_admin}


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
        if (db_users.UserExists(username) == False):
            db_users.NewUser(username=username, email=email, name=name)
            log2term('I', f'New user {username} registered to the database')
        else:
            log2term('I',
                     f'User {username} is already registered to the database')

            # Checking if user, that already exists, is an admin
            admin = db_users.GetAdmin(username)
            if (admin != None):
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

        # Check if vidro is registered to the database
        if (db_videos.VideoExists(video_id) == False):
            log2term('E', f"Video {video_id} doesn't exist in the database")
            return abort(404)

        # Get video information needed for the html template
        video_info = db_videos.GetVideo(video_id).to_dictionary()

        return render_template("video.html",
                               video_id=video_id,
                               video_url=video_info["url"],
                               video_desc=video_info["desc"],
                               video_posted_by=video_info["posted_by"],
                               video_views=video_info["views"],
                               username=username)


######################## MAIN #########################
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
