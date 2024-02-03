FROM python:3.12
ENV PYTHONBUFFERED 1

WORKDIR /controlpanel

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY web web
COPY migrations migrations
COPY scripts/entrypoint.sh entrypoint.sh

RUN useradd -mU gunicron
RUN chown -R gunicron:gunicron /controlpanel
USER gunicron

ENV FLASK_APP=web

ENTRYPOINT ["bash", "entrypoint.sh"]

