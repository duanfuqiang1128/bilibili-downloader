# _*_ coding: utf-8 _*_
"""
@Author     : tyler
@Email      : tyler_d1128@outlook.com
@Project    : bilibili-video-download 
@File       : user.py
@License    : GNU GENERAL PUBLIC LICENSE
"""

from sql import get_up_video, insert_video
from config import get_session
from bilibili_api.user import get_videos_raw


class User:
    def __init__(self, uid):
        self._uid = uid
        self._get_local_data()
        self._session = get_session()

    def _get_local_data(self):
        self._videos = get_up_video()

    def update_video(self):
        page = 1
        while True:
            for video in get_videos_raw(uid=self._uid, pn=page)['list']['vlist']:
                if video['bvid'] in self._videos:
                    break
                insert_video({
                    'pic': video['pic'],
                    'title': video['title'],
                    'author': video['author'],
                    'mid': video['mid'],
                    'create': video['created'],
                    'bvid': video['bvid'],
                    'is_union_video': video['is_union_video']
                })
            page += 1

