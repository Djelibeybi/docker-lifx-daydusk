FROM python:3.10.1-slim

RUN set -x && apt-get update \
  && apt-get install -y curl tzdata gcc \
  && export ARCH=$(uname -m) \
  && case "${ARCH}" in \
    i386) SC_ARCH='386'; SUPERCRONIC_SHA1SUM='9c40fcff02fa4e153d2f55826e1fa362cd0e448e';; \
    x86_64) SC_ARCH='amd64'; SUPERCRONIC_SHA1SUM='048b95b48b708983effb2e5c935a1ef8483d9e3e';; \
    aarch64) SC_ARCH='arm64'; SUPERCRONIC_SHA1SUM='8baba3dd0b0b13552aca179f6ef10d55e5dee28b';; \
    armv7l) SC_ARCH='arm'; SUPERCRONIC_SHA1SUM='d72d3d40065c0188b3f1a0e38fe6fecaa098aad5';; \
    *) echo "Unsupported architecture."; exit 1 ;; \
  esac \
  && curl -fsSLO "https://github.com/aptible/supercronic/releases/download/v0.1.12/supercronic-linux-${SC_ARCH}" \
  && echo "${SUPERCRONIC_SHA1SUM} supercronic-linux-${SC_ARCH}" | sha1sum -c - \
  && chmod +x "supercronic-linux-${SC_ARCH}" \
  && mv "supercronic-linux-${SC_ARCH}" "/usr/local/bin/supercronic" \
  && rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/* \
  && pip install lifx-photons-core python-crontab \
  && apt-get purge -y curl gcc \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/*

# Set the LIFX_CONFIG path for Supercronic
ENV LIFX_CONFIG=/config/lifx.yml

COPY rootfs /
RUN  chmod +x /scripts/entrypoint.sh

ENTRYPOINT ["/scripts/entrypoint.sh"]
CMD ["daydusk"]
