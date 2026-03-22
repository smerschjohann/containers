
FROM docker.io/library/golang:1.26.1-alpine@sha256:2389ebfa5b7f43eeafbd6be0c3700cc46690ef842ad962f6c5bd6be49ed82039 AS build

ADD main.go /main.go
RUN go build -ldflags="-s -w" -o /gencert /main.go

FROM docker.io/nvidia/cuda:13.2.0-devel-rockylinux10@sha256:d5808c145d1a8bef253c759081d28925ecc9ecf64d2ce47bd9a9c390fd4deda1 AS cuda

LABEL org.opencontainers.image.source="https://github.com/smerschjohann/containers/"
LABEL org.opencontainers.image.description="Image for AI/ML development with CUDA 13.2.0"
LABEL org.opencontainers.image.title="CUDA 13.2.0"
LABEL maintainer="Simon Merschjohann"

# renovate: datasource=github-releases depName=coder/code-server
ARG CODE_SERVER_VERSION=v4.112.0

ARG COMFYUI_REF=master

ARG SAGEATTENTION_VERSION=v2
ARG SAGEATTENTION_USE=1
ARG TORCH_CUDA_ARCH_LIST="8.6 8.9 12.0" # RTX 3000, NVIDIA L4, RTX 5000 series + RTX Pro 6000 
ARG TORCH_WHEEL_URL=https://download.pytorch.org/whl/cu130/torch-2.10.0%2Bcu130-cp312-cp312-manylinux_2_28_x86_64.whl
ARG TORCHVISION_WHEEL_URL=https://download.pytorch.org/whl/cu130/torchvision-0.25.0%2Bcu130-cp312-cp312-manylinux_2_28_x86_64.whl
ARG TORCHAUDIO_WHEEL_URL=https://download.pytorch.org/whl/cu130/torchaudio-2.10.0%2Bcu130-cp312-cp312-manylinux_2_28_x86_64.whl


