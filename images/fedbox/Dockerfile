FROM docker.io/library/fedora:43@sha256:781b7642e8bf256e9cf75d2aa58d86f5cc695fd2df113517614e181a5eee9138 as fedbox
ARG TARGETARCH

RUN dnf remove -y shadow-utils && dnf install -y \
        procps-ng moreutils btop git wget \
        jq vim quilt fzf zsh age gdu \
        python python3-pip \
        zstd zip p7zip p7zip-plugins \
        bash-completion tmux \
        just nodejs sqlite3 \
        podman podman-compose podman-docker buildah \
        libicu make \
        shadow-utils mkfs.ext4 iproute && \
    dnf clean all && rm -rf /var/cache/yum

COPY --chown=0:0 system_files /

ENV HELM_PLUGINS=/opt/helm-plugins

ENV PATH="/usr/local/go/bin:${PATH}"

# renovate: datasource=github-releases depName=helm/helm
ARG HELM_VERSION=v4.1.1

# renovate: datasource=github-releases depName=helmfile/helmfile
ARG HELMFILE_VERSION=v1.2.3

# renovate: datasource=github-releases depName=helmfile/vals
ARG VALS_VERSION=v0.43.3

# Install Go from official tarball instead of distro package
ARG GO_VERSION=1.25.1

# renovate: datasource=github-releases depName=kubernetes/kubernetes
ARG KUBERNETES_VERSION=v1.35.1

# renovate: datasource=github-releases depName=cli/cli
ARG GITHUB_CLI_VERSION=v2.86.0

# renovate: datasource=github-releases depName=gokcehan/lf
ARG LF_VERSION=r32

ARG CRANE_VERSION=v0.20.7

RUN curl -LO https://github.com/cli/cli/releases/download/${GITHUB_CLI_VERSION}/gh_${GITHUB_CLI_VERSION#v}_linux_${TARGETARCH}.rpm && \
    dnf install -y gh_${GITHUB_CLI_VERSION#v}_linux_${TARGETARCH}.rpm && \
    rm gh_${GITHUB_CLI_VERSION#v}_linux_${TARGETARCH}.rpm && \
    dnf clean all && rm -rf /var/cache/yum

RUN curl -Lo /usr/local/bin/kubectl "https://dl.k8s.io/release/${KUBERNETES_VERSION}/bin/linux/${TARGETARCH}/kubectl" && \
    curl -sL "https://get.helm.sh/helm-${HELM_VERSION}-linux-${TARGETARCH}.tar.gz" | tar zxvf - -C /usr/local/bin --strip-components=1 && \
    curl -sL "https://github.com/helmfile/helmfile/releases/download/${HELMFILE_VERSION}/helmfile_${HELMFILE_VERSION#v}_linux_${TARGETARCH}.tar.gz" | tar zxvf - -C /usr/local/bin && \
    curl -sL "https://github.com/helmfile/vals/releases/download/${VALS_VERSION}/vals_${VALS_VERSION#v}_linux_${TARGETARCH}.tar.gz" | tar zxvf - -C /usr/local/bin && \
    curl -sL "https://github.com/gokcehan/lf/releases/download/${LF_VERSION}/lf-linux-${TARGETARCH}.tar.gz" | tar zxvf - -C /usr/local/bin && \
    curl -sL "https://github.com/google/go-containerregistry/releases/download/${CRANE_VERSION}/go-containerregistry_Linux_${TARGETARCH}.tar.gz" | tar zxvf - -C /usr/local/bin && \
    rm -f /usr/local/bin/LICENSE /usr/local/bin/README* && chmod a+x /usr/local/bin/* && \
    mkdir -p /opt/helm-plugins && \
    helm plugin install https://github.com/databus23/helm-diff --verify=false && \
    TMPDIR=$(mktemp -d) && \
    cd $TMPDIR; curl -sL "https://github.com/kubernetes-sigs/krew/releases/latest/download/krew-linux_${TARGETARCH}.tar.gz" | tar zxvf - && HOME=/etc/skel ./krew-linux_${TARGETARCH} install krew ctx ns && \
    rm -rf $TMPDIR

RUN curl -sSL "https://go.dev/dl/go${GO_VERSION}.linux-${TARGETARCH}.tar.gz" -o /tmp/go${GO_VERSION}.linux-${TARGETARCH}.tar.gz && \
    rm -rf /usr/local/go && \
    tar -C /usr/local -xzf /tmp/go${GO_VERSION}.linux-${TARGETARCH}.tar.gz && \
    rm -f /tmp/go${GO_VERSION}.linux-${TARGETARCH}.tar.gz && \
    chmod -R 0755 /usr/local/go/bin && \
    ln -sf /usr/local/go/bin/go /usr/local/bin/go

RUN useradd -s /usr/bin/zsh -G wheel -pcoder coder && \
    echo "coder ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/nopasswd && \
    chmod 0400 /etc/shadow

VOLUME [ "/home/coder" ]
ENV HOME=/home/coder
CMD [ "/usr/bin/zsh" ]

USER coder

FROM fedbox as fedbox-vscode
ARG TARGETARCH

# renovate: datasource=github-releases depName=microsoft/vscode
ARG VSCODE_VERSION=1.109.2

USER root

RUN set -eux; \
    case "${TARGETARCH}" in \
        amd64|x86_64) VS_CODE_OS=cli-alpine-x64 ;; \
        arm64|aarch64) VS_CODE_OS=cli-alpine-arm64 ;; \
        *) echo "Unsupported TARGETARCH=${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    VS_CODE_URL="https://code.visualstudio.com/sha/download?build=stable&os=${VS_CODE_OS}"; \
    curl -sL "$VS_CODE_URL" | tar zxvf - -C /usr/local/bin;

USER coder


FROM fedbox as fedbox-codeserver

ARG TARGETARCH

# renovate: datasource=github-releases depName=coder/code-server
ARG CODE_SERVER_VERSION=v4.109.2

USER root
RUN curl -LO https://github.com/coder/code-server/releases/download/${CODE_SERVER_VERSION}/code-server-${CODE_SERVER_VERSION#v}-${TARGETARCH}.rpm && \
    dnf install -y code-server*.rpm && rm code-server*.rpm && \
    dnf install -y openssh-server && \
    dnf clean all && \
  	rm -rf /var/cache/yum
RUN chmod a+x /usr/bin/*
USER coder
EXPOSE 8080/tcp
CMD [ "/usr/bin/code-server" ]

