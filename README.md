# powerpipe

[![CI](https://github.com/devops-ia/powerpipe/actions/workflows/docker-build.yml/badge.svg)](https://github.com/devops-ia/powerpipe/actions/workflows/docker-build.yml)
[![GitHub release](https://img.shields.io/github/v/release/devops-ia/powerpipe)](https://github.com/devops-ia/powerpipe/releases)
[![Docker Hub](https://img.shields.io/docker/v/devopsiaci/powerpipe?label=Docker%20Hub&logo=docker)](https://hub.docker.com/r/devopsiaci/powerpipe)
[![Docker Pulls](https://img.shields.io/docker/pulls/devopsiaci/powerpipe?logo=docker)](https://hub.docker.com/r/devopsiaci/powerpipe)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Community Docker image for [Powerpipe](https://powerpipe.io) — dashboards for DevOps. Visualize cloud configurations and assess security posture against compliance benchmarks.

> **Why this image?** Turbot stopped publishing official Docker images after Powerpipe v0.1.1. This project provides multi-arch container images built from official pre-compiled binaries.

## Quick start

```bash
# Run Powerpipe server (HTTP dashboard on port 9033)
docker run -d --name powerpipe \
  -p 9033:9033 \
  -e POWERPIPE_DATABASE="postgres://steampipe:password@steampipe-host:9193/steampipe" \
  ghcr.io/devops-ia/powerpipe:1.5.1

# Install a mod
docker exec powerpipe powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance

# Access dashboards
open http://localhost:9033
```

## Image details

| Property | Value |
|----------|-------|
| Base image | `debian:bookworm-slim` |
| Architectures | `linux/amd64`, `linux/arm64` |
| User | `powerpipe` (UID 9193, GID 0) |
| Port | 9033 (HTTP) |
| Default CMD | `powerpipe server` |

## Registries

```bash
# GitHub Container Registry
docker pull ghcr.io/devops-ia/powerpipe:1.5.1

# Docker Hub
docker pull devopsiaci/powerpipe:1.5.1
```

## `server` flags

| Flag | Description | Default |
|------|-------------|---------|
| `--listen` | Accept connections from `local` or `network` | `local` (image default: `network`) |
| `--port` | HTTP server port | `9033` |
| `--dashboard-timeout` | Dashboard execution timeout (seconds) | `0` (no timeout) |
| `--watch` | Watch mod files for changes | `true` |
| `--var` | Set a variable value (`key=value`) | — |
| `--var-file` | Path to `.ppvar` file | — |

## `benchmark run` flags

| Flag | Description | Default |
|------|-------------|---------|
| `--output` | Output format: `text`, `brief`, `csv`, `json`, `html`, `md`, `snapshot`, `none` | `text` |
| `--export` | Export results to file (format inferred from extension: `.json`, `.html`, `.csv`, `.md`) | — |
| `--dry-run` | Preview controls that would run without executing | `false` |
| `--search-path` | Steampipe connection search path | — |
| `--search-path-prefix` | Prepend connections to search path (e.g. `aws_all`) | — |
| `--var` | Set a variable value (`key=value`) | — |
| `--var-file` | Path to `.ppvars` file | — |
| `--tag` | Filter controls by tag (`key=value`) | — |
| `--where` | Filter controls by SQL where clause | — |
| `--timing` | Print timing information | `false` |
| `--max-parallel` | Maximum parallel control executions | `10` |
| `--benchmark-timeout` | Benchmark execution timeout (seconds, `0` = unlimited) | `0` |
| `--progress` | Show execution progress | `true` |
| `--mod-install` | Install mod dependencies before running | `true` |

### Output format examples

```bash
# Human-readable summary
docker exec powerpipe powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 --output brief

# Export as JSON
docker exec powerpipe powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 --export /workspace/results.json

# Export as HTML report
docker exec powerpipe powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 --export /workspace/results.html

# Filter controls by tag
docker exec powerpipe powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 --tag cis_level=1

# Run across specific accounts
docker exec powerpipe powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 --search-path-prefix aws_all
```

## `detection` subcommand

The `detection` subcommand runs detection queries against your data source.

| Subcommand | Description |
|------------|-------------|
| `detection list` | List all detections in installed mods |
| `detection run <name>` | Run a specific detection |
| `detection show <name>` | Show detection details |

### Detection flags (`detection run`)

| Flag | Description | Default |
|------|-------------|---------|
| `--output` | Output format: `text`, `csv`, `json`, `html`, `md`, `snapshot`, `none` | `text` |
| `--export` | Export results to file | — |
| `--search-path` | Steampipe connection search path | — |
| `--max-parallel` | Maximum parallel executions | `10` |
| `--detection-timeout` | Execution timeout (seconds, `0` = unlimited) | `0` |
| `--var` | Set a variable value | — |
| `--var-file` | Path to `.ppvars` file | — |

```bash
# List available detections
docker exec powerpipe powerpipe detection list

# Run a detection
docker exec powerpipe powerpipe detection run <mod>.<detection_name>
```

## Environment variables

Container-optimized defaults are pre-configured. Override as needed:

| Variable | Image default | Description |
|----------|--------------|-------------|
| `POWERPIPE_UPDATE_CHECK` | `false` | Disable update checking |
| `POWERPIPE_TELEMETRY` | `none` | Disable telemetry |
| `POWERPIPE_LISTEN` | `network` | Listen on all interfaces |
| `POWERPIPE_PORT` | `9033` | HTTP server port |
| `POWERPIPE_LOG_LEVEL` | `warn` | Logging level |
| `POWERPIPE_MOD_LOCATION` | `/workspace` | Mod working directory |
| `POWERPIPE_MEMORY_MAX_MB` | `1024` | Process memory soft limit (MB) |
| `POWERPIPE_MAX_PARALLEL` | `10` | Maximum parallel executions |
| `POWERPIPE_INSTALL_DIR` | `/home/powerpipe/.powerpipe` | Installation directory |
| `POWERPIPE_DATABASE` | — | Database connection string (deprecated — use config files) |
| `POWERPIPE_DASHBOARD_TIMEOUT` | — (binary default: `0`) | Dashboard timeout in seconds (`0` = unlimited) |
| `POWERPIPE_BENCHMARK_TIMEOUT` | — (binary default: `0`) | Benchmark timeout in seconds (`0` = unlimited) |

Full reference: [Powerpipe Environment Variables](https://powerpipe.io/docs/reference/env-vars)

## Kubernetes / Helm

This image is designed to work with the [helm-steampipe](https://github.com/devops-ia/helm-steampipe) Helm chart (Powerpipe component):

- **UID 9193 / GID 0** — compatible with OpenShift restricted SCC
- **`/workspace`** — mod working directory, mountable as volume
- **`git` included** — required for `powerpipe mod install` from GitHub
- **Shell available** (`/bin/bash`, `/bin/sh`) for init container scripts

## Documentation

| Topic | Description |
|-------|-------------|
| [Getting Started](docs/getting-started.md) | Docker, Docker Compose, mod install, first dashboard |
| [Configuration](docs/configuration.md) | Environment variables, database connection, mod workspace |
| [Mods](docs/mods.md) | Installing, updating, persisting mods; popular mods list |
| [Integrations](docs/integrations.md) | Compose, nginx reverse proxy, Grafana, CI/CD exports |
| [Kubernetes](docs/kubernetes.md) | Helm chart, workspace PVC, Secrets, health checks |
| [Examples](docs/examples.md) | AWS benchmarks, multi-account, CI/CD integration |
| [Troubleshooting](docs/troubleshooting.md) | Connection errors, mod not found, OOM, debug mode |

## Versioning

Image versions track upstream Powerpipe releases 1:1:

| Image tag | Powerpipe version |
|-----------|-------------------|
| `1.5.1` | [v1.5.1](https://github.com/turbot/powerpipe/releases/tag/v1.5.1) |

New versions are detected automatically via [updatecli](https://www.updatecli.io/) and published after merge.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).