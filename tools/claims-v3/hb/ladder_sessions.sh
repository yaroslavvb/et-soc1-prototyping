#!/usr/bin/env bash
# E65 block C: the two hart-ladder sessions, one after the other, on the local card.
#   bash tools/claims-v3/hb/ladder_sessions.sh        # started detached by run_e65.sh c
# run_hm.py holds the card lock for each session and releases it between them; a session that is refused or
# stopped does not stop the other, and both exit codes are logged.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
PY=${PY:-$PWD/.venv/bin/python3}
[ -x "$PY" ] || PY=python3
for v in randn zeros; do
  [ -e build/e65-STOP ] && { echo "$(date +%T) build/e65-STOP exists: stopping before $v"; exit 0; }
  echo "$(date +%T) $v starts"
  "$PY" tools/claims-v3/hm/run_hm.py --protocol "tools/claims-v3/hb/protocol-$v.json" \
    --out "build/claims-v3/aifoundry3/e65/$v" --no-cam --root "$PWD" < /dev/null
  echo "$(date +%T) $v rc=$?"
  sleep 60
done
echo "$(date +%T) ladder sessions done"
