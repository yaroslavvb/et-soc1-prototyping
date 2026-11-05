#!/usr/bin/env bash
# E172 (Q142(k6), tools/claims-v3/e172/E172.md): pool 8 in E164's form on aifoundry1 card 1: the card session on aifoundry1 card 1, launched by box/launch_e172.sh after the claim is in the day's post. A port
# of tools/claims-v3/e164/session_e164.sh, unchanged but for E172's names and files: check_e172.py (every reused file, every E172 card
# file, the registration and plan, the pinned watcher files, pool 8's files and tiles, every binary byte-identical to harness-e172.json)
# and preflight_e172.sh (dmcmd_audit GO) before any device opens; the identity by continuity (the host booted before E82's firmware read
# of 2026-10-31 13:45:24 PDT, never the firmware-revisions query); nothing of ours on either card of aifoundry1; the two config reads
# through E128's guard under card 1's lock; the stop-path test (17202), the smoke (17201) and its gate; then queue_e172.sh.
# E172_T0 and E172_DEADLINE are required (no default). Nothing is set.
#
#   E172_T0=<epoch> E172_DEADLINE='<date>' [E172_DROP_P2=1] setsid nohup bash tools/claims-v3/e172/session_e172.sh > build/e172/session.out 2>&1 < /dev/null &
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
: "${E172_T0:?E172_T0 - the session anchor, epoch seconds}"
: "${E172_DEADLINE:?E172_DEADLINE - the round time gate less 10 minutes (no default)}"                                  # E172 change 2
export E172_T0 E172_DEADLINE
[ -n "${E172_DROP_P2:-}" ] && export E172_DROP_P2
mkdir -p build/e172
LOG=build/e172/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E172_T0" '+%T %Z'); deadline $E172_DEADLINE; E172_DROP_P2=${E172_DROP_P2:-0}${V3_DRY:+; DRY})"
if [ -n "${V3_DRY:-}" ]; then
  python3 -B tools/claims-v3/e172/check_e172.py --desk >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }   # E172 change 6
else
  python3 -B tools/claims-v3/e172/check_e172.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E172 change 1
fi
bash tools/claims-v3/e172/preflight_e172.sh > build/e172/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e172/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
if [ -n "${V3_DRY:-}" ]; then
  say "DRY: identity (uptime -s against E82's read), our own holders and et-who not read"
else
  boot=$(date -d "$(uptime -s)" +%s); e82=$(date -d '2026-10-31 13:45:24 PDT' +%s)                                       # E172 change 3
  say "identity: host booted $(uptime -s) ($boot); E82's firmware read 2026-10-31 13:45:24 PDT ($e82)"
  [ "$boot" -lt "$e82" ] || { say "the host booted after E82's firmware read: the build cannot be confirmed read-only; no device opened"; exit 8; }
  ours=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" '$1 == me && $3 ~ /_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$/ {print $2":"$3}' | tr '\n' ' ')
  held=$(sudo -n /usr/local/sbin/et-holders 2>/dev/null | grep -v 'et-holders' | awk -v me="$USER" '$2 == me {print $1}' | tr '\n' ' ')
  if [ -n "${ours// /}${held// /}" ]; then say "another session of ours is on aifoundry1 (procs [$ours], held [$held]): no device opened"; exit 3; fi   # E172 change 4
  timeout 20 et-who >> "$LOG" 2>&1
fi
sha256sum build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/sparsity/kernel/sparsity.elf build/ettelem/ettelem \
  tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/ccheck/sparsity_ccheck.sh > build/e172/binaries.sha256 2>/dev/null
cfg build/e172/config-session-start.json
bash tools/claims-v3/e172/block_e172.sh 17202 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?                                  # E172 change 5
say "stop-path test rc=$st"
if [ "$st" -eq 0 ] || [ -n "${V3_DRY:-}" ]; then
  bash tools/claims-v3/e172/block_e172.sh 17201 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no pass"
fi
R=build/claims-v3/aifoundry1-c1; [ -n "${V3_DRY:-}" ] && R=build/claims-v3-dry/aifoundry1-c1
python3 -B tools/claims-v3/e172/smoke_gate_e172.py "$R/e172-smoke/p17201" "$R/e172-stoptest/p17202" >> "$LOG" 2>&1; g=$?
if [ -n "${V3_DRY:-}" ]; then
  say "DRY: stop test rc $st, smoke rc $rc, gate $g (the gate reads live records; a dry run has none): the queue runs dry"
  bash tools/claims-v3/e172/queue_e172.sh < /dev/null > build/e172/queue.out 2>&1
  say "queue: $(tail -1 build/e172/queue.out)"
elif [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e172/queue_e172.sh < /dev/null > build/e172/queue.out 2>&1
  say "queue: $(tail -1 build/e172/queue.out)"
fi
cfg build/e172/config-session-end.json
[ -n "${V3_DRY:-}" ] || timeout 20 et-who >> "$LOG" 2>&1
say "session end"
