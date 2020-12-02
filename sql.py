# _*_ coding: utf-8 _*_
"""
@Author     : tyler
@Email      : tyler_d1128@outlook.com
@Project    : bilibili-video-download 
@File       : sql.py
@License    : GNU GENERAL PUBLIC LICENSE
"""

import sqlite3
from os import path, makedirs
from config import config
from bilibili_api import user
import bilibili_api
from shutil import rmtree

db_path = path.join(config['DATA_PATH'], '.db')
if not path.exists(db_path):
    makedirs(db_path)
conn = sqlite3.connect(path.join(db_path, 'bilibili.db'))


def get_up_name(mid):
    cursor = conn.cursor()
    name = cursor.execute("SELECT name FROM up WHERE mid = ?", (mid,)).fetchone()
    if not name:
        return "None"
    return name[0]


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
        cursor.execute("INSERT INTO up VALUES (?, ?, ?, ?)", (mid, info['name'], info['face'], info['sign'],))
        conn.commit()
    except sqlite3.IntegrityError:
        print('up主已经在跟踪中...'
              '\n请勿重复添加！')
        return
    print(f"添加成功：{info['name']}")


def delete_up(mid):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM video where mid = ?", (mid,))
    cursor.execute("DELETE FROM up where mid = ?", (mid,))
    conn.commit()
    if input('是否删除该up主所有视频文件?(yes/no)').strip() == 'yes':
        try:
            rmtree(path.join(config['DATA_PATH'], get_up_name(mid)))
        except FileNotFoundError:
            pass
    return True


def insert_video(video):
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE video (bvid TEXT PRIMARY KEY, title TEXT, mid INTEGER, author TEXT, status TEXT, is_union_video TEXT, create INTEGER, pic TEXT)")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("INSERT INTO video VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (video['bvid'], video['title'], video['mid'], video['author'], 'deficiency', str(video['is_union_video']), video['create'], video['pic'],))
        conn.commit()
    except sqlite3.IntegrityError:
        pass


def get_failed_video():
    pass


def get_video_info(bvid):
    pass


def set_video_dl_status_success(bvid: str):
    pass


if __name__ == '__main__':
    add_up(206837580)
