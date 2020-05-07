FROM python:3.6

COPY ./requirements.txt /requirements.txt
WORKDIR /

RUN python -m pip install -r requirements.txt
COPY . /

CMD [ "python", "./main.py" ]


