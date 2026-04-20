# Getting Started

## Prerequisites

You'll need Docker installed. Powerpipe connects to [Steampipe](https://steampipe.io) as its data source — the simplest way to run both is Docker Compose.

## Quick start with Docker Compose

The fastest way to get dashboards running:

```bash
# Clone the examples
curl -O https://raw.githubusercontent.com/devops-ia/powerpipe/main/examples/docker-compose.yml

# Start Steampipe + Powerpipe
docker compose up -d

# Open dashboards
open http://localhost:9033
```

## Manual Docker run

### 1. Create a Docker network

```bash
docker network create powerpipe-net
```

### 2. Start Steampipe first

Powerpipe needs a running Steampipe PostgreSQL endpoint:

```bash
docker run -d --name steampipe \
  --network powerpipe-net \
  -p 9193:9193 \
  -e STEAMPIPE_DATABASE_PASSWORD=mypassword \
  ghcr.io/devops-ia/steampipe:2.4.1 \
  steampipe service start --foreground --database-listen network
```

### 3. Install a plugin

```bash
docker exec steampipe steampipe plugin install aws
```

### 4. Start Powerpipe

```bash
docker run -d --name powerpipe \
  --network powerpipe-net \
  -p 9033:9033 \
  -e POWERPIPE_DATABASE="postgresql://steampipe:mypassword@steampipe:9193/steampipe" \
  ghcr.io/devops-ia/powerpipe:1.5.1
```

### 4. Install a mod

```bash
# Install the AWS Compliance mod
docker exec powerpipe powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance
```

### 5. Open the dashboard

Navigate to [http://localhost:9033](http://localhost:9033) in your browser.

## Docker Compose (recommended)

Using the example compose file from this repo:

```yaml
services:
  steampipe:
    image: ghcr.io/devops-ia/steampipe:2.4.1
    command: ["steampipe", "service", "start", "--foreground", "--database-listen", "network"]
    environment:
      STEAMPIPE_DATABASE_PASSWORD: steampipe
    volumes:
      - steampipe-data:/home/steampipe/.steampipe
      - ./aws.spc:/home/steampipe/.steampipe/config/aws.spc:ro
    healthcheck:
      test: ["CMD", "pg_isready", "-h", "localhost", "-p", "9193"]
      interval: 10s
      timeout: 5s
      retries: 5

  powerpipe:
    image: ghcr.io/devops-ia/powerpipe:1.5.1
    command: ["powerpipe", "server", "--listen", "network"]
    ports:
      - "9033:9033"
    environment:
      POWERPIPE_DATABASE: "postgresql://steampipe:steampipe@steampipe:9193/steampipe"
    volumes:
      - ./workspace:/workspace
    depends_on:
      steampipe:
        condition: service_healthy

volumes:
  steampipe-data:
```

```bash
docker compose up -d
```

## Next steps

- [Configuration](configuration.md) — database connection, env vars, mod workspace
- [Examples](examples.md) — running benchmarks, AWS compliance, mod patterns
- [Kubernetes](kubernetes.md) — deploy with Helm
