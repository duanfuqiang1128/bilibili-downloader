# _*_ coding: utf-8 _*_
"""
@Author     : tyler
@Email      : tyler_d1128@outlook.com
@Project    : bilibili-video-download 
@File       : manage.py
@License    : GNU GENERAL PUBLIC LICENSE
"""
from sql import get_up_all_track, db_init, up_is_exist
import sql
from user import get_track_up, User, mid2name
from video import download_failed_video
import logging

logger = logging.getLogger('pontus.manage')


def help_command():
    print('''
    这是一个管理和自动下载更新b站视频的工具

    command
      help          显示可用的命令列表和帮助文档
      update        更新视频库
      add           通过mid号来添加要跟踪的up主
      delete        通过mid号从跟踪列表中移除up主
      show          显示该视频库跟踪的up主列表
    ''')
    logger.info('打印帮助菜单')


def update_video():
    logger.info('开始更新视频')
    db_init()
    ups = get_track_up()
    if len(ups) == 0:
        logger.info('数据库中没有跟踪的up主')
        print('没有正在跟踪的up主！')
        return
    for up in ups:
        user = User(up)
        new_video_num = user.update_video()
        up_name = mid2name(up)
        print('%-15s' % up_name, f'{new_video_num} 新视频')
    print('开始下载视频...')
    logger.info('开始下载视频')
    download_failed_video()


def add_up(mid):
    db_init()
    sql.add_up(mid)


def delete_up(mid):
    logger.info('删除跟踪的up主')
    db_init()
    if not up_is_exist(mid):
        print('未跟踪该up主!')
        return
    if not sql.delete_up(mid):
        print('删除失败！')
        return
    print('删除成功！')


def show_track_up():
    logger.info('输出up跟踪列表')
    db_init()
    count = 0
    for up in get_up_all_track():
        print('%-10s' % up['mid'], up['name'])
        count += 1
    if count == 0:
        logger.info('没有正在跟踪的up主')
        print('\n还没有跟踪的up主(～￣(OO)￣)ブ')
        return
    print(f'\n共跟踪{count}个up主 φ(≧ω≦*)♪')
