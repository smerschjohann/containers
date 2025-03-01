# CUDA container



## run with

```bash
podman run --rm -it -p 8443:8443 --userns=keep-id --device nvidia.com/gpu=all --security-opt=label=disable -e PROVISION_SCRIPT=http://download.link -e IP_DOMAIN=nip.io --name mycuda cuda
```
