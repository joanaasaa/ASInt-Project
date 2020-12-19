#!/usr/bin/env python3
from os import path
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Time
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from aux.logs import log2term

DB_FILE = "VQAdb_videos.sqlite"

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
class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    desc = Column(String)
    posted_by = Column(String, nullable=False)
    views = Column(Integer, default=0, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Video(id='{self.id}', url='{self.url}', desc='{self.desc}', posted_by='{self.posted_by}', views='{self.views}', date='{self.date}')>"

    def to_dictionary(self):
        return {
            "id": self.id,
            "url": self.url,
            "desc": self.desc,
            "posted_by": self.posted_by,
            "views": self.views,
            "date": self.date,
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
def NewVideo(url=str, desc=str, posted_by=str):
    new_video = Video(url=url, desc=desc, posted_by=posted_by)
    try:
        session.add(new_video)
        session.commit()
        session.close()
        log2term('I', f'New video with ID {new_video.id}')
        return new_video.id
    except Exception as e:
        session.rollback()
        session.commit()
        session.close()
        log2term(
            'E',
            f'{e.__class__.__name__} (when adding video {desc}): {str(e)}')
        return None


def GetVideo(id=int):
    video = session.query(Video).filter(Video.id == id).first()
    session.close()
    return video


def GetUserVideos(username=str):
    user_videos = session.query(Video).filter(
        Video.posted_by == username).all()
    session.close()
    return user_videos


def GetOtherUsersVideos(username=str):
    other_users_videos = session.query(Video).filter(
        Video.posted_by != username).all()
    session.close()
    return other_users_videos


def AddView2Video(video_id=int):
    # Iterate the video's views
    video = session.query(Video).filter(Video.id == video_id).first()
    video.views += 1

    # Save iterations to DB
    session.commit()
    session.close()
    return video.views


########################################################
#                        MAIN                          #
########################################################
if __name__ == '__main__':
    pass