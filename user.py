# _*_ coding: utf-8 _*_
"""
@Author     : tyler
@Email      : tyler_d1128@outlook.com
@Project    : bilibili-video-download 
@File       : user.py
@License    : GNU GENERAL PUBLIC LICENSE
"""

from sql import get_up_video, insert_video, get_up_name, get_up_all_track
from config import get_session
from bilibili_api.user import get_videos_raw


class User:
    def __init__(self, uid):
        self._uid = uid
        self._get_local_data()
        self._session = get_session()
        self._up_name = mid2name(uid)

    def _get_local_data(self):
        self._videos = get_up_video(self._uid)

    def update_video(self):
        page = 1
        videos = []
        while True:
            try:
                count = 0
                for video in get_videos_raw(uid=self._uid, pn=page)['list']['vlist']:
                    if video['bvid'] in self._videos:
                        raise ValueError
                    videos.append({
                        'pic': video['pic'],
                        'title': video['title'],
                        'author': self._up_name,
                        'mid': self._uid,
                        'create': video['created'],
                        'bvid': video['bvid'],
                        'is_union_video': video['is_union_video']
                    })
                    count += 1
                if count < 30:
                    break
            except ValueError:
                break
            page += 1
        new_video_num = len(videos)
        for i in range(new_video_num):
            i += 1
            insert_video(videos[new_video_num-i])
        return new_video_num


def mid2name(mid):
    return get_up_name(mid)


def get_track_up():
    temp_up_list = []
    for up in get_up_all_track():
        temp_up_list.append(up['mid'])
    return temp_up_list
