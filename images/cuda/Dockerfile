FROM docker.io/library/golang:1.24.2-alpine@sha256:7772cb5322baa875edd74705556d08f0eeca7b9c4b5367754ce3f2f00041ccee AS build

ADD main.go /main.go
RUN go build -ldflags="-s -w" -o /gencert /main.go

FROM docker.io/nvidia/cuda:12.8.1-cudnn-runtime-rockylinux9@sha256:77ee6a8dd2d493f2189b964b43d53bd56984421e1e8d34a829459540c8ed2156 AS cuda

LABEL org.opencontainers.image.source="https://github.com/smerschjohann/containers/"
LABEL org.opencontainers.image.description="Image for AI/ML development with CUDA 12.4.1 and Python 3.11"
LABEL org.opencontainers.image.title="CUDA 12.4.1 with Python 3.11"
LABEL maintainer="Simon Merschjohann"

RUN dnf install epel-release -y && crb enable && \
    dnf install -y --nogpgcheck https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm && \
    dnf install -y which gperftools-libs python3-pip python3.11 git acl xz zstd bzip2 procps-ng sudo mesa-libGLU g++ btop \
    aria2 \
    ffmpeg \
    && dnf clean all
RUN ln -s /usr/bin/python3.11 /usr/bin/python
RUN rm /usr/bin/python3; ln -s /usr/bin/python3.11 /usr/bin/python3

RUN groupadd -g 1000 user && \
    useradd -ms /bin/bash user -u 1000 -g 1000 && \
    echo "PATH=${PATH}" >> /home/user/.bashrc && \
    echo "user ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/user && \
    sudo chmod 0440 /etc/sudoers.d/user && \
    mkdir -m 700 -p /run/user/1000 && \
    chown 1000:1000 /run/user/1000 && \
    mkdir /run/dbus && \
    mkdir /opt/workspace-internal/ && \
    chown 1000:1000 /opt/workspace-internal/ && \
    chmod g+s /opt/workspace-internal/ && \
    chmod 775 /opt/workspace-internal/ && \
    setfacl -d -m g:user:rw- /opt/workspace-internal/

# renovate: datasource=github-releases depName=coder/code-server
ARG CODE_SERVER_VERSION=v4.99.3

RUN curl -L https://github.com/coder/code-server/releases/download/${CODE_SERVER_VERSION}/code-server-${CODE_SERVER_VERSION#v}-amd64.rpm -o /tmp/code-server-${CODE_SERVER_VERSION#v}-amd64.rpm && \
    dnf install -y /tmp/code-server-${CODE_SERVER_VERSION#v}-amd64.rpm && rm /tmp/*.rpm && \
    dnf clean all

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
    # Re-add as default.  We don't want users accidentally installing packages in the system python
    /venv/main/bin/python -m ipykernel install \
        --name="python3" \
        --display-name="Python3 (ipykernel)" && \
    chown -R user:user /venv

# renovate: datasource=github-releases depName=just-containers/s6-overlay
ARG S6_OVERLAY_VERSION=v3.2.0.2

RUN curl -Lo - https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz | tar -C / -Jxpf - && \
    curl -Lo - https://github.com/just-containers/s6-overlay/releases/download/${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz | tar -C / -Jxpf -

COPY --from=caddy:2.10.0-alpine@sha256:e2e3a089760c453bc51c4e718342bd7032d6714f15b437db7121bfc2de2654a6 /usr/bin/caddy /usr/bin/caddy
ADD Caddyfile.tmpl /etc/caddy/Caddyfile.tmpl
RUN chmod a+rwx /etc/caddy

VOLUME [ "/workspace" ]
WORKDIR /workspace

RUN chown -R user:user /workspace /home/user

USER user
ENV HOME /home/user
ENV PATH /home/user/.local/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN code-server --install-extension ms-toolsai.jupyter ms-python.python

# renovate: datasource=github-releases depName=comfyanonymous/ComfyUI
ARG COMFYUI_REF=v0.3.18

RUN source /venv/main/bin/activate && \
    pip install --no-cache-dir -U torch torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu124 && \
    cd /opt/workspace-internal/ && \
    git clone https://github.com/comfyanonymous/ComfyUI -b "${COMFYUI_REF}" && \
    cd /opt/workspace-internal/ComfyUI && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir accelerate clip_interrogator>=0.6.0 lark opencv-python sentencepiece spandrel matplotlib onnxruntime-gpu peft pywavelets diffusers && \
    # Avoid Jupyter directory display bug
    ln -s /opt/workspace-internal/ComfyUI/models/checkpoints /opt/workspace-internal/ComfyUI/models/ckpt && \
    # Install critical custom nodes
    cd /opt/workspace-internal/ComfyUI/custom_nodes && \
    git clone https://github.com/ltdrdata/ComfyUI-Manager && \
    pip install --no-cache-dir -r ComfyUI-Manager/requirements.txt && \
    git clone https://github.com/cubiq/ComfyUI_essentials && \
    pip install --no-cache-dir -r ComfyUI_essentials/requirements.txt && \
    git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes && \
    git clone https://github.com/ssitu/ComfyUI_UltimateSDUpscale --recursive --depth 1 && \
    pip install --no-cache-dir gguf imageio-ffmpeg && \
    # Download custom models into the build if you want them - None included in default build
    # wget -O /opt/workspace-internal/ComfyUI/models/checkpoints/model1.safetensors https://url.to.files/model1.safetensors && \
    # wget -O /opt/workspace-internal/ComfyUI/models/checkpoints/model2.safetensors https://url.to.files/model2.safetensors && \
    # Quick startup test in CPU mode to ensure requirements ready and startup succeeds
    cd /opt/workspace-internal/ComfyUI && \
    LD_PRELOAD=libtcmalloc_minimal.so.4 \
        python main.py \
            --cpu \
            --listen 127.0.0.1 \
            --port 11404 \
            --disable-auto-launch \
            --quick-test-for-ci && \
    # Cleanup
    pip cache purge

COPY --chown=user:user --from=build /gencert /usr/local/bin/gencert
ADD --chown=user:user ROOT/ /

ENTRYPOINT ["/init"]