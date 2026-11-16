#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE SESSION'S WRAPPER on aifoundry1 card 1. E192's wrapper
# (tools/claims-v3/e192/session_e192.sh, a6fe5c20, unchanged beside it) made card 1's, as new files: it runs E192's reference session AS
# COMMITTED (tools/claims-v3/e192/proposal/src/run_session.sh, which runs run_block.py and stopwatch.py, all three at E192's registration's
# sha256, unchanged), with ET_DEVICES=1 exported to every process that may open a device and card 1's lock, and adds only what E199.md
# sections 3, 7 and 15 ask of the kit, each before the first launch or through the registered stop file (OUT/STOP), never by editing,
# killing or re-ordering. Step 9 (rb/s11_a1_session_e199.sh) starts it detached; step 8 (rb/s10_a1_dry_e199.sh) runs it with --dry.
#   - before anything opens a card node (exit 2, "no device opened"): the host's name is aifoundry1 by hostname and by Python (the
#     registered order is drawn on "aifoundry1|<pass>"); USER the login; E192's registration list (dd0a8963...) and its six session files;
#     E199's registration list (4d05fe0a...) and its order file; the kit's list at the sha256 the runbook passed and its six session
#     files; the shared list and its six files (E191's identity module at E191's kit pin among them); the host, the reader (at E191's pin
#     8008f96f...), the heater and the per-sensor sampler present; THE SELECTION CHECK: the host, the reader and the heater each carry
#     ET_DEVICES (run_session.sh's own grep, made here first so that run_session.sh never refuses after a card command was sent);
#     dmcmd_audit GO (preflight_e199.sh); AIFOUNDRY1'S TWO CARDS' NODES ONLY, counted by name (exactly /dev/et0_ops, /dev/et1_ops,
#     /dev/et0_mgmt, /dev/et1_mgmt) and card 1's lock file /run/lock/etsoc-shire1.lock present; the window's last end the cap away;
#   - the free check (exit 3, "no device opened"): et-who --check exit 0 (no holder on EITHER card: E191's look's rule), no other user's
#     device process, a probe of card 1's lock (read-only, never created);
#   - THE FIRST CARD COMMAND: the start config read (`ettelem config` through ettelem_guard_e199.sh, ET_DEVICES=1, under card 1's lock,
#     timeout 10, its stderr kept), read by THE IDENTITY GATE (a) (ident_e199.py: /dev/et1_mgmt, physical device ID 1, TDP 65 W, 65 C,
#     600 MHz, minion_mv in (450, 510)); failing: no launch, "stopped before any pass completed" (16; a session: it sent a command);
#   - the per-sensor probe (pvt_sample.py --probe, its card read from ET_DEVICES=1, under card 1's lock, timeout 10): SAMPLER=pvt when it
#     answers with 34 sensors on every tick and the per-sensor chain is GO; else the plain sampler (E192.md section 4's fallback);
#   - THE KIT'S GATE (gate_e199.py, beside the session): E192's smoke gate and cap, CARD 1'S LIVE STOP LINES (board >= 65 W or minshire[0]
#     >= 70 C on any live sample), THE IDENTITY GATE (b) (with the sampler running and before the smoke's first launch) and THE WATCH on
#     every device process (its stderr's identity block and its open card nodes: another card is a STOP); a gate that dies is a STOP;
#   - run_session.sh's SESSION_DONE written by the wrapper when run_session.sh exits before its EXIT trap (E192's fix-e192 item 1);
#   - the end config read (its stderr kept; recorded, not a gate), the kits' session log (build/e199/T<T0>/session.log: "session start",
#     "session end (T0 <T0>)"; every rest rule of ours reads it), MANIFEST.sha256 last, then wrapper.rc.
# The box layout: k6's tree for aifoundry1 is ~/nekko (no git); E199's root R = <tree>/build/claims-v3/aifoundry1-c1/e199 (lib.sh's card-1
# data root) holds the synced files at their repository paths and the build (R/build/intbits); the session writes <tree>/build/e199/T<T0>/
# (the reference session's own OUT is its run/ directory). The box's tools: the reader <tree>/build/ettelem/ettelem, E78's heater
# <tree>/build/sparsity/host/sparsity_host (lib.sh's HEATER on aifoundry1; E157 ran it as E78's heater on card 1, 3 Nov 2026), the
# per-sensor sampler R/tools/claims-v3/e89/pvt_sample.py (E89's, synced).
#   E199_T0=<epoch> E199_DEADLINE_EPOCH=<epoch> E199_KITLIST_SHA256=<sha256> bash <R>/tools/claims-v3/e199/session_e199.sh
#   E199_T0=<epoch> E199_KITLIST_SHA256=<sha256> bash <R>/tools/claims-v3/e199/session_e199.sh --dry       (nothing opened)
# Desk-test variables, read ONLY with E199_DESKTEST=1 (the card day never sets it; the session start line names it when set):
# E199_CAP_S, E199_D0_S, E199_PVT_SAMPLE with E199_PVT_SHA256, E199_READER_SHA256, E199_B_DEADLINE_S. Set without E199_DESKTEST=1 they
# are refused before anything.
# Exit codes: 0 done (every pass, or a registered stop after the smoke); 2 a refusal before anything (no device opened); 3 the card not
# free (no device opened) or a holder between passes; 16 the identity gate (a) failed (no launch); else the reference session's own (75 the
# card lock busy, 8 a stop in a block, 9 the heater check, 4 telemetry stale, 6 hot).
# SPDX-License-Identifier: Apache-2.0
set -u
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)
TREE=$(cd "$R/../../../.." && pwd -P)
cd "$TREE" || exit 2
RR=${R#"$TREE"/}
DRY=; [ "${1:-}" = --dry ] && DRY=1
T0=${E199_T0:-}
case "$T0" in ''|*[!0-9]*) echo "E199_T0 must be the launch's epoch seconds"; exit 2 ;; esac
OUTD=build/e199/T$T0; [ -n "$DRY" ] && OUTD=$OUTD-dry
[ -e "$OUTD" ] && { echo "$OUTD exists: one session a T0"; exit 2; }
mkdir -p "$OUTD/run" || exit 2
LOG=$OUTD/session.log
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %Z') ${DRY:+DRY }$*" | tee -a "$LOG"; }
KIT=$RR/tools/claims-v3/e199
SRC=$RR/tools/claims-v3/e192/proposal/src
H=$RR/build/intbits/host/intbits_host
ETTELEM=build/ettelem/ettelem
HEATER=build/sparsity/host/sparsity_host
PVT_SAMPLE=$RR/tools/claims-v3/e89/pvt_sample.py
PVT_SHA=c4e4aed59fbdc08ca6155c5a8a877105692d87c80b29b00f5bfd09a9b27c2134      # dmcmd_table.json's reviewed raw client
READER_SHA=8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325   # E191's READER_SHA256 (E157's, E164's, E172's, E190 B's)
REG192=tools/claims-v3/e192/SHA256SUMS-e192-registration
REG192_SHA=dd0a89635800818cd17c429be2d02c9710a434364f4196e6fd1a0f8e2dd74326
REG199=tools/claims-v3/e199/SHA256SUMS-e199-registration
REG199_SHA=4d05fe0a7e6cadb6e3a2f0bf303d5f6804345c4ce9f738033a598ae926fff35f
LOCK=/run/lock/etsoc-shire1.lock
PASSES=9; CAP_S=3900; D0_S=400; GAP=30; B_DEADLINE_S=8
DESK=
if [ "${E199_DESKTEST:-}" = 1 ]; then
  DESK=" DESKTEST"
  CAP_S=${E199_CAP_S:-$CAP_S}; D0_S=${E199_D0_S:-$D0_S}; B_DEADLINE_S=${E199_B_DEADLINE_S:-$B_DEADLINE_S}
  [ -n "${E199_PVT_SAMPLE:-}" ] && { PVT_SAMPLE=$E199_PVT_SAMPLE; PVT_SHA=${E199_PVT_SHA256:?}; }
  READER_SHA=${E199_READER_SHA256:-$READER_SHA}
