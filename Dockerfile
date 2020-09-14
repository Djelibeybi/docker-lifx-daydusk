FROM python:3.7-slim

LABEL org.opencontainers.image.title="LIFX Day and Dusk in Docker"
LABEL org.opencontainers.image.authors="Avi Miller <me@dje.li>"
LABEL org.opencontainers.image.description="This container reproduces the LIFX Day and Dusk scheduling functionality locally but removes the dependency on the LIFX Cloud and adds fine-grained control over bulb selection, timing, kelvin value and power status."
LABEL org.opencontainers.image.documentation="https://omg.dje.li/2020/02/improving-the-lifx-day-dusk-functionality/"
LABEL org.opencontainers.image.source="https://github.com/Djelibeybi/docker-lifx-daydusk"
LABEL org.opencontainers.image.licenses="MIT"

RUN set -x && apt-get update \
  && apt-get install -y curl tzdata gcc \
  && export ARCH=$(uname -m) \
  && case "${ARCH}" in \
    i386) SC_ARCH='386'; SUPERCRONIC_SHA1SUM='daaddd5403638a24db5999bbb445ff4c300769ee';; \
    x86_64) SC_ARCH='amd64'; SUPERCRONIC_SHA1SUM='a2e2d47078a8dafc5949491e5ea7267cc721d67c';; \
    aarch64) SC_ARCH='arm64'; SUPERCRONIC_SHA1SUM='f011a67f4c56acbef7a75222cb1d7c0d1bb29968';; \
    armv7l) SC_ARCH='arm'; SUPERCRONIC_SHA1SUM='0fd443072c2e028fbe6e78dc7880a1870f8ccac8';; \
    *) echo "Unsupported architecture."; exit 1 ;; \
  esac \
  && curl -fsSLO "https://github.com/aptible/supercronic/releases/download/v0.1.11/supercronic-linux-${SC_ARCH}" \
  && echo "${SUPERCRONIC_SHA1SUM} supercronic-linux-${SC_ARCH}" | sha1sum -c - \
  && apt-get purge -y curl \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* \
  && chmod +x "supercronic-linux-${SC_ARCH}" \
  && mv "supercronic-linux-${SC_ARCH}" "/usr/local/bin/supercronic" \
  && rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/* \
  && pip install lifx-photons-core python-crontab

# Set the LIFX_CONFIG path for Supercronic
ENV LIFX_CONFIG=/config/lifx.yml

COPY rootfs /
RUN  chmod +x /scripts/entrypoint.sh

ENTRYPOINT ["/scripts/entrypoint.sh"]
CMD ["daydusk"]