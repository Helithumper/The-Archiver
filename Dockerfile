FROM python:3.8.0-alpine

RUN apk add build-base

RUN mkdir /code

WORKDIR /code

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "/code/archive.py" ]
