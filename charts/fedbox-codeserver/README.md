# fedbox-codeserver

A Helm chart for standard code-server deployments as well as sandboxed codejail deployments.

## Installation

### Via OCI Registry (Recommended)

```bash
helm install fedbox-codeserver oci://ghcr.io/smerschjohann/containers/charts/fedbox-codeserver --version 0.1.0
```

Or using [Helmfile](https://helmfile.readthedocs.io/):

```yaml
repositories:
  - name: containers-charts
    oci: true
    url: ghcr.io/smerschjohann/containers/charts

releases:
  - name: my-code-server
    chart: containers-charts/fedbox-codeserver
    version: 0.1.0
```

### Via Direct Release Tarball

You can also download or install the packaged chart directly from GitHub Releases:

```bash
helm install fedbox-codeserver https://github.com/smerschjohann/containers/releases/download/fedbox-codeserver-0.1.0/fedbox-codeserver-0.1.0.tgz
```

## Modes

The default is `mode: standard`. Setting `mode: codejail` automatically applies codejail defaults.

```yaml
mode: codejail
domain: code.example.invalid
portHostCode: code-{{port}}.example.invalid
```

Mode defaults can be explicitly overridden:

```yaml
mode: codejail
runtimeClassName: ""
privileged: false
authEnabled: true
containersStorage:
  mode: loopback
```

Key derived defaults in `codejail` mode:

- `runtimeClassName: kata-clh-runtime-rs`
- `authEnabled: false`
- `privileged: true`
- `containersStorage.mode: block`
- `networkPolicy.enabled: true`

`FQDNNetworkPolicy` remains disabled by default because it is GKE-specific; it can be enabled with `fqdnNetworkPolicy.enabled: true`.

## Remote SSH

In `codejail` mode, `remoteSsh` is enabled by default. In `standard` mode, it is disabled by default. This behavior can be overridden:

```yaml
remoteSsh:
  enabled: true
  proxy:
    enabled: true
```

Proxy environment variables are configured via `SetEnv` directives in the generated `sshd_config`. Without `remoteSsh.proxy.enabled`, no `SetEnv` lines are rendered.