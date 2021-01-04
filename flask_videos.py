#!/usr/bin/env python3
"""
Flask Videos Module
===================

The Flask Videos Module provides API REST endpoints to interact
directly with the videos database.
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
import db_videos as db

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

    flask_videos_dict = config["flask_videos"]

    me.set(flask_videos_dict["address"], flask_videos_dict["port"])


########################################################
#                 FLASK API ENDPOINTS                  #
########################################################
@app.route("/API/videos/<int:video_id>/", methods=['GET'])
def GetVideo(video_id):
    user = db.GetVideo(video_id)
    if user == None:
        log2term(
            'E',
            f"Failed to fetch video data for video {video_id} from the database"
        )
        return {}

    log2term('I', f"Fetched information for video with ID {video_id}")
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
        log2term('I', f"Fetched all the videos posted by uder {username}")

        for video in my_videos:
            video_dict = video.to_dictionary()
            user_videos.append(video_dict)  # This is a list

    # Create a list with all of the videos from other users
    if (other_videos == None):
        log2term('W',
                 f'There were no videos found for other users ({username})')
    else:
        log2term(
            'I',
            f"Fetched all the videos which weren't posted by user {username}")

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
    if video_id == None:
        log2term('E', 'Failed to add new video to the database')
        return {}

    log2term('I', f'New video with ID {video_id} was added to the database')
    return {"video_id": video_id}


@app.route("/API/<int:video_id>/views/", methods=['PUT', 'PATCH'])
def AddView(video_id):
    video_views = db.AddView2Video(video_id)
    log2term('I', 'Successfully iterated video views')
    return {"video_views": video_views}


########################################################
#                        MAIN                          #
########################################################
if __name__ == "__main__":
    global pid
    pid = os.getpid()

    readYAML('config.yaml')
    app.run(host=me.addr, port=me.port, debug=True)
