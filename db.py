#!/usr/bin/env python3

from os import path, remove

db_users_exists = path.exists("VQAdb_users.sqlite")
db_videos_exists = path.exists("VQAdb_videos.sqlite")

if path.exists("VQAdb_users.sqlite"):
    remove("VQAdb_users.sqlite")

if path.exists("VQAdb_videos.sqlite"):
    remove("VQAdb_videos.sqlite")

import db_videos, db_users

db_users.NewUser('ist426524', 'joana.sa@tecnico.ulisboa.pt', 'Joana Sá')
db_users.NewAdmin('ist426524')

db_users.NewUser('ist186412', 'filipe.reynaud@tecnico.ulisboa.pt',
                 'Filipe Reynaud')
db_users.NewUser('ist187612', 'miguel.de.matos.e.sa@tecnico.ulisboa.pt',
                 'Miguel Sá')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=QtMzV73NAgk&ab_channel=PlayStation',
    'PlayStation 5 Unboxing & Accessories!', 'ist426524')
db_videos.NewVideo(
    'https://www.youtube.com/watch?v=RkC0l4iekYo&ab_channel=PlayStationPlayStationVerified',
    'PS5 Hardware Reveal Trailer', 'ist426524')
db_videos.NewVideo(
    'https://www.youtube.com/watch?v=Lq594XmpPBg&ab_channel=PlayStation',
    'Horizon Forbidden West - Announcement Trailer | PS5', 'ist426524')
db_videos.NewVideo(
    'https://www.youtube.com/watch?v=II5UsqP2JAk',
    'The Last of Us Part II – Release Date Reveal Trailer | PS4', 'ist426524')
db_videos.NewVideo(
    'https://www.youtube.com/watch?v=iqysmS4lxwQ&ab_channel=IGN',
    'Ghost of Tsushima - Official Trailer | The Game Awards', 'ist426524')
db_videos.NewVideo(
    'https://www.youtube.com/watch?v=thgb_ZGrM9Q&ab_channel=IGN',
    'Horizon 2: Forbidden West - Official Reveal Trailer | PS5 Reveal Event',
    'ist426524')
db_videos.NewVideo(
    'https://www.youtube.com/watch?v=rTMG51P6F-Q&ab_channel=Zaypixel',
    'Minecraft | How to Build a Farmhouse', 'ist426524')
db_videos.NewVideo(
    'https://www.youtube.com/watch?v=D6XzFbjtcBU&ab_channel=Zaypixel',
    'Minecraft | How to Build a Greenhouse', 'ist426524')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=cOgfcdZwdbc&ab_channel=FuriousTechnology',
    '2020 Nintendo Switch Unboxing', 'ist186412')
db_videos.NewVideo(
    'https://www.youtube.com/watch?v=HCbCMb6nplI&ab_channel=CommonwealthRealm',
    'Top 10 Nintendo Switch Games of All Time!', 'ist186412')

db_videos.NewVideo(
    'https://www.youtube.com/watch?v=cBoPbdOaw7M&ab_channel=IGN',
    'Cuphead Review', 'ist187612')
