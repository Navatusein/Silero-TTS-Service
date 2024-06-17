FROM python:3.10

WORKDIR /usr/app

RUN apt-get update --fix-missing && apt-get upgrade -y
RUN apt-get install -y sox libsox-fmt-mp3 sox

ENV PYTHONUNBUFFERED=1

RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN pip3 install torch>=2.0.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

ADD requirements_docker.txt .
RUN pip3 install -r requirements_docker.txt

ADD ./ ./

EXPOSE 9898

CMD [ "python3", "-u", "./main.py" ]

