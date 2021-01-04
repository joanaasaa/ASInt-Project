#!/usr/bin/env python3
"""
Flask QAs Module
================

The Flask QAs Module is a Flask server which provides
API REST endpoints to interact directly with the video's 
questions and answers database. 
"""

import os
import signal
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
import db_QAs as db

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

    flask_QAs_dict = config["flask_QAs"]

    me.set(flask_QAs_dict["address"], flask_QAs_dict["port"])


########################################################
#                 FLASK API ENDPOINTS                  #
########################################################
@app.route("/API/questions/<int:question_id>/", methods=['GET'])
def GetQuestion(question_id):
    question = db.GetQuestion(question_id)
    if (question == None):
        log2term(
            'E',
            f'Failed to fetch information for video with ID {question_id}')
        return {}

    log2term('I', f'Fetch information for question with ID {question_id}')
    return question.to_dictionary()


@app.route("/API/<int:video_id>/questions/answers/", methods=['GET'])
def GetVideoQuestionsAndAnswers(video_id):
    # Fetch videos according to username
    video_questions = []

    questions = db.GetVideoQuestions(video_id)
    if (questions == None):
        log2term(
            'W', f'There were no questions found for video with ID {video_id}')
    else:
        log2term('I',
                 f'Fetched all the questions for video with ID {video_id}')

        for question in questions:
            question_dict = question.to_dictionary()

            # Fetch question answers
            question_answers = []
            answers = db.GetQuestionAnswers(question_dict["id"])
            if (answers == None):
                log2term(
                    'W',
                    f'There were no answers found for question with ID {question_dict["id"]}'
                )
            else:
                log2term(
                    'I',
                    f'Fetched all the answers for question with ID {question_dict["id"]}'
                )

                for answer in answers:
                    answer_dict = answer.to_dictionary()
                    question_answers.append(answer_dict)
            # Adding question's answers to question's dict
            question_dict["answers"] = question_answers

            # Add question's info to question' list
            video_questions.append(question_dict)

    return {"video_questions": video_questions}


@app.route("/API/videos/<int:video_id>/new_question/", methods=['POST'])
def NewQuestion(video_id):
    question_data = request.get_json()
    username = question_data["username"]
    question = question_data["question"]
    instant = question_data["instant"]

    new_question = db.NewQuestion(question, instant, username, video_id)
    if new_question == None:
        log2term(
            'E', f'Failed to create new question for video with Id {video_id}')
        return {}

    log2term('I', f'Created new question with ID {new_question}')
    return {"question_id": new_question}


@app.route("/API/questions/<int:question_id>/new_answer/", methods=['POST'])
def NewAnswer(question_id):
    answer_data = request.get_json()
    username = answer_data["username"]
    answer = answer_data["answer"]

    new_answer = db.NewAnswer(answer, question_id, username)
    if new_answer == None:
        log2term(
            'E',
            f'Failed to create new answer for question with ID {question_id}')
        return {}

    log2term('I', f'Created new answer with ID {new_answer}')
    return {"answer_id": new_answer}


########################################################
#                        MAIN                          #
########################################################
if __name__ == "__main__":
    global pid
    pid = os.getpid()

    readYAML('config.yaml')
    app.run(host=me.addr, port=me.port, debug=True)
