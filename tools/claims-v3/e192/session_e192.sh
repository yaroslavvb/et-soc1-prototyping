#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): THE SESSION'S WRAPPER on aifoundry3. Step 9
# (rb/s11_a3_session_e192.sh) starts it detached (setsid nohup) after k6's guard, THE REST RULE, today's dry pass and today's build; step 8
# (rb/s10_a3_dry_e192.sh) runs it with --dry. It runs the proposal's reference session AS COMMITTED (proposal/src/run_session.sh, which
# runs run_block.py and stopwatch.py, all three at the registration's sha256, unchanged), driven with the box's own tools, and adds only
# what E192.md section 17.2 asks of the kit, each through the registered stop file (OUT/STOP), never by editing, killing or re-ordering:
#   - before anything opens a card node: the host's name is aifoundry3 (the order draws on it), USER is the login, the registered and kit
#     files at their pins, the binaries present, dmcmd_audit GO (preflight_e192.sh), ONE CARD'S NODES ONLY (exactly /dev/et0_ops and
#     /dev/et0_mgmt, counted by name: E192.md section 3, "before opening anything the host counts the card nodes"; fix-e192, below), the
#     window's last end at least the cap away;
#   - the free check (et-who --check exit 0, no other user's device process, a probe of the existing card lock), then THE FIRST CARD
#     COMMAND: the per-sensor sampler's own probe (pvt_sample.py --probe: three READ ticks under the card lock, timeout 10). SAMPLER=pvt
#     when the probe answers with 34 sensors on every tick and pvt_sample.py is at the audit table's reviewed sha256; else the plain
#     sampler (ettelem sample --every-ms 100, no statistics reset), the fallback E192.md section 4 names. Which ran is in the log;
#   - THE KIT'S GATE (gate_e192.py, beside the session): the smoke gate on the smoke's INTBITS lines, and the cap (65 card-minutes from
#     the first card command: no pass starts that could end after it; 30 s before it, the run in flight finishes and the session ends);
#     a gate watcher that dies mid-session writes STOP (no gate, no session);
#   - the kits' session log (build/e192/T<T0>/session.log: "session start", "session end (T0 <T0>)"; every rest rule of ours reads it),
#     and MANIFEST.sha256 last (the collection's exact copy-back reads it); wrapper.rc after it.
# FIXED IN PLACE BEFORE THE LAND (Q176, lane fix-e192, Sat 14 Nov 2026 evening, answering verify-e192's findings 1, 2 and 8):
#   1. run_session.sh writes run/SESSION_DONE only in its EXIT trap, which it sets after its own refusals and its free check; the gate
#      ends only at SESSION_DONE, a STOP or its end-stop. So when run_session.sh exits before that trap (a holder, a lock or another
#      user's process at its own free check, a node count, ET_DEVICES, no lock file, or a kill), the wrapper waited for the gate's
#      end-stop: about 64 minutes and a false cap STOP. Now, once run_session.sh has exited, the wrapper writes run/SESSION_DONE itself if
#      it is absent (one JSON line naming the wrapper and run_session.sh's exit; the reference's own marker is empty), logs it, and the
#      gate ends at once. Nothing else reads SESSION_DONE but the gate and stopwatch.py.
#   2. the node count above, before the free check and the probe (the probe had been the first card command before any node count).
#   8. the launches recorded are counted only from a runs.jsonl that exists (no stray error line in the launch output).
# The box layout: E192's root R = <tree>/build/claims-v3/aifoundry3/e192 holds the synced files at their repository paths and the build
# (R/build/intbits); the session writes build/e192/T<T0>/ (the reference session's own OUT is its run/ directory). The box's tools: the
# sampler build/ettelem/ettelem (the audit table's reviewed variant 'ettelem'), E78's heater build/sparsity/host/sparsity_host (lib.sh's
# HEATER on aifoundry3; workloads/sparsity, ops node only), the per-sensor sampler R/tools/claims-v3/e89/pvt_sample.py (E89's, synced).
#   E192_T0=<epoch> E192_DEADLINE_EPOCH=<epoch> E192_KITLIST_SHA256=<sha256> bash <R>/tools/claims-v3/e192/session_e192.sh
#   E192_T0=<epoch> E192_KITLIST_SHA256=<sha256> bash <R>/tools/claims-v3/e192/session_e192.sh --dry       (nothing opened)
# Desk-test variables, read ONLY with E192_DESKTEST=1 (the card day never sets it; the session start line names it when set):
# E192_CAP_S, E192_D0_S, E192_PVT_SAMPLE with E192_PVT_SHA256. Set without E192_DESKTEST=1 they are refused before anything.
# Exit codes: 0 done (every pass, or a registered stop after the smoke); 2 a refusal before anything (no device opened); 3 the card not
# free (no device opened) or a holder between passes; else the reference session's own (75 the card lock busy, 8 a stop in a block, 9
# the heater check, 4 telemetry stale, 6 hot).
# SPDX-License-Identifier: Apache-2.0
set -u
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)
TREE=$(cd "$R/../../../.." && pwd -P)
cd "$TREE" || exit 2
RR=${R#"$TREE"/}
DRY=; [ "${1:-}" = --dry ] && DRY=1
T0=${E192_T0:-}
case "$T0" in ''|*[!0-9]*) echo "E192_T0 must be the launch's epoch seconds"; exit 2 ;; esac
OUTD=build/e192/T$T0; [ -n "$DRY" ] && OUTD=$OUTD-dry
[ -e "$OUTD" ] && { echo "$OUTD exists: one session a T0"; exit 2; }
mkdir -p "$OUTD/run" || exit 2
LOG=$OUTD/session.log
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %Z') ${DRY:+DRY }$*" | tee -a "$LOG"; }
KIT=$RR/tools/claims-v3/e192
SRC=$KIT/proposal/src
H=$RR/build/intbits/host/intbits_host
ETTELEM=build/ettelem/ettelem
HEATER=build/sparsity/host/sparsity_host
PVT_SAMPLE=$RR/tools/claims-v3/e89/pvt_sample.py
PVT_SHA=c4e4aed59fbdc08ca6155c5a8a877105692d87c80b29b00f5bfd09a9b27c2134   # dmcmd_table.json's reviewed raw client
REG_LIST=$KIT/SHA256SUMS-e192-registration
REG_LIST_SHA=dd0a89635800818cd17c429be2d02c9710a434364f4196e6fd1a0f8e2dd74326
LOCK=/run/lock/etsoc-shire0.lock
PASSES=9; CAP_S=3900; D0_S=400; GAP=30
DESK=
if [ "${E192_DESKTEST:-}" = 1 ]; then
  DESK=" DESKTEST"
  CAP_S=${E192_CAP_S:-$CAP_S}; D0_S=${E192_D0_S:-$D0_S}
  [ -n "${E192_PVT_SAMPLE:-}" ] && { PVT_SAMPLE=$E192_PVT_SAMPLE; PVT_SHA=${E192_PVT_SHA256:?}; }
