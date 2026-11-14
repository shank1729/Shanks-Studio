# Oracle deployment

Live URL: https://shanks-studio.129-225-102-84.sslip.io/

First deployed: 14 November 2026. Release: `shanks-studio-2026-11-14T15-36-43-522Z`.

## Server layout

- VM: `ubuntu@129.225.102.84`; local SSH identity: `C:/Users/shank/.ssh/collab-oracle-ed25519`. Never copy the private key into this project or upload it.
- Existing gateway: Docker container `realtime-collab-gateway-1`, Caddy 2.11.7, ports 80/443.
- Gateway configuration: `/home/ubuntu/realtime-collab/Caddyfile`, bind-mounted at `/etc/caddy/Caddyfile`.
- Portfolio files: `/config/sites/shanks-studio/releases/<release>` inside the gateway, with `/config/sites/shanks-studio/current` pointing to the active release.
- Host storage: `/var/lib/docker/volumes/realtime-collab_caddy_config/_data/sites/shanks-studio`. The existing named volume keeps these files separate from Collab Loop's frontend release directory. Preserve this volume when updating the gateway; `docker compose down -v` would delete it along with other Caddy configuration data.
- Uploads and gateway backups: `/home/ubuntu/shanks-studio-deploy/`.

The portfolio is static. Caddy serves it directly and manages HTTPS. No Node process, extra container, database, new firewall port, or new VM was added. The original Collab Loop routing block was retained. Caddy was gracefully reloaded without restarting its container.

## Update procedure

1. Run `node scripts/package-oracle.mjs`. It builds and emits a dated archive and SHA-256 inventory under `tmp/oracle/`.
2. Download the **current** server Caddyfile, retain a backup, and record its SHA-256. Prepare a candidate that preserves all existing routes and contains exactly one portfolio block matching `scripts/oracle-site.caddy`. Do not append duplicate hostname blocks on updates.
3. Upload the archive, candidate named `Caddyfile.studio`, and `scripts/deploy-oracle.sh` to `/home/ubuntu/shanks-studio-deploy/`.
4. Syntax-check the script with `bash -n`, then run it via sudo with the release name, archive SHA-256, and original server Caddyfile SHA-256 as its three arguments. The script checks both hashes and the expected volume mount, extracts into a new release directory, validates the candidate with Caddy, switches the current symlink, and reloads Caddy. It restores the previous configuration if the reload or Collab Loop HTTP check fails.
5. Verify public HTTPS, scene loading, project selection, credits, and Collab Loop. Keep prior releases and the gateway backup until the new release is accepted.

The deploy script and route are specific to the inspected server layout. Inspect again before using them after an infrastructure change. Do not publish `assets/`, private keys, CV source files, or the full workspace; upload the generated archive only.

## Rollback

The first-deployment gateway backup is:

`/home/ubuntu/shanks-studio-deploy/Caddyfile.before-shanks-studio-2026-11-14T15-36-43-522Z`

To remove the portfolio route, restore that backup **in place** to the host Caddyfile and reload Caddy after validation. Preserve the Caddyfile inode because it is bind-mounted into a running container. If other routing edits have been made since this deployment, remove only the portfolio block from a fresh copy instead of restoring an older whole-file backup.

To roll back only portfolio content on future updates, point `/config/sites/shanks-studio/current` to the previous release directory from within the gateway container. No gateway reload is required when only the static content symlink changes.

## First-deployment checks

Production build and release SHA-256 passed. Public portfolio HTTPS returned 200 with certificate verification successful. The live browser loaded the 3D scene and showed the six-project picker; choosing Collab Loop showed its dedicated details and live link. Collab Loop itself returned HTTP 200 after the gateway reload.
