#--------- layer 1
FROM python:3.10

WORKDIR /usr/app

RUN apt-get update --fix-missing && apt-get upgrade -y && apt-get autoremove && apt-get autoclean
RUN apt-get install -y sox libsox-fmt-mp3 sox

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD ./ ./

EXPOSE 9898

CMD [ "python3", "-u", "./main.py" ]
