# _*_ coding: utf-8 _*_
"""
@Author     : tyler
@Email      : tyler_d1128@outlook.com
@Project    : bilibili-video-download 
@File       : main.py
@License    : GNU GENERAL PUBLIC LICENSE
"""
from manage import update_video, add_up, delete_up, show_track_up, help_command
from fire import Fire
import logging
import os

if not os.path.exists('log'):
    os.makedirs('log')
#  日志格式：时间-消息文本记录级别-日志记录器名称-文件名-发出日志记录行数-消息内容
logger = logging.getLogger('pontus')
logger.setLevel(logging.DEBUG)
file_handle = logging.FileHandler('log/pontus.log')
formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(name)s-%(filename)s, line:%(lineno)d-%(message)s')
file_handle.setFormatter(formatter)
logger.addHandler(file_handle)
logger.info("程序启动")


if __name__ == '__main__':
    Fire({
        'help': help_command,
        'update': update_video,
        'add': add_up,
        'delete': delete_up,
        'show': show_track_up,
    })
