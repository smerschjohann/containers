# STAGE 1: Go Tools for Certificate Generation
FROM docker.io/library/golang:1.26.2-alpine@sha256:f85330846cde1e57ca9ec309382da3b8e6ae3ab943d2739500e08c86393a21b1 AS go-build
ADD main.go /main.go
RUN go build -ldflags="-s -w" -o /gencert /main.go

# STAGE 2: Builder (Compilation and Venv Setup)
FROM docker.io/nvidia/cuda:12.8.1-devel-rockylinux9 AS builder

ARG TORCH_CUDA_ARCH_LIST="8.0 8.6 8.9 9.0 12.0"
ARG TORCH_WHEEL_URL=https://download.pytorch.org/whl/cu128/torch-2.7.0%2Bcu128-cp312-cp312-manylinux_2_28_x86_64.whl
ARG TORCHVISION_WHEEL_URL=https://download.pytorch.org/whl/cu128/torchvision-0.22.0%2Bcu128-cp312-cp312-manylinux_2_28_x86_64.whl
ARG TORCHAUDIO_WHEEL_URL=https://download.pytorch.org/whl/cu128/torchaudio-2.7.0%2Bcu128-cp312-cp312-manylinux_2_28_x86_64.whl
ARG AI_TOOLKIT_REF=main

ENV TORCH_CUDA_ARCH_LIST="${TORCH_CUDA_ARCH_LIST}"

RUN dnf install epel-release -y && crb enable && \
    dnf install -y python3.12 python3.12-devel git gcc-c++ make ninja-build cmake which acl nodejs npm && \
    python3.12 -m ensurepip --upgrade && \
    ln -sf /usr/bin/python3.12 /usr/bin/python && \
    ln -sf /usr/bin/python3.12 /usr/bin/python3

RUN mkdir -p /venv /opt/workspace-internal && \
    python3.12 -m venv /venv/main && \
    /venv/main/bin/pip install --no-cache-dir --upgrade pip wheel huggingface_hub[cli] ipykernel ipywidgets

RUN source /venv/main/bin/activate && \
    pip install --no-cache-dir "${TORCH_WHEEL_URL}" "${TORCHVISION_WHEEL_URL}" "${TORCHAUDIO_WHEEL_URL}"

# Create a constraints file to protect PyTorch versions
RUN echo "torch @ ${TORCH_WHEEL_URL}" > /opt/workspace-internal/constraints.txt && \
    echo "torchvision @ ${TORCHVISION_WHEEL_URL}" >> /opt/workspace-internal/constraints.txt && \
    echo "torchaudio @ ${TORCHAUDIO_WHEEL_URL}" >> /opt/workspace-internal/constraints.txt
ENV PIP_CONSTRAINT=/opt/workspace-internal/constraints.txt

# Clone and install ai-toolkit
RUN source /venv/main/bin/activate && \
    git clone https://github.com/ostris/ai-toolkit.git /opt/workspace-internal/ai-toolkit && \
    cd /opt/workspace-internal/ai-toolkit && \
    git checkout ${AI_TOOLKIT_REF} && \
    pip install --no-cache-dir -c /opt/workspace-internal/constraints.txt -r requirements.txt

# Build ai-toolkit UI
RUN cd /opt/workspace-internal/ai-toolkit/ui && \
    npm install && \
    npm run build && \
    npm run update_db

# STAGE 3: Final Runtime
FROM docker.io/nvidia/cuda:12.8.1-base-rockylinux9 AS cuda

LABEL org.opencontainers.image.source="https://github.com/smerschjohann/containers/"
LABEL org.opencontainers.image.description="Image for AI-Toolkit training with CUDA 12.8 on RockyLinux 9"
LABEL org.opencontainers.image.title="AI-Toolkit CUDA 12.8"
LABEL maintainer="Simon Merschjohann"

# renovate: datasource=github-releases depName=coder/code-server
ARG CODE_SERVER_VERSION=v4.117.0

