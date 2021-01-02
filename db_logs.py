from os import path
from enum import Enum
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from aux import EventType

DB_FILE = "VQAdb_logs.sqlite"

if path.exists(DB_FILE):
    exit

Engine = create_engine(f'sqlite:///{DB_FILE}', echo=False)
Base = declarative_base()


########################################################
#                        TABLES                        #
########################################################
class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    event_type = Column(Integer, nullable=False)
    username = Column(String, nullable=False)  # User who made the request
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    origin_addr = Column(String, nullable=False)
    origin_port = Column(Integer, nullable=False)
    dest_addr = Column(String, nullable=False)
    dest_port = Column(Integer, nullable=False)
    content = Column(String, nullable=False)

    def __repr__(self):
        return f"<Log(id='{self.id}', username='{self.username}', date='{self.date}', origin_addr='{self.origin_addr}', origin_port='{self.origin_port}', dest_addr='{self.dest_addr}', dest_port='{self.dest_port}', content='{self.content}')>"

    def to_dictionary(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "username": self.username,
            "date": self.date,
            "origin_addr": self.origin_addr,
            "origin_port": self.origin_port,
            "dest_addr": self.dest_addr,
            "dest_port": self.dest_port,
            "content": self.content,
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
def NewLog(event_type=int,
           username=str,
           origin_addr=str,
           origin_port=int,
           dest_addr=str,
           dest_port=int,
           content=str):
    new_log = Log(event_type=event_type,
                  username=username,
                  origin_addr=origin_addr,
                  origin_port=origin_port,
                  dest_addr=dest_addr,
                  dest_port=dest_port,
                  content=content)
    try:
        session.add(new_log)
        session.commit()
        session.close()
        return new_log.id
    except Exception as e:
        session.rollback()
        session.commit()
        session.close()
        print(e)
        return None


def GetLog(id=int):
    log = session.query(Log).filter(Log.id == id).first()
    session.close()
    return log


def ListAllLogs():
    return session.query(Log).all()


########################################################
#                        MAIN                          #
########################################################
if __name__ == '__main__':
    pass