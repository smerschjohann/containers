FROM ghcr.io/linuxserver/webtop:fedora-kde@sha256:e1815340bbd97c947f3125b6bfdd24c8bee4d606db3159c044afd6261be5f4ca AS fedtop

# renovate: datasource=github-releases depName=microsoft/vscode
ARG VSCODE_VERSION=1.96.4

# renovate: datasource=github-releases depName=brave/brave-browser
ARG BRAVE_VERSION=v1.76.45

RUN dnf install -y dnf-plugins-core; \
    dnf config-manager addrepo --from-repofile=https://brave-browser-rpm-release.s3.brave.com/brave-browser.repo; \
    rpm --import https://brave-browser-rpm-release.s3.brave.com/brave-core.asc; \
    rpm --import https://packages.microsoft.com/keys/microsoft.asc; \
    echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" | tee /etc/yum.repos.d/vscode.repo > /dev/null; \
    dnf check-update; \
    dnf install -y brave-browser vim ark code jq; \
    dnf clean all