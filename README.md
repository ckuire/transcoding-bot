# ffmpeg
**[ffmpeg](https://hub.docker.com/r/linuxserver/ffmpeg)**
## gpu
> docker run —name=ffmpeg  -dit --runtime=nvidia --entrypoint='bash' linuxserver/ffmpeg 
## cpu
> docker run —name=ffmpeg  -dit --entrypoint='bash' jrottenberg/ffmpeg

# srs
**[srs](https://github.com/ossrs/srs)**
> docker run --rm -d -p 1935:1935 -p 1985:1985 -p 8080:8080     --env CANDIDATE=$CANDIDATE -p 8000:8000/udp     registry.cn-hangzhou.aliyuncs.com/ossrs/srs:4 ./objs/srs -c conf/docker.conf

# 推送命令
## 转码的
> ffmpeg -hwaccel nvdec -hwaccel_device {gpu_num} -rtsp_transport tcp -i {拉流地址} -c:v h264_nvenc -crf 35 -c:a copy -f flv -an rtmp://localhost/live
## 不转的
> ffmpeg -hwaccel nvdec -i {拉流地址} -c:v copy -c:a copy -f flv -an rtmp://localhost/live

