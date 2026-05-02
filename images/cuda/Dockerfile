# STAGE 1: Go Tools for Certificate Generation
FROM docker.io/library/golang:1.26.2-alpine@sha256:f85330846cde1e57ca9ec309382da3b8e6ae3ab943d2739500e08c86393a21b1 AS go-build
ADD main.go /main.go
RUN go build -ldflags="-s -w" -o /gencert /main.go

# STAGE 2: Builder (Compilation and Venv Setup)
FROM docker.io/nvidia/cuda:13.2.1-devel-rockylinux10@sha256:6e66f5288ea88c69ec31030610c2afaeb3ed7a693004fd79d08fe43fa6d94d55 AS builder

ARG TORCH_CUDA_ARCH_LIST="8.6 8.9 12.0"
ARG TORCH_WHEEL_URL=https://download.pytorch.org/whl/cu130/torch-2.10.0%2Bcu130-cp312-cp312-manylinux_2_28_x86_64.whl
ARG TORCHVISION_WHEEL_URL=https://download.pytorch.org/whl/cu130/torchvision-0.25.0%2Bcu130-cp312-cp312-manylinux_2_28_x86_64.whl
ARG TORCHAUDIO_WHEEL_URL=https://download.pytorch.org/whl/cu130/torchaudio-2.10.0%2Bcu130-cp312-cp312-manylinux_2_28_x86_64.whl
ARG SAGEATTENTION_VERSION=v2
ARG COMFYUI_REF=master

RUN dnf install epel-release -y && crb enable && \
    dnf install -y python3-pip python3 python3-devel git gcc-c++ make ninja-build cmake which acl && \
    ln -s /usr/bin/python3 /usr/bin/python

RUN mkdir -p /venv /opt/workspace-internal && \
    python -m venv /venv/main && \
    /venv/main/bin/pip install --no-cache-dir wheel huggingface_hub[cli] ipykernel ipywidgets

RUN source /venv/main/bin/activate && \
    pip install "${TORCH_WHEEL_URL}" "${TORCHVISION_WHEEL_URL}" "${TORCHAUDIO_WHEEL_URL}"

# Create a constraints file to protect PyTorch versions
RUN echo "torch @ ${TORCH_WHEEL_URL}" > /opt/workspace-internal/constraints.txt && \
    echo "torchvision @ ${TORCHVISION_WHEEL_URL}" >> /opt/workspace-internal/constraints.txt && \
    echo "torchaudio @ ${TORCHAUDIO_WHEEL_URL}" >> /opt/workspace-internal/constraints.txt
ENV PIP_CONSTRAINT=/opt/workspace-internal/constraints.txt

# SageAttention Build
RUN if [ "$SAGEATTENTION_VERSION" != "none" ]; then \
      source /venv/main/bin/activate && \
      pip install triton -c /opt/workspace-internal/constraints.txt && \
      git clone https://github.com/thu-ml/SageAttention.git /tmp/sageattention && \
      cd /tmp/sageattention && \
      if [ "$SAGEATTENTION_VERSION" = "v3" ]; then cd sageattention3_blackwell; fi && \
      pip install --no-build-isolation -c /opt/workspace-internal/constraints.txt . && \
      cd /tmp && \
      rm -rf /tmp/sageattention; \
    fi

# ComfyUI & Custom Nodes Pre-setup
RUN source /venv/main/bin/activate && \
    cd /opt/workspace-internal/ && \
    git clone https://github.com/comfyanonymous/ComfyUI -b "${COMFYUI_REF}" && \
    cd ComfyUI && pip install --no-cache-dir -r requirements.txt && \
    cd custom_nodes && \
    git clone https://github.com/Comfy-Org/ComfyUI-Manager.git --depth 1 && \
    pip install --no-cache-dir -r ComfyUI-Manager/requirements.txt && \
    git clone https://github.com/city96/ComfyUI-GGUF.git --depth 1 && \
    pip install --no-cache-dir -r ComfyUI-GGUF/requirements.txt && \
    git clone https://github.com/kijai/ComfyUI-KJNodes.git --depth 1 && \
    pip install --no-cache-dir -r ComfyUI-KJNodes/requirements.txt && \
    git clone https://github.com/slahiri/ComfyUI-Workflow-Models-Downloader.git --depth 1 && \
    pip install --no-cache-dir -r ComfyUI-Workflow-Models-Downloader/requirements.txt

# STAGE 3: Final Runtime
FROM docker.io/nvidia/cuda:13.2.1-base-rockylinux10@sha256:2d040b8c67d130c0a7f514204d8704ddcef4103cd5118b949401e8153c6dfad6 AS cuda

LABEL org.opencontainers.image.source="https://github.com/smerschjohann/containers/"
LABEL org.opencontainers.image.description="Image for AI/ML development with CUDA 13.2.0 (Optimized)"
LABEL org.opencontainers.image.title="CUDA 13.2.0 Optimized"
LABEL maintainer="Simon Merschjohann"

# renovate: datasource=github-releases depName=coder/code-server
ARG CODE_SERVER_VERSION=v4.117.0

# renovate: datasource=github-releases depName=just-containers/s6-overlay
ARG S6_OVERLAY_VERSION=v3.2.0.2

# renovate: datasource=github-releases depName=rclone/rclone
ARG RCLONE_VERSION=v1.74.0