fi
nodev() { say "refused: $* (no device opened)"; finish_files 2; exit 2; }
notfree() { say "the card is not free: $* (no device opened)"; finish_files 3; exit 3; }
finish_files() {  # the manifest last, then wrapper.rc
  ( cd "$OUTD" && find . -type f ! -name 'MANIFEST.sha256*' ! -name wrapper.rc | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$OUTD/MANIFEST.sha256.tmp"
  mv "$OUTD/MANIFEST.sha256.tmp" "$OUTD/MANIFEST.sha256"
  echo "$1" > "$OUTD/wrapper.rc"
}
say "session start (T0 $T0 = $(date -d @"$T0" '+%H:%M:%S %Z' 2>/dev/null); E199, E192's reference session as committed on aifoundry1 card 1, kit-e199$DESK${DRY:+; DRY})"
# ---- refusals before anything opens a card node (both paths) -----------------------------------------------------------------
if [ "${E199_DESKTEST:-}" != 1 ]; then
  for v in E199_CAP_S E199_D0_S E199_PVT_SAMPLE E199_PVT_SHA256 E199_READER_SHA256 E199_B_DEADLINE_S; do
    [ -z "${!v:-}" ] || nodev "$v is a desk-test variable, read only with E199_DESKTEST=1 (the card day never sets it)"
  done
fi
hn=$(hostname 2>/dev/null); pyhn=$(python3 -I -B -c 'import socket; print(socket.gethostname())' 2>/dev/null)
[ "$hn" = aifoundry1 ] && [ "$pyhn" = aifoundry1 ] || nodev "this host is '$hn' (Python reads '$pyhn'), not aifoundry1: the registered order is drawn on 'aifoundry1|<pass>'"
[ -n "${USER:-}" ] && [ "$USER" = "$(id -un)" ] || nodev "USER is not this login (E183 kit note 6's carried rule)"
[ "$(sha256sum "$RR/$REG192" 2>/dev/null | cut -d' ' -f1)" = "$REG192_SHA" ] || nodev "E192's registration list is not at its sha256 ${REG192_SHA:0:12}"
SESS192='  tools/claims-v3/e192/(proposal/src/(run_session\.sh|run_block\.py|stopwatch\.py|arms\.txt|check_elf\.py)|desk/arm-table-e192\.jsonl)$'
( cd "$R" && grep -E "$SESS192" "$REG192" | sha256sum -c --quiet - ) > "$OUTD/pins-registration.txt" 2>&1 ||
  nodev "a registered session file of E192's is off its sha256 ($(head -c 200 "$OUTD/pins-registration.txt"))"
[ "$(grep -cE "$SESS192" "$RR/$REG192")" = 6 ] || nodev "E192's registration list does not name the six session files"
[ "$(sha256sum "$RR/$REG199" 2>/dev/null | cut -d' ' -f1)" = "$REG199_SHA" ] || nodev "E199's registration list is not at its sha256 ${REG199_SHA:0:12}"
( cd "$R" && grep -E '  tools/claims-v3/e199/order-e199-aifoundry1\.txt$' "$REG199" | sha256sum -c --quiet - ) >> "$OUTD/pins-registration.txt" 2>&1 &&
  [ "$(grep -cE '  tools/claims-v3/e199/order-e199-aifoundry1\.txt$' "$RR/$REG199")" = 1 ] || nodev "E199's registered order file is off its sha256"
KL=$KIT/SHA256SUMS-e199-kit
[ -n "${E199_KITLIST_SHA256:-}" ] && [ "$(sha256sum "$KL" 2>/dev/null | cut -d' ' -f1)" = "$E199_KITLIST_SHA256" ] ||
  nodev "the kit's list is not at the sha256 the runbook passed (E199_KITLIST_SHA256)"
SESSKIT='  tools/claims-v3/e199/(session_e199\.sh|gate_e199\.py|ident_e199\.py|ettelem_guard_e199\.sh|preflight_e199\.sh|drycheck_e199\.py)$'
( cd "$R" && grep -E "$SESSKIT" tools/claims-v3/e199/SHA256SUMS-e199-kit | sha256sum -c --quiet - ) > "$OUTD/pins-kit.txt" 2>&1 ||
  nodev "a kit session file is off its sha256 ($(head -c 200 "$OUTD/pins-kit.txt"))"
[ "$(grep -cE "$SESSKIT" "$KL")" = 6 ] || nodev "the kit's list does not name the six kit session files"
SH=$KIT/SHA256SUMS-e199-shared
grep -qE '^[0-9a-f]{64}  tools/claims-v3/e199/SHA256SUMS-e199-shared$' "$KL" && ( cd "$R" && grep -E '  tools/claims-v3/e199/SHA256SUMS-e199-shared$' tools/claims-v3/e199/SHA256SUMS-e199-kit | sha256sum -c --quiet - ) > /dev/null 2>&1 ||
  nodev "the shared list is not at the kit list's sha256"
( cd "$R" && sha256sum -c --quiet tools/claims-v3/e199/SHA256SUMS-e199-shared ) > "$OUTD/pins-shared.txt" 2>&1 || nodev "a shared file is off its sha256 ($(head -c 200 "$OUTD/pins-shared.txt"))"
grep -qE '^3fabb60379c81b097473f1cd9b52ccda24dbd924aa00533535aec4ca4256f959  tools/claims-v3/e191/e191_ident\.py$' "$SH" || nodev "E191's identity module is not pinned at E191's kit pin 3fabb603"
for f in "$H" "$ETTELEM" "$HEATER"; do [ -x "$f" ] || nodev "no executable $f"; done
[ -r "$PVT_SAMPLE" ] || nodev "no per-sensor sampler $PVT_SAMPLE"
[ "$(sha256sum "$ETTELEM" 2>/dev/null | cut -d' ' -f1)" = "$READER_SHA" ] || nodev "the reader $ETTELEM is not at E191's pin ${READER_SHA:0:12}"
for f in "$H" "$ETTELEM" "$HEATER"; do   # run_session.sh's own check on a two-card host, made here before anything (never after a command)
  grep -aqw ET_DEVICES "$f" || nodev "$f does not carry ET_DEVICES: on aifoundry1 it would open every card (run_session.sh would refuse it after the first card command)"
done
case "${E199_SAMPLER:-}" in ''|ettelem) ;; *) nodev "E199_SAMPLER may only be 'ettelem' (the go's choice of the plain sampler), not '${E199_SAMPLER}'" ;; esac
bash "$KIT/preflight_e199.sh" > "$OUTD/dmcmd-preflight.txt" 2>&1; prc=$?
[ "$prc" -eq 0 ] && grep -q '^PLAIN-CHAIN: GO' "$OUTD/dmcmd-preflight.txt" || nodev "the device-command audit of the plain chain is not GO (rc $prc)"
PVTOK=; PV=NO-GO; grep -q '^PVT-CHAIN: GO' "$OUTD/dmcmd-preflight.txt" && { PVTOK=1; PV=GO; }
# aifoundry1's two cards' nodes only, by name, before anything opens one; card 1's lock file (never created here)
ops=""; for d in /dev/et*_ops; do [ -e "$d" ] && ops="$ops $d"; done
mgs=""; for d in /dev/et*_mgmt; do [ -e "$d" ] && mgs="$mgs $d"; done
[ "$ops" = " /dev/et0_ops /dev/et1_ops" ] && [ "$mgs" = " /dev/et0_mgmt /dev/et1_mgmt" ] ||
  nodev "the card nodes here are '${ops# }' and '${mgs# }', not exactly aifoundry1's two cards (/dev/et0_ops /dev/et1_ops, /dev/et0_mgmt /dev/et1_mgmt)"
