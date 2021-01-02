#!/usr/bin/env python3
import os
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
from aux import EventType
from aux import log2term
import db_logs as db

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
        log2term('E', f'While opening config file: {e}')
        exit

    flask_logs_dict = config["flask_logs"]

    me.set(flask_logs_dict["address"], flask_logs_dict["port"])


########################################################
#                 FLASK API ENDPOINTS                  #
########################################################
@app.route("/API/new_log/", methods=['POST'])
def NewLog():
    log_data = request.get_json()
    event_type = log_data["event_type"]
    username = log_data["username"]
    origin_addr = log_data["origin_addr"]
    origin_port = log_data["origin_port"]
    dest_addr = log_data["dest_addr"]
    dest_port = log_data["dest_port"]
    content = log_data["content"]

    log_id = db.NewLog(event_type, username, origin_addr, origin_port,
                       dest_addr, dest_port, content)
    if log_id == None:
        log2term('E', 'Failed to add log to the database')
        return {}

    log2term('I', f'New log with ID {log_id} was added to the database')
    return {"log_id": log_id}


@app.route("/API/log/<int:id>/", methods=['GET'])
def GetLog(id):
    log = db.GetLog(id)

    if (log == None):
        log2term('W',
                 f"There's no log with ID {id} registered in the database")
        return {}

    log2term('I', f"Fetched log with ID {id} from the database")
    return log.to_dictionary()


@app.route("/API/logs/", methods=['GET'])
def GetLogs():
    # Get entire list of logs
    all_logs = db.ListAllLogs()
    if (all_logs == None):
        log2term('W', f"There are no logs registered in the database")
        return {"logs": None}

    logs = []
    for log in all_logs:
        log_dict = log.to_dictionary()
        log_dict["event_type"] = str(EventType(log_dict["event_type"]).name)
        logs.append(log_dict)

    log2term('I', f"Fetched entire list of logs from the database")
    return {"logs": logs}


########################################################
#                        MAIN                          #
########################################################
if __name__ == "__main__":
    readYAML('config.yaml')
    app.run(host=me.addr, port=me.port, debug=True)
