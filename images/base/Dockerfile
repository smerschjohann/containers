#FROM registry.fedoraproject.org/fedora:38 as base
# a bit bigger but compatible with toolbox/distrobox
FROM registry.fedoraproject.org/fedora-toolbox:latest as base

RUN dnf install -y \
        procps-ng btop \
        docker docker-compose \
        jq vim quilt fzf zsh \
        golang python python3-pip \
        zstd zip p7zip p7zip-plugins \
        bash-completion tmux \
        just \
        && \
    dnf clean all && rm -rf /var/cache/yum

COPY --chown=0:0 system_files /

RUN if [[ "$TARGETARCH" == "arm64" ]]; then \
        DOCKERARCH="aarch64"; GOARCH="arm64"; \
    else \
        DOCKERARCH="x86_64"; GOARCH="amd64"; \
    fi; \
    curl -Lo /usr/bin/kubectl "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/${GOARCH}/kubectl" && \
    TMPDIR=$(mktemp -d) && \
    cd $TMPDIR; curl -sL "https://github.com/kubernetes-sigs/krew/releases/latest/download/krew-linux_${GOARCH}.tar.gz" | tar zxvf - && HOME=/etc/skel ./krew-linux_${GOARCH} install krew ctx ns && \
    rm -rf $TMPDIR

RUN useradd -s /usr/bin/zsh -G docker,wheel -pcoder coder && \
    echo "coder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/nopasswd

USER coder