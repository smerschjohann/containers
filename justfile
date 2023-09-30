set export
TAG := "dev"

build-fedbox platform=arch():
    buildah bud \
        --platform linux/{{platform}} \
        -f $PWD/images/fedbox/Dockerfile \
        --format docker \
        --tls-verify=true \
        -t fedbox:$TAG-{{platform}} \
        --target fedbox \
        --layers \
        $PWD/images/fedbox

build-fedbox-codeserver platform=arch():
    buildah bud \
        --platform linux/$platform \
        -f $PWD/images/fedbox/Dockerfile \
        --format docker \
        --tls-verify=true \
        -t fedbox-codeserver:$TAG-$platform \
        --target fedbox-codeserver \
        --layers \
        $PWD/images/fedbox

build-all: build-fedbox build-fedbox-codeserver

merge:
    #!/bin/bash
    set -ex
    manifest=ghcr.io/smerschjohann/containers/fedbox-codeserver:latest
    buildah manifest rm $manifest || true
    buildah manifest create $manifest
    for arch in "arm64" "amd64"; do
        # would be cool if this is not required ..
        buildah pull --arch $arch $manifest-$arch
        buildah manifest add $manifest docker://$manifest-$arch
    done
    buildah push --all $manifest docker://$manifest

