FROM python:3.12.3-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY entrypoint.sh /usr/src/app/entrypoint.sh
COPY ./config /usr/src/app/

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]