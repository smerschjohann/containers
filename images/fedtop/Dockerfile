FROM ghcr.io/linuxserver/webtop:fedora-kde@sha256:19c9b281896ae86b8f03ac9455ba1102102711f82fad8761d50fdbd6db065555 AS fedtop

# renovate: datasource=github-releases depName=microsoft/vscode
ARG VSCODE_VERSION=1.99.3

# renovate: datasource=github-releases depName=brave/brave-browser
ARG BRAVE_VERSION=v1.80.28

RUN dnf install -y dnf-plugins-core; \
    dnf config-manager addrepo --from-repofile=https://brave-browser-rpm-release.s3.brave.com/brave-browser.repo; \
    rpm --import https://brave-browser-rpm-release.s3.brave.com/brave-core.asc; \
    rpm --import https://packages.microsoft.com/keys/microsoft.asc; \
    echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" | tee /etc/yum.repos.d/vscode.repo > /dev/null; \
    dnf check-update; \
    dnf install -y brave-browser vim ark code jq; \
    dnf clean all