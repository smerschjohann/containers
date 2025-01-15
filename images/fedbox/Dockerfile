FROM docker.io/library/fedora:41@sha256:3ec60eb34fa1a095c0c34dd37cead9fd38afb62612d43892fcf1d3425c32bc1e as fedbox
ARG TARGETARCH

RUN dnf remove -y shadow-utils && dnf install -y \
        procps-ng btop git \
        jq vim quilt fzf zsh \
        python python3-pip \
        zstd zip p7zip p7zip-plugins \
        bash-completion tmux \
        just nodejs sqlite3 golang \
        podman podman-compose podman-docker buildah \
        libicu make \
        shadow-utils && \
    dnf clean all && rm -rf /var/cache/yum

COPY --chown=0:0 system_files /

ENV HELM_PLUGINS=/opt/helm-plugins

# renovate: datasource=github-releases depName=helm/helm
ARG HELM_VERSION=v3.17.0

# renovate: datasource=github-releases depName=helmfile/helmfile
ARG HELMFILE_VERSION=v0.169.2

# renovate: datasource=github-releases depName=helmfile/vals
ARG VALS_VERSION=v0.38.0

# renovate: datasource=github-releases depName=kubernetes/kubernetes
ARG KUBERNETES_VERSION=v1.32.0

# renovate: datasource=github-releases depName=cli/cli
ARG GITHUB_CLI_VERSION=v2.65.0

# renovate: datasource=github-releases depName=gokcehan/lf
ARG LF_VERSION=r32

RUN curl -LO https://github.com/cli/cli/releases/download/${GITHUB_CLI_VERSION}/gh_${GITHUB_CLI_VERSION#v}_linux_${TARGETARCH}.rpm && \
    dnf install -y gh_${GITHUB_CLI_VERSION#v}_linux_${TARGETARCH}.rpm && \
    rm gh_${GITHUB_CLI_VERSION#v}_linux_${TARGETARCH}.rpm && \
    dnf clean all && rm -rf /var/cache/yum

RUN curl -Lo /usr/local/bin/kubectl "https://dl.k8s.io/release/${KUBERNETES_VERSION}/bin/linux/${TARGETARCH}/kubectl" && \
    curl -sL "https://get.helm.sh/helm-${HELM_VERSION}-linux-${TARGETARCH}.tar.gz" | tar zxvf - -C /usr/local/bin --strip-components=1 && \
    curl -sL "https://github.com/helmfile/helmfile/releases/download/${HELMFILE_VERSION}/helmfile_${HELMFILE_VERSION#v}_linux_${TARGETARCH}.tar.gz" | tar zxvf - -C /usr/local/bin && \
    curl -sL "https://github.com/helmfile/vals/releases/download/${VALS_VERSION}/vals_${VALS_VERSION#v}_linux_${TARGETARCH}.tar.gz" | tar zxvf - -C /usr/local/bin && \
    curl -sL "https://github.com/gokcehan/lf/releases/download/${LF_VERSION}/lf-linux-${TARGETARCH}.tar.gz" | tar zxvf - -C /usr/local/bin && \
    rm -f /usr/local/bin/LICENSE /usr/local/bin/README* && chmod a+x /usr/local/bin/* && \
    mkdir -p /opt/helm-plugins && \
    helm plugin install https://github.com/databus23/helm-diff && \
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

# renovate: datasource=github-releases depName=coder/code-server
ARG CODE_SERVER_VERSION=v4.96.2

USER root
RUN curl -LO https://github.com/coder/code-server/releases/download/${CODE_SERVER_VERSION}/code-server-${CODE_SERVER_VERSION#v}-${TARGETARCH}.rpm && \
    dnf install -y code-server*.rpm && rm code-server*.rpm && \
    dnf clean all && \
  	rm -rf /var/cache/yum
RUN chmod a+x /usr/bin/*
USER coder
EXPOSE 8080/tcp
CMD [ "/usr/bin/code-server" ]
