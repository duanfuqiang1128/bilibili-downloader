# _*_ coding: utf-8 _*_
"""
@Author     : tyler
@Email      : tyler_d1128@outlook.com
@Project    : bilibili-video-download 
@File       : video.py
@License    : GNU GENERAL PUBLIC LICENSE
"""
from config import get_session, verify, config
from sql import get_failed_video, set_video_dl_status_success, get_video_info
from bilibili_api.video import get_download_url, get_pages
from user import mid2name
import os
from shutil import rmtree
from threading import Thread


def get_media_thread(url, media_content_list, index, media_range):
    session = get_session()
    session.headers.update({
        'Range': f'bytes={media_range}'
    })
    try:
        r = session.get(url)
    except Exception:
        return
    if r.status_code != 206:
        return
    media_content_list[index] = r


def get_media(url, file_path, media_range):
    media_range = media_range.split('-')
    thread_num = config['THREAD']
    start = int(media_range[0])
    end = int(media_range[1])
    step = int((end-start) / thread_num)
    if end - start < 5000000:
        media_content_list = [None] * 1
        get_media_thread(url, media_content_list, 0, f'{start}-{end}')
    else:
        media_content_list = [None] * thread_num
        thread_pool = []
        for index in range(thread_num):
            thread_end = start + (index + 1) * step - 1
            if index == thread_num - 1:
                thread_end = end
            thread_temp = Thread(target=get_media_thread, args=(url, media_content_list, index, f'{start+step*index}-{thread_end}'))
            thread_pool.append(thread_temp)
            thread_temp.start()
        for thread in thread_pool:
            thread.join()
    with open(file_path, 'ab+') as f:
        for r in media_content_list:
            try:
                f.write(r.content)
            except AttributeError:
                return False
    return True


def _split_media(url) -> []:
    split_step = 20000000  # 每个分段大小，单位是bytes
    session = get_session()
    session.headers.update({
        'Range': 'bytes=0-10',
    })
    split_list = []
    try:
        r = session.get(url)
    except Exception:
        return split_list
    if not r.headers['Content-Range']:
        return split_list
    content_range = r.headers['Content-Range'].split('/')
    content_range = int(content_range[1])
    split_num = int(content_range / split_step)
    if split_num == 0:
        return [f'0-{content_range}']
    for i in range(split_num):
        split_list.append(f'{split_step*i}-{split_step*(i+1)-1}')
    split_list.append(f'{split_step*split_num}-{content_range}')
    return split_list


class Video:
    def __init__(self, bvid):
        self._bvid = bvid
        self._get_video_info()
        up_dir_path = os.path.join(config['DATA_PATH'], self._up_name)
        self._video_path_temp = os.path.join(up_dir_path, self._title, 'temp')
        self._video_path = os.path.join(up_dir_path, self._title)
        try:
            rmtree(self._video_path)
        except FileNotFoundError:
            pass
        for path in [up_dir_path, self._video_path, self._video_path_temp]:
            if not os.path.exists(path):
                os.makedirs(path)

    def _get_video_info(self):
        video_info = get_video_info(self._bvid)
        self._title = video_info['title']
        self._mid = video_info['mid']
        self._up_name = mid2name(self._mid)

    def _get_video(self, dl_url):
        split_list = _split_media(dl_url)
        video_path = os.path.join(self._video_path_temp, 'video_temp.mp4')
        for url_part in split_list:
            if not get_media(dl_url, video_path, url_part):
                return False
        return True

    def _get_audio(self, dl_url):
        split_list = _split_media(dl_url)
        video_path = os.path.join(self._video_path_temp, 'audio_temp.mp4')
        for url_part in split_list:
            if not get_media(dl_url, video_path, url_part):
                return False
        return True

    def _combine_video(self, file_name):
        temp_video_path = os.path.join(self._video_path_temp, 'video_temp.mp4')
        temp_audio_path = os.path.join(self._video_path_temp, 'audio_temp.mp4')
        video_path = os.path.join(self._video_path, f'{file_name}.mp4')
        cmd = f'ffmpeg -hide_banner -loglevel panic -i "{temp_audio_path}" -i "{temp_video_path}" -acodec copy -vcodec copy "{video_path}"'
        if os.system(cmd) != 0:
            return False
        try:
            rmtree(self._video_path_temp)
        except FileNotFoundError:
            pass
        os.makedirs(self._video_path_temp)
        return True

    def get_video(self):
        pages = get_pages(bvid=self._bvid, verify=verify)
        for page in range(len(pages)):
            info = get_download_url(bvid=self._bvid, page=page, verify=verify)
            if not self._get_video(info['dash']['video'][0]['baseUrl']):
                return False
            if not self._get_audio(info['dash']['audio'][0]['baseUrl']):
                return False
            if not self._combine_video(f"P{page+1} {pages[page]['part']}"):
                return False
        try:
            rmtree(self._video_path_temp)
        except FileNotFoundError:
            pass
        return True


def download_failed_video():
    data = get_failed_video()
    for video in data:
        video_dl = Video(video['bvid'])
        if video_dl.get_video():
            set_video_dl_status_success(video['bvid'])
