#!/usr/bin/env bash
# E197 (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum): THE SITTING'S WRAPPER on aifoundry3. Step 9
# (rb/s11_a3_session_e197.sh) starts it detached (setsid nohup) after k6's guard, THE REST RULE, today's dry pass, today's build and
# step 7's reads (the sitting's first card command); step 8 (rb/s10_a3_dry_e197.sh) runs it with --dry. It runs THE PROPOSAL'S REFERENCE
# SESSION AS REGISTERED (E197.md 5): proposal/src/run_session.sh, proposal/src/stopwatch.py and proposal/src/trains.tsv, with the lab's
# runner lab/run_trains.py in place of src/run_trains.py (departure D1: `timeout 10`, never a KILL), all four at the registration's
# sha256, copied into the sitting's directory (run_session.sh runs the runner and the stopwatch from its own folder) and checked there,
# driven with the box's tools, and adds only what E197.md 18.2 asks of the kit, each before the session or through the registered stop
# file (OUT/STOP), never by editing, killing or re-ordering:
#   - before anything opens a card node (exit 2, "no device opened by the session"): the host's name is aifoundry3; USER is the login;
#     harness-e197.json at the sha256 the launch passes and every file of it at its pin (the registration's 35 among them); the
#     registration's list at its sha256; the host and E128's guard and the box's sampler present, the host the one today's build
#     recorded; dmcmd_audit GO (preflight_e197.sh); ONE CARD'S NODES ONLY (exactly /dev/et0_ops and /dev/et0_mgmt, by name: E197.md 3);
#     the sitting's first card command today and at most 120 s ago (FIRST_MAX), and its cap before the window's last end;
#   - THE FIRST CARD COMMAND is not this script's: E197.md 6 names the first command of the sitting that reaches the card or its
#     management node, and step 7's config read (k6's reads, `ettelem config` through E128's guard) comes before this session's holder
#     checks; step 7's wrapper stamps it and step 9 passes it (E197_FIRST). The cap (sitting 1 full 3,000 s, short 2,400 s; sitting 2
#     2,100 s) counts from it (E197.md 10);
#   - the free check (et-who --check exit 0, no other user's device process, a probe of the existing card lock: exit 3, "no device opened
#     by the session"), then the reference session with CAP_S = the cap - 60 s - (now - the first card command), so that its deadline
#     (its sampler's start + CAP_S - 60 s) falls at the first card command + the cap - 120 s, never past the window's last end - 180 s
#     (KIT.md 4), and ETTELEM = E128's guard (the plain sampler, E197.md 4: `sample --seconds --every-ms 100` only);
#   - THE KIT'S WATCH beside it (watch_e197.py: the kit's live stops, the kit's smoke check, the end-stop at the cap - 30 s, and the hang
#     watch for a device process that outlives its timeout's TERM: a STOP and a report, never a kill); a watch that dies while the
#     session runs is a stop (the wrapper writes STOP); a signal to the wrapper writes STOP and waits for the session's own end;
#   - when run_session.sh has exited without its own end marker (it writes OUT/SESSION_DONE only in its EXIT trap, set after its
#     refusals and its free check), the wrapper writes OUT/SESSION_DONE itself (one JSON line naming the wrapper: E192's fix 1), so the
#     watch and the stopwatch end;
#   - the kits' session log build/e197/T<T0>/session.log ("session start", "session end (T0 <T0>)": every rest rule of ours reads it),
#     the end read by check_e197.py summary (the smoke gate, the kit's smoke check, the blocks, the stop and whether it names the card,
#     SITTING-RESULT, and GATE-STOP when no block of trains.tsv began), a crash written apart from a registered stop ("the trains ended
#     without a registered stop": exit 9), then MANIFEST.sha256 last and wrapper.rc after it.
# The box layout: E197's root R = <tree>/build/claims-v3/aifoundry3/e197 holds the synced files at their repository paths and the build
# (R/build/regfile, R/build/regfile-built.txt); the sitting writes build/e197/T<T0>/ (the reference session's OUT is its run/
# directory, its four files in ref/). The box's tools: the sampler build/ettelem/ettelem behind E128's guard (the audit table's reviewed
# variant 'ettelem'), et-who (/usr/local/bin), coreutils' timeout, util-linux's flock.
#   E197_T0=<epoch> E197_SIT=1|2 E197_PLAN=full|short|ext E197_FIRST=<epoch> E197_LAST_END_EPOCH=<epoch> E197_HARNESS_SHA256=<sha256> \
#     bash <R>/tools/claims-v3/e197/session_e197.sh
#   E197_T0=<epoch> E197_SIT=1|2 E197_PLAN=full|short|ext E197_HARNESS_SHA256=<sha256> bash <R>/tools/claims-v3/e197/session_e197.sh --dry
# Desk-test variables, read ONLY with E197_DESKTEST=1 (the card day never sets it; the session start line names it when set): E197_CAP_S.
# Exit codes: 0 done (every block, or the runner's deadline skipped or cut trains); 2 a refusal before anything (no device opened by
# the session); 3 the card not free (no device opened by the session) or a holder between blocks; 9 the trains ended without a
# registered stop (a crash: nothing is killed; a dated note decides); else the reference session's own: 75 the card lock busy, 7 the
# smoke gate, 8 a stop by the stop file (watch, stopwatch, wrapper, by hand), 4 telemetry stale, 5 failing processes, 6 hot, 128+n a signal.
# SPDX-License-Identifier: Apache-2.0
set -u
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)
TREE=$(cd "$R/../../../.." && pwd -P)
cd "$TREE" || exit 2
RR=${R#"$TREE"/}
DRYRUN=; [ "${1:-}" = --dry ] && DRYRUN=1
unset DRY   # the reference session reads DRY from its environment: only the dry path below sets it, for that one call
T0=${E197_T0:-}; SIT=${E197_SIT:-}; PLAN=${E197_PLAN:-}
case "$T0" in ''|*[!0-9]*) echo "E197_T0 must be the launch's epoch seconds"; exit 2 ;; esac
case "$SIT:$PLAN" in 1:full|1:short|2:ext) ;; *) echo "E197_SIT:E197_PLAN must be 1:full, 1:short or 2:ext, not '$SIT:$PLAN'"; exit 2 ;; esac
OUTD=build/e197/T$T0; [ -n "$DRYRUN" ] && OUTD=$OUTD-dry
[ -e "$OUTD" ] && { echo "$OUTD exists: one session a T0"; exit 2; }
mkdir -p "$OUTD/ref" "$OUTD/run" || exit 2
LOG=$OUTD/session.log
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %Z') ${DRYRUN:+DRY }$*" | tee -a "$LOG"; }
KIT=$RR/tools/claims-v3/e197
SRC=$KIT/proposal/src
H=$RR/build/regfile/host/regfile_host
GUARD=$RR/tools/claims-v3/e128/ettelem_guard.sh
SBIN=build/ettelem/ettelem
BUILT=$RR/build/regfile-built.txt
REG_LIST=$KIT/SHA256SUMS-e197-registration
REG_LIST_SHA=992a35e577617489d571f1af6e37f78b08e967d82e6529261ebf7db19e05ad95
LOCK=/run/lock/etsoc-shire0.lock
case "$PLAN" in full) CAP=3000 ;; short) CAP=2400 ;; ext) CAP=2100 ;; esac
GAP=30; DLM=120; FIRST_MAX=120   # 120 s since fix-e197 (Q191; verify-e197 F2: was 600); step 9 the same (E197_FIRST_MAX_S)
DESK=
if [ "${E197_DESKTEST:-}" = 1 ]; then DESK=" DESKTEST"; CAP=${E197_CAP_S:-$CAP}; fi
finish_files() {  # the manifest last, then wrapper.rc
  ( cd "$OUTD" && find . -type f ! -name 'MANIFEST.sha256*' ! -name wrapper.rc | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$OUTD/MANIFEST.sha256.tmp"
  mv "$OUTD/MANIFEST.sha256.tmp" "$OUTD/MANIFEST.sha256"
  echo "$1" > "$OUTD/wrapper.rc"
}
nodev() { say "GATE-STOP: refused: $* (no device opened by the session)"; say "session end (T0 $T0)"; finish_files 2; exit 2; }
notfree() { say "GATE-STOP: the card is not free: $* (no device opened by the session)"; say "session end (T0 $T0)"; finish_files 3; exit 3; }
say "session start (T0 $T0 = $(date -d @"$T0" '+%H:%M:%S %Z' 2>/dev/null); E197 sitting $SIT, plan $PLAN; the proposal's reference session with the lab's runner (departure D1), kit-e197$DESK${DRYRUN:+; DRY})"
# ---- refusals before anything opens a card node (both paths) -----------------------------------------------------------------
if [ "${E197_DESKTEST:-}" != 1 ]; then
  for v in E197_CAP_S; do [ -z "${!v:-}" ] || nodev "$v is a desk-test variable, read only with E197_DESKTEST=1 (the card day never sets it)"; done
fi
hn=$(hostname 2>/dev/null); pyhn=$(python3 -I -B -c 'import socket; print(socket.gethostname())' 2>/dev/null)
[ "$hn" = aifoundry3 ] && [ "$pyhn" = aifoundry3 ] || nodev "this host is '$hn' (Python reads '$pyhn'), not aifoundry3 (E197.md 3: aifoundry3 card 0)"
[ -n "${USER:-}" ] && [ "$USER" = "$(id -un)" ] || nodev "USER is not this login (E183 kit note 6's carried rule)"
HJ=$KIT/harness-e197.json
[ -n "${E197_HARNESS_SHA256:-}" ] && [ "$(sha256sum "$HJ" 2>/dev/null | cut -d' ' -f1)" = "$E197_HARNESS_SHA256" ] ||
  nodev "harness-e197.json is not at the sha256 the launch passed (E197_HARNESS_SHA256)"
python3 -I -B "$KIT/harness_e197.py" --box --root "$RR" > "$OUTD/harness.txt" 2>&1 || nodev "the harness: $(tail -n 1 "$OUTD/harness.txt" | cut -c1-200)"
[ "$(sha256sum "$REG_LIST" 2>/dev/null | cut -d' ' -f1)" = "$REG_LIST_SHA" ] || nodev "the registration's list is not at its sha256 ${REG_LIST_SHA:0:12}"
for f in "$H" "$GUARD" "$SBIN"; do [ -x "$f" ] || nodev "no executable $f"; done
[ -s "$BUILT" ] && grep -q '^REGFILE-BUILT ' "$BUILT" || nodev "no build record $BUILT (step 6)"
[ "$(TZ=America/Los_Angeles date -r "$BUILT" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] || nodev "the build record was not written today (Pacific)"
[ "$(awk '$1 == "host" {print $2}' "$BUILT")" = "$(sha256sum "$H" | cut -d' ' -f1)" ] || nodev "the host is not the one today's build recorded"
bash "$KIT/preflight_e197.sh" > "$OUTD/preflight.txt" 2>&1; prc=$?
[ "$prc" -eq 0 ] && head -n 1 "$OUTD/preflight.txt" | grep -q '^dmcmd_audit: GO' || nodev "the device-command audit is not GO (rc $prc)"
ops=""; for d in /dev/et*_ops; do [ -e "$d" ] && ops="$ops $d"; done
mgs=""; for d in /dev/et*_mgmt; do [ -e "$d" ] && mgs="$mgs $d"; done
[ "$ops" = " /dev/et0_ops" ] && [ "$mgs" = " /dev/et0_mgmt" ] ||
  nodev "the card nodes here are '${ops# }' and '${mgs# }', not exactly /dev/et0_ops and /dev/et0_mgmt: one card only, counted before anything opens a node (E197.md 3)"
for f in run_session.sh stopwatch.py trains.tsv; do cp "$SRC/$f" "$OUTD/ref/$f" || nodev "cannot copy $f"; done
cp "$KIT/lab/run_trains.py" "$OUTD/ref/run_trains.py" || nodev "cannot copy lab/run_trains.py"
for p in proposal/src/run_session.sh proposal/src/stopwatch.py proposal/src/trains.tsv lab/run_trains.py; do
  w=$(awk -v p="tools/claims-v3/e197/$p" '$2 == p {print $1}' "$REG_LIST")
  [ -n "$w" ] && [ "$(sha256sum "$OUTD/ref/${p##*/}" | cut -d' ' -f1)" = "$w" ] || nodev "the session's copy of $p is not at the registration's sha256"
done
say "checked: host aifoundry3; USER the login; harness-e197.json at the launch's sha256, $(tail -n 1 "$OUTD/harness.txt" | cut -c1-80); the registration's list ${REG_LIST_SHA:0:12}; the host (today's build), E128's guard, the box's sampler; dmcmd_audit GO; one card's nodes (/dev/et0_ops, /dev/et0_mgmt); ref/: run_session.sh, stopwatch.py, trains.tsv (proposal/src) and run_trains.py (lab/, D1) at the registration's sha256"
export H GAP LOCK
export ETTELEM=$RR/tools/claims-v3/e128/ettelem_guard.sh   # = $GUARD, written out so that dmcmd_audit resolves run_session.sh's "$ETTELEM" to the guard
unset ET_DEVICES V3_DEVICE SAMPLER SAMPLER_S PVT_SAMPLE CAP_S
# ---- the dry path: the reference session's DRY mode, every device call listed, nothing opened --------------------------------------
if [ -n "$DRYRUN" ]; then
  say "would run: the free check (et-who --check; other users' device processes; a probe of $LOCK, read-only, never created)"
  say "would run: the reference session with CAP_S = the cap ($CAP s) - 60 s - (now - the first card command, step 7's read), ETTELEM = E128's guard; the kit's watch beside it (its live stops, its smoke check, the end-stop at the cap - 30 s, the hang watch)"
  DRY=1 bash "$OUTD/ref/run_session.sh" "$OUTD/run" "$PLAN" > "$OUTD/run_session.out" 2>&1; rc=$?
  python3 -I -B "$KIT/check_e197.py" drycmp "$OUTD/run_session.out" "$KIT/desk/dry-e197-$PLAN.txt" --host "$H" --out "$OUTD/run" > "$OUTD/drycmp.txt" 2>&1; dc=$?
  say "the reference session's DRY mode: rc $rc; $(head -n 1 "$OUTD/drycmp.txt" | cut -c1-200)"
  say "session end (T0 $T0)"
  r=$rc; [ "$dc" -ne 0 ] && r=16
  finish_files "$r"; exit "$r"
fi
# ---- the real path -----------------------------------------------------------------------------------------------------------
FIRST=${E197_FIRST:-}
case "$FIRST" in ''|*[!0-9]*) nodev "no E197_FIRST (the sitting's first card command, step 7's read, epoch seconds)" ;; esac
NOW=$(date +%s)
[ "$FIRST" -le "$NOW" ] || nodev "the first card command $FIRST lies in the future"
[ "$(TZ=America/Los_Angeles date -d @"$FIRST" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] || nodev "the first card command was not today (Pacific)"
[ $((NOW - FIRST)) -le "$FIRST_MAX" ] || nodev "the first card command was $((NOW - FIRST)) s ago, more than $FIRST_MAX s: its cap counts from it (run step 9 right after step 7)"
LE=${E197_LAST_END_EPOCH:-}
case "$LE" in ''|*[!0-9]*) nodev "no E197_LAST_END_EPOCH (the window's last end)" ;; esac
[ $((FIRST + CAP)) -le "$LE" ] || nodev "the cap ($CAP s from the first card command) passes the window's last end"
[ -e "$LOCK" ] || nodev "no card lock file $LOCK (the host makes it at boot; never created here)"
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner.Worker$'
o=$(timeout 30 et-who --check 2>&1); wrc=$?
[ "$wrc" -eq 0 ] || notfree "et-who --check exit $wrc ($(printf '%s' "$o" | grep -cE '^(/dev/et|lock:)') holder lines)"
p=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
[ "$p" -eq 0 ] || notfree "$p device process(es) of another user"
exec 9< "$LOCK"; flock -n -E 75 9; lrc=$?; exec 9<&-
[ "$lrc" -eq 0 ] || notfree "the card lock is held (probe exit $lrc)"
echo "$FIRST" > "$OUTD/first-card-command.txt"
NOW=$(date +%s)
CAPS=$((CAP - DLM + 60 - (NOW - FIRST)))
WCAP=$((LE - 180 + 60 - NOW)); [ "$WCAP" -lt "$CAPS" ] && CAPS=$WCAP
[ "$CAPS" -ge 300 ] || nodev "too little of the cap is left for a block ($CAPS s)"
export CAP_S=$CAPS
say "the first card command at $(date -d @"$FIRST" '+%H:%M:%S %Z') (step 7's config read, k6's reads through E128's guard); the cap $CAP s, at $(date -d @$((FIRST + CAP)) '+%H:%M:%S %Z'); CAP_S $CAPS s, the runner's deadline at about $(date -d @$((NOW + CAPS - 60)) '+%H:%M:%S %Z') (the first card command + the cap - $DLM s); the end-stop at $(date -d @$((FIRST + CAP - 30)) '+%H:%M:%S %Z')"
python3 -I -B "$KIT/watch_e197.py" "$OUTD/run" --first "$FIRST" --cap "$CAP" --host "$H" --log-dir "$OUTD" --session-log "$LOG" > "$OUTD/watch.out" 2>&1 < /dev/null &
WATCH=$!
bash "$OUTD/ref/run_session.sh" "$OUTD/run" "$PLAN" > "$OUTD/run_session.out" 2>&1 < /dev/null &
RS=$!
stopw() {  # stopw <why>: the registered stop file, created once with O_EXCL (set -C, verify-e197 F5): the first writer's reason stands
  ( set -C; printf '{"by": "session_e197", "why": "%s", "t_ms": %s, "card": false}\n' "$1" "$(date +%s%3N)" > "$OUTD/run/STOP" ) 2> /dev/null || :
}
trap 'stopw "a signal to the wrapper: the launch in flight finishes"; say "signal: STOP written; waiting for the session to end"' TERM INT HUP
say "running: run_session.sh $PLAN (pid $RS), watch_e197.py (pid $WATCH)"
while kill -0 "$RS" 2>/dev/null; do
  if ! kill -0 "$WATCH" 2>/dev/null && [ ! -e "$OUTD/run/SESSION_DONE" ] && [ ! -e "$OUTD/run/STOP" ]; then
    stopw "the kit's watch is gone"; say "the kit's watch is gone: STOP written"
  fi
  sleep 1
done
wait "$RS"; rc=$?
if [ ! -e "$OUTD/run/SESSION_DONE" ]; then   # E192's fix 1: run_session.sh exited before its EXIT trap wrote it
  printf '{"by": "session_e197", "why": "run_session.sh exited (rc %s) before its own end marker: written by the wrapper so the watch ends", "t_ms": %s}\n' \
    "$rc" "$(date +%s%3N)" > "$OUTD/run/SESSION_DONE"
  say "run_session.sh exited (rc $rc) before its own end marker (its EXIT trap writes SESSION_DONE): the wrapper wrote run/SESSION_DONE"
fi
trap - TERM INT HUP
wait "$WATCH" 2>/dev/null
END=$(date +%s)
say "run_session.sh rc $rc; its log's last lines: $(tail -n 2 "$OUTD/run/session.log" 2>/dev/null | tr '\n' ' ' | cut -c1-300)"
python3 -I -B "$KIT/check_e197.py" summary "$OUTD/run" --plan "$PLAN" --watch "$OUTD/watch.jsonl" > "$OUTD/summary.txt" 2>&1
nodevtxt=""
[ -e "$OUTD/run/telemetry.jsonl" ] || [ -e "$OUTD/run/runs.jsonl" ] || [ -e "$OUTD/run/marks.jsonl" ] || nodevtxt=" (no device opened by the session)"
while IFS= read -r ln; do
  case "$ln" in "GATE-STOP: "*) say "$ln$nodevtxt" ;; *) say "$ln" ;; esac
done < "$OUTD/summary.txt"
nl=0; [ -f "$OUTD/run/runs.jsonl" ] && nl=$(wc -l < "$OUTD/run/runs.jsonl"); nl=${nl:-0}
r=$rc
case "$rc" in
  0|2|3|75) ;;
  4|5|6|7|8) [ -e "$OUTD/run/STOP" ] || { say "the trains ended without a registered stop: run_session.sh rc $rc and no STOP written; nothing is killed; a dated note decides whether its trains are reduced"; r=9; } ;;
  *) if [ "$rc" -ge 128 ] && [ -e "$OUTD/run/STOP" ]; then :; else
       say "the trains ended without a registered stop: run_session.sh rc $rc, no stop recorded (a crash); nothing is killed; a dated note decides whether its trains are reduced"; r=9
     fi ;;
esac
say "launches recorded $nl; card time $((END - FIRST)) s from the first card command (cap $CAP s)"
say "session end (T0 $T0)"
finish_files "$r"
exit "$r"
