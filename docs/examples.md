# Examples

## Running a benchmark

With a mod installed, run a compliance benchmark:

```bash
# Install the AWS Compliance mod
docker exec powerpipe powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance

# List available benchmarks
docker exec powerpipe powerpipe benchmark list

# Run the CIS AWS Foundations benchmark
docker exec powerpipe powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300

# Export results as JSON
docker exec powerpipe \
  powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 \
  --export /workspace/results.json
```

## Docker Compose — Full stack

The complete stack for Powerpipe + Steampipe + AWS:

```yaml
# docker-compose.yml
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
    ports:
      - "9033:9033"
    environment:
      POWERPIPE_DATABASE: "postgresql://steampipe:steampipe@steampipe:9193/steampipe"
    volumes:
      - workspace:/workspace
    depends_on:
      steampipe:
        condition: service_healthy

volumes:
  steampipe-data:
  workspace:
```

```bash
# Install AWS plugin in Steampipe
docker compose exec steampipe steampipe plugin install aws

# Install AWS compliance mod in Powerpipe
docker compose exec powerpipe powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance

# Open dashboards
open http://localhost:9033
```

## AWS credentials

Mount AWS credentials read-only:

```yaml
# In your docker-compose.yml steampipe service:
volumes:
  - "$HOME/.aws:/home/steampipe/.aws:ro"
```

Or set environment variables:

```yaml
environment:
  AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
  AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
  AWS_DEFAULT_REGION: us-east-1
```

## Running benchmarks via CLI (non-interactive)

Run benchmarks from the command line without starting the server:

```bash
# One-shot benchmark (no server needed)
docker run --rm \
  -v "$HOME/.aws:/home/powerpipe/.aws:ro" \
  -v "$PWD/workspace:/workspace" \
  -e POWERPIPE_DATABASE="postgresql://steampipe:pass@host.docker.internal:9193/steampipe" \
  ghcr.io/devops-ia/powerpipe:1.5.1 \
  powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 \
  --output brief
```

## Multiple AWS accounts

Configure Steampipe with an aggregator connection, then query across all accounts from Powerpipe:

**`aws.spc`:**
```hcl
connection "aws_prod" {
  plugin  = "aws"
  profile = "production"
  regions = ["us-east-1", "eu-west-1"]
}

connection "aws_dev" {
  plugin  = "aws"
  profile = "development"
  regions = ["us-east-1"]
}

connection "aws_all" {
  plugin      = "aws"
  type        = "aggregator"
  connections = ["aws_prod", "aws_dev"]
}
```

Run compliance benchmarks against all accounts:

```bash
docker exec powerpipe \
  powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 \
  --search-path-prefix aws_all
```

## Kubernetes compliance

Install and run the Kubernetes compliance mod:

```bash
# Requires the kubernetes plugin in Steampipe
docker exec steampipe steampipe plugin install kubernetes

# Install the mod
docker exec powerpipe powerpipe mod install github.com/turbot/steampipe-mod-kubernetes-compliance

# Run NSA/CISA Kubernetes hardening benchmark
docker exec powerpipe \
  powerpipe benchmark run kubernetes_compliance.benchmark.nsa_cisa_v10
```

## CI/CD integration

Export benchmark results for CI pipelines:

```bash
#!/bin/bash
# Run benchmark and fail if any controls are in alarm state
docker run --rm \
  -v "$HOME/.aws:/home/powerpipe/.aws:ro" \
  -v "$PWD/workspace:/workspace" \
  -e POWERPIPE_DATABASE="${STEAMPIPE_CONNECTION_STRING}" \
  ghcr.io/devops-ia/powerpipe:1.5.1 \
  powerpipe benchmark run aws_compliance.benchmark.cis_aws_foundations_benchmark_v300 \
  --export /workspace/results.json \
  --output brief

# Check exit code — non-zero means controls failed
if [ $? -ne 0 ]; then
  echo "Compliance benchmark failed — review results.json"
  exit 1
fi
```
