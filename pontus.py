# _*_ coding: utf-8 _*_
"""
@Author     : tyler
@Email      : tyler_d1128@outlook.com
@Project    : bilibili-video-download 
@File       : main.py
@License    : GNU GENERAL PUBLIC LICENSE
"""
from manage import update_video, add_up, delete_up, show_track_up
from fire import Fire


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


if __name__ == '__main__':
    Fire({
        'help': help_command,
        'update': update_video,
        'add': add_up,
        'delete': delete_up,
        'show': show_track_up,
    })
