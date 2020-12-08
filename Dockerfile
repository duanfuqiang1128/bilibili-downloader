FROM python:3.7

WORKDIR /usr/src/bilibili

COPY requirements.txt ./
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "./pontus.py" ]