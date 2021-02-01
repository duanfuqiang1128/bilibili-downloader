FROM python:3.9

WORKDIR /usr/src/bilibili

COPY requirements.txt ./
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN apt update
RUN apt install -y ffmpeg

COPY . .

ENTRYPOINT [ "python", "./pontus.py" ]