[ -e "$LOCK" ] || nodev "no card lock file $LOCK (the host makes it at boot; never created here)"
say "checked: host aifoundry1; USER the login; E192's registration list ${REG192_SHA:0:12} and its six session files; E199's registration list ${REG199_SHA:0:12} and its order; the kit's list and its six session files; the shared list (E191's identity module 3fabb603); the host, the reader (E191's pin), the heater, each carrying ET_DEVICES; dmcmd_audit: the plain chain GO (the stock table), the per-sensor chain $PV (E144's table); aifoundry1's two cards' nodes; card 1's lock file"
export H ETTELEM HEATER GAP TARGET=58 PREHEAT=59 LOCK
export ET_DEVICES=1
unset V3_DEVICE SAMPLER_S
# ---- the dry path: the reference session's DRY mode, every device call listed, nothing opened --------------------------------------
if [ -n "$DRY" ]; then
  say "would run: the free check (et-who --check on both cards; other users' device processes; a probe of $LOCK, read-only, never created)"
  say "would run, the first card command: flock -n $LOCK timeout 10 bash $KIT/ettelem_guard_e199.sh config (ET_DEVICES=1; THE IDENTITY GATE (a): /dev/et1_mgmt, ID 1, 65 W / 65 C / 600 MHz, minion_mv in (450, 510))"
  say "would run: flock -n $LOCK timeout 10 python3 -B $PVT_SAMPLE --probe (ET_DEVICES=1: card 1; SAMPLER pvt if it answers with 34 sensors on every tick, else ettelem)"
  say "would run: gate_e199.py beside the session (the smoke gate; the cap, $CAP_S s from the first card command; card 1's live stops 65 W / 70 C; THE IDENTITY GATE (b) within $B_DEADLINE_S s of the first sample; THE WATCH on every device process)"
  unset SAMPLER PVT_SAMPLE
  DRY=1 bash "$SRC/run_session.sh" "$OUTD/run" "$PASSES" > "$OUTD/run_session.out" 2>&1; rc=$?
  python3 -I -B "$KIT/drycheck_e199.py" "$OUTD/run_session.out" "$KIT/order-e199-aifoundry1.txt" > "$OUTD/drycheck.txt" 2>&1; dc=$?
  say "the reference session's DRY mode: rc $rc; $(tail -n 1 "$OUTD/drycheck.txt")"
  say "session end (T0 $T0)"
  r=$rc; [ "$dc" -ne 0 ] && r=16
  finish_files "$r"; exit "$r"
