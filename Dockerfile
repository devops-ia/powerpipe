FROM debian:bookworm-slim

ARG POWERPIPE_VERSION=1.5.1
ARG TARGETARCH

LABEL maintainer="amartingarcia, ialejandro"
LABEL org.opencontainers.image.title="Powerpipe"
LABEL org.opencontainers.image.description="Powerpipe — Dashboards for DevOps"
LABEL org.opencontainers.image.source="https://github.com/devops-ia/powerpipe"
LABEL org.opencontainers.image.vendor="devops-ia"
LABEL org.opencontainers.image.url="https://powerpipe.io"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# hadolint ignore=DL3008,DL3005
# git is required for 'powerpipe mod install' from GitHub repos
RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get install -y --no-install-recommends ca-certificates curl git jq && \
    rm -rf /var/lib/apt/lists/*

# Powerpipe uses DOTS as separator in release asset names
RUN curl -fsSL "https://github.com/turbot/powerpipe/releases/download/v${POWERPIPE_VERSION}/powerpipe.linux.${TARGETARCH}.tar.gz" \
    | tar -xz -C /usr/local/bin && \
    chmod +x /usr/local/bin/powerpipe

# UID 9193, GID 0 (OpenShift compatible, consistent with Steampipe)
RUN useradd -u 9193 -g 0 -d /home/powerpipe -m -s /bin/bash powerpipe

RUN mkdir -p /home/powerpipe/.powerpipe \
             /workspace && \
    chown -R 9193:0 /home/powerpipe /workspace && \
    chmod -R g=u /home/powerpipe /workspace

ENV POWERPIPE_UPDATE_CHECK=false \
    POWERPIPE_TELEMETRY=none \
    POWERPIPE_INSTALL_DIR=/home/powerpipe/.powerpipe \
    POWERPIPE_LISTEN=network \
    POWERPIPE_LOG_LEVEL=warn \
    POWERPIPE_MOD_LOCATION=/workspace

USER 9193
WORKDIR /workspace

EXPOSE 9033

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -sf http://localhost:9033/ || exit 1

CMD ["powerpipe", "server"]
