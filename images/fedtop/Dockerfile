FROM ghcr.io/linuxserver/webtop:fedora-kde@sha256:6ce4e279333fc769ca5d90c079fa35a30d99e2ace9e6a5d3a53ecef3726314db AS fedtop

# renovate: datasource=github-releases depName=microsoft/vscode
ARG VSCODE_VERSION=1.144.0

RUN dnf install -y dnf-plugins-core; \
    dnf config-manager addrepo --from-repofile=https://brave-browser-rpm-release.s3.brave.com/brave-browser.repo; \
    rpm --import https://brave-browser-rpm-release.s3.brave.com/brave-core.asc; \
    rpm --import https://packages.microsoft.com/keys/microsoft.asc; \
    echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" | tee /etc/yum.repos.d/vscode.repo > /dev/null; \
    dnf check-update; \
    dnf install -y brave-browser vim ark code jq golang; \
    dnf clean all
