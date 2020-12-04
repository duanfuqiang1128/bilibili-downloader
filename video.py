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
from shutil import rmtree, copy
from threading import Thread
import subprocess
import logging
import time

MB = 1000000

logger = logging.getLogger('pontus.video')


def get_media_thread(url, media_content_list, index, media_range):
    logger.info(f'子线程获取分段视频数据，index: {index}，media_range: {media_range}')
    start_time = time.time()
    session = get_session()
    session.headers.update({
        'Range': f'bytes={media_range}'
    })
    try:
        r = session.get(url)
    except Exception as e:
        logger.error(f'子线程下载分段视频失败，ERROR：{repr(e)}')
        return
    if r.status_code != 206:
        logger.error(f'子线程分段视频获取错误，HTTP CODE：{r.status_code}')
        return
    media_content_list[index] = r
    logger.info(f'子线程分段视频下载成功，index: {index}用时：{time.time()-start_time}')


def get_media(url, file_path, media_range):
    media_range = media_range.split('-')
    thread_num = config['THREAD']
    start = int(media_range[0])
    end = int(media_range[1])
    step = int((end-start) / thread_num)
    logger.info(f'下载分段视频，长度:{end-start}')
    if end - start < config['SEGMENT']['MIN_SIZE'] * MB:
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
    logger.info(f'写入分段视频')
    start_time = time.time()
    with open(file_path, 'ab+') as f:
        for r in media_content_list:
            try:
                f.write(r.content)
            except AttributeError:
                logger.error('分段视频文件写入错误，r.content属性不存在')
                return False
    logger.info(f'写入成功，用时：{time.time()-start_time}')
    return True


def _split_media(url) -> []:
    logger.info('开始文件分块')
    split_step = config['SEGMENT']['MAX_SIZE'] * MB  # 每个分段大小，单位是bytes
    session = get_session()
    session.headers.update({
        'Range': 'bytes=0-10',
    })
    split_list = []
    try:
        r = session.get(url)
    except Exception:
        logger.error('请求发送失败')
        return split_list
    if not r.headers['Content-Range']:
        logger.error('返回头不包含Content-Range字段')
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
        logger.info(f'初始化Video, bvid: {bvid}')
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
        logger.info('获取video信息')
        video_info = get_video_info(self._bvid)
        self._title = video_info['title']
        self._mid = video_info['mid']
        self._up_name = mid2name(self._mid)

    def _get_video(self, dl_url):
        logger.info('开始下载视频')
        split_list = _split_media(dl_url)
        video_path = os.path.join(self._video_path_temp, 'video_temp.mp4')
        for url_part in split_list:
            if not get_media(dl_url, video_path, url_part):
                logger.warning(f'获取分段视频错误, 分片:{url_part}')
                return False
        return True

    def _get_audio(self, dl_url):
        logger.info('开始下载音频')
        split_list = _split_media(dl_url)
        video_path = os.path.join(self._video_path_temp, 'audio_temp.mp4')
        for url_part in split_list:
            if not get_media(dl_url, video_path, url_part):
                logger.warning(f'获取分段视频错误, 分片:{url_part}')
                return False
        return True

    def _combine_video(self, file_name):
        logger.info('开始合并音视频文件')
        temp_video_path = os.path.join(self._video_path_temp, 'video_temp.mp4')
        temp_audio_path = os.path.join(self._video_path_temp, 'audio_temp.mp4')
        video_path = os.path.join(self._video_path, f'{file_name.strip()}.mp4')
        cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-i', temp_audio_path, '-i', temp_video_path, '-acodec', 'copy', '-vcodec', 'copy', video_path]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            logger.info('合并成功')
        except subprocess.CalledProcessError:
            logger.warning(f'合并失败，cmd: {cmd}')
            try:
                rmtree(self._video_path_temp)
            except FileNotFoundError:
                pass
            logger.info('残留文件清理成功')
            return False
        try:
            rmtree(self._video_path_temp)
        except FileNotFoundError:
            pass
        os.makedirs(self._video_path_temp)
        return True

    def get_video(self):
        pages = get_pages(bvid=self._bvid, verify=verify)
        logger.info(f'bvid: {self._bvid}, 开始下载视频，page: {len(pages)}')
        for page in range(len(pages)):
            logger.info(f'开始下载第{page+1}个视频')
            try:
                logger.info('开始获取视频地址')
                info = get_download_url(bvid=self._bvid, page=page, verify=verify)
                try:
                    logger.info('开始下载视频流')
                    if not self._get_video(info['dash']['video'][0]['baseUrl']):
                        logger.warning('视频流下载失败')
                        return False
                except KeyError:
                    logger.info('开始下载音视频合一视频')
                    if not self._get_video(info['durl'][0]['url']):
                        logger.info('音视频下载失败')
                        return False
                    logger.info('音视频下载成功')
                    temp_video_path = os.path.join(self._video_path_temp, 'video_temp.mp4')
                    file_name = f"P{page+1} {pages[page]['part']}"
                    video_path = os.path.join(self._video_path, f'{file_name}.mp4')
                    logger.info('开始移动音视频位置')
                    copy(temp_video_path, video_path)
                    logger.info('清理残余文件')
                    try:
                        rmtree(self._video_path_temp)
                    except FileNotFoundError:
                        logger.warning('找不到残余文件')
                        pass
                    os.makedirs(self._video_path_temp)
                    continue

                if not self._get_audio(info['dash']['audio'][0]['baseUrl']):
                    return False
                if not self._combine_video(f"P{page+1} {pages[page]['part']}"):
                    return False
            except KeyError:
                logger.warning(f'KeyError: bvid={self._bvid}, page={page}')
                return False
        try:
            rmtree(self._video_path_temp)
        except FileNotFoundError:
            pass
        return True


def download_failed_video():
    logger.info(f'开始下载所有未下载的视频')
    data = get_failed_video()
    for video in data:
        video_dl = Video(video['bvid'])
        if video_dl.get_video():
            set_video_dl_status_success(video['bvid'])
            logger.info(f'视频下载成功su')
