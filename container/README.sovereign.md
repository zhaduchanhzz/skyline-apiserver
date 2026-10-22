# Skyline all-in-one image with Sovereign Next console

`Dockerfile.sovereign` builds the RackerLabs Skyline API with the customized
[`zhaduchanhzz/skyline-console`](https://github.com/zhaduchanhzz/skyline-console)
package. Its startup script generates the Skyline Nginx configuration, starts
Nginx for the console and API proxy, then runs Gunicorn for the API.

The console displays `mbfs-logo.svg` on the login page and in the navigation
bar. The source asset is `src/asset/image/mbfs-logo.svg` in the console
repository; the built image serves it from
`skyline_console/static/asset/image/mbfs-logo.svg`.

The upstream Dockerfile's `skyline-apiserver` entrypoint does not exist in this
API package. The image uses `skyline-nginx-generator` and `gunicorn`, pins the
OpenStack `stable/2025.1` constraints, and uses Pydantic 1.10.26 so the API
imports on Python 3.12.

The original snippet also calls `scripts/skyline-cve-patching.sh`. That script
is not present in this workspace, so this local image does not run it.

Build from the `skyline-apiserver` directory:

```powershell
docker build -f container/Dockerfile.sovereign -t skyline-sovereign:local .
```

The Dockerfile pins the API and console revisions that were checked in this
workspace. To build a newer pushed console revision, pass
`--build-arg CONSOLE_REF=<commit>`; that revision must contain compiled files
under `skyline_console/static`. After changing FE source, run `npm run build`
(`npm run build:win` in PowerShell on Windows) and commit the resulting static
files to the console repository first.

The combined image needs a Skyline configuration file with reachable Keystone
credentials. Bootstrap its database, then start the service. In PowerShell,
set `$SkylineConfig` to the absolute path of your `skyline.yaml`:

```powershell
$SkylineConfig = 'C:\path\to\skyline.yaml'
docker run --rm --name skyline-bootstrap `
  --mount "type=bind,source=$SkylineConfig,target=/etc/skyline/skyline.yaml,readonly" `
  -v skyline-sovereign-data:/tmp `
  -e KOLLA_BOOTSTRAP=1 skyline-sovereign:local
docker run -d --name skyline-sovereign -p 19999:9999 `
  --mount "type=bind,source=$SkylineConfig,target=/etc/skyline/skyline.yaml,readonly" `
  -v skyline-sovereign-data:/tmp `
  skyline-sovereign:local
```

The shared `/tmp` volume matches the sample SQLite URL
`sqlite:////tmp/skyline.db`; use the directory from your own `database_url` if
it differs. Open `http://localhost:19999/auth/login`. The image
listens on HTTP port 9999 by default. Set `LISTEN_ADDRESS` and provide
`SSL_CERTFILE`/`SSL_KEYFILE` if TLS termination must happen inside the image.

Quick checks:

```powershell
docker run --rm --entrypoint python skyline-sovereign:local -c "from skyline_console import static_path; print(static_path); print((static_path / 'index.html').read_text()[:200])"
Invoke-WebRequest http://localhost:19999/auth/login -UseBasicParsing
Invoke-WebRequest http://localhost:19999/main.js -UseBasicParsing
Invoke-WebRequest http://localhost:19999/api/openstack/skyline/api/v1/contrib/regions -UseBasicParsing
```

The last response should be JSON. HTML at that API path means the request
fell through to the SPA instead of reaching the API proxy.
