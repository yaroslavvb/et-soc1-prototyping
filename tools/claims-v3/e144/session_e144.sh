#!/usr/bin/env bash
# E144 (Q138) on aifoundry3 card 0, one stage per call, from the tree that holds the binaries (~/aifoundry), after copying
# tools/claims-v3/e144/ there (tools/claims-v3/e97/, e89/, e128/, kinds/ and lib.sh are already there; setup checks their sha256):
#
#   bash tools/claims-v3/e144/session_e144.sh setup    # NO device access: tree, sha256 of the reused files, binaries, tiles, the
#                                                      #   device-command preflight (preflight_e144.sh), dry runs
#   bash tools/claims-v3/e144/session_e144.sh probe    # AFTER the claim: the session-start config read (E128's guard, config only),
#                                                      #   then three read-only sampler ticks (are command 74 group 0's answers raw codes?)
#   bash tools/claims-v3/e144/session_e144.sh smoke    # the smoke plan, then the stop-path tests on live samples (block 14401)
#   bash tools/claims-v3/e144/session_e144.sh go       # the measured pass (block 14420), detached on the box, then the session-end config read
#   bash tools/claims-v3/e144/session_e144.sh status
#
# Everything that touches the card holds the card lock (flock -n) and runs under `timeout 10`. Nothing waits for a person, nothing is set.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
stage=${1:?setup|probe|smoke|go|status}
mkdir -p build/e144
say() { echo "$(date +%T) $*"; }
cfg_read() {   # $1 = output file: `ettelem config` through E128's guard (config only), under the card lock, timeout 10
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  say "config read -> $1: $(head -c 400 "$1")"
}

case "$stage" in
setup)
  say "== host (no device access) =="
  hostname; who | wc -l | sed 's/^/logins: /'; uptime
  command -v et-who > /dev/null && timeout 20 et-who 2>&1 | head -8
  say "== reused files against E97's freeze, tiles =="
  python3 tools/claims-v3/e97/e97_common.py --verify | tail -3; echo "verify rc=$?"
  sha256sum tools/claims-v3/e97/run_e97b.py tools/claims-v3/e97/e97_common.py tools/claims-v3/e89/pvt_sample.py tools/claims-v3/e89/run_e89.py \
    tools/claims-v3/lib.sh tools/claims-v3/e128/ettelem_guard.sh build/sparsity/host/sparsity_host build/ettelem/ettelem | tee build/e144/sha256-setup.txt
  ls -l /dev/et0_mgmt /run/lock/etsoc-shire0.lock 2>&1
  python3 tools/claims-v3/e144/run_e144.py /dev/null --root "$ROOT" --pass-no 14420 --list; echo "list rc=$?"
  say "== device-command preflight (dmcmd_audit.py, E144's table: command 74 group 0 classified) =="
  bash tools/claims-v3/e144/preflight_e144.sh > build/e144/dmcmd-preflight.txt 2>&1; echo "preflight rc=$?"
  head -1 build/e144/dmcmd-preflight.txt
  say "== dry runs (V3_DRY=1: lib.sh stubs every device call) =="
  V3_DRY=1 bash tools/claims-v3/e144/block_e144.sh 14499 > build/e144/dry-subset.log 2>&1; echo "dry subset rc=$?"
  grep -c 'DRY hold10: .*--test fma' build/e144/dry-subset.log | sed 's/^/device launches the dry subset printed: /'
  grep -E 'decision|hold H|rest R|rest die' build/e144/dry-subset.log | cut -c1-160 | tail -12
  ;;
probe)
  cfg_read build/e144/config-session-start.json
  ( flock -n 9 || { echo '{"probe":"lock held"}'; exit 3; }
    timeout 10 python3 tools/claims-v3/e89/pvt_sample.py --probe < /dev/null
  ) 9<>/run/lock/etsoc-shire0.lock > build/e144/probe.out 2>&1
  echo "probe rc=$?"
  grep -c '^{"t_ms"' build/e144/probe.out | sed 's/^/ticks: /'
  tail -1 build/e144/probe.out | cut -c1-300
  ;;
smoke)
  bash tools/claims-v3/e144/block_e144.sh 14401 --smoke > build/e144/smoke.log 2>&1; echo "smoke block rc=$?"
  grep -E 'hold |rest |watch|stop tests|STOP|done' build/e144/smoke.log | cut -c1-220 | tail -30
  ;;
go)
  setsid nohup bash tools/claims-v3/e144/queue_e144.sh > "$ROOT/build/e144/queue.log" 2>&1 < /dev/null &
  say "e144 queue started, log $ROOT/build/e144/queue.log"
  ;;
status)
  tail -8 build/e144/queue.log 2>/dev/null
  d=build/claims-v3/$(hostname)/e144/p14420
  tail -4 "$d/run.log" 2>/dev/null
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
