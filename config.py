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
from json import loads
import logging
from subprocess import check_output

logger = logging.getLogger('pontus.config')
logger.info('读取配置文件')

with open('config.json', 'rt', encoding='utf-8') as f:
    user_config = loads(f.read())
config = {
    'BILIBILI': {
        'SESSDATA': user_config['BILIBILI_ACCOUNT']['SESSDATA'],
        'CSRF': user_config['BILIBILI_ACCOUNT']['CSRF'],
    },
    'DATA_PATH': user_config['DATA_PATH'],
    'THREAD': user_config['THREAD']['NUM'],
    'SEGMENT': {
        "MAX_SIZE": user_config['SEGMENT']['MAX_SIZE'],
        "MIN_SIZE": user_config['SEGMENT']['MIN_SIZE'],
    },
    'LOG': {
        'MAX_FILE_BACKUP_NUM': user_config['LOG']['MAX_FILE_BACKUP_NUM'],
        'MAX_SIZE': user_config['LOG']['MAX_SIZE'],
    },
    'FFMPEG': 'ffmpeg',
}


def check_ffmpeg():
    try:
        check_output(['ffmpeg', '-version'])
    except Exception:
        logger.debug('ffmpeg不存在')
        return False
    return True


if (config['BILIBILI']['SESSDATA'] == "") | (config['BILIBILI']['CSRF'] == ""):
    logger.info('登录账号')
    verify = Verify()
else:
    verify = Verify(sessdata=config['BILIBILI']['SESSDATA'], csrf=config['BILIBILI']['CSRF'])
if not check_ffmpeg():
    config['FFMPEG'] = './bin/ffmpeg'

def get_session():
    sessions = session()
    sessions.headers.update({
        'Referer': 'https://www.bilibili.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/86.0.4240.198 Safari/537.36',
        'Origin': 'https://www.bilibili.com',
    })
    logger.info('获取session')
    return sessions


def clean_path(path: str) -> str:
    path = path.replace('/', '#')
    path = path.replace(':', ' ')
    path = path.replace('&', '#')
    path = path.replace('|', '#')
    return path.replace('\\', '#').strip()
