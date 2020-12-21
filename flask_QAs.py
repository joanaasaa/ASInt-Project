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
import db_QAs as db

app = Flask(__name__)


########################################################
#                 FLASK API ENDPOINTS                  #
########################################################
@app.route("/API/questions/<int:question_id>/", methods=['GET'])
def GetQuestion(question_id):
    question = db.GetQuestion(question_id)
    if (question == None):
        return None
    else:
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
    return {"question_id": new_question}


@app.route("/API/questions/<int:question_id>/new_answer/", methods=['POST'])
def NewAnswer(question_id):
    answer_data = request.get_json()
    username = answer_data["username"]
    answer = answer_data["answer"]

    new_answer = db.NewAnswer(answer, question_id, username)
    return {"answer_id": new_answer}


########################################################
#                        MAIN                          #
########################################################
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
