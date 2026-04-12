# Troubleshooting

## Powerpipe exits immediately

**Symptom:** Container exits right after starting with no error message.

**Cause:** Missing `POWERPIPE_DATABASE` or unreachable Steampipe endpoint.

**Fix:**

```bash
# Check logs
docker logs powerpipe

# Verify Steampipe is reachable from Powerpipe container
docker exec powerpipe bash -c "pg_isready -h steampipe -p 9193"

# Ensure Steampipe is listening on network (not just localhost)
# Steampipe must be started with --database-listen network
docker logs steampipe | grep "Listen"
```

---

## Cannot connect to database

**Symptom:** `Error: connection refused` or `FATAL: password authentication failed`

**Fix:**

```bash
# Verify the connection string
docker run --rm \
  -e POWERPIPE_DATABASE="postgresql://steampipe:yourpassword@steampipe:9193/steampipe" \
  ghcr.io/devops-ia/powerpipe:1.5.1 \
  powerpipe query "select 1"

# Check Steampipe password
docker exec steampipe steampipe service status --show-password
```

---

## Port 9033 already in use

**Symptom:** `address already in use: 9033`

**Fix:**

```bash
# Find the conflicting process
lsof -i :9033

# Use a different host port (container still uses 9033 internally)
docker run -d -p 19033:9033 ghcr.io/devops-ia/powerpipe:1.5.1
```

---

## Mod not found

**Symptom:** `Error: no mods found in /workspace` or benchmark commands fail with `not found`.

**Cause:** Mod not installed, or `POWERPIPE_MOD_LOCATION` not set correctly.

**Fix:**

```bash
# Verify mod location
docker exec powerpipe ls /workspace

# Install the mod
docker exec powerpipe powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance

# Verify mod was installed
docker exec powerpipe powerpipe mod list
```

If using a mounted volume, ensure the mount is writable:

```bash
docker run -d \
  -v "$PWD/workspace:/workspace" \  # writable, no :ro
  -e POWERPIPE_MOD_LOCATION=/workspace \
  ghcr.io/devops-ia/powerpipe:1.5.1
```

---

## Permission denied on /workspace

**Symptom:** `mkdir: cannot create directory '/workspace': Permission denied` or mod install fails.

**Cause:** The workspace volume is owned by root and Powerpipe runs as UID 9193.

**Fix:**

```bash
# Set correct ownership before mounting
mkdir -p workspace
chown -R 9193:0 workspace
chmod -R g=u workspace
```

Or in Docker Compose:

```yaml
services:
  powerpipe:
    user: "9193:0"
    volumes:
      - workspace:/workspace
```

---

## Out of memory / OOM killed

**Symptom:** Container killed by OOM. `dmesg | grep -i oom` shows the process.

**Fix:**

```bash
docker run -d \
  -e POWERPIPE_MEMORY_MAX_MB=2048 \
  -e POWERPIPE_MAX_PARALLEL=5 \
  --memory=3g \
  ghcr.io/devops-ia/powerpipe:1.5.1
```

Rule of thumb: set `--memory` to `POWERPIPE_MEMORY_MAX_MB` × 1.5 to allow headroom.

---

## Dashboard timeout

**Symptom:** Dashboard loads but queries never complete, showing spinners indefinitely.

**Fix:**

```bash
# Increase timeouts (0 = unlimited)
docker run -d \
  -e POWERPIPE_DASHBOARD_TIMEOUT=300 \
  -e POWERPIPE_BENCHMARK_TIMEOUT=600 \
  ghcr.io/devops-ia/powerpipe:1.5.1
```

Also check Steampipe query timeout:

```bash
docker exec steampipe bash -c "echo 'SHOW steampipe_query_timeout' | psql -h localhost -p 9193 -U steampipe -d steampipe"
```

---

## Enabling debug logs

```bash
docker run --rm \
  -e POWERPIPE_LOG_LEVEL=debug \
  -e POWERPIPE_DATABASE="..." \
  ghcr.io/devops-ia/powerpipe:1.5.1 \
  powerpipe server 2>&1 | tee powerpipe-debug.log
```
