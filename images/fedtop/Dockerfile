FROM ghcr.io/linuxserver/webtop:fedora-kde@sha256:e5599b59531191af6ae92f7c9eb72b55975368e264a53e7a0d6d89acef4b5ec4 AS fedtop

# renovate: datasource=github-releases depName=microsoft/vscode
ARG VSCODE_VERSION=1.95.2

# renovate: datasource=github-releases depName=brave/brave-browser
ARG BRAVE_VERSION=v1.75.18

RUN sudo dnf install -y dnf-plugins-core; \
    sudo dnf config-manager --add-repo https://brave-browser-rpm-release.s3.brave.com/brave-browser.repo; \
    sudo rpm --import https://brave-browser-rpm-release.s3.brave.com/brave-core.asc; \
    sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc; \
    echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/vscode.repo > /dev/null; \
    dnf check-update; \
    sudo dnf install -y brave-browser vim ark code jq