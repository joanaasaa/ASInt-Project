#!/usr/bin/env python3
import os
import sys

from aux.logs import log2term

if os.path.exists("VQAdb_users.sqlite"):
    os.remove("VQAdb_users.sqlite")

if os.path.exists("VQAdb_videos.sqlite"):
    os.remove("VQAdb_videos.sqlite")

if os.path.exists("VQAdb_QAs.sqlite"):
    os.remove("VQAdb_QAs.sqlite")

import db_users
import db_videos
import db_QAs

db_users.NewUser('ist426524', 'joana.sa@tecnico.ulisboa.pt', 'Joana Sá')
db_users.NewAdmin('ist426524')

db_users.NewUser('ist186412', 'filipe.reynaud@tecnico.ulisboa.pt',
                 'Filipe Reynaud')

db_users.NewUser('ist187612', 'miguel.de.matos.e.sa@tecnico.ulisboa.pt',
                 'Miguel Sá')

video_id = db_videos.NewVideo(
    'https://www.youtube.com/watch?v=QtMzV73NAgk&ab_channel=PlayStation',
    'PlayStation 5 Unboxing & Accessories!', 'ist426524')
db_users.Add2VideosPosted('ist426524')
new_question_id = db_QAs.NewQuestion('When does the PS5 come out?', '2',
                                     'ist186412', video_id)
db_QAs.NewAnswer("I think it's next month", new_question_id, 'ist426524')
db_QAs.NewAnswer("No, it already came out!", new_question_id, 'ist187612')
db_QAs.NewQuestion("Marques' editting is so good! Who agrees with me?", '27',
                   'ist426524', '1')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=RkC0l4iekYo&ab_channel=PlayStationPlayStationVerified',
    'PS5 Hardware Reveal Trailer', 'ist426524')
db_users.Add2VideosPosted('ist426524')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=Lq594XmpPBg&ab_channel=PlayStation',
    'Horizon Forbidden West - Announcement Trailer | PS5', 'ist426524')
db_users.Add2VideosPosted('ist426524')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=II5UsqP2JAk',
    'The Last of Us Part II – Release Date Reveal Trailer | PS4', 'ist426524')
db_users.Add2VideosPosted('ist426524')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=iqysmS4lxwQ&ab_channel=IGN',
    'Ghost of Tsushima - Official Trailer | The Game Awards', 'ist426524')
db_users.Add2VideosPosted('ist426524')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=thgb_ZGrM9Q&ab_channel=IGN',
    'Horizon 2: Forbidden West - Official Reveal Trailer | PS5 Reveal Event',
    'ist426524')
db_users.Add2VideosPosted('ist426524')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=rTMG51P6F-Q&ab_channel=Zaypixel',
    'Minecraft | How to Build a Farmhouse', 'ist426524')
db_users.Add2VideosPosted('ist426524')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=D6XzFbjtcBU&ab_channel=Zaypixel',
    'Minecraft | How to Build a Greenhouse', 'ist426524')
db_users.Add2VideosPosted('ist426524')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=cOgfcdZwdbc&ab_channel=FuriousTechnology',
    '2020 Nintendo Switch Unboxing', 'ist186412')
db_users.Add2VideosPosted('ist186412')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=HCbCMb6nplI&ab_channel=CommonwealthRealm',
    'Top 10 Nintendo Switch Games of All Time!', 'ist186412')
db_users.Add2VideosPosted('ist186412')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=cBoPbdOaw7M&ab_channel=IGN',
    'Cuphead Review', 'ist187612')
db_users.Add2VideosPosted('ist187612')
