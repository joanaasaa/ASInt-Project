from os import path

from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Time
from sqlalchemy import Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from aux.logs import log2term
import db_users

DB_FILE = "VQAdb_QAs.sqlite"

if path.exists(DB_FILE):
    log2term('D', 'Database already exists')
    exit
else:
    log2term('D', 'Creating new database file')

Engine = create_engine(f'sqlite:///{DB_FILE}', echo=False)
Base = declarative_base()


########################################################
#                        TABLES                        #
########################################################
class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    instant = Column(Time, nullable=False)
    username = Column(Integer, nullable=False)
    video_id = Column(Integer, nullable=False)

    # To convert time object to string
    # instant_str = time.strftime(instant, '%H:%M:%S')

    def __repr__(self):
        return f"<Question(id='{self.id}', question='{self.question}', instant='{self.instant}, username='{self.username}', video_id='{self.video_id}')>"


class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    answer = Column(String, nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    user_id = Column(Integer, nullable=False)

    # Many-to-one relationship between question and answer
    question = relationship('Question', back_populates='answers')

    def __repr__(self):
        return f"<Answer(id='{self.id}', answer='{self.answer}', question_id='{self.question_id}', user_id='{self.user_id}')>"


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
def NewQuestion(question=str, instant=time, username=str, video_id=int):
    new_question = Question(question=question,
                            instant=instant,
                            user_id=username,
                            video_id=video_id)
    try:
        session.add(new_question)
        session.commit()
        log2term(
            'I',
            f'New question with ID {new_question.id}, regarding video {video_id}'
        )
        session.close()
        return new_question.id
    except:
        return None


def ListAllQuestions():
    return session.query(Question).all()


def ListAllAnswers():
    return session.query(Answer).all()


########################################################
#                        MAIN                          #
########################################################
if __name__ == '__main__':
    pass