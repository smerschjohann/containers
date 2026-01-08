FROM ghcr.io/linuxserver/webtop:fedora-kde@sha256:e31e8a81faad0d1aa04cf1b2990e0fe51aef8a43a4343778c78605d11466d3fb AS fedtop

# renovate: datasource=github-releases depName=microsoft/vscode
ARG VSCODE_VERSION=1.108.0

RUN dnf install -y dnf-plugins-core; \
    dnf config-manager addrepo --from-repofile=https://brave-browser-rpm-release.s3.brave.com/brave-browser.repo; \
    rpm --import https://brave-browser-rpm-release.s3.brave.com/brave-core.asc; \
    rpm --import https://packages.microsoft.com/keys/microsoft.asc; \
    echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" | tee /etc/yum.repos.d/vscode.repo > /dev/null; \
    dnf check-update; \
    dnf install -y brave-browser vim ark code jq golang; \
    dnf clean all