fi
# ---- the real path -----------------------------------------------------------------------------------------------------------
[ -n "${E199_DEADLINE_EPOCH:-}" ] || nodev "no E199_DEADLINE_EPOCH (the window's last end)"
[ $(( $(date +%s) + CAP_S )) -le "$E199_DEADLINE_EPOCH" ] || nodev "the session would not start: its cap ($CAP_S s) passes the window's last end"
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner.Worker$'
o=$(et-who --check 2>&1); wrc=$?
printf '%s\n' "$o" | grep -E '^(/dev/et|lock:)' | awk '{c="?"; if ($1 ~ /^\/dev\/et0_/ || $1 == "lock:etsoc-shire0.lock") c="0"; if ($1 ~ /^\/dev\/et1_/ || $1 == "lock:etsoc-shire1.lock") c="1"; n[c]++} END {printf "card 1 %d, card 0 %d, other %d\n", n["1"]+0, n["0"]+0, n["?"]+0}' > "$OUTD/etwho-before.txt"
[ "$wrc" -eq 0 ] || notfree "et-who --check exit $wrc (holder lines by card: $(cat "$OUTD/etwho-before.txt"); either card blocks)"
p=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
[ "$p" -eq 0 ] || notfree "$p device process(es) of another user"
exec 9< "$LOCK"; flock -n -E 75 9; lrc=$?; flock -u 9 2>/dev/null; exec 9<&-
[ "$lrc" -eq 0 ] || notfree "card 1's lock is held (probe exit $lrc)"
# THE FIRST CARD COMMAND: the start config read, THE IDENTITY GATE (a)
FIRST=$(date +%s); echo "$FIRST" > "$OUTD/first-card-command.txt"
flock -n -E 75 "$LOCK" timeout 10 bash "$KIT/ettelem_guard_e199.sh" config > "$OUTD/config-start.out" 2> "$OUTD/config-start.err" < /dev/null; crc=$?
if [ "$crc" -eq 75 ]; then rm -f "$OUTD/first-card-command.txt"; notfree "card 1's lock was taken before the start config read (flock exit 75)"; fi
if [ "$crc" -ne 0 ] && ! grep -q '^{' "$OUTD/config-start.out" 2>/dev/null; then
  # no config came back (our own live collector can hold card 1's management node for a moment; E191's step 7 note): ONE more read
  mv "$OUTD/config-start.out" "$OUTD/config-start-try1.out"; mv "$OUTD/config-start.err" "$OUTD/config-start-try1.err"
  say "the start config read exited $crc with no config: one more read in 3 s (a read, the same command)"
  sleep 3
  flock -n -E 75 "$LOCK" timeout 10 bash "$KIT/ettelem_guard_e199.sh" config > "$OUTD/config-start.out" 2> "$OUTD/config-start.err" < /dev/null; crc=$?
