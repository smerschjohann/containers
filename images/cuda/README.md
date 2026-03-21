# CUDA container



## run with

```bash
podman run --rm -it -p 8443:8443 --userns=keep-id --device nvidia.com/gpu=all --security-opt=label=disable -e PROVISION_SCRIPT=http://download.link -e IP_DOMAIN=nip.io --name mycuda cuda
```

ComfyUI starts with `--novram` by default in this image (safer for 8-12GB GPUs).

Optional environment variables:

- `COMFYUI_VRAM_FLAG` to override VRAM mode, e.g. `--normalvram`, `--lowvram`, `--novram`.
- `COMFYUI_ARGS` to append arbitrary ComfyUI CLI args.
- `PYTORCH_CUDA_ALLOC_CONF` to override allocator tuning.

Example:

```bash
podman run --rm -it -p 8443:8443 --userns=keep-id --device nvidia.com/gpu=all --security-opt=label=disable \
	-e IP_DOMAIN=nip.io \
	-e COMFYUI_VRAM_FLAG=--novram \
	-e COMFYUI_ARGS="--force-fp16" \
	--name mycuda cuda
```
