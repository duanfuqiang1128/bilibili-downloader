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
from config import config, clean_path
from bilibili_api import user
import bilibili_api
from shutil import rmtree
import logging

logger = logging.getLogger('pontus.sql')

db_path = path.join(config['DATA_PATH'], '.db')
if not path.exists(db_path):
    logger.info('数据库不存在，自动创建新数据库')
    makedirs(db_path)
conn = sqlite3.connect(path.join(db_path, 'bilibili.db'))


def get_up_name(mid):
    logger.info(f'获取up主名称')
    cursor = conn.cursor()
    name = cursor.execute("SELECT name FROM up WHERE mid = ?", (mid,)).fetchone()
    if not name:
        logger.error('up主不存在')
        return "None"
    return name[0]


def get_up_video(mid):
    logger.info(f'获取up主的视频列表')
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE video (bvid TEXT PRIMARY KEY, title TEXT, mid INTEGER, author TEXT, status TEXT, "
                       "is_union_video TEXT, create_time INTEGER, pic TEXT)")
    except sqlite3.OperationalError:
        pass
    videos_temp = cursor.execute("SELECT bvid from video where mid = ?", (mid,)).fetchall()
    videos = []
    for video in videos_temp:
        videos.append(video[0])
    return videos


def get_up_all_track():
    logger.info(f'获取跟踪的所有up主')
    cursor = conn.cursor()
    temp_up_list = []
    for up in cursor.execute("SELECT mid, name FROM up").fetchall():
        temp_up_list.append({
            'mid': up[0],
            'name': up[1],
        })
    return temp_up_list


def add_up(mid):
    logger.info(f'添加up主')
    try:
        info = user.get_user_info(uid=int(mid))
    except bilibili_api.exceptions.BilibiliException:
        logger.warning('up主不存在')
        print('该up主不存在')
        return
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE up (mid INTEGER PRIMARY KEY, name TEXT, face TEXT, sign TEXT)")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("INSERT INTO up VALUES (?, ?, ?, ?)", (mid, clean_path(info['name']), info['face'], info['sign'],))
        conn.commit()
    except sqlite3.IntegrityError:
        logger.warning('up主已经在跟踪列表')
        print('up主已经在跟踪中...'
              '\n请勿重复添加！')
        return
    print(f"添加成功：{info['name']}")


def delete_up(mid):
    logger.info(f'开始删除up主')
    if input('是否删除该up主所有视频文件?(yes/no)').strip() == 'yes':
        logger.info(f'删除up主本地的所有视频')
        try:
            rmtree(path.join(config['DATA_PATH'], get_up_name(mid)))
        except FileNotFoundError:
            pass
    cursor = conn.cursor()
    cursor.execute("DELETE FROM video where mid = ?", (mid,))
    cursor.execute("DELETE FROM up where mid = ?", (mid,))
    conn.commit()
    return True


def insert_video(video):
    logger.info(f'添加新视频到数据库')
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE video (bvid TEXT PRIMARY KEY, title TEXT, mid INTEGER, author TEXT, status TEXT, "
                       "is_union_video TEXT, create_time INTEGER, pic TEXT)")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("INSERT INTO video VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (video['bvid'], video['title'], video['mid']
                        , video['author'], 'deficiency',
                        str(video['is_union_video']),
                        video['create'], video['pic'],))
        conn.commit()
    except sqlite3.IntegrityError:
        logger.warning('添加的视频已经存在')
        pass


def get_failed_video():
    logger.info(f'获取所有没下载的视频')
    cursor = conn.cursor()
    videos_temp = []
    for video in cursor.execute("SELECT bvid FROM video WHERE status = ?", ('deficiency',)).fetchall():
        videos_temp.append({
            'bvid': video[0],
        })
    return videos_temp


def get_video_info(bvid):
    logger.info(f'获取视频信息')
    cursor = conn.cursor()
    video_info = cursor.execute("SELECT mid, title FROM video WHERE bvid = ?", (bvid,)).fetchone()
    return {
        'mid': video_info[0],
        'title': video_info[1],
    }


def set_video_dl_status_success(bvid: str):
    logger.info(f'更新视频状态为已下载')
    cursor = conn.cursor()
    cursor.execute("UPDATE video SET status = ? WHERE bvid = ?", ('success', bvid,))
    conn.commit()


def db_init():
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE video (bvid TEXT PRIMARY KEY, title TEXT, mid INTEGER, author TEXT, status TEXT, "
                       "is_union_video TEXT, create_time INTEGER, pic TEXT)")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("CREATE TABLE up (mid INTEGER PRIMARY KEY, name TEXT, face TEXT, sign TEXT)")
    except sqlite3.OperationalError:
        pass


def up_is_exist(mid):
    cursor = conn.cursor()
    data = cursor.execute('SELECT mid FROM up WHERE mid = ?', (mid,))
    if not data.fetchone():
        return False
    return True


if __name__ == '__main__':
    pass
