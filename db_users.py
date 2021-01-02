#!/usr/bin/env python3

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

DB_FILE = "VQAdb_users.sqlite"

if path.exists(DB_FILE):
    exit

Engine = create_engine(f'sqlite:///{DB_FILE}', echo=False)
Base = declarative_base()


########################################################
#                        TABLES                        #
########################################################
class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', name='{self.name}')>"

    def to_dictionary(self):
        return {
            "username": self.username,
            "email": self.email,
            "name": self.name,
        }


class Admin(Base):
    __tablename__ = 'admins'

    username = Column(String, ForeignKey('users.username'), primary_key=True)

    def __repr__(self):
        return f"<Admin(username='{self.username}')>"

    def to_dictionary(self):
        return {
            "username": self.username,
        }


class UserStats(Base):
    __tablename__ = 'user_stats'

    username = Column(String, ForeignKey('users.username'), primary_key=True)
    views = Column(Integer, default=0, nullable=False)
    videos = Column(Integer, default=0, nullable=False)
    questions = Column(Integer, default=0, nullable=False)
    answers = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<UserStats(username='{self.username}', views='{self.views}', videos='{self.videos}', questions='{self.questions}', answers='{self.answers}')>"

    def to_dictionary(self):
        return {
            "username": self.username,
            "views": self.views,
            "videos": self.videos,
            "questions": self.questions,
            "answers": self.answers,
        }


########################################################
#                     CREATING DB                      #
########################################################
Base.metadata.create_all(Engine)
Session = sessionmaker(bind=Engine, expire_on_commit=False)
session = scoped_session(Session)


########################################################
#                      FUNCTIONS                       #
########################################################
def GetUser(username=str):
    user = session.query(User).filter(User.username == username).first()
    session.close()
    return user


def GetAdmin(username=str):
    admin = session.query(Admin).filter(Admin.username == username).first()
    session.close()
    return admin


def GetUserStats(username=str):
    user_stats = session.query(UserStats).filter(
        UserStats.username == username).first()
    session.close()
    return user_stats


def NewUser(username=str, email=str, name=str):
    new_user = User(username=username, email=email, name=name)
    new_stats = UserStats(username=username)
    try:
        session.add(new_user)
        session.add(new_stats)
        session.commit()
        session.close()
        return new_user.username
    except Exception as e:
        session.rollback()
        session.commit()
        session.close()
        print(e)
        return None


def NewAdmin(username=str):
    # Promote user to admin
    new_admin = Admin(username=username)
    try:
        session.add(new_admin)
        session.commit()
        session.close()
        return new_admin.username
    except Exception as e:
        session.rollback()
        session.commit()
        session.close()
        print(e)
        return None


def ListAllUsers():
    return session.query(User).all()


def ListAllAdmins():
    return session.query(Admin).all()


def ListAllUserStats():
    return session.query(UserStats).all()


def Add2VideosPosted(username=str):
    stats = session.query(UserStats).filter(
        UserStats.username == username).first()
    stats.videos += 1
    session.commit()
    session.close()
    return stats.videos


def AddView2User(username=str):
    # Iterate the user's views
    user_stats = session.query(UserStats).filter(
        UserStats.username == username).first()
    user_stats.views += 1

    session.commit()
    session.close()
    return user_stats.views


def Add2Questions(username=str):
    # Iterate the user's question
    user_stats = session.query(UserStats).filter(
        UserStats.username == username).first()
    user_stats.questions += 1

    session.commit()
    session.close()
    return user_stats.questions


def Add2Answers(username=str):
    # Iterate the user's question
    user_stats = session.query(UserStats).filter(
        UserStats.username == username).first()
    user_stats.answers += 1

    session.commit()
    session.close()
    return user_stats.answers


########################################################
#                        MAIN                          #
########################################################
if __name__ == '__main__':
    pass