FROM alpine:3.16.0

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
    g++ \
    py3-pip \
    logrotate \
    unison \
    python3-dev \
    #&& apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/v3.13/community unison==2.48.15_p4-r1 \
    && pip3 install flask flask_restful uwsgi requests  flask-basicAuth flask-autoindex psutil apscheduler sqlalchemy \
    && apk del libc-dev linux-headers gcc g++ python3-dev

RUN mkdir -p /var/run/sshd /run/nginx /usr/local/unicloud
ADD app/    /usr/local/unicloud/
ADD app_client/    /usr/local/unicloud_client/
ADD conf/sshd/sshd_config_alpine /etc/sshd_config
ADD conf/sshd/sshd_config_alpine_debug /etc/sshd_config_debug
RUN mv /etc/nginx/http.d/default.conf /etc/nginx/http.d/default.conf.install
RUN rm -f /etc/logrotate.d/*
ADD conf/nginx/default.conf /etc/nginx/http.d/default.conf
ADD conf/logrotate.d/ /etc/logrotate.d/
ADD start/ /start/
WORKDIR "/start"

EXPOSE 22
EXPOSE 80
VOLUME ["/data"]

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3","-u","start.py"]
