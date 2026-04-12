# Kubernetes

The recommended way to run Powerpipe on Kubernetes is via the [helm-steampipe](https://github.com/devops-ia/helm-steampipe) chart, which manages both Steampipe and Powerpipe as a single release.

## Quick install with Helm

```bash
helm repo add devops-ia https://devops-ia.github.io/helm-charts
helm repo update

helm install steampipe devops-ia/steampipe \
  --set powerpipe.enabled=true \
  --set bbdd.enabled=true \
  --set bbdd.listen=network
```

Powerpipe will be available on port 9033 of the Powerpipe Service.

## Custom values

Create a `values.yaml` to configure both components:

```yaml
# Steampipe (required by Powerpipe)
bbdd:
  enabled: true
  listen: network

# Powerpipe
powerpipe:
  enabled: true
  image:
    repository: ghcr.io/devops-ia/powerpipe
    tag: "1.5.1"
  env:
    - name: POWERPIPE_MAX_PARALLEL
      value: "10"
    - name: POWERPIPE_LOG_LEVEL
      value: "warn"
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "2Gi"
      cpu: "1"
  ingress:
    enabled: true
    className: nginx
    hosts:
      - host: powerpipe.example.com
        paths:
          - path: /
            pathType: Prefix
```

```bash
helm install steampipe devops-ia/steampipe -f values.yaml
```

## Mounting a mod workspace

Use a PersistentVolumeClaim to persist installed mods:

```yaml
powerpipe:
  enabled: true
  extraVolumes:
    - name: workspace
      persistentVolumeClaim:
        claimName: powerpipe-workspace
  extraVolumeMounts:
    - name: workspace
      mountPath: /workspace
  env:
    - name: POWERPIPE_MOD_LOCATION
      value: /workspace
```

Install a mod in the PVC on first run using an init container:

```yaml
powerpipe:
  initContainers:
    - name: install-mods
      image: ghcr.io/devops-ia/powerpipe:1.5.1
      command:
        - sh
        - -c
        - |
          powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance
      env:
        - name: POWERPIPE_MOD_LOCATION
          value: /workspace
      volumeMounts:
        - name: workspace
          mountPath: /workspace
```

## Database connection with Kubernetes Secrets

Store the Steampipe database password in a Secret:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: steampipe-db-password
type: Opaque
stringData:
  password: "mysecretpassword"
```

Reference it in the Powerpipe deployment:

```yaml
powerpipe:
  enabled: true
  extraEnvVarsSecret: steampipe-db-password
  env:
    - name: STEAMPIPE_DATABASE_PASSWORD
      valueFrom:
        secretKeyRef:
          name: steampipe-db-password
          key: password
```

## OpenShift

The image is OpenShift compatible (UID 9193, GID 0):

```yaml
# No securityContext overrides needed — runs with the default SCC
powerpipe:
  enabled: true
  securityContext:
    runAsUser: 9193
    runAsGroup: 0
    fsGroup: 0
```

## Health checks

Powerpipe exposes an HTTP endpoint. The chart configures these automatically:

```yaml
livenessProbe:
  httpGet:
    path: /
    port: 9033
  initialDelaySeconds: 30
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /
    port: 9033
  initialDelaySeconds: 10
  periodSeconds: 10
```

## Verifying the deployment

```bash
# Check pods are running
kubectl get pods -l app.kubernetes.io/name=steampipe

# Port-forward to access Powerpipe locally
kubectl port-forward svc/steampipe-powerpipe 9033:9033

# Open browser
open http://localhost:9033
```
