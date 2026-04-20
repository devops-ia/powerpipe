# Integrations

Powerpipe serves an HTTP dashboard on port 9033. It works with any tool that can embed or proxy HTTP.

## Steampipe + Powerpipe (Docker Compose)

The standard full-stack setup pairs Powerpipe with Steampipe as the data source:

```yaml
# docker-compose.yml
services:
  steampipe:
    image: ghcr.io/devops-ia/steampipe:2.4.1
    container_name: steampipe
    command: ["steampipe", "service", "start", "--foreground", "--database-listen", "network"]
    ports:
      - "9193:9193"
    environment:
      STEAMPIPE_DATABASE_PASSWORD: steampipe
    volumes:
      - steampipe-data:/home/steampipe/.steampipe
      - ./aws.spc:/home/steampipe/.steampipe/config/aws.spc:ro
    healthcheck:
      test: ["CMD", "pg_isready", "-h", "localhost", "-p", "9193", "-U", "steampipe"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s

  powerpipe:
    image: ghcr.io/devops-ia/powerpipe:1.5.1
    container_name: powerpipe
    command: ["powerpipe", "server", "--listen", "network"]
    ports:
      - "9033:9033"
    environment:
      POWERPIPE_DATABASE: "postgresql://steampipe:steampipe@steampipe:9193/steampipe"
    volumes:
      - powerpipe-workspace:/workspace
    depends_on:
      steampipe:
        condition: service_healthy

volumes:
  steampipe-data:
  powerpipe-workspace:
```

```bash
docker compose up -d
open http://localhost:9033
```

## Reverse proxy (nginx)

Expose Powerpipe dashboards under a custom path or domain:

```nginx
# nginx.conf
server {
    listen 80;
    server_name dashboards.example.com;

    location / {
        proxy_pass         http://powerpipe:9033;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

Set `POWERPIPE_BASE_URL` so that share links use the public URL:

```yaml
services:
  powerpipe:
    image: ghcr.io/devops-ia/powerpipe:1.5.1
    environment:
      POWERPIPE_DATABASE: "postgresql://steampipe:steampipe@steampipe:9193/steampipe"
      POWERPIPE_BASE_URL: "https://dashboards.example.com"
```

Full compose with nginx:

```yaml
# docker-compose-nginx.yml
services:
  steampipe:
    image: ghcr.io/devops-ia/steampipe:2.4.1
    command: ["steampipe", "service", "start", "--foreground", "--database-listen", "network"]
    environment:
      STEAMPIPE_DATABASE_PASSWORD: steampipe
    volumes:
      - steampipe-data:/home/steampipe/.steampipe
    healthcheck:
      test: ["CMD", "pg_isready", "-h", "localhost", "-p", "9193", "-U", "steampipe"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s

  powerpipe:
    image: ghcr.io/devops-ia/powerpipe:1.5.1
    environment:
      POWERPIPE_DATABASE: "postgresql://steampipe:steampipe@steampipe:9193/steampipe"
      POWERPIPE_BASE_URL: "https://dashboards.example.com"
    volumes:
      - powerpipe-workspace:/workspace
    depends_on:
      steampipe:
        condition: service_healthy

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - powerpipe

volumes:
  steampipe-data:
  powerpipe-workspace:
```

## Grafana

Embed Powerpipe dashboards in Grafana using the [Text panel](https://grafana.com/docs/grafana/latest/panels-visualizations/visualizations/text/) with an iframe, or use the [Infinity datasource](https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/) to query benchmark JSON exports.

### Iframe embed

In a Grafana Text panel (HTML mode):

```html
<iframe
  src="http://powerpipe:9033/aws_compliance.benchmark.cis_aws_foundations_benchmark_v300"
  width="100%"
  height="800px"
  frameborder="0">
</iframe>
```

> **Note:** Grafana must have `security.allow_embedding = true` in `grafana.ini`, and Powerpipe must be reachable from the Grafana container.

### Compose with Grafana

```yaml
# docker-compose-grafana.yml
services:
  steampipe:
    image: ghcr.io/devops-ia/steampipe:2.4.1
    command: ["steampipe", "service", "start", "--foreground", "--database-listen", "network"]
    environment:
      STEAMPIPE_DATABASE_PASSWORD: steampipe
    volumes:
      - steampipe-data:/home/steampipe/.steampipe
    healthcheck:
      test: ["CMD", "pg_isready", "-h", "localhost", "-p", "9193", "-U", "steampipe"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s

  powerpipe:
    image: ghcr.io/devops-ia/powerpipe:1.5.1
    environment:
      POWERPIPE_DATABASE: "postgresql://steampipe:steampipe@steampipe:9193/steampipe"
    volumes:
      - powerpipe-workspace:/workspace
    depends_on:
      steampipe:
        condition: service_healthy

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ALLOW_EMBEDDING: "true"
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  steampipe-data:
  powerpipe-workspace:
  grafana-data:
```

## CI/CD — benchmark exports

Export benchmark results as JSON for integration with CI pipelines or reporting tools:

```bash
# GitHub Actions — run compliance check on schedule
docker run --rm \
  -v "$HOME/.aws:/home/powerpipe/.aws:ro" \
  -v "$PWD/workspace:/workspace" \
  -e POWERPIPE_DATABASE="${STEAMPIPE_CONNECTION_STRING}" \
  ghcr.io/devops-ia/powerpipe:1.5.1 \
  powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 \
  --export /workspace/results.json \
  --output brief
```

Parse the JSON output with standard tools:

```bash
# Count failed controls
jq '[.groups[].controls[] | select(.status == "alarm")] | length' workspace/results.json
```
