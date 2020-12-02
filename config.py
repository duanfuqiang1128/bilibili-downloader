# _*_ coding: utf-8 _*_
"""
@Author     : tyler
@Email      : tyler_d1128@outlook.com
@Project    : bilibili-video-download 
@File       : config.py
@License    : GNU GENERAL PUBLIC LICENSE
"""
from requests import session
from bilibili_api import Verify

config = {
    'BILIBILI': {
        'SESSDATA': '',
        'CSRF': '',
    },
    'DATA_PATH': '',
    'THREAD': 8,
}

verify = Verify(sessdata=config['BILIBILI']['SESSDATA'], csrf=config['BILIBILI']['CSRF'])


def get_session():
    sessions = session()
    sessions.headers.update({
        'Referer': 'https://www.bilibili.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/86.0.4240.198 Safari/537.36',
        'Origin': 'https://www.bilibili.com',
    })
    return sessions

