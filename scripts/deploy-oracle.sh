#!/usr/bin/env bash
set -euo pipefail

# Run with sudo on the existing Collab Loop VM after uploading the release,
# candidate Caddyfile, and this script to /home/ubuntu/shanks-studio-deploy.
release=${1:?release name required}
archive_sha=${2:?archive SHA-256 required}
config_sha=${3:?original Caddyfile SHA-256 required}
[[ "$release" =~ ^shanks-studio-[0-9TZ.-]+$ ]] || exit 2
[[ "$archive_sha" =~ ^[a-f0-9]{64}$ && "$config_sha" =~ ^[a-f0-9]{64}$ ]] || exit 2

upload=/home/ubuntu/shanks-studio-deploy
gateway=realtime-collab-gateway-1
config=/home/ubuntu/realtime-collab/Caddyfile
volume=/var/lib/docker/volumes/realtime-collab_caddy_config/_data
base="$volume/sites/shanks-studio"
container_base=/config/sites/shanks-studio
archive="$upload/$release.tar.gz"
candidate="$upload/Caddyfile.studio"
actual_volume=$(docker inspect "$gateway" --format '{{range .Mounts}}{{if eq .Destination "/config"}}{{.Source}}{{end}}{{end}}')
[[ "$actual_volume" == "$volume" ]] || { echo 'Gateway storage changed; refusing deployment.'; exit 2; }
printf '%s  %s\n' "$archive_sha" "$archive" | sha256sum -c -
printf '%s  %s\n' "$config_sha" "$config" | sha256sum -c -
[[ ! -e "$base/releases/$release" ]] || { echo 'Release already exists; refusing overwrite.'; exit 2; }
mkdir -p "$base/releases/$release"
tar --no-same-owner -xzf "$archive" -C "$base/releases/$release"
test -s "$base/releases/$release/index.html"
test -s "$base/releases/$release/models/cyber-home.glb"
test -s "$base/releases/$release/draco/draco_decoder.wasm"
chmod -R a+rX "$base/releases/$release"

docker cp "$candidate" "$gateway:/tmp/Caddyfile.studio"
docker exec "$gateway" caddy validate --config /tmp/Caddyfile.studio --adapter caddyfile
backup="$upload/Caddyfile.before-$release"
cp -p "$config" "$backup"
previous=$(readlink "$base/current" || true)
changed=0
committed=0
rollback() {
  status=$?
  if [[ "$committed" != 1 && "$changed" == 1 ]]; then
    echo 'Restoring gateway configuration after failed deployment.'
    cat "$backup" > "$config"
    if [[ -n "$previous" ]]; then
      ln -s "$previous" "$base/rollback-$release"
      mv -Tf "$base/rollback-$release" "$base/current"
    fi
    docker exec "$gateway" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile || true
  fi
  exit "$status"
}
trap rollback EXIT
ln -s "$container_base/releases/$release" "$base/current-$release"
mv -Tf "$base/current-$release" "$base/current"
changed=1
# Preserve the inode: Caddyfile is already bind-mounted into the running gateway.
cat "$candidate" > "$config"
docker exec "$gateway" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
collab_status=$(curl --max-time 20 -s -o /dev/null -w '%{http_code}' https://collabloop.129-225-102-84.sslip.io/)
[[ "$collab_status" == 200 ]] || { echo "Collab Loop returned $collab_status; rolling back."; exit 1; }
committed=1
echo "DEPLOYED_RELEASE=$release"
echo "CONFIG_BACKUP=$backup"
echo "COLLAB_LOOP_STATUS=$collab_status"
