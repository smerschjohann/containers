ARG TAGORDIGEST=:39
FROM docker.io/library/fedora${TAGORDIGEST} as fedbox
# a bit bigger but compatible with toolbox/distrobox
#FROM registry.fedoraproject.org/fedora-toolbox:latest as fedbox
ARG TARGETARCH

RUN dnf install -y \
        procps-ng btop git \
        jq vim quilt fzf zsh \
        python python3-pip \
        zstd zip p7zip p7zip-plugins \
        bash-completion tmux \
        just nodejs sqlite3 \
        podman podman-compose podman-docker buildah \
        libicu \
        && \
    dnf reinstall -y shadow-utils && \
    dnf clean all && rm -rf /var/cache/yum

COPY --chown=0:0 system_files /

RUN curl -Lo /usr/bin/kubectl "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/${TARGETARCH}/kubectl" && \
    # manually install go version as Fedora 39 still has 1.21.1 with the CVE unfixed https://github.com/golang/go/issues/63427
    curl -sL https://go.dev/dl/go1.21.3.linux-${TARGETARCH}.tar.gz | tar zxvf - -C /usr/local && \
    chmod a+x /usr/local/go/bin/* && \
    ln -s /usr/local/go/bin/* /usr/local/bin/ && \
    TMPDIR=$(mktemp -d) && \
    cd $TMPDIR; curl -sL "https://github.com/kubernetes-sigs/krew/releases/latest/download/krew-linux_${TARGETARCH}.tar.gz" | tar zxvf - && HOME=/etc/skel ./krew-linux_${TARGETARCH} install krew ctx ns && \
    rm -rf $TMPDIR

RUN useradd -s /usr/bin/zsh -G wheel -pcoder coder && \
    echo "coder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/nopasswd

VOLUME [ "/home/coder" ]
ENV HOME=/home/coder
CMD [ "/usr/bin/zsh" ]

USER coder

FROM fedbox as fedbox-codeserver

ARG TARGETARCH
ARG CODE_SERVER_VERSION=4.22.1

USER root
RUN curl -LO https://github.com/coder/code-server/releases/download/v${CODE_SERVER_VERSION}/code-server-${CODE_SERVER_VERSION}-${TARGETARCH}.rpm && \
    dnf install -y code-server*.rpm && rm code-server*.rpm && \
    dnf clean all && \
  	rm -rf /var/cache/yum
RUN chmod a+x /usr/bin/*
USER coder
EXPOSE 8080/tcp
CMD [ "/usr/bin/code-server" ]