fi
python3 -I -B "$KIT/ident_e199.py" config "$OUTD/config-start.out" "$OUTD/config-start.err" > "$OUTD/identity-a.txt" 2>&1; irc=$?
if [ "$crc" -ne 0 ] || [ "$irc" -ne 0 ]; then
  say "THE IDENTITY GATE (a) FAILED: the start config read exited $crc; $(head -c 400 "$OUTD/identity-a.txt" | tr '\n' ' ')"
  say "stopped before any pass completed: the identity gate (a) (no launch; card time $(( $(date +%s) - FIRST )) s from the first card command)"
  say "session end (T0 $T0)"
  finish_files 16; exit 16
fi
say "identity (a): $(head -n 1 "$OUTD/identity-a.txt" | cut -c1-260)"
SAMPLER=ettelem; why="the fallback"
if [ "${E199_SAMPLER:-}" = ettelem ]; then
  why="the go named the plain sampler (E199_SAMPLER=ettelem): no probe sent"
elif [ -z "$PVTOK" ]; then
  why="the fallback: the per-sensor chain is not GO by the audit (no probe sent)"
elif [ "$(sha256sum "$PVT_SAMPLE" | cut -d' ' -f1)" = "$PVT_SHA" ]; then
  flock -n -E 75 "$LOCK" timeout 10 python3 -B "$PVT_SAMPLE" --probe > "$OUTD/pvt-probe.jsonl" 2> "$OUTD/pvt-probe.err" < /dev/null; prc=$?
  if [ "$prc" -eq 75 ]; then why="the fallback: card 1's lock was taken at the probe (flock exit 75; no probe sent)"
  elif [ "$prc" -eq 0 ] && tail -n 1 "$OUTD/pvt-probe.jsonl" | grep -q '"cmd74": true'; then SAMPLER=pvt; why="its probe answered with 34 sensors on every tick"
  else why="the fallback: the per-sensor probe exited $prc ($(tail -n 1 "$OUTD/pvt-probe.jsonl" 2>/dev/null | cut -c1-120))"; fi
