#!/usr/bin/env bash
# Create an account for someone on every AI Foundry lab machine (aifoundry1, aifoundry2, ...).
# Usage: add-lab-user.sh <username> [<ssh-pubkey-file>] ["Full Name"]
# Needs `ssh root@aifoundryN` to work from this machine. Safe to re-run: an existing account is
# left alone and the key is only added if it is missing.
set -euo pipefail

usage() { echo "usage: $0 <username> [<ssh-pubkey-file>] [\"Full Name\"]" >&2; exit 1; }
user=${1:-} keyfile=${2:-} name=${3:-}
[[ $user =~ ^[a-z][a-z0-9_-]{0,31}$ ]] || usage

key=
if [[ -n $keyfile ]]; then
  key=$(head -n1 "$keyfile")
  if [[ ! $key =~ ^(ssh-|ecdsa-|sk-) ]] || ! ssh-keygen -lf - <<<"$key" >/dev/null 2>&1; then
    echo "$keyfile is not an SSH public key (pass the .pub file)" >&2; exit 1
  fi
fi

# Every aifoundryN on the tailnet, unless HOSTS="aifoundry1 aifoundry2" is set.
hosts=${HOSTS:-$(tailscale status 2>/dev/null | awk '$2 ~ /^aifoundry[0-9]+$/ {print $2}' | sort)}
hosts=${hosts:-aifoundry1 aifoundry2 aifoundry3}

rc=0
for h in $hosts; do
  echo "== $h"
  {
    printf 'user=%q key=%q name=%q\n' "$user" "$key" "$name"
    cat <<'EOF'
set -euo pipefail
if id "$user" >/dev/null 2>&1; then
  echo "account exists: $(id "$user")"
else
  adduser --quiet --disabled-password --comment "$name" --shell /bin/bash "$user" </dev/null
  echo "created: $(id "$user")"
fi
if [ -n "$key" ]; then
  # Write as the user, so a symlink in their home cannot redirect a root write.
  runuser -u "$user" -- sh -c 'umask 077; mkdir -p "$1/.ssh"; f="$1/.ssh/authorized_keys"; touch "$f"
    if grep -qxF "$2" "$f"; then echo "key already present"; else printf "%s\n" "$2" >>"$f"; echo "key added"; fi' \
    sh "$(getent passwd "$user" | cut -d: -f6)" "$key"
fi
for d in /dev/et*; do
  [ -e "$d" ] || continue
  if runuser -u "$user" -- test -r "$d" -a -w "$d"; then echo "$d: read/write ok"; else echo "$d: NO ACCESS"; fi
done
EOF
  } | ssh -o BatchMode=yes -o ConnectTimeout=15 "root@$h" bash -s || { echo "!! $h: failed" >&2; rc=1; }
done
exit $rc
