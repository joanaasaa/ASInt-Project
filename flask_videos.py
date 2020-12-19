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
import db_videos as db

app = Flask(__name__)


########################################################
#                 FLASK API ENDPOINTS                  #
########################################################
@app.route("/API/videos/<int:video_id>/", methods=['GET'])
def GetVideo(video_id):
    user = db.GetVideo(video_id)
    if (user == None):
        return None
    else:
        return user.to_dictionary()


@app.route("/API/<string:username>/videos/", methods=['GET'])
def GetVideos(username):
    # Fetch videos according to username
    user_videos = []
    other_users_videos = []

    my_videos = db.GetUserVideos(username)
    other_videos = db.GetOtherUsersVideos(username)

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
def NewVideo(username):
    video_data = request.get_json()
    url = video_data["url"]
    desc = video_data["desc"]

    video_id = db.NewVideo(url, desc, username)
    return {"video_id": video_id}


@app.route("/API/<int:video_id>/views/", methods=['PUT', 'PATCH'])
def AddView(video_id):
    video_views = db.AddView2Video(video_id)
    return {"video_views": video_views}


########################################################
#                        MAIN                          #
########################################################
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=7000, debug=True)