RUN dnf install epel-release -y && crb enable && \
    dnf install -y --nogpgcheck https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm && \
    dnf install -y which gperftools-libs python3 python3-pip git acl xz zstd openssl bzip2 procps-ng sudo mesa-libGLU btop ffmpeg aria2 && \
    dnf install -y https://github.com/coder/code-server/releases/download/${CODE_SERVER_VERSION}/code-server-${CODE_SERVER_VERSION#v}-amd64.rpm && \
    dnf install -y https://downloads.rclone.org/${RCLONE_VERSION}/rclone-${RCLONE_VERSION}-linux-amd64.rpm && \
    dnf clean all && rm -rf /var/cache/dnf/* && \
    ln -s /usr/bin/python3 /usr/bin/python

# S6 Overlay
RUN curl -Lo - https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz | tar -C / -Jxpf - && \
    curl -Lo - https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz | tar -C / -Jxpf -

# renovate: datasource=github-releases depName=sigoden/dufs
ARG DUFS_VERSION=v0.45.0

# renovate: datasource=github-releases depName=smerschjohann/ocige
ARG OCIGE_VERSION=v0.1.2

# renovate: datasource=github-releases depName=jpillora/chisel
ARG CHISEL_VERSION=v1.11.5

RUN curl -L https://github.com/sigoden/dufs/releases/download/${DUFS_VERSION}/dufs-${DUFS_VERSION}-x86_64-unknown-linux-musl.tar.gz -o /tmp/dufs.tar.gz && \
    tar -xzf /tmp/dufs.tar.gz -C /tmp/ && \
    mv /tmp/dufs /usr/local/bin/dufs && \
    chmod +x /usr/local/bin/dufs && \
    rm /tmp/dufs.tar.gz && \
    curl -L https://github.com/smerschjohann/ocige/releases/download/${OCIGE_VERSION}/ocige_linux_amd64.tar.gz -o /tmp/ocige.tar.gz && \
    tar -xzf /tmp/ocige.tar.gz -C /tmp/ && \
    mv /tmp/ocige /usr/local/bin/ocige && \
    chmod +x /usr/local/bin/ocige && \
    rm /tmp/ocige.tar.gz && \
    curl -L https://github.com/jpillora/chisel/releases/download/${CHISEL_VERSION}/chisel_${CHISEL_VERSION#v}_linux_amd64.gz -o /tmp/chisel.gz && \
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
ENV SAGEATTENTION_USE=1
ENV LD_LIBRARY_PATH=/usr/local/cuda/targets/x86_64-linux/lib:/usr/local/cuda-13.0/targets/x86_64-linux/lib:${LD_LIBRARY_PATH}

VOLUME [ "/workspace" ]
WORKDIR /workspace
RUN chown -R user:user /workspace /home/user

USER user
RUN code-server --install-extension ms-toolsai.jupyter ms-python.python

ADD --chown=user:user ROOT/ /
ADD --chown=user:user Caddyfile.tmpl landing.html /etc/caddy/

ENTRYPOINT ["/init"]

# STAGE 4: AI Toolkit Builder (separate venv for additive image)
FROM docker.io/nvidia/cuda:13.2.1-devel-rockylinux10@sha256:6e66f5288ea88c69ec31030610c2afaeb3ed7a693004fd79d08fe43fa6d94d55 AS aitoolkit-builder

ARG TORCH_CUDA_ARCH_LIST="8.6 8.9 12.0"
ARG TORCH_WHEEL_URL=https://download.pytorch.org/whl/cu130/torch-2.10.0%2Bcu130-cp312-cp312-manylinux_2_28_x86_64.whl
ARG TORCHVISION_WHEEL_URL=https://download.pytorch.org/whl/cu130/torchvision-0.25.0%2Bcu130-cp312-cp312-manylinux_2_28_x86_64.whl
ARG TORCHAUDIO_WHEEL_URL=https://download.pytorch.org/whl/cu130/torchaudio-2.10.0%2Bcu130-cp312-cp312-manylinux_2_28_x86_64.whl
ARG AI_TOOLKIT_REF=main

RUN dnf install epel-release -y && crb enable && \
    dnf install -y python3 python3-pip python3-devel git gcc-c++ make cmake which nodejs npm && \
    ln -s /usr/bin/python3 /usr/bin/python

RUN mkdir -p /venv /opt/workspace-internal && \
    python -m venv /venv/aitoolkit && \
    /venv/aitoolkit/bin/pip install --no-cache-dir --upgrade pip wheel

RUN source /venv/aitoolkit/bin/activate && \
    pip install --no-cache-dir "${TORCH_WHEEL_URL}" "${TORCHVISION_WHEEL_URL}" "${TORCHAUDIO_WHEEL_URL}"

RUN source /venv/aitoolkit/bin/activate && \
    git clone https://github.com/ostris/ai-toolkit.git /opt/workspace-internal/ai-toolkit && \
    cd /opt/workspace-internal/ai-toolkit && \
    git checkout "${AI_TOOLKIT_REF}" && \
    pip install --no-cache-dir -r requirements.txt

RUN cd /opt/workspace-internal/ai-toolkit/ui && \
    npm install && \
    npm run build && \
    npm run update_db

# STAGE 5: CUDA + AI Toolkit Add-on
FROM cuda AS cuda-aitoolkit

USER root

RUN dnf install epel-release -y && crb enable && \
    dnf install -y nodejs npm && \
    dnf clean all && rm -rf /var/cache/dnf/*

COPY --from=aitoolkit-builder --chown=1000:1000 /venv/aitoolkit /venv/aitoolkit
COPY --from=aitoolkit-builder --chown=1000:1000 /opt/workspace-internal/ai-toolkit /opt/workspace-internal/ai-toolkit

ADD --chown=user:user ROOT-aitoolkit/ /
ADD --chown=user:user landing.aitoolkit.html /etc/caddy/landing.html

ENV PATH=/venv/aitoolkit/bin:${PATH}

USER user

ENTRYPOINT ["/init"]
