FROM ghcr.io/linuxserver/webtop:fedora-kde@sha256:1e52ed68f0ac4113fcfcbbfbd96b39985db01e7c51ebdbe0fc3bac57ae1c9394 AS fedtop

# renovate: datasource=github-releases depName=microsoft/vscode
ARG VSCODE_VERSION=1.106.1

RUN dnf install -y dnf-plugins-core; \
    dnf config-manager addrepo --from-repofile=https://brave-browser-rpm-release.s3.brave.com/brave-browser.repo; \
    rpm --import https://brave-browser-rpm-release.s3.brave.com/brave-core.asc; \
    rpm --import https://packages.microsoft.com/keys/microsoft.asc; \
    echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" | tee /etc/yum.repos.d/vscode.repo > /dev/null; \
    dnf check-update; \
    dnf install -y brave-browser vim ark code jq golang; \
    dnf clean all