# renovate: datasource=github-releases depName=just-containers/s6-overlay
ARG S6_OVERLAY_VERSION=v3.2.0.2

RUN dnf install epel-release -y && crb enable && \
    dnf install -y --nogpgcheck https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm && \
    dnf install -y which python3.12 python3.12-devel git acl xz zstd openssl bzip2 procps-ng sudo nodejs npm btop ffmpeg aria2 && \
    dnf install -y https://github.com/coder/code-server/releases/download/${CODE_SERVER_VERSION}/code-server-${CODE_SERVER_VERSION#v}-amd64.rpm && \
    dnf install -y https://downloads.rclone.org/v1.73.3/rclone-v1.73.3-linux-amd64.rpm && \
    dnf clean all && rm -rf /var/cache/dnf/* && \
    python3.12 -m ensurepip --upgrade && \
    ln -sf /usr/bin/python3.12 /usr/bin/python && \
    ln -sf /usr/bin/python3.12 /usr/bin/python3

# S6 Overlay
RUN curl -Lo - https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz | tar -C / -Jxpf - && \
    curl -Lo - https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz | tar -C / -Jxpf -

# Install dufs
RUN curl -L https://github.com/sigoden/dufs/releases/download/v0.45.0/dufs-v0.45.0-x86_64-unknown-linux-musl.tar.gz -o /tmp/dufs.tar.gz && \
    tar -xzf /tmp/dufs.tar.gz -C /tmp/ && \
    mv /tmp/dufs /usr/local/bin/dufs && \
    chmod +x /usr/local/bin/dufs && \
    rm /tmp/dufs.tar.gz

# Install ocige
RUN curl -L https://github.com/smerschjohann/ocige/releases/download/v0.1.1/ocige_linux_amd64.tar.gz -o /tmp/ocige.tar.gz && \
    tar -xzf /tmp/ocige.tar.gz -C /tmp/ && \
    mv /tmp/ocige /usr/local/bin/ocige && \
    chmod +x /usr/local/bin/ocige && \
    rm /tmp/ocige.tar.gz

# Install chisel
RUN curl -L https://github.com/jpillora/chisel/releases/download/v1.11.5/chisel_1.11.5_linux_amd64.gz -o /tmp/chisel.gz && \
    gunzip /tmp/chisel.gz && \
    mv /tmp/chisel /usr/local/bin/chisel && \
    chmod +x /usr/local/bin/chisel

# Setup User and Workspace
RUN groupadd -g 1000 user && \
    useradd -ms /bin/bash user -u 1000 -g 1000 && \
    echo "user ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/user && \
    sudo chmod 0440 /etc/sudoers.d/user && \
    mkdir -m 700 -p /run/user/1000 /run/dbus && \
    chown 1000:1000 /run/user/1000 /run/dbus

# Copy artifacts from builders
COPY --from=builder --chown=1000:1000 /venv /venv
COPY --from=builder --chown=1000:1000 /opt/workspace-internal /opt/workspace-internal
COPY --from=go-build /gencert /usr/local/bin/gencert
COPY --from=caddy:2.11.2-alpine@sha256:834468128c7696cec0ceea6172f7d692daf645ae51983ca76e39da54a97c570d /usr/bin/caddy /usr/bin/caddy

ENV PATH=/home/user/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/go/bin:/venv/main/bin:$PATH
ENV HOME=/home/user
ENV LD_LIBRARY_PATH=/usr/local/cuda/targets/x86_64-linux/lib:/usr/local/cuda-12.8/targets/x86_64-linux/lib:${LD_LIBRARY_PATH}

VOLUME [ "/workspace" ]
WORKDIR /workspace
RUN chown -R user:user /workspace /home/user

USER user
RUN code-server --install-extension ms-toolsai.jupyter ms-python.python

ADD --chown=user:user ROOT/ /
ADD --chown=user:user Caddyfile.tmpl landing.html /etc/caddy/

ENTRYPOINT ["/init"]
