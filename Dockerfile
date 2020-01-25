FROM python:3.7

RUN set -x && apt-get update \
  && apt-get install -y curl tzdata locales psmisc procps iputils-ping logrotate cron \
  && locale-gen en_US.UTF-8 \
  && curl -SLO "https://github.com/just-containers/s6-overlay/releases/download/v1.21.1.1/s6-overlay-amd64.tar.gz" \
  && tar -xzf s6-overlay-amd64.tar.gz -C / \
  && tar -xzf s6-overlay-amd64.tar.gz -C /usr ./bin \
  && rm -rf s6-overlay-amd64.tar.gz \
  && useradd -u 911 -U -d /config -s /bin/false abc \
  && usermod -G users abc \
  && mkdir -p /app /config /defaults \
  && apt-get clean \
  && rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/* \
  && rm -rf /etc/cron.daily/apt-compat /etc/cron.daily/dpkg /etc/cron.daily/passwd /etc/cron.daily/exim4-base \
  && sed -i "s#/var/log/messages {}.*# #g" /etc/logrotate.conf \
  && pip install lifx-photons-core

COPY rootfs /

ENTRYPOINT ["/init"]
