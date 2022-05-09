import os
import random
from pathlib import Path

from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
import uvicorn

ROOT = Path(__file__).parent
app = FastAPI()

server_addr = '10.73.190.250'
# server_addr = '192.168.101.242'
online_server_addr = ''

exec_pre = 'docker exec -i ffmpeg bash -c'

log_path = '/push_logs'


class Video(BaseModel):
    video_url: str
    is_h265: Optional[bool] = None
    ar: Optional[str] = None
    bit: Optional[str] = None
    gpu: Optional[str] = None


@app.post("/video")
async def root(video: Video):
    if not video.video_url.startswith('rtsp://'):
        return '视频流协议不支持'
    video_id = get_video_id(video.video_url)

    command = [
        'ffmpeg',
        '-hwaccel nvdec',
        f'-hwaccel_device {video.gpu}' if video.gpu else '',
        '-rtsp_transport tcp' if video.is_h265 else '',
        '-i',
        f'\'{video.video_url}\'',
        '-c:v h264_nvenc -crf 35 -c:a copy' if video.is_h265 else '-c:v copy -c:a copy',
        f'-b:v {video.bit}k' if video.bit else '',
        f'-ar {video.ar}' if video.ar else '',
        f'-f flv -an \'rtmp://{server_addr}/moniter/{video_id}\''
    ]
    exec_command = ' '.join([c for c in command if c != ''])
    # 判断是否有对应进程执行
    # has_process = os.popen(f'ps -ef | grep {video_url} | grep -v grep | awk \'{{print $2}}\'')
    process_content = os.popen(f'{exec_pre} "ps -ef | grep \'{video.video_url}\' | grep -v grep"').read()
    print(process_content)
    if process_content != '':
        exec_content = ' '.join(process_content.split()[7:])
        if exec_command.replace('\'', '') != exec_content:
            # 如果命令不相等则停掉，用当前命令重启
            pid = process_content.split()[1]
            os.system(f'{exec_pre} \'kill -9 {pid}\'')
            os.system(f'{exec_pre} "nohup {exec_command} >{log_path}/{video_id}.log 2>&1 &"')
            print(video.video_url + ' restart')
    else:
        # 进程不存在直接执行
        print(video.video_url + ' init start')
        os.system(f'{exec_pre} "nohup {exec_command} >{log_path}/{video_id}.log 2>&1 &"')

    save(video.video_url, video_id)
    # ffmpeg -rtsp_transport tcp -i rtsp://admin:ds12345678@10.73.190.101:554/Streaming/Channels/101 -vcodec h264 -b:v 1080k -f flv rtmp://10.73.190.250/moniter/test
    return f'http://{server_addr}:18080/moniter/{video_id}.m3u8'


def get_video_id(video_url):
    file = open(ROOT / 'db', mode='r')
    file_data = file.read()
    try:
        video_id = eval(file_data)[video_url]
    except:
        return ''.join(random.sample('1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM', 6))
    return video_id


def save(video_url, video_id):
    file = open(ROOT / 'db', mode='r')
    try:
        file_data = eval(file.read())
    except:
        file_data = {}
    file_data.update({video_url: video_id})
    file = open(ROOT / 'db', mode='w+')
    file.write(str(file_data))
    file.close()


if __name__ == '__main__':
    uvicorn.run("2flv:app", host="0.0.0.0", port=5001, log_level="info")