fi
nodev() { say "refused: $* (no device opened)"; finish_files 2; exit 2; }
notfree() { say "the card is not free: $* (no device opened)"; finish_files 3; exit 3; }
finish_files() {  # the manifest last, then wrapper.rc
  ( cd "$OUTD" && find . -type f ! -name 'MANIFEST.sha256*' ! -name wrapper.rc | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$OUTD/MANIFEST.sha256.tmp"
  mv "$OUTD/MANIFEST.sha256.tmp" "$OUTD/MANIFEST.sha256"
  echo "$1" > "$OUTD/wrapper.rc"
}
say "session start (T0 $T0 = $(date -d @"$T0" '+%H:%M:%S %Z' 2>/dev/null); E192, the proposal's reference session as committed, kit-e192$DESK${DRY:+; DRY})"
# ---- refusals before anything opens a card node (both paths) -----------------------------------------------------------------
if [ "${E192_DESKTEST:-}" != 1 ]; then
  for v in E192_CAP_S E192_D0_S E192_PVT_SAMPLE E192_PVT_SHA256; do
    [ -z "${!v:-}" ] || nodev "$v is a desk-test variable, read only with E192_DESKTEST=1 (the card day never sets it)"
  done
fi
hn=$(hostname 2>/dev/null); pyhn=$(python3 -I -B -c 'import socket; print(socket.gethostname())' 2>/dev/null)
[ "$hn" = aifoundry3 ] && [ "$pyhn" = aifoundry3 ] || nodev "this host is '$hn' (Python reads '$pyhn'), not aifoundry3: the registered order is drawn on 'aifoundry3|<pass>'"
[ -n "${USER:-}" ] && [ "$USER" = "$(id -un)" ] || nodev "USER is not this login (E183 kit note 6's carried rule)"
[ "$(sha256sum "$REG_LIST" 2>/dev/null | cut -d' ' -f1)" = "$REG_LIST_SHA" ] || nodev "the registration's list is not at its sha256 ${REG_LIST_SHA:0:12}"
( cd "$R" && grep -E '  tools/claims-v3/e192/(proposal/src/(run_session\.sh|run_block\.py|stopwatch\.py|arms\.txt|check_elf\.py)|desk/(arm-table-e192\.jsonl|order-e192-aifoundry3\.txt))$' \
    tools/claims-v3/e192/SHA256SUMS-e192-registration | sha256sum -c --quiet - ) > "$OUTD/pins-registration.txt" 2>&1 ||
  nodev "a registered session file is off its sha256 ($(head -c 200 "$OUTD/pins-registration.txt"))"
[ "$(grep -cE '  tools/claims-v3/e192/(proposal/src/(run_session\.sh|run_block\.py|stopwatch\.py|arms\.txt|check_elf\.py)|desk/(arm-table-e192\.jsonl|order-e192-aifoundry3\.txt))$' "$REG_LIST")" = 7 ] ||
  nodev "the registration's list does not name the seven session files"
KL=$KIT/SHA256SUMS-e192-kit
[ -n "${E192_KITLIST_SHA256:-}" ] && [ "$(sha256sum "$KL" 2>/dev/null | cut -d' ' -f1)" = "$E192_KITLIST_SHA256" ] ||
  nodev "the kit's list is not at the sha256 the runbook passed (E192_KITLIST_SHA256)"
( cd "$R" && grep -E '  tools/claims-v3/e192/(session_e192\.sh|gate_e192\.py|preflight_e192\.sh|drycheck_e192\.py)$' tools/claims-v3/e192/SHA256SUMS-e192-kit |
    sha256sum -c --quiet - ) > "$OUTD/pins-kit.txt" 2>&1 || nodev "a kit session file is off its sha256 ($(head -c 200 "$OUTD/pins-kit.txt"))"
[ "$(grep -cE '  tools/claims-v3/e192/(session_e192\.sh|gate_e192\.py|preflight_e192\.sh|drycheck_e192\.py)$' "$KL")" = 4 ] || nodev "the kit's list does not name the four kit session files"
for f in "$H" "$ETTELEM" "$HEATER"; do [ -x "$f" ] || nodev "no executable $f"; done
[ -r "$PVT_SAMPLE" ] || nodev "no per-sensor sampler $PVT_SAMPLE"
case "${E192_SAMPLER:-}" in ''|ettelem) ;; *) nodev "E192_SAMPLER may only be 'ettelem' (his go's choice of the plain sampler), not '${E192_SAMPLER}'" ;; esac
bash "$KIT/preflight_e192.sh" > "$OUTD/dmcmd-preflight.txt" 2>&1; prc=$?
[ "$prc" -eq 0 ] && grep -q '^PLAIN-CHAIN: GO' "$OUTD/dmcmd-preflight.txt" || nodev "the device-command audit of the plain chain is not GO (rc $prc)"
PVTOK=; PV=NO-GO; grep -q '^PVT-CHAIN: GO' "$OUTD/dmcmd-preflight.txt" && { PVTOK=1; PV=GO; }
# one card's nodes only, by name, before anything opens one (fix-e192, verify-e192 finding 2): exactly /dev/et0_ops and /dev/et0_mgmt
ops=""; for d in /dev/et*_ops; do [ -e "$d" ] && ops="$ops $d"; done
mgs=""; for d in /dev/et*_mgmt; do [ -e "$d" ] && mgs="$mgs $d"; done
[ "$ops" = " /dev/et0_ops" ] && [ "$mgs" = " /dev/et0_mgmt" ] ||
  nodev "the card nodes here are '${ops# }' and '${mgs# }', not exactly /dev/et0_ops and /dev/et0_mgmt: one card only, counted before anything opens a node (E192.md section 3)"
