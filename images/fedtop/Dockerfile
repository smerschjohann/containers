FROM ghcr.io/linuxserver/webtop:fedora-kde@sha256:fb4aabc161e54d972ca72bd48b0daebaeead60d4ffacb7cc3da9399b68156270 AS fedtop

# renovate: datasource=github-releases depName=microsoft/vscode
ARG VSCODE_VERSION=1.94.0

# renovate: datasource=github-releases depName=brave/brave-browser
ARG BRAVE_VERSION=v1.72.55

RUN sudo dnf install -y dnf-plugins-core; \
    sudo dnf config-manager --add-repo https://brave-browser-rpm-release.s3.brave.com/brave-browser.repo; \
    sudo rpm --import https://brave-browser-rpm-release.s3.brave.com/brave-core.asc; \
    sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc; \
    echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/vscode.repo > /dev/null; \
    dnf check-update; \
    sudo dnf install -y brave-browser vim ark code