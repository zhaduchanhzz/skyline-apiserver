# Run Skyline locally on Windows

For the running OpenStack Docker deployment and Sovereign Next console on
<http://127.0.0.1:8088/auth/login>, see
[`../openstack-local/README.md`](../openstack-local/README.md). The instructions
below cover the standalone API development container on port 28000.

Docker Desktop runs the API server with Python 3.10. The console runs on the
Windows host with Node.js.

## API server

From `skyline-apiserver` in PowerShell:

```powershell
if (-not (Test-Path etc/skyline.yaml)) {
    Copy-Item etc/skyline.yaml.sample etc/skyline.yaml
}
```

In the ignored `etc/skyline.yaml`, set `default.database_url` to
`sqlite:////var/lib/skyline/skyline.db`, set `default.ssl_enabled` to `false`,
and replace the sample `default.secret_key` with a random value. Set the
`openstack` connection fields for your deployment when available.

```powershell
docker compose -f compose.local.yaml up -d --build
docker compose -f compose.local.yaml logs -f apiserver
```

The container runs Alembic migrations before Uvicorn. The SQLite database is
kept in the `skyline-local-data` Docker volume. Check
<http://127.0.0.1:28000/docs> or
<http://127.0.0.1:28000/api/v1/config>.

`compose.local.yaml` sets `RACKSPACE_STATUS_BANNERS_ENABLED=false`. This stops
fetching the Rackspace status RSS feed and hides any previously saved RSS
banners from the public, active, and admin list routes. Manually created
banners remain visible. Other deployments keep RSS banners enabled by default.

## Console

In `skyline-console`, create the ignored `config/local_config.yaml`:

```yaml
server:
  target: http://127.0.0.1:28000
  pathRewrite:
    '^/api/openstack/skyline': ''
```

Then run `npm run dev` and open <http://127.0.0.1:8088/>. This proxy maps the
console's Skyline API path to Uvicorn's `/api/v1` path.

For login and OpenStack operations, configure a reachable Keystone URL and
service account in `etc/skyline.yaml`. A Keystone service on the Windows host
is reachable from the container as `host.docker.internal`, not `127.0.0.1`.
The console's other `/api/openstack/...` service paths also require the Skyline
Nginx gateway generated from the OpenStack service catalog; the local rewrite
above only serves the Skyline API.

Stop the API server with `docker compose -f compose.local.yaml down` from
`skyline-apiserver`. This leaves the SQLite volume intact.