RUN dnf install epel-release -y && crb enable && \
    dnf install -y --nogpgcheck https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm && \
    dnf install -y which gperftools-libs python3-pip python3 python3-devel git acl xz zstd bzip2 procps-ng sudo mesa-libGLU g++ btop \
    aria2 ninja-build \
    ffmpeg && \
    curl -L https://github.com/coder/code-server/releases/download/${CODE_SERVER_VERSION}/code-server-${CODE_SERVER_VERSION#v}-amd64.rpm -o /tmp/code-server-${CODE_SERVER_VERSION#v}-amd64.rpm && \
    dnf install -y /tmp/code-server-${CODE_SERVER_VERSION#v}-amd64.rpm && rm /tmp/*.rpm && \
    dnf clean all && rm -rf /var/cache/dnf/*

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN groupadd -g 1000 user && \
    useradd -ms /bin/bash user -u 1000 -g 1000 && \
    echo "PATH=${PATH}" >> /home/user/.bashrc && \
    echo "user ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/user && \
    sudo chmod 0440 /etc/sudoers.d/user && \
    mkdir -m 700 -p /run/user/1000 && \
    chown 1000:1000 /run/user/1000 && \
    mkdir -m 700 /run/dbus && \
    chown 1000:1000 /run/dbus && \
    mkdir /opt/workspace-internal/ && \
    chown 1000:1000 /opt/workspace-internal/ && \
    chmod g+s /opt/workspace-internal/ && \
    chmod 775 /opt/workspace-internal/ && \
    setfacl -d -m g:user:rw- /opt/workspace-internal/

RUN mkdir -p /venv && \
    # Create a virtual env - This gives us portability without sacrificing any functionality
    python -m venv /venv/main && \
    /venv/main/bin/pip install --no-cache-dir \
        wheel \
        huggingface_hub[cli] \
        ipykernel \
        ipywidgets && \
    /venv/main/bin/python -m ipykernel install \
        --name="main" \
        --display-name="Python3 (main venv)" && \
    /venv/main/bin/python -m ipykernel install \
        --name="python3" \
        --display-name="Python3 (ipykernel)" && \
    chown -R user:user /venv

# renovate: datasource=github-releases depName=just-containers/s6-overlay
ARG S6_OVERLAY_VERSION=v3.2.0.2

RUN curl -Lo - https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz | tar -C / -Jxpf - && \
    curl -Lo - https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz | tar -C / -Jxpf -

COPY --from=caddy:2.11.2-alpine@sha256:fce4f15aad23222c0ac78a1220adf63bae7b94355d5ea28eee53910624acedfa /usr/bin/caddy /usr/bin/caddy
ADD Caddyfile.tmpl /etc/caddy/Caddyfile.tmpl
ADD landing.html /etc/caddy/landing.html
RUN chmod a+rwx /etc/caddy

VOLUME [ "/workspace" ]
WORKDIR /workspace

RUN chown -R user:user /workspace /home/user

USER user
ENV HOME=/home/user
ENV PATH=/home/user/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN code-server --install-extension ms-toolsai.jupyter ms-python.python

ENV SAGEATTENTION_VERSION=${SAGEATTENTION_VERSION}
ENV SAGEATTENTION_USE=${SAGEATTENTION_USE}
ENV TORCH_CUDA_ARCH_LIST=${TORCH_CUDA_ARCH_LIST}
ENV PIP_NO_CACHE_DIR=1

RUN --mount=type=cache,target=/home/user/.cache/pip \
    source /venv/main/bin/activate && \
    PIP_NO_CACHE_DIR=0 pip install \
    "${TORCH_WHEEL_URL}" \
    "${TORCHVISION_WHEEL_URL}" \
    "${TORCHAUDIO_WHEEL_URL}"

# Create a constraints file to protect PyTorch versions
# This prevents custom nodes from accidentally downgrading/upgrading PyTorch
RUN echo "torch @ ${TORCH_WHEEL_URL}" > /opt/workspace-internal/constraints.txt && \
    echo "torchvision @ ${TORCHVISION_WHEEL_URL}" >> /opt/workspace-internal/constraints.txt && \
    echo "torchaudio @ ${TORCHAUDIO_WHEEL_URL}" >> /opt/workspace-internal/constraints.txt
ENV PIP_CONSTRAINT=/opt/workspace-internal/constraints.txt


# Install SageAttention for improved attention mechanism performance
# Triton is required for SageAttention's CUDA kernels
RUN if [ "$SAGEATTENTION_VERSION" != "none" ]; then \
      source /venv/main/bin/activate && \
      pip install triton -c /opt/workspace-internal/constraints.txt && \
      git clone https://github.com/thu-ml/SageAttention.git /tmp/sageattention && \
      if [ "$SAGEATTENTION_VERSION" = "v3" ]; then \
        cd /tmp/sageattention/sageattention3_blackwell; \
      elif [ "$SAGEATTENTION_VERSION" = "v2" ]; then \
        cd /tmp/sageattention; \
      else \
        echo "ERROR: SAGEATTENTION_VERSION must be v2, v3 or none" && exit 1; \
      fi && \
      pip install --no-build-isolation -c /opt/workspace-internal/constraints.txt . && \
      cd /tmp && \
      rm -rf /tmp/sageattention; \
    fi


RUN source /venv/main/bin/activate && \
    cd /opt/workspace-internal/ && \
    git clone https://github.com/comfyanonymous/ComfyUI -b "${COMFYUI_REF}" && \
    cd /opt/workspace-internal/ComfyUI && \
    pip install --no-cache-dir -r requirements.txt && \
    cd /opt/workspace-internal/ComfyUI && \
    LD_PRELOAD=libtcmalloc_minimal.so.4 \
        python main.py \
            --cpu \
            --listen 127.0.0.1 \
            --port 11404 \
            --disable-auto-launch \
            --quick-test-for-ci

# install essential custom nodes
 # Install critical custom nodes
RUN source /venv/main/bin/activate && \
    cd /opt/workspace-internal/ComfyUI/custom_nodes && \
    git clone https://github.com/Comfy-Org/ComfyUI-Manager.git --depth 1 && \
    pip install --no-cache-dir -r ComfyUI-Manager/requirements.txt && \
    git clone https://github.com/city96/ComfyUI-GGUF.git --depth 1 && \
    pip install --no-cache-dir -r ComfyUI-GGUF/requirements.txt && \
    git clone https://github.com/kijai/ComfyUI-KJNodes.git --depth 1 && \
    pip install --no-cache-dir -r ComfyUI-KJNodes/requirements.txt

COPY --chown=user:user --from=build /gencert /usr/local/bin/gencert
ADD --chown=user:user ROOT/ /

ENTRYPOINT ["/init"]