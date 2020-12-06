from os import path

from datetime import time

from sqlalchemy import create_engine, ForeignKey, Column
from sqlalchemy import Integer, String, Time, Boolean
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from aux.logs import log2term

DB_FILE = "VQAdb.sqlite"

new_db = True
if path.exists(DB_FILE):
    new_db = True
    log2term('I', 'Database already exists')
else:
    log2term('I', 'Creating new database file')

Engine = create_engine(f'sqlite:///{DB_FILE}', echo=False)
Base = declarative_base()


######################## USERS ########################
class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', name='{self.name}')>"


class Admin(Base):
    __tablename__ = 'admins'

    username = Column(String, ForeignKey('users.username'), primary_key=True)

    def __repr__(self):
        return f"<Admin(username='{self.username}')>"


def NewUser(username=str, email=str, name=str):
    new_user = User(username=username, email=email, name=name)
    new_stats = UserStats(username=username)
    try:
        session.add(new_user)
        session.add(new_stats)
        session.commit()
        session.close()
        log2term('D', f'New user with username {new_user.username}')
        return True
    except Exception as e:
        session.rollback()
        session.commit()
        session.close()
        log2term('E', f'{e.__class__.__name__} (when adding user {username})')
        return False


def NewAdmin(username=str):
    # Check if user exists before promoting it do admin
    user = GetUser(username)
    if user == None:
        log2term('E', f"User {username} can't be admin since it doesn't exist")
        return False

    # Promote user to admin
    new_admin = Admin(username=username)
    try:
        session.add(new_admin)
        session.commit()
        session.close()
        log2term('D', f'New admin with username {new_admin.username}')
        return True
    except Exception as e:
        session.rollback()
        session.commit()
        session.close()
        log2term(
            'E',
            f'{e.__class__.__name__} (when adding admin with username {username})'
        )
        return False


def GetUser(username=str):
    user = session.query(User).filter(User.username == username).first()
    session.close()
    return user


def GetAdmin(username=str):
    admin = session.query(Admin).filter(Admin.username == username).first()
    session.close()
    return admin


def ListAllUsers():
    return session.query(User).all()


def ListAllAdmins():
    return session.query(Admin).all()


##################### USER STATS ######################
class UserStats(Base):
    __tablename__ = 'user_stats'

    username = Column(String, ForeignKey('users.username'), primary_key=True)
    nr_views = Column(Integer, default=0, nullable=False)
    videos_posted = Column(Integer, default=0, nullable=False)
    questions_made = Column(Integer, default=0, nullable=False)
    answers_given = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<UserStats(username='{self.username}', nr_views='{self.nr_views}', videos_posted='{self.videos_posted}', questions_made='{self.questions_made}', answers_given='{self.answers_given}')>"


def ListAllUserStats():
    return session.query(UserStats).all()


####################### VIDEOS ########################
class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    desc = Column(String)
    posted_by = Column(String, ForeignKey('users.username'), nullable=False)
    views = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<Video(id='{self.id}', url='{self.url}', desc='{self.desc}', posted_by='{self.posted_by}', views='{self.views}')>"

    def to_dictionary(self):
        return {
            "id": self.id,
            "url": self.url,
            "desc": self.desc,
            "posted_by": self.posted_by,
            "views": self.views,
        }

def NewVideo(url=str, desc=str, posted_by=str):
    # Check if user exists before adding video to DB
    user = GetUser(posted_by)
    if user == None:
        log2term('E', f"Video can't be added to database since user {posted_by} doesn't exist")
        return False

    # Add new video to DB
    new_video = Video(url=url, desc=desc, posted_by=posted_by)
    try:
        session.add(new_video)
        session.commit()
        log2term('D', f'New video with ID {new_video.id}')
        session.close()
        return True
    except Exception as e:
        session.rollback()
        session.commit()
        session.close()
        log2term('E', f'{e.__class__.__name__} (when adding video {desc})')
        return False


def ListAllVideos():
    return session.query(Video).all()

def GetUserVideos(username=str):
    user_videos = session.query(Video).filter(Video.posted_by == username).all()
    session.close()
    return user_videos

def GetOtherUsersVideos(username=str):
    other_users_videos = session.query(Video).filter(Video.posted_by != username).all()
    session.close()
    return other_users_videos