say "checked: host aifoundry3; USER the login; the registration's list ${REG_LIST_SHA:0:12} and its seven session files; the kit's list and its four session files; the host, the sampler, the heater; dmcmd_audit: the plain chain GO (the stock table), the per-sensor chain $PV (E144's table); one card's nodes (/dev/et0_ops, /dev/et0_mgmt)"
export H ETTELEM HEATER GAP TARGET=58 PREHEAT=59 LOCK
unset ET_DEVICES V3_DEVICE SAMPLER_S
# ---- the dry path: the reference session's DRY mode, every device call listed, nothing opened --------------------------------------
if [ -n "$DRY" ]; then
  say "would run: the free check (et-who --check; other users' device processes; a probe of $LOCK, read-only, never created)"
  say "would run, the first card command: flock -n $LOCK timeout 10 python3 -B $PVT_SAMPLE --probe (SAMPLER pvt if it answers with 34 sensors on every tick, else ettelem)"
  say "would run: gate_e192.py beside the session (the smoke gate; the cap, $CAP_S s from the first card command; a pass starts only if it can end inside it)"
  unset SAMPLER PVT_SAMPLE
  DRY=1 bash "$SRC/run_session.sh" "$OUTD/run" "$PASSES" > "$OUTD/run_session.out" 2>&1; rc=$?
  python3 -I -B "$KIT/drycheck_e192.py" "$OUTD/run_session.out" "$KIT/desk/order-e192-aifoundry3.txt" > "$OUTD/drycheck.txt" 2>&1; dc=$?
  say "the reference session's DRY mode: rc $rc; $(tail -n 1 "$OUTD/drycheck.txt")"
  say "session end (T0 $T0)"
  r=$rc; [ "$dc" -ne 0 ] && r=16
  finish_files "$r"; exit "$r"