else
  why="the fallback: $PVT_SAMPLE is not at the audit table's reviewed sha256 (no probe sent)"
fi
say "sampler: $SAMPLER ($why)"
say "the first card command at $(date -d @"$FIRST" '+%H:%M:%S %Z') (the start config read); the cap at $(date -d @$((FIRST + CAP_S)) '+%H:%M:%S %Z') ($CAP_S s)"
export SAMPLER PVT_SAMPLE
python3 -I -B "$KIT/gate_e199.py" "$OUTD/run" --first "$FIRST" --cap "$CAP_S" --d0 "$D0_S" --gap "$GAP" --passes "$PASSES" \
  --root-pid $$ --b-deadline "$B_DEADLINE_S" > "$OUTD/gate.out" 2>&1 < /dev/null &
GATE=$!
bash "$SRC/run_session.sh" "$OUTD/run" "$PASSES" > "$OUTD/run_session.out" 2>&1 < /dev/null &
RS=$!
stopw() {  # stopw <why>: the registered stop file, written once (the first writer's reason stands)
  [ -e "$OUTD/run/STOP" ] || printf '{"by": "session_e199", "why": "%s", "t_ms": %s}\n' "$1" "$(date +%s%3N)" > "$OUTD/run/STOP"
}
trap 'stopw "a signal to the wrapper: the run in flight finishes"; say "signal: STOP written; waiting for the session to end"' TERM INT HUP
say "running: run_session.sh (pid $RS), gate_e199.py (pid $GATE), ET_DEVICES=1, LOCK $LOCK"
while kill -0 "$RS" 2>/dev/null; do
  if ! kill -0 "$GATE" 2>/dev/null && [ ! -e "$OUTD/run/SESSION_DONE" ] && [ ! -e "$OUTD/run/STOP" ]; then
    stopw "the kit's gate watcher is gone"; say "the gate watcher is gone: STOP written"
  fi
  sleep 1
