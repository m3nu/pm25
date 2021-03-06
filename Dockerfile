FROM python:2
MAINTAINER manu@snapdragon.cc

VOLUME ["/opt/pm25"]

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y vim less net-tools inetutils-ping curl \
    git telnet socat tree unzip sudo software-properties-common python-mysqldb \
    pkg-config apt-utils wget build-essential python-dev python python-pip wget \
    liblapack-dev libatlas-dev gfortran libfreetype6 libfreetype6-dev libpng12-dev \
    python-lxml libyaml-dev g++ libffi-dev libzmq-dev libzmq1 \
    memcached supervisor && \
    pip install -U setuptools pip distribute configobj numpy && \
    mkdir -p /var/log/supervisor

ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -U -r /tmp/requirements.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 11211

CMD ["/usr/bin/supervisord"]
