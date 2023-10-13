set export
TAG := "dev"

update-digests:
    podman manifest inspect registry.fedoraproject.org/fedora:38 | jq -r '.manifests | .[] | select(.platform.architecture == "arm64" or .platform.architecture == "amd64") | "digest_\(.platform.architecture)=\(.digest)"' | sort > images/fedbox/builddigests

build-fedbox $platform=arch():
    #!/bin/bash
    if [[ $platform == 'aarch64' ]]; then
      platform='arm64'
    fi

    source images/fedbox/builddigests

    var_name="digest_$platform"
    echo $var_name
    digest=${!var_name}

    buildah bud \
        --build-arg TAGORDIGEST="@$digest" \
        --platform linux/$platform \
        -f $PWD/images/fedbox/Dockerfile \
        --format docker \
        --tls-verify=true \
        -t fedbox:$TAG-$platform \
        --target fedbox \
        --layers \
        $PWD/images/fedbox

build-fedbox-codeserver platform=arch():
    #!/bin/bash
    if [[ $platform == 'aarch64' ]]; then
      platform='arm64'
    fi

    source images/fedbox/builddigests

    var_name="digest_$platform"
    echo $var_name
    digest=${!var_name}

    buildah bud \
        --build-arg TAGORDIGEST="@$digest" \
        --platform linux/$platform \
        -f $PWD/images/fedbox/Dockerfile \
        --format docker \
        --tls-verify=true \
        -t fedbox:$TAG-$platform \
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

