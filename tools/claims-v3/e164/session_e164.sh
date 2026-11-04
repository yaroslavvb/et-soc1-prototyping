#!/usr/bin/env bash
# E164 (Q141(b)): the card session on aifoundry1 card 1, detached on the box after the claim is in the day's post. A port of
# tools/claims-v3/e157/session_e157.sh with these changes, each marked E164:
#   1. check_e164.py first (every reused file, every E164 card file, blind pool 7, the eleven pool-6 tiles and every binary - the
#      patched C-logging host and the kernel included - byte-identical to harness-e164.json, or no device opens), then the
#      device-command preflight preflight_e164.sh (Q136(w)'s tools/claims-v3/dmcmd_audit.py on every file the session runs; anything
#      but GO stops it before any device opens);
#   2. E164_DEADLINE must be set (the queue's last pass end: the round's time gate less 10 minutes; no default);
#   3. the read-only identity check of the build (E164.md, Device commands sent): the host's boot time (`uptime -s`) must precede
#      E82's firmware read of 2026-10-31 13:45:24 PDT, so nothing can have flashed the card through a host restart since; else no
#      device opens (exit 8). The firmware-revisions query is never sent (it writes the PMIC's firmware-management register);
#   4. never two of our sessions on aifoundry1: before anything opens, any device process of ours (lib.sh's DEV_COMM names) or any
#      device node or card lock et-holders shows held by us, on either card, stops the session (exit 3);
#   5. the stop-path test first (block_e164.sh 16402 --stoptest: no launch; the guard's die and board stops and the in-run watcher must
#      each fire on a live sample), then the smoke (block_e164.sh 16401 --smoke: eleven items, 2 s runs, C logged), then the gate
#      smoke_gate_e164.py on both; the queue is queue_e164.sh, and it starts only if the gate passes;
#   6. V3_DRY=1 (the Intel's dry pass, never on a real session): check_e164.py --desk, no identity or holder read, every device call
#      printed by lib.sh's dry functions, and the smoke gate (which needs live records) reported and passed over so the queue's loop
#      and budget run dry too. Data then go to build/claims-v3-dry/.
#
#   E164_T0=$(date +%s) E164_DEADLINE='<YYYY-MM-DD HH:MM PST>' setsid nohup bash tools/claims-v3/e164/session_e164.sh \
#       > build/e164/session.out 2>&1 < /dev/null &
#
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query, no residency read.
# build/e164/STOP stops the queue before its next pass.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
export V3_DEVICE=1
: "${E164_T0:?E164_T0 - the session anchor, epoch seconds}"
: "${E164_DEADLINE:?E164_DEADLINE - the round time gate less 10 minutes (no default)}"                                  # E164 change 2
export E164_T0 E164_DEADLINE
[ -n "${E164_DROP_P2:-}" ] && export E164_DROP_P2
mkdir -p build/e164
LOG=build/e164/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
cfg() {
  if [ -n "${V3_DRY:-}" ]; then echo '{"dry":true}' > "$1"; say "DRY config $(basename "$1")"; return 0; fi
  ET_DEVICES=1 flock -n /run/lock/etsoc-shire1.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2>"$1.err" | grep '^{' | tail -1 > "$1"
  date -Iseconds > "$1.time"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
say "session start (budget anchor T0 $(date -d @"$E164_T0" '+%T %Z'); deadline $E164_DEADLINE; E164_DROP_P2=${E164_DROP_P2:-0}${V3_DRY:+; DRY})"
if [ -n "${V3_DRY:-}" ]; then
  python3 -B tools/claims-v3/e164/check_e164.py --desk >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }   # E164 change 6
else
  python3 -B tools/claims-v3/e164/check_e164.py >> "$LOG" 2>&1 || { say "harness check failed: no device opened"; exit 9; }    # E164 change 1
fi
bash tools/claims-v3/e164/preflight_e164.sh > build/e164/dmcmd-preflight.txt 2>&1; a=$?
say "dmcmd_audit preflight rc=$a ($(grep -m1 '^dmcmd_audit:' build/e164/dmcmd-preflight.txt))"
[ "$a" -eq 0 ] || { say "device-command preflight is not GO: no device opened"; exit 3; }
if [ -n "${V3_DRY:-}" ]; then
  say "DRY: identity (uptime -s against E82's read), our own holders and et-who not read"
else
  boot=$(date -d "$(uptime -s)" +%s); e82=$(date -d '2026-10-31 13:45:24 PDT' +%s)                                       # E164 change 3
  say "identity: host booted $(uptime -s) ($boot); E82's firmware read 2026-10-31 13:45:24 PDT ($e82)"
  [ "$boot" -lt "$e82" ] || { say "the host booted after E82's firmware read: the build cannot be confirmed read-only; no device opened"; exit 8; }
  ours=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" '$1 == me && $3 ~ /_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$/ {print $2":"$3}' | tr '\n' ' ')
  held=$(sudo -n /usr/local/sbin/et-holders 2>/dev/null | grep -v 'et-holders' | awk -v me="$USER" '$2 == me {print $1}' | tr '\n' ' ')
  if [ -n "${ours// /}${held// /}" ]; then say "another session of ours is on aifoundry1 (procs [$ours], held [$held]): no device opened"; exit 3; fi   # E164 change 4
  timeout 20 et-who >> "$LOG" 2>&1
fi
sha256sum build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/sparsity/kernel/sparsity.elf build/ettelem/ettelem \
  tools/claims-v3/e128/ettelem_guard.sh tools/claims-v3/ccheck/sparsity_ccheck.sh > build/e164/binaries.sha256 2>/dev/null
cfg build/e164/config-session-start.json
bash tools/claims-v3/e164/block_e164.sh 16402 --stoptest < /dev/null >> "$LOG" 2>&1; st=$?                                  # E164 change 5
say "stop-path test rc=$st"
if [ "$st" -eq 0 ] || [ -n "${V3_DRY:-}" ]; then
  bash tools/claims-v3/e164/block_e164.sh 16401 --smoke < /dev/null >> "$LOG" 2>&1; rc=$?
  say "smoke rc=$rc"
else
  rc=99; say "stop-path test failed: no smoke, no pass"
fi
R=build/claims-v3/aifoundry1-c1; [ -n "${V3_DRY:-}" ] && R=build/claims-v3-dry/aifoundry1-c1
python3 -B tools/claims-v3/e164/smoke_gate_e164.py "$R/e164-smoke/p16401" "$R/e164-stoptest/p16402" >> "$LOG" 2>&1; g=$?
if [ -n "${V3_DRY:-}" ]; then
  say "DRY: stop test rc $st, smoke rc $rc, gate $g (the gate reads live records; a dry run has none): the queue runs dry"
  bash tools/claims-v3/e164/queue_e164.sh < /dev/null > build/e164/queue.out 2>&1
  say "queue: $(tail -1 build/e164/queue.out)"
elif [ "$st" -ne 0 ] || [ "$rc" -ne 0 ] || [ "$g" -ne 0 ]; then
  say "smoke gate failed (stop test rc $st, smoke rc $rc, gate $g): no pass runs"
else
  say "smoke gate passed: queue starts"
  bash tools/claims-v3/e164/queue_e164.sh < /dev/null > build/e164/queue.out 2>&1
  say "queue: $(tail -1 build/e164/queue.out)"
fi
cfg build/e164/config-session-end.json
[ -n "${V3_DRY:-}" ] || timeout 20 et-who >> "$LOG" 2>&1
say "session end"
