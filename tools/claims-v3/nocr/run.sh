#!/usr/bin/env bash
# nocr: run passes one after another on the local card, stopping at the first that does not end ok. For aifoundry1,
# where queue.sh must not run nocr: with V3_DEVICE set, queue.sh samples the die (lib.sh die_c: timeout 20 ettelem,
# no card lock, no et-who check) before every block, which breaks the 10 s, lock and et-who rules on a two-card host.
# This runner opens nothing itself; every device access is block.sh's (et-who, the card lock, timeout 10, HALT).
#
#   V3_DEVICE=1 setsid nohup bash tools/claims-v3/nocr/run.sh 9 > build/claims-v3/nocr-run-aifoundry1-c1-p9.log 2>&1 < /dev/null &
#   V3_DEVICE=1 setsid nohup bash tools/claims-v3/nocr/run.sh 1 2 3 > build/claims-v3/nocr-run-aifoundry1-c1-dev.log 2>&1 < /dev/null &
#
# Like queue.sh: a pass whose block.json says ok is skipped; an earlier attempt that did not end ok is moved aside to
# p<pass>.attempt-<epoch> first; build/claims-v3/STOP stops it before the next pass. Unlike queue.sh: any exit code
# but 0 stops it (including 3, someone else on the card: start it again later), and it pauses 20 s between passes.
# Exit: the first nonzero block exit code, else 0.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$ROOT"
[ $# -gt 0 ] || { echo "usage: run.sh <pass> [<pass> ...]" >&2; exit 2; }
card=$(hostname)${V3_DEVICE:+-c$V3_DEVICE}
if [ -n "${V3_DRY:-}" ]; then card=${NOCR_DRY_CARD:-$card}; data=build/claims-v3-dry/$card/nocr; else data=build/claims-v3/$card/nocr; fi
say() { echo "$(date +%FT%T) [$card] nocr run.sh: $*"; }
say "passes $*"
first=1
for p in "$@"; do
  case "$p" in ''|*[!0-9]*) say "pass must be a number: $p"; exit 2 ;; esac
  [ -e build/claims-v3/STOP ] && { say "STOP file present: stopping before p$p"; exit 0; }
  if [ -e "$data/p$p/block.json" ]; then
    if grep -q '"status":"ok"' "$data/p$p/block.json"; then say "skip p$p (done)"; continue; fi
    mv "$data/p$p" "$data/p$p.attempt-$(date +%s)"
  fi
  [ -n "$first" ] || sleep 20
  first=
  bash tools/claims-v3/nocr/block.sh "$p" < /dev/null
  rc=$?
  say "p$p exit $rc"
  [ $rc -eq 0 ] || { say "stopping: p$p did not end ok (rc $rc)"; exit $rc; }
done
say "done"
