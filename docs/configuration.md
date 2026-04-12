# Configuration

## Database connection

Powerpipe requires a PostgreSQL-compatible database (Steampipe). Set this with `POWERPIPE_DATABASE`:

```bash
docker run -d \
  -e POWERPIPE_DATABASE="postgresql://steampipe:mypassword@steampipe:9193/steampipe" \
  ghcr.io/devops-ia/powerpipe:1.5.1
```

The connection string format: `postgresql://<user>:<password>@<host>:<port>/<dbname>`

## Environment variables

All variables can be set via `-e` flags or a `.env` file in Docker Compose.

### Server settings

| Variable | Default (image) | Description |
|----------|----------------|-------------|
| `POWERPIPE_DATABASE` | — | **Required.** Steampipe connection string |
| `POWERPIPE_LISTEN` | `network` | `local` or `network` (bind to all interfaces) |
| `POWERPIPE_PORT` | `9033` | HTTP port for the dashboard server |
| `POWERPIPE_BASE_URL` | — | Public URL used in share links (e.g. `https://my.domain`) |

### Execution settings

| Variable | Default (image) | Description |
|----------|----------------|-------------|
| `POWERPIPE_MAX_PARALLEL` | `10` | Max concurrent queries |
| `POWERPIPE_MEMORY_MAX_MB` | `1024` | Memory limit in MB |
| `POWERPIPE_BENCHMARK_TIMEOUT` | `0` | Benchmark timeout (0 = unlimited) |
| `POWERPIPE_DASHBOARD_TIMEOUT` | `0` | Dashboard timeout (0 = unlimited) |

### Mod and workspace

| Variable | Default (image) | Description |
|----------|----------------|-------------|
| `POWERPIPE_MOD_LOCATION` | `/workspace` | Directory containing `mod.pp` files |
| `POWERPIPE_WORKSPACE_PROFILES_LOCATION` | — | Custom workspace profiles directory |

### Operational

| Variable | Default (image) | Description |
|----------|----------------|-------------|
| `POWERPIPE_UPDATE_CHECK` | `false` | Disable update check |
| `POWERPIPE_TELEMETRY` | `none` | Disable telemetry |
| `POWERPIPE_LOG_LEVEL` | `warn` | Log verbosity: `error`, `warn`, `info`, `debug`, `trace` |
| `POWERPIPE_INSTALL_DIR` | `/home/powerpipe/.powerpipe` | Powerpipe install directory |

## Mounting a mod workspace

Mods are installed into the workspace volume. Mount your mod directory:

```bash
docker run -d \
  -v "$PWD/workspace:/workspace" \
  -e POWERPIPE_MOD_LOCATION=/workspace \
  -e POWERPIPE_DATABASE="postgresql://steampipe:pass@steampipe:9193/steampipe" \
  ghcr.io/devops-ia/powerpipe:1.5.1
```

Inside the container, install mods:

```bash
docker exec powerpipe powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance
```

## Variable files (`.ppvars`)

For mods that accept input variables, create a `.ppvars` file:

```hcl
# workspace/steampipe.ppvars
benchmark_tags = {
  environment = "production"
  team        = "platform"
}
```

Mount it alongside your workspace:

```bash
docker run -d \
  -v "$PWD/workspace:/workspace" \
  -v "$PWD/steampipe.ppvars:/workspace/steampipe.ppvars:ro" \
  ghcr.io/devops-ia/powerpipe:1.5.1
```

## Using secrets for the database password

In production, avoid passing plaintext passwords via environment variables. Use Docker secrets or Kubernetes Secrets:

```yaml
# docker-compose.yml (Docker Swarm)
services:
  powerpipe:
    image: ghcr.io/devops-ia/powerpipe:1.5.1
    environment:
      POWERPIPE_DATABASE: "postgresql://steampipe:{{ secret('db_password') }}@steampipe:9193/steampipe"
    secrets:
      - db_password
secrets:
  db_password:
    external: true
```

## Debug mode

Enable verbose logging:

```bash
docker run --rm \
  -e POWERPIPE_LOG_LEVEL=debug \
  -e POWERPIPE_DATABASE="..." \
  ghcr.io/devops-ia/powerpipe:1.5.1 \
  powerpipe server
```