done
wait "$RS"; rc=$?
if [ ! -e "$OUTD/run/SESSION_DONE" ]; then   # E192's fix-e192 item 1: run_session.sh exited before its EXIT trap wrote it
  printf '{"by": "session_e199", "why": "run_session.sh exited (rc %s) before its own end marker: written by the wrapper so the gate ends", "t_ms": %s}\n' \
    "$rc" "$(date +%s%3N)" > "$OUTD/run/SESSION_DONE"
  say "run_session.sh exited (rc $rc) before its own end marker (its EXIT trap writes SESSION_DONE): the wrapper wrote run/SESSION_DONE, so the gate ends now"
fi
trap - TERM INT HUP
wait "$GATE" 2>/dev/null
END=$(date +%s)
# the end config read (its stderr kept): recorded beside the start's, not a gate (the session is over); never while card 1's lock is held
flock -n -E 75 "$LOCK" timeout 10 bash "$KIT/ettelem_guard_e199.sh" config > "$OUTD/config-end.out" 2> "$OUTD/config-end.err" < /dev/null; erc=$?
python3 -I -B "$KIT/ident_e199.py" config "$OUTD/config-end.out" "$OUTD/config-end.err" > "$OUTD/identity-end.txt" 2>&1
say "the end config read: exit $erc; $(head -n 1 "$OUTD/identity-end.txt" | cut -c1-240) (recorded, not a gate)"
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
grep -h '"kind": "identity_b"' "$OUTD/run/gate.jsonl" 2>/dev/null | tail -n 1 | cut -c1-300 | sed 's/^/identity (b): /' | while IFS= read -r l; do say "$l"; done
if [ "$npass" -eq 0 ]; then
  say "stopped before any pass completed: rc $rc${st:+; $st}"
fi
say "passes complete: $npass of $PASSES (pass 0 the registered warm-up); launches recorded $nl; card time $((END - FIRST)) s from the first card command (cap $CAP_S s)"
say "session end (T0 $T0)"
finish_files "$rc"
exit "$rc"
