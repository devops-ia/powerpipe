# Contributing

Thank you for your interest in contributing! This repo builds and publishes a community Docker image for [Powerpipe](https://powerpipe.io).

## Prerequisites

- Docker 20.10+
- `bash`, `jq`, `python3`, `pip`
- A running Steampipe instance (see [devops-ia/steampipe](https://github.com/devops-ia/steampipe))

## Build the image locally

```bash
# Build with the default Powerpipe version from the Dockerfile
docker build -t powerpipe:dev .

# Build with a specific version
docker build --build-arg POWERPIPE_VERSION=1.5.1 -t powerpipe:dev .
```

## Run the test suite

### Unit tests (no Docker needed)

```bash
pip install -r tests/requirements.txt
python3 -m pytest tests/ --cov=compare_snapshots --cov-report=term-missing
```

### Lint the Dockerfile

```bash
docker run --rm -i hadolint/hadolint < Dockerfile
```

### Container structure tests (requires built image)

```bash
docker run --rm \
  -v "$PWD/structure-tests.yaml:/structure-tests.yaml:ro" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gcr.io/gcp-runtimes/container-structure-test:latest \
  test --image powerpipe:dev --config /structure-tests.yaml
```

### Security scan

```bash
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image --severity CRITICAL --ignore-unfixed powerpipe:dev
```

## How releases work

Releases are **fully automated** — do not bump versions manually.

1. [updatecli](https://www.updatecli.io/) detects new Powerpipe releases and opens a PR updating `ARG POWERPIPE_VERSION` in the `Dockerfile`.
2. The PR CI runs all tests.
3. On merge to `main`, [semantic-release](https://semantic-release.gitbook.io/) reads conventional commits, bumps the version, and publishes to GHCR and Docker Hub automatically.

## Commit message format

This repo uses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add support for multi-arch builds
fix: correct workspace directory permissions
chore: bump powerpipe to 1.6.0
docs: add mod installation example
```

| Type | When to use |
|------|------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `chore` | Maintenance (version bumps, CI tweaks) |
| `docs` | Documentation only |
| `refactor` | Code restructure without behaviour change |

## Reporting bugs

Please [open an issue](https://github.com/devops-ia/powerpipe/issues/new) with:

- Powerpipe image version
- Docker version (`docker --version`)
- Steps to reproduce
- Expected vs actual behaviour
- Relevant logs (`docker logs powerpipe`)

## Pull requests

1. Fork the repo and create a branch: `git checkout -b feat/my-improvement`
2. Make your changes
3. Run the tests (see above)
4. Commit using Conventional Commits format
5. Open a PR against `main`
