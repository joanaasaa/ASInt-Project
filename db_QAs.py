from os import path
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_FILE = "VQAdb_QAs.sqlite"

if path.exists(DB_FILE):
    exit

Engine = create_engine(f'sqlite:///{DB_FILE}', echo=False)
Base = declarative_base()


########################################################
#                        TABLES                        #
########################################################
class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    instant = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    video_id = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # To convert time object to string
    # instant_str = time.strftime(instant, '%H:%M:%S')

    def __repr__(self):
        return f"<Question(id='{self.id}', question='{self.question}', instant='{self.instant}, username='{self.username}', video_id='{self.video_id}', date='{self.date}')>"

    def to_dictionary(self):
        return {
            "id": self.id,
            "question": self.question,
            "instant": self.instant,
            "username": self.username,
            "video_id": self.video_id,
            "date": self.date,
        }


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    answer = Column(String, nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    username = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Many-to-one relationship between question and answer
    question = relationship('Question', back_populates='answers')

    def __repr__(self):
        return f"<Answer(id='{self.id}', answer='{self.answer}', question_id='{self.question_id}', user_id='{self.username}', date='{self.date}')>"

    def to_dictionary(self):
        return {
            "id": self.id,
            "answer": self.answer,
            "question_id": self.question_id,
            "username": self.username,
            "date": self.date,
        }


# Many-to-one relationship between question and answer
Question.answers = relationship('Answer',
                                order_by=Answer.id,
                                back_populates='question')

########################################################
#                     CREATING DB                      #
########################################################
Base.metadata.create_all(Engine)
Session = sessionmaker(bind=Engine, expire_on_commit=False)
session = scoped_session(Session)


########################################################
#                      FUNCTIONS                       #
########################################################
def GetQuestion(question_id=int):
    question = session.query(Question).filter(
        Question.id == question_id).first()
    session.close()
    return question


def NewQuestion(question=str, instant=int, username=str, video_id=int):
    new_question = Question(question=question,
                            instant=instant,
                            username=username,
                            video_id=video_id)
    try:
        session.add(new_question)
        session.commit()
        session.close()
        return new_question.id
    except Exception as e:
        session.rollback()
        session.commit()
        session.close()
        print(e)
        return None


def NewAnswer(answer=str, question_id=int, username=str):
    new_answer = Answer(answer=answer,
                        question_id=question_id,
                        username=username)
    try:
        session.add(new_answer)
        session.commit()
        session.close()
        return new_answer.id
    except Exception as e:
        session.rollback()
        session.commit()
        session.close()
        return None


def ListAllQuestions():
    return session.query(Question).all()


def ListAllAnswers():
    return session.query(Answer).all()


def GetVideoQuestions(video_id=int):
    questions = session.query(Question).filter(
        Question.video_id == video_id).all()
    session.close()
    return questions


def GetQuestionAnswers(question_id=int):
    answers = session.query(Answer).filter(
        Answer.question_id == question_id).all()
    session.close()
    return answers


########################################################
#                        MAIN                          #
########################################################
if __name__ == '__main__':
    pass