fi
# ---- the real path -----------------------------------------------------------------------------------------------------------
[ -n "${E192_DEADLINE_EPOCH:-}" ] || nodev "no E192_DEADLINE_EPOCH (the window's last end)"
[ $(( $(date +%s) + CAP_S )) -le "$E192_DEADLINE_EPOCH" ] || nodev "the session would not start: its cap ($CAP_S s) passes the window's last end"
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner.Worker$'
o=$(et-who --check 2>&1); wrc=$?
[ "$wrc" -eq 0 ] || notfree "et-who --check exit $wrc ($(printf '%s' "$o" | grep -cE '^(/dev/et|lock:)') holder lines)"
p=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
[ "$p" -eq 0 ] || notfree "$p device process(es) of another user"
[ -e "$LOCK" ] || nodev "no card lock file $LOCK (the host makes it at boot; never created here)"
exec 9< "$LOCK"; flock -n -E 75 9; lrc=$?; flock -u 9 2>/dev/null; exec 9<&-
[ "$lrc" -eq 0 ] || notfree "the card lock is held (probe exit $lrc)"
SAMPLER=ettelem; why="the fallback"
FIRST=$(date +%s); echo "$FIRST" > "$OUTD/first-card-command.txt"
if [ "${E192_SAMPLER:-}" = ettelem ]; then
  why="his go named the plain sampler (E192_SAMPLER=ettelem): no probe sent"; FIRST=""; rm -f "$OUTD/first-card-command.txt"
elif [ -z "$PVTOK" ]; then
  why="the fallback: the per-sensor chain is not GO by the audit (no probe sent)"; FIRST=""; rm -f "$OUTD/first-card-command.txt"
elif [ "$(sha256sum "$PVT_SAMPLE" | cut -d' ' -f1)" = "$PVT_SHA" ]; then
  flock -n -E 75 "$LOCK" timeout 10 python3 -B "$PVT_SAMPLE" --probe > "$OUTD/pvt-probe.jsonl" 2> "$OUTD/pvt-probe.err" < /dev/null; prc=$?
  if [ "$prc" -eq 75 ]; then FIRST=""; rm -f "$OUTD/first-card-command.txt"; notfree "the card lock was taken before the probe (flock exit 75)"; fi
  if [ "$prc" -eq 0 ] && tail -n 1 "$OUTD/pvt-probe.jsonl" | grep -q '"cmd74": true'; then SAMPLER=pvt; why="its probe answered with 34 sensors on every tick"
  else why="the fallback: the per-sensor probe exited $prc ($(tail -n 1 "$OUTD/pvt-probe.jsonl" 2>/dev/null | cut -c1-120))"; fi
else
  why="the fallback: $PVT_SAMPLE is not at the audit table's reviewed sha256 (no probe sent)"
  FIRST=""; rm -f "$OUTD/first-card-command.txt"
fi
say "sampler: $SAMPLER ($why)"
[ -n "$FIRST" ] || { FIRST=$(date +%s); echo "$FIRST" > "$OUTD/first-card-command.txt"; }   # without a probe the sampler is the first card command
say "the first card command at $(date -d @"$FIRST" '+%H:%M:%S %Z'); the cap at $(date -d @$((FIRST + CAP_S)) '+%H:%M:%S %Z') ($CAP_S s)"
export SAMPLER PVT_SAMPLE
python3 -I -B "$KIT/gate_e192.py" "$OUTD/run" --first "$FIRST" --cap "$CAP_S" --d0 "$D0_S" --gap "$GAP" --passes "$PASSES" > "$OUTD/gate.out" 2>&1 < /dev/null &
GATE=$!
bash "$SRC/run_session.sh" "$OUTD/run" "$PASSES" > "$OUTD/run_session.out" 2>&1 < /dev/null &
RS=$!
stopw() {  # stopw <why>: the registered stop file, written once (the first writer's reason stands)
  [ -e "$OUTD/run/STOP" ] || printf '{"by": "session_e192", "why": "%s", "t_ms": %s}\n' "$1" "$(date +%s%3N)" > "$OUTD/run/STOP"
}
trap 'stopw "a signal to the wrapper: the run in flight finishes"; say "signal: STOP written; waiting for the session to end"' TERM INT HUP
say "running: run_session.sh (pid $RS), gate_e192.py (pid $GATE)"
while kill -0 "$RS" 2>/dev/null; do
  if ! kill -0 "$GATE" 2>/dev/null && [ ! -e "$OUTD/run/SESSION_DONE" ] && [ ! -e "$OUTD/run/STOP" ]; then
    stopw "the kit's gate watcher is gone"; say "the gate watcher is gone: STOP written"
  fi
  sleep 1
done
wait "$RS"; rc=$?
if [ ! -e "$OUTD/run/SESSION_DONE" ]; then   # fix-e192 (verify-e192 finding 1): run_session.sh exited before its EXIT trap wrote it
  printf '{"by": "session_e192", "why": "run_session.sh exited (rc %s) before its own end marker: written by the wrapper so the gate ends", "t_ms": %s}\n' \
    "$rc" "$(date +%s%3N)" > "$OUTD/run/SESSION_DONE"
  say "run_session.sh exited (rc $rc) before its own end marker (its EXIT trap writes SESSION_DONE): the wrapper wrote run/SESSION_DONE, so the gate ends now"
fi
trap - TERM INT HUP
wait "$GATE" 2>/dev/null
END=$(date +%s)
npass=$(python3 -I -B -c 'import json,sys
n=0
for l in open(sys.argv[1]):
    try: m=json.loads(l)
    except ValueError: continue
    if m.get("kind")=="idle" and m.get("label")=="after" and m.get("pass",-1)>=0: n+=1
print(n)' "$OUTD/run/marks.jsonl" 2>/dev/null); npass=${npass:-0}
nl=0; [ -f "$OUTD/run/runs.jsonl" ] && nl=$(wc -l < "$OUTD/run/runs.jsonl"); nl=${nl:-0}
st=""; [ -e "$OUTD/run/STOP" ] && st=$(head -c 300 "$OUTD/run/STOP")
say "run_session.sh rc $rc; the last lines of its log: $(tail -n 2 "$OUTD/run/session.log" 2>/dev/null | tr '\n' ' ' | cut -c1-300)"
[ -n "$st" ] && say "STOP: $st"
if [ "$npass" -eq 0 ]; then
  say "stopped before any pass completed: rc $rc${st:+; $st}"
fi
say "passes complete: $npass of $PASSES (pass 0 the registered warm-up); launches recorded $nl; card time $((END - FIRST)) s from the first card command (cap $CAP_S s)"
say "session end (T0 $T0)"
finish_files "$rc"
exit "$rc"
