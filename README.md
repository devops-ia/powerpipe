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
| `--listen` | Accept connections from `local` or `network` | `local` |
| `--port` | HTTP server port | `9033` |
| `--dashboard-timeout` | Dashboard execution timeout (seconds) | `0` (no timeout) |
| `--watch` | Watch mod files for changes | `true` |
| `--var` | Set a variable value (`key=value`) | — |
| `--var-file` | Path to `.ppvar` file | — |

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
| `POWERPIPE_DATABASE` | — | Database connection string (deprecated — use config) |
| `POWERPIPE_DASHBOARD_TIMEOUT` | `0` | Dashboard timeout (seconds) |
| `POWERPIPE_BENCHMARK_TIMEOUT` | `0` | Benchmark timeout (seconds) |
| `POWERPIPE_MEMORY_MAX_MB` | `1024` | Process memory soft limit (MB) |
| `POWERPIPE_MAX_PARALLEL` | `10` | Maximum parallel executions |
| `POWERPIPE_INSTALL_DIR` | `/home/powerpipe/.powerpipe` | Installation directory |

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