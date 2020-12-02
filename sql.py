# _*_ coding: utf-8 _*_
"""
@Author     : tyler
@Email      : tyler_d1128@outlook.com
@Project    : bilibili-video-download 
@File       : sql.py
@License    : GNU GENERAL PUBLIC LICENSE
"""

import sqlite3
from time import sleep
from os import path, makedirs
from config import config
from bilibili_api import user
import bilibili_api

db_path = path.join(config['DATA_PATH'], '.db')
if not path.exists(db_path):
    makedirs(db_path)
conn = sqlite3.connect(path.join(db_path, '.bilibili.db'))


def get_up_name(mid):
    pass


def get_up_video():
    pass


def get_up_all_track():
    pass


def add_up(mid):
    try:
        info = user.get_user_info(uid=int(mid))
    except bilibili_api.exceptions.BilibiliException:
        print('该up主不存在')
        return
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE up (mid INTEGER PRIMARY KEY, name TEXT, face TEXT, sign TEXT)")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("INSERT INTO up VALUES (? , ?, ?, ?)", (mid, info['name'], info['face'], info['sign']))
        conn.commit()
    except sqlite3.IntegrityError:
        print('up主已经在跟踪中...'
              '\n请勿重复添加！')
        return
    print(f"添加成功：{info['name']}")
    conn.close()


def delete_up(mid):
    pass


def insert_video(video):
    pass


def get_failed_video():
    pass


def get_video_info(bvid):
    pass


def set_video_dl_status_success(bvid: str):
    pass


if __name__ == '__main__':
    pass
