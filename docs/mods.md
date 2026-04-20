# Mods

Powerpipe mods are collections of dashboards, benchmarks, and controls that run against your Steampipe data. Find mods at [hub.powerpipe.io](https://hub.powerpipe.io).

## Managing mods

```bash
# Install a mod
docker exec powerpipe powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance

# Install multiple mods
docker exec powerpipe sh -c "
  powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance &&
  powerpipe mod install github.com/turbot/steampipe-mod-kubernetes-compliance
"

# List installed mods
docker exec powerpipe powerpipe mod list
# Output:
# NAME                                            VERSION   PATH
# github.com/turbot/steampipe-mod-aws-compliance  v0.85.0   /workspace/.powerpipe/mods/...

# Update a mod to the latest version
docker exec powerpipe powerpipe mod update github.com/turbot/steampipe-mod-aws-compliance

# Update all mods
docker exec powerpipe powerpipe mod update

# Remove a mod
docker exec powerpipe powerpipe mod uninstall github.com/turbot/steampipe-mod-aws-compliance
```

## Persisting mods across restarts

Mods are installed inside the container at `/workspace`. Mount a named volume to persist them:

```yaml
services:
  powerpipe:
    image: ghcr.io/devops-ia/powerpipe:1.5.1
    volumes:
      - powerpipe-workspace:/workspace

volumes:
  powerpipe-workspace:
```

Without a persistent volume, mods are lost when the container is removed.

## Popular mods

| Mod | Description | Install |
|-----|-------------|---------|
| [aws-compliance](https://hub.powerpipe.io/mods/turbot/aws_compliance) | CIS, NIST, SOC 2, PCI DSS for AWS | `powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance` |
| [aws-thrifty](https://hub.powerpipe.io/mods/turbot/aws_thrifty) | AWS cost optimization checks | `powerpipe mod install github.com/turbot/steampipe-mod-aws-thrifty` |
| [azure-compliance](https://hub.powerpipe.io/mods/turbot/azure_compliance) | CIS, NIST benchmarks for Azure | `powerpipe mod install github.com/turbot/steampipe-mod-azure-compliance` |
| [gcp-compliance](https://hub.powerpipe.io/mods/turbot/gcp_compliance) | CIS, NIST benchmarks for GCP | `powerpipe mod install github.com/turbot/steampipe-mod-gcp-compliance` |
| [kubernetes-compliance](https://hub.powerpipe.io/mods/turbot/kubernetes_compliance) | NSA/CISA, CIS benchmarks for K8s | `powerpipe mod install github.com/turbot/steampipe-mod-kubernetes-compliance` |

## Mod workspace structure

After installation, mods live under `/workspace/.powerpipe/mods/`:

```
/workspace/
├── .powerpipe/
│   └── mods/
│       └── github.com/
│           └── turbot/
│               └── steampipe-mod-aws-compliance@v0.85.0/
│                   ├── mod.pp
│                   ├── benchmarks/
│                   └── controls/
└── mod.pp          # your workspace mod file (optional)
```

## Running benchmarks from a mod

```bash
# List all benchmarks in installed mods
docker exec powerpipe powerpipe benchmark list

# Run a specific benchmark
docker exec powerpipe \
  powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300

# Run and export results
docker exec powerpipe \
  powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 \
  --export /workspace/results.json \
  --output brief

# Run a one-shot benchmark (no server)
docker run --rm \
  -v "$HOME/.aws:/home/powerpipe/.aws:ro" \
  -v "$PWD/workspace:/workspace" \
  -e POWERPIPE_DATABASE="postgresql://steampipe:pass@host.docker.internal:9193/steampipe" \
  ghcr.io/devops-ia/powerpipe:1.5.1 \
  powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 \
  --output brief
```

## Creating a custom mod

Mount a local directory with your own `mod.pp` and controls:

```bash
# workspace/mod.pp
mod "local_checks" {
  title = "My Custom Checks"
}
```

```yaml
services:
  powerpipe:
    image: ghcr.io/devops-ia/powerpipe:1.5.1
    volumes:
      - ./workspace:/workspace
    environment:
      POWERPIPE_DATABASE: "postgresql://steampipe:pass@steampipe:9193/steampipe"
```
