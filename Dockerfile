FROM alpine:3.19.1
ARG UNISON_VERSION=2.53.4

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
    python3-dev \
    ocaml \
    curl \
    musl-dev \
    make \
    # Download & Install Unison
    && curl -L https://github.com/bcpierce00/unison/archive/refs/tags/v${UNISON_VERSION}.tar.gz | tar zxv -C /tmp \
    && cd /tmp/unison-${UNISON_VERSION} \
    && make \
    && cp src/unison src/unison-fsmonitor /usr/bin \
    && pip3 install --break-system-packages flask flask_restful uwsgi requests  flask-basicAuth flask-autoindex psutil apscheduler sqlalchemy \
    && apk del libc-dev linux-headers gcc g++ python3-dev curl musl-dev ocaml make \
    && rm -rf /tmp/unison-${UNISON_VERSION}

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
