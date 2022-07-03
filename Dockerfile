FROM python:3.10
ENV PYTHONBUFFERED 1

RUN apt-get update
RUN apt-get install -y ffmpeg

COPY bot bot
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

WORKDIR /bot

CMD python bot.py
