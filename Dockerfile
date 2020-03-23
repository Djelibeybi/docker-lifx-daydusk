FROM python:3.7-slim

RUN set -x && apt-get update \
  && apt-get install -y curl tzdata gcc \
  && export ARCH=$(uname -m) \
  && case "${ARCH}" in \
    i386) SC_ARCH='386';; \
    x86_64) SC_ARCH='amd64';; \
    aarch64) SC_ARCH='arm64';; \
    armv7l) SC_ARCH='arm';; \
    *) echo "Unsupported architecture."; exit 1 ;; \
  esac \
  && curl -fsSLO "https://github.com/aptible/supercronic/releases/download/v0.1.9/supercronic-linux-${SC_ARCH}" \
  && apt-get purge -y \
        curl \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/* \
  && chmod +x "supercronic-linux-${SC_ARCH}" \
  && mv "supercronic-linux-${SC_ARCH}" "/usr/local/bin/supercronic" \
  && rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/* \
  && pip install lifx-photons-core python-crontab

COPY rootfs /
RUN  chmod +x /scripts/entrypoint.sh

ENTRYPOINT ["/scripts/entrypoint.sh"]
CMD ["daydusk"]