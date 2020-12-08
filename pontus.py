# _*_ coding: utf-8 _*_
"""
@Author     : tyler
@Email      : tyler_d1128@outlook.com
@Project    : bilibili-video-download 
@File       : main.py
@License    : GNU GENERAL PUBLIC LICENSE
"""
from manage import update_video, add_up, delete_up, show_track_up, help_command
import logging
import logging.handlers
import os
from config import config
from time import sleep

MB = 1000000

if not os.path.exists('log'):
    os.makedirs('log')
#  日志格式：时间-消息文本记录级别-日志记录器名称-文件名-发出日志记录行数-消息内容
logger = logging.getLogger('pontus')
logger.setLevel(logging.DEBUG)
file_handle = logging.handlers.RotatingFileHandler('log/pontus.log', maxBytes=config['LOG']['MAX_SIZE']*MB, backupCount=config['LOG']['MAX_FILE_BACKUP_NUM'])
formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(name)s-%(filename)s, line:%(lineno)d-%(message)s')
file_handle.setFormatter(formatter)
logger.addHandler(file_handle)
logger.info("启动程序")


def read_up_list():
    up_list_temp = []
    with open('up_list.txt', 'rt') as f:
        while True:
            line = f.readline().strip()
            if line and line != '':
                up_list_temp.append(int(line))
                continue
            break
    return up_list_temp


if __name__ == '__main__':
    if not os.path.exists(config['DATA_PATH']):
        os.makedirs(config['DATA_PATH'])
    up_list = []
    while True:
        try:
            up_list_new = read_up_list()
        except ValueError:
            print('up列表格式不正确，回滚旧配置。')
            up_list_new = up_list
        for up in up_list_new:
            if up not in up_list:
                add_up(up)
        for up in up_list:
            if up not in up_list_new:
                delete_up(up)
        update_video()
        sleep(300)
