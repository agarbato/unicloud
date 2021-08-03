FROM alpine:latest

MAINTAINER andrea***REMOVED***garbato@gmail***REMOVED***com

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
    py3-pip \
    python3-dev \
    && apk add --no-cache --repository http://dl-cdn***REMOVED***alpinelinux***REMOVED***org/alpine/v3***REMOVED***13/community unison==2***REMOVED***48***REMOVED***15_p4-r1 \
    && pip3 install flask flask_restful uwsgi requests flask-basicAuth flask-autoindex psutil apscheduler \
    && apk del libc-dev linux-headers gcc python3-dev 

RUN mkdir -p /var/run/sshd /run/nginx /usr/local/unicloud
ADD app/    /usr/local/unicloud/
ADD app_client/    /usr/local/unicloud_client/
ADD conf/sshd/sshd_config_alpine /etc/sshd_config
RUN mv /etc/nginx/http***REMOVED***d/default***REMOVED***conf /etc/nginx/http***REMOVED***d/default***REMOVED***conf***REMOVED***install
ADD conf/nginx/default***REMOVED***conf /etc/nginx/http***REMOVED***d/default***REMOVED***conf

ADD start/ /start/
WORKDIR "/start"

EXPOSE 22
EXPOSE 80
VOLUME ["/data"]

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3","-u","start***REMOVED***py"]