###################### QUESTIONS ######################
class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    instant = Column(Time, nullable=False)
    user_id = Column(Integer, ForeignKey('users.username'), nullable=False)
    video_id = Column(Integer, ForeignKey('videos.id'), nullable=False)

    # Many-to-one relationship between video and question
    video = relationship('Video', back_populates='questions')

    # To convert time object to string
    # instant_str = time.strftime(instant, '%H:%M:%S')

    def __repr__(self):
        return f"<Question(id='{self.id}', question='{self.question}', instant='{self.instant}, user_id='{self.user_id}', video_id='{self.video_id}')>"


Video.questions = relationship('Question',
                               order_by=Question.id,
                               back_populates='video')


def NewQuestion(question=str, instant=time, username=str, video_id=int):
    new_question = Question(question=question,
                            instant=instant,
                            user_id=username,
                            video_id=video_id)
    try:
        session.add(new_question)
        session.commit()
        log2term(
            'D',
            f'New question with ID {new_question.id}, regarding video {video_id}'
        )
        session.close()
        return True
    except:
        return False


def ListAllQuestions():
    return session.query(Question).all()


####################### ANSWERS #######################
class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True)
    answer = Column(String, nullable=False)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.username'), nullable=False)

    # Many-to-one relationship between question and answer
    question = relationship('Question', back_populates='answers')

    def __repr__(self):
        return f"<Answer(id='{self.id}', answer='{self.answer}', question_id='{self.question_id}', user_id='{self.user_id}')>"


Question.answers = relationship('Answer',
                                order_by=Answer.id,
                                back_populates='question')


def ListAllAnswers():
    return session.query(Answer).all()


##################### CREATING DB #####################
Base.metadata.create_all(Engine)
Session = sessionmaker(bind=Engine, expire_on_commit=False)
session = scoped_session(Session)

######################## MAIN #########################
if __name__ == '__main__':
    if new_db == True:
        NewUser('ist426524', 'joana.sa@tecnico.ulisboa.pt', 'Joana Sá')
        NewAdmin('ist426524')

        NewUser('ist186412', 'filipe.reynaud@tecnico.ulisboa.pt', 'Filipe Reynaud')
        NewUser('ist187612', 'miguel.de.matos.e.sa@tecnico.ulisboa.pt', 'Miguel Sá')

        NewVideo(
            'https://www.youtube.com/watch?v=QtMzV73NAgk&ab_channel=PlayStation',
            'PlayStation 5 Unboxing & Accessories!', 'ist426524')
        NewVideo(
            'https://www.youtube.com/watch?v=RkC0l4iekYo&ab_channel=PlayStationPlayStationVerified',
            'PS5 Hardware Reveal Trailer', 'ist426524')
        NewVideo(
            'https://www.youtube.com/watch?v=Lq594XmpPBg&ab_channel=PlayStation',
            'Horizon Forbidden West - Announcement Trailer | PS5', 'ist426524')
        NewVideo(
            'https://www.youtube.com/watch?v=II5UsqP2JAk',
            'The Last of Us Part II – Release Date Reveal Trailer | PS4', 'ist426524')
        NewVideo(
            'https://www.youtube.com/watch?v=iqysmS4lxwQ&ab_channel=IGN',
            'Ghost of Tsushima - Official Trailer | The Game Awards', 'ist426524')
        NewVideo(
            'https://www.youtube.com/watch?v=thgb_ZGrM9Q&ab_channel=IGN',
            'Horizon 2: Forbidden West - Official Reveal Trailer | PS5 Reveal Event', 'ist426524')
        NewVideo(
            'https://www.youtube.com/watch?v=rTMG51P6F-Q&ab_channel=Zaypixel',
            'Minecraft | How to Build a Farmhouse', 'ist426524')
        NewVideo(
            'https://www.youtube.com/watch?v=D6XzFbjtcBU&ab_channel=Zaypixel',
            'Minecraft | How to Build a Greenhouse', 'ist426524')

        NewVideo(
            'https://www.youtube.com/watch?v=cOgfcdZwdbc&ab_channel=FuriousTechnology',
            '2020 Nintendo Switch Unboxing', 'ist186412')
        NewVideo(
            'https://www.youtube.com/watch?v=HCbCMb6nplI&ab_channel=CommonwealthRealm',
            'Top 10 Nintendo Switch Games of All Time!', 'ist186412')

        NewVideo(
            'https://www.youtube.com/watch?v=cBoPbdOaw7M&ab_channel=IGN',
            'Cuphead Review', 'ist187612')

        print('All videos')
        print(ListAllVideos())

        print('All user stats')
        print(ListAllUserStats())