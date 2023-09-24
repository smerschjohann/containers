set export
TAG := "dev"

build-fedbox platform="amd64":
    buildah bud \
        --platform linux/$platform \
        -f $PWD/images/fedbox/Dockerfile \
        --format docker \
        --tls-verify=true \
        -t fedbox:$TAG-$platform \
        --target fedbox \
        --layers \
        $PWD/images/fedbox

build-fedbox-codeserver platform="amd64":
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