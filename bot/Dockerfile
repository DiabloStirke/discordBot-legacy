FROM python:3.12
ENV PYTHONBUFFERED 1

RUN apt-get update
RUN apt-get install -y ffmpeg

WORKDIR /discord_bot

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY assets assets
COPY data data
COPY service_account.json service_account.json
COPY src src

WORKDIR /discord_bot/src

CMD python bot.py --sync