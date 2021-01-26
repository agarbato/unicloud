FROM alpine:latest

MAINTAINER andrea.garbato@gmail.com

# Install packages

ENV TZ=Europe/Rome

RUN apk add --no-cache \
    bash \
    procps \
    openssh \
    ssmtp \
    supervisor \
    mutt \
    unison \
    shadow \
    sqlite \ 
    pwgen \
    nginx \
    fcgiwrap \
    tzdata \
    gcc \
    libc-dev \
    linux-headers \
    dumb-init \
    python3 \
    py3-pip \
    python3-dev  

RUN mkdir -p /var/run/sshd 
RUN mkdir -p /run/nginx
RUN mkdir -p /usr/local/unicloud
RUN pip3 install flask flask_restful uwsgi requests flask-basicAuth flask-autoindex psutil apscheduler
RUN apk del libc-dev linux-headers gcc python3-dev 
ADD app/    /usr/local/unicloud/
ADD app_client/    /usr/local/unicloud_client/
ADD conf/sshd/sshd_config_alpine /etc/sshd_config
RUN mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.install
ADD conf/nginx/default.conf /etc/nginx/conf.d/default.conf

ADD start/ /start/
WORKDIR "/start"

EXPOSE 22
EXPOSE 80
VOLUME ["/data"]

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3","-u","start.py"]
