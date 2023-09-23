# code-server container

This container includes code-server and additional tools like kubectl, docker, nvm, jq, go, ...

See the Dockerfile for more details.

## Usage
The container is uploaded to the GHCR registry. A few examples are present below
## plain container

```bash
docker run --rm --network=host -v privhome:/home/coder ghcr.io/smerschjohann/febox/code-server:latest --port=8154 --auth=none
```

## with docker usage

```bash
docker run --rm --network=host -v privhome:/home/coder -v /var/run/docker.sock:/var/run/docker.sock ghcr.io/smerschjohann/febox/code-server:latest --port=8154 --auth=none

# if the docker group is not 998 on the docker host, you can allow the container access by:
sudo setfacl -m user:coder:rw /var/run/docker.sock
```

## Kubernetes

This example creates a code-server deployment in the namespace "code". It also adds a sidecar container with chisel to allow accessing the ports directly.

WARNING: The example expects the traefik ingress controller to be configured to only allow access to the resources using client certificates. If applied without these settings, the service can be accessed by anyone knowing the domain address.

```yaml
apiVersion: traefik.containo.us/v1alpha1
kind: TLSOption
metadata:
  name: clientcerts
  namespace: default
spec:
  cipherSuites:
  - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
  - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
  - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
  - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
  - TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305
  - TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305
  clientAuth:
    clientAuthType: RequireAndVerifyClientCert
    secretNames:
    - your-ca
  minVersion: VersionTLS12
  sniStrict: true
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: code-server
  namespace: code
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/instance: code-server
      app.kubernetes.io/name: code-server
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app.kubernetes.io/instance: code-server
        app.kubernetes.io/name: code-server
    spec:
      containers:
      - command:
        - /app/bin
        - server
        - --reverse
        - --socks5
        - --port=1953
        image: jpillora/chisel
        imagePullPolicy: Always
        name: chisel
        resources: {}
        securityContext:
          allowPrivilegeEscalation: false
          seccompProfile:
            type: RuntimeDefault
      - args:
        - --port=8154
        - --disable-getting-started-override
        - --auth=none
        - --proxy-domain=code.your.tld
        - --disable-workspace-trust
        env:
        - name: DISABLE_TELEMETRY
          value: "true"
        - name: VSCODE_PROXY_URI
          value: https://{{port}}.code.your.tld
        - name: PASSWORD
          valueFrom:
            secretKeyRef:
              key: password
              name: code-server
        image: ghcr.io/smerschjohann/febox/code-server:latest
        imagePullPolicy: Always
        livenessProbe:
          failureThreshold: 3
          httpGet:
            path: /
            port: http
            scheme: HTTP
          periodSeconds: 10
          successThreshold: 1
          timeoutSeconds: 1
        name: code-server
        ports:
        - containerPort: 8154
          name: http
          protocol: TCP
        readinessProbe:
          failureThreshold: 3
          httpGet:
            path: /
            port: http
            scheme: HTTP
          periodSeconds: 10
          successThreshold: 1
          timeoutSeconds: 1
        resources: {}
        securityContext:
          runAsUser: 1000
        volumeMounts:
        - mountPath: /var/run/docker.sock
          name: docker-sock
        - mountPath: /home/coder
          name: data
      dnsPolicy: ClusterFirst
      hostname: devbox
      initContainers:
      - command:
        - sh
        - -c
        - |
          chown -R 1000:1000 /home/coder
        image: busybox:latest
        imagePullPolicy: IfNotPresent
        name: init-chmod-data
        resources: {}
        securityContext:
          runAsUser: 0
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
        volumeMounts:
        - mountPath: /home/coder
          name: home
#      nodeSelector:
#        kubernetes.io/hostname: THE_NODE_TO_RUN_IT_ON
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext:
        fsGroup: 1000
      serviceAccount: code-server
      serviceAccountName: code-server
      terminationGracePeriodSeconds: 30
      volumes:
      - hostPath:
          path: /var/run/docker.sock
          type: Socket
        name: docker-sock
      - name: home
        persistentVolumeClaim:
          claimName: code-server
```

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    meta.helm.sh/release-name: code-server
    meta.helm.sh/release-namespace: code
  labels:
    app.kubernetes.io/instance: code-server
    app.kubernetes.io/name: code-server
  name: code-server
  namespace: code
spec:
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
  ports:
  - name: http
    port: 8080
    protocol: TCP
    targetPort: http
  selector:
    app.kubernetes.io/instance: code-server
    app.kubernetes.io/name: code-server
  sessionAffinity: None
  type: ClusterIP
```

```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: code-chisel
  name: code-chisel
  namespace: code
spec:
  ipFamilyPolicy: SingleStack
  ports:
  - name: 1953-1953
    port: 1953
    protocol: TCP
    targetPort: 1953
  selector:
    app.kubernetes.io/instance: code-server
  sessionAffinity: None
  type: ClusterIP
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    traefik.ingress.kubernetes.io/router.priority: "1"
  labels:
    app.kubernetes.io/instance: code-server
    app.kubernetes.io/name: code-server
  name: code-server
  namespace: code
spec:
  ingressClassName: traefik
  rules:
  - host: code.your.tld
    http:
      paths:
      - backend:
          service:
            name: code-server
            port:
              number: 8080
        path: /
        pathType: Prefix
  - host: '*.code.your.tld'
    http:
      paths:
      - backend:
          service:
            name: code-server
            port:
              number: 8080
        path: /
        pathType: Prefix
  tls:
  - hosts:
    - '*.code.your.tld'
    secretName: wildcard-code-your-tld
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    traefik.ingress.kubernetes.io/router.priority: "42"
  name: code-chisel
  namespace: code
spec:
  ingressClassName: traefik
  rules:
  - host: chisel.code.your.tld
    http:
      paths:
      - backend:
          service:
            name: code-chisel
            port:
              number: 1953
        path: /
        pathType: Prefix
  tls:
  - hosts:
    - '*.code.your.tld'
    secretName: wildcard-code-your-tld
```

### chisel access

```bash
chisel client -v --tls-key ~/cert-private.pem --tls-cert ~/cert-public.pem https://chisel.code.your.tld '8080'
```
