# _*_ coding: utf-8 _*_
"""
@Author     : tyler
@Email      : tyler_d1128@outlook.com
@Project    : bilibili-video-download 
@File       : manage.py
@License    : GNU GENERAL PUBLIC LICENSE
"""
from sql import get_up_all_track
import sql
from user import get_track_up, User, mid2name
from video import download_failed_video


def update_video():
    ups = get_track_up()
    if len(ups) == 0:
        print('没有正在跟踪的up主！')
        return
    for up in ups:
        user = User(up)
        new_video_num = user.update_video()
        up_name = mid2name(up)
        print('%-15s' % up_name, f'{new_video_num} 新视频')
    print('开始下载视频...')
    download_failed_video()


def add_up(mid):
    if not sql.add_up(mid):
        return False
    return True


def delete_up(mid):
    if not sql.delete_up(mid):
        print('删除失败！')
        return False
    print('删除成功！')
    return True


def show_track_up():
    count = 0
    for up in get_up_all_track():
        print('%-10s' % up['mid'], up['name'])
        count += 1
    if count == 0:
        print('\n还没有跟踪的up主(～￣(OO)￣)ブ')
        return
    print(f'\n共跟踪{count}个up主 φ(≧ω≦*)♪')
