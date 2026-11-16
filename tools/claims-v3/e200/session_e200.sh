#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): THE SITTING'S WRAPPER on aifoundry2, run on aifoundry2 itself. Step 9
# (rb/s11_session_e200.sh) starts it detached (setsid nohup) after fwgate's guard, THE REST RULE, THE P2 COUNT, today's dry pass, today's
# build and step 7's reads (the sitting's first card command); step 8 (rb/s10_dry_e200.sh) runs it with --dry. It is E197's wrapper
# (tools/claims-v3/e197/session_e197.sh, unchanged beside it) ported to this card (E200.md 2-4 and 19). It runs E197'S REFERENCE SESSION AS
# REGISTERED (E197.md 5; E200.md 2): E197's proposal/src/run_session.sh, proposal/src/stopwatch.py and proposal/src/trains.tsv at E197's
# registration's sha256, with E200'S RUNNER in place of src/run_trains.py: E197's lab runner (lab/run_trains.py, departure D1: `timeout
# 10`, never a KILL) with E200's departure W1 applied (lab/run_trains-e200-W1.diff: --window 320000000, two lines), made here by `patch`
# into the sitting's ref/ and checked at E200's runner sha256 8774027b... (E200.md 4), all four copied into the sitting's directory
# (run_session.sh runs the runner and the stopwatch from its own folder), driven with the box's tools, and adds only what E200.md 19 asks of
# the kit, each before the session or through the registered stop file (OUT/STOP), never by editing, killing or re-ordering:
#   - before anything opens a card node (exit 2, "no device opened by the session"): the box tree's layout (E200's root
#     build/claims-v3/aifoundry2/e200); the host's name is aifoundry2; USER is the login; harness-e200.json at the sha256 the launch
#     passes and every file of it at its pin (E197's registration's 35 among them); E197's registration list at its sha256; the host, E200's
#     guard and the box's reader present, the reader at its pin (77a46171...), the host the one today's build recorded; dmcmd_audit_v2 GO
#     (preflight_e200.sh); ONE CARD'S NODES ONLY (exactly /dev/et0_ops and /dev/et0_mgmt, by name: E197.md 3); ref/'s three E197 files at
#     E197's registration's sha256 and E200's runner at its sha256; step 7's folder of this sitting (E200_FIRSTDIR,
#     build/e200/first-s<n>-<first card command>: the config read's stdout and stderr, and fwgate's EQUAL records of this boot when the
#     look read NEEDS-READ), copied into first/, with the firmware identity the launch passed (E200_FWGATE: "read", every record EQUAL, or
#     "continuity", no read); the sitting's first card command today and at most 120 s ago (FIRST_MAX), and its cap before the window's
#     last end;
#   - THE FIRST CARD COMMAND is not this script's: step 7's first command to the card (fwgate's one firmware read when the look read
#     NEEDS-READ, else the config read through E200's guard) comes before this session's holder checks; step 7's wrapper stamps it and step
#     9 passes it (E200_FIRST). The cap (sitting 1 full 3,000 s, short 2,400 s; sitting 2 2,100 s; E197.md 10, E200.md 10) counts from it;
#   - the free check (et-who --check exit 0, no other user's device process, a probe of the existing card lock: exit 3, "no device opened
#     by the session"), re-read up to 3 times 2 s apart while every holder line is a reader of ours on /dev/et0_mgmt (our live collector's
#     `ettelem temp` holds the node for a moment once a second while nothing holds the card: E194's holder re-read);
#   - THE DIE GATE (E200.md 9): the shires' mean (minshire[0]) read through E200's guard (`sample --seconds 1 --every-ms 200`, under
#     timeout 10, the card lock held for the read) until a read's every sample reads 57 C or less, every 20 s for up to 10 minutes (counted
#     in the card time and the cap); else GATE-STOP (the die gate), no train, exit 12;
#   - then the reference session with CAP_S = the cap - 60 s - (now - the first card command), so that its deadline (its sampler's start +
#     CAP_S - 60 s) falls at the first card command + the cap - 120 s, never past the window's last end - 180 s (E197's kit section 4), and
#     ETTELEM = E200's guard (the plain sampler, E197.md 4: `sample --seconds --every-ms 100` only);
#   - THE KIT'S WATCH beside it (watch_e200.py: E197's live stops (65 W, 70 C) with aifoundry2's own lines beside them (85 W on 3 samples in
#     a row; minshire[0] or the latch minshire[2] at or above 80 C), its clock stop replaced by C3 (three train processes in a row off
#     800 MHz after their first 1.5 s), the kit's smoke check with the smoke's clock (C3), the end-stop at the cap - 30 s, and the hang watch
#     for a device process that outlives its timeout's TERM: a STOP and a report, never a kill); a watch that dies while the session runs is
#     a stop (the wrapper writes STOP); a signal to the wrapper writes STOP and waits for the session's own end;
#   - when run_session.sh has exited without its own end marker, the wrapper writes OUT/SESSION_DONE itself (E192's fix 1);
#   - THE CONFIGURATION AT THE SITTING'S END (E200.md 3: read at each sitting's start and end, the end reading reported): once the session
#     has ended, when its sampler ran, no host was seen hung and et-who --check reads the card free, one `ettelem config` through E200's
#     guard under the card lock with timeout 10 (config-end.out, config-end.err), reported, never a gate; else "not made" and why;
#   - the kits' session log build/e200/T<T0>/session.log ("session start", "session end (T0 <T0>)": every rest rule of ours reads it), the
#     end read by check_e200.py summary (the smoke gate, the kit's smoke check, the blocks, the stop and whether it names the card,
#     SITTING-RESULT, and GATE-STOP when no block of trains.tsv began), a crash written apart from a registered stop ("the trains ended without
#     a registered stop": exit 9), then MANIFEST.sha256 last and wrapper.rc after it.
# The box layout: E200's root R = <box tree>/build/claims-v3/aifoundry2/e200 holds the synced files at their repository paths and the build
# (R/build/regfile, R/build/regfile-built.txt); the sitting writes build/e200/T<T0>/ in the box tree (the reference session's OUT is its run/
# directory, its four files in ref/). The box's tools: the reader build/ettelem-hpl/ettelem behind E200's guard (the audit's reviewed
# variant for build/ettelem-hpl), et-who (/usr/local/bin), coreutils' timeout, util-linux's flock, GNU patch.
#   E200_T0=<epoch> E200_SIT=1|2 E200_PLAN=full|short|ext E200_FIRST=<epoch> E200_LAST_END_EPOCH=<epoch> E200_HARNESS_SHA256=<sha256> \
#     E200_FIRSTDIR=build/e200/first-s<n>-<first> E200_FWGATE=read|continuity bash <R>/tools/claims-v3/e200/session_e200.sh
#   E200_T0=<epoch> E200_SIT=1|2 E200_PLAN=full|short|ext E200_HARNESS_SHA256=<sha256> bash <R>/tools/claims-v3/e200/session_e200.sh --dry
# Desk-test variables, read ONLY with E200_DESKTEST=1 (the card day never sets it; the session start line names it when set): E200_CAP_S,
# E200_READER_SHA256 (the stand-in reader's), E200_DIE_MAX_S, E200_DIE_POLL_S.
# Exit codes: 0 done (every block, or the runner's deadline skipped or cut trains); 2 a refusal before anything (no device opened by the
# session); 3 the card not free (no device opened by the session) or a holder between blocks; 9 the trains ended without a registered stop
# (a crash: nothing is killed; a dated note decides); 12 the die gate held the sitting off (no train); else the reference session's own:
# 75 the card lock busy, 7 the smoke gate, 8 a stop by the stop file (watch, stopwatch, wrapper, by hand), 4 telemetry stale, 5 failing
# processes, 6 hot, 128+n a signal.
# SPDX-License-Identifier: Apache-2.0
set -u
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)
TREE=$(cd "$R/../../../.." && pwd -P)
cd "$TREE" || exit 2
RR=${R#"$TREE"/}
DRYRUN=; [ "${1:-}" = --dry ] && DRYRUN=1
unset DRY   # the reference session reads DRY from its environment: only the dry path below sets it, for that one call
T0=${E200_T0:-}; SIT=${E200_SIT:-}; PLAN=${E200_PLAN:-}
case "$T0" in ''|*[!0-9]*) echo "E200_T0 must be the launch's epoch seconds"; exit 2 ;; esac
case "$SIT:$PLAN" in 1:full|1:short|2:ext) ;; *) echo "E200_SIT:E200_PLAN must be 1:full, 1:short or 2:ext, not '$SIT:$PLAN'"; exit 2 ;; esac
[ "$RR" = build/claims-v3/aifoundry2/e200 ] || { echo "this wrapper must run from E200's root build/claims-v3/aifoundry2/e200 in the box tree, not '$RR'"; exit 2; }
OUTD=build/e200/T$T0; [ -n "$DRYRUN" ] && OUTD=$OUTD-dry
[ -e "$OUTD" ] && { echo "$OUTD exists: one session a T0"; exit 2; }
mkdir -p "$OUTD/ref" "$OUTD/run" || exit 2
LOG=$OUTD/session.log
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %Z') ${DRYRUN:+DRY }$*" | tee -a "$LOG"; }
KIT=$RR/tools/claims-v3/e200
K197=$RR/tools/claims-v3/e197
K194=$RR/tools/claims-v3/e194
SRC=$K197/proposal/src
H=$RR/build/regfile/host/regfile_host
GUARD=$RR/tools/claims-v3/e200/ettelem_guard_e200.sh
SBIN=build/ettelem-hpl/ettelem
SBIN_SHA=77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5     # E194's pin (e194_common.READER_SHA256): this card's reader
BUILT=$RR/build/regfile-built.txt
REG_LIST=$K197/SHA256SUMS-e197-registration
REG_LIST_SHA=992a35e577617489d571f1af6e37f78b08e967d82e6529261ebf7db19e05ad95   # E197's registration list (35 entries)
W1=$KIT/lab/run_trains-e200-W1.diff
W1_SHA=24224f12eea201614358a40272525825e81dd1d9376912b6d3c65ee36f203349         # E200.md 4: W1's diff
RUNNER_SHA=8774027b4bba78c6b532988c46446987f75eec6d32985bd7b400cbb963eb5a41     # E200.md 4: E197's runner with W1 applied
LOCK=/run/lock/etsoc-shire0.lock
case "$PLAN" in full) CAP=3000 ;; short) CAP=2400 ;; ext) CAP=2100 ;; esac
GAP=30; DLM=120; FIRST_MAX=120   # E197's kit's bounds (its fix-e197): step 9 the same (E200_FIRST_MAX_S)
DIE_C=57; DIE_MAX=600; DIE_POLL=20   # THE DIE GATE (E200.md 9): 57 C, up to 10 minutes
DESK=
if [ "${E200_DESKTEST:-}" = 1 ]; then
  DESK=" DESKTEST"; CAP=${E200_CAP_S:-$CAP}; SBIN_SHA=${E200_READER_SHA256:-$SBIN_SHA}
  DIE_MAX=${E200_DIE_MAX_S:-$DIE_MAX}; DIE_POLL=${E200_DIE_POLL_S:-$DIE_POLL}
fi
finish_files() {  # the manifest last, then wrapper.rc
  ( cd "$OUTD" && find . -type f ! -name 'MANIFEST.sha256*' ! -name wrapper.rc | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$OUTD/MANIFEST.sha256.tmp"
  mv "$OUTD/MANIFEST.sha256.tmp" "$OUTD/MANIFEST.sha256"
  echo "$1" > "$OUTD/wrapper.rc"
}
nodev() { say "GATE-STOP: refused: $* (no device opened by the session)"; say "session end (T0 $T0)"; finish_files 2; exit 2; }
notfree() { say "GATE-STOP: the card is not free: $* (no device opened by the session)"; say "session end (T0 $T0)"; finish_files 3; exit 3; }
say "session start (T0 $T0 = $(date -d @"$T0" '+%H:%M:%S %Z' 2>/dev/null); E200 sitting $SIT, plan $PLAN; E197's reference session with E200's runner (E197's D1 with W1), kit-e200$DESK${DRYRUN:+; DRY})"
# ---- refusals before anything opens a card node (both paths) -----------------------------------------------------------------
if [ "${E200_DESKTEST:-}" != 1 ]; then
  for v in E200_CAP_S E200_READER_SHA256 E200_DIE_MAX_S E200_DIE_POLL_S; do
    [ -z "${!v:-}" ] || nodev "$v is a desk-test variable, read only with E200_DESKTEST=1 (the card day never sets it)"
  done
fi
hn=$(hostname 2>/dev/null); pyhn=$(python3 -I -B -c 'import socket; print(socket.gethostname())' 2>/dev/null)
[ "$hn" = aifoundry2 ] && [ "$pyhn" = aifoundry2 ] || nodev "this host is '$hn' (Python reads '$pyhn'), not aifoundry2 (E200.md 3: aifoundry2 card 0)"
[ -n "${USER:-}" ] && [ "$USER" = "$(id -un)" ] || nodev "USER is not this login (E183 kit note 6's carried rule)"
HJ=$KIT/harness-e200.json
[ -n "${E200_HARNESS_SHA256:-}" ] && [ "$(sha256sum "$HJ" 2>/dev/null | cut -d' ' -f1)" = "$E200_HARNESS_SHA256" ] ||
  nodev "harness-e200.json is not at the sha256 the launch passed (E200_HARNESS_SHA256)"
python3 -I -B "$KIT/harness_e200.py" --box --root "$RR" > "$OUTD/harness.txt" 2>&1 || nodev "the harness: $(tail -n 1 "$OUTD/harness.txt" | cut -c1-200)"
[ "$(sha256sum "$REG_LIST" 2>/dev/null | cut -d' ' -f1)" = "$REG_LIST_SHA" ] || nodev "E197's registration list is not at its sha256 ${REG_LIST_SHA:0:12}"
for f in "$H" "$GUARD" "$SBIN"; do [ -x "$f" ] || nodev "no executable $f"; done
[ "$(sha256sum "$SBIN" | cut -d' ' -f1)" = "$SBIN_SHA" ] || nodev "the reader $SBIN is not at its pin ${SBIN_SHA:0:12} (this card's sampler)"
[ -s "$BUILT" ] && grep -q '^REGFILE-BUILT ' "$BUILT" || nodev "no build record $BUILT (step 6)"
[ "$(TZ=America/Los_Angeles date -r "$BUILT" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] || nodev "the build record was not written today (Pacific)"
[ "$(awk '$1 == "host" {print $2}' "$BUILT")" = "$(sha256sum "$H" | cut -d' ' -f1)" ] || nodev "the host is not the one today's build recorded"
bash "$KIT/preflight_e200.sh" > "$OUTD/preflight.txt" 2>&1; prc=$?
[ "$prc" -eq 0 ] && head -n 1 "$OUTD/preflight.txt" | grep -q '^dmcmd_audit: GO' || nodev "the device-command audit (v2) is not GO (rc $prc)"
ops=""; for d in /dev/et*_ops; do [ -e "$d" ] && ops="$ops $d"; done
mgs=""; for d in /dev/et*_mgmt; do [ -e "$d" ] && mgs="$mgs $d"; done
[ "$ops" = " /dev/et0_ops" ] && [ "$mgs" = " /dev/et0_mgmt" ] ||
  nodev "the card nodes here are '${ops# }' and '${mgs# }', not exactly /dev/et0_ops and /dev/et0_mgmt: one card only, counted before anything opens a node (E197.md 3)"
for f in run_session.sh stopwatch.py trains.tsv; do cp "$SRC/$f" "$OUTD/ref/$f" || nodev "cannot copy $f"; done
for p in proposal/src/run_session.sh proposal/src/stopwatch.py proposal/src/trains.tsv lab/run_trains.py; do
  w=$(awk -v p="tools/claims-v3/e197/$p" '$2 == p {print $1}' "$REG_LIST")
  [ -n "$w" ] && [ "$(sha256sum "$K197/$p" | cut -d' ' -f1)" = "$w" ] || nodev "E197's $p is not at its registration's sha256"
  case "$p" in lab/*) continue ;; esac
  [ "$(sha256sum "$OUTD/ref/${p##*/}" | cut -d' ' -f1)" = "$w" ] || nodev "the session's copy of $p is not at E197's registration's sha256"
done
[ "$(sha256sum "$W1" 2>/dev/null | cut -d' ' -f1)" = "$W1_SHA" ] || nodev "E200's W1 diff is not at its sha256 ${W1_SHA:0:12} (E200.md 4)"
patch -s --no-backup-if-mismatch -r - -o "$OUTD/ref/run_trains.py" "$K197/lab/run_trains.py" < "$W1" > "$OUTD/ref-patch.txt" 2>&1 ||
  nodev "W1 did not apply to E197's lab runner (ref-patch.txt)"
[ "$(sha256sum "$OUTD/ref/run_trains.py" | cut -d' ' -f1)" = "$RUNNER_SHA" ] || nodev "the runner made from E197's lab runner and W1 is not at E200's runner sha256 ${RUNNER_SHA:0:12} (E200.md 4)"
[ "$(ls -A "$OUTD/ref" | LC_ALL=C sort | tr '\n' ' ')" = "run_session.sh run_trains.py stopwatch.py trains.tsv " ] || nodev "ref/ holds files other than the four"
say "checked: host aifoundry2; USER the login; harness-e200.json at the launch's sha256, $(tail -n 1 "$OUTD/harness.txt" | cut -c1-80); E197's registration list ${REG_LIST_SHA:0:12}; the host (today's build), E200's guard, the reader at ${SBIN_SHA:0:12}; dmcmd_audit_v2 GO; one card's nodes (/dev/et0_ops, /dev/et0_mgmt); ref/: run_session.sh, stopwatch.py, trains.tsv (E197's proposal/src, at its registration's sha256) and run_trains.py (E197's lab runner with W1, at ${RUNNER_SHA:0:12})"
export H GAP LOCK
export ETTELEM=$RR/tools/claims-v3/e200/ettelem_guard_e200.sh   # = $GUARD, written out so that dmcmd_audit resolves run_session.sh's "$ETTELEM" to the guard
unset ET_DEVICES V3_DEVICE SAMPLER SAMPLER_S PVT_SAMPLE CAP_S
# ---- the dry path: the reference session's DRY mode, every device call listed, nothing opened --------------------------------------
if [ -n "$DRYRUN" ]; then
  say "would run: the firmware identity as the launch passes it (fwgate's EQUAL record of this sitting, or continuity); the free check (et-who --check, re-read for a reader of ours on the management node; other users' device processes; a probe of $LOCK, read-only, never created)"
  say "would run: THE DIE GATE (minshire[0] at or below $DIE_C C, every $DIE_POLL s for up to $DIE_MAX s, through E200's guard); the reference session with CAP_S = the cap ($CAP s) - 60 s - (now - the first card command, step 7's), ETTELEM = E200's guard; the kit's watch beside it (its live stops with aifoundry2's lines, C3, its smoke check with the smoke's clock, the end-stop at the cap - 30 s, the hang watch)"
  DRY=1 bash "$OUTD/ref/run_session.sh" "$OUTD/run" "$PLAN" > "$OUTD/run_session.out" 2>&1; rc=$?
  python3 -I -B "$KIT/check_e200.py" drycmp "$OUTD/run_session.out" "$K197/desk/dry-e197-$PLAN.txt" --host "$H" --out "$OUTD/run" > "$OUTD/drycmp.txt" 2>&1; dc=$?
  say "the reference session's DRY mode with E200's runner: rc $rc; $(head -n 1 "$OUTD/drycmp.txt" | cut -c1-220)"
  say "session end (T0 $T0)"
  r=$rc; [ "$dc" -ne 0 ] && r=16
  finish_files "$r"; exit "$r"
fi
# ---- the real path -----------------------------------------------------------------------------------------------------------
FIRST=${E200_FIRST:-}
case "$FIRST" in ''|*[!0-9]*) nodev "no E200_FIRST (the sitting's first card command, step 7's, epoch seconds)" ;; esac
NOW=$(date +%s)
[ "$FIRST" -le "$NOW" ] || nodev "the first card command $FIRST lies in the future"
[ "$(TZ=America/Los_Angeles date -d @"$FIRST" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] || nodev "the first card command was not today (Pacific)"
[ $((NOW - FIRST)) -le "$FIRST_MAX" ] || nodev "the first card command was $((NOW - FIRST)) s ago, more than $FIRST_MAX s: its cap counts from it (run step 9 right after step 7)"
LE=${E200_LAST_END_EPOCH:-}
case "$LE" in ''|*[!0-9]*) nodev "no E200_LAST_END_EPOCH (the window's last end)" ;; esac
[ $((FIRST + CAP)) -le "$LE" ] || nodev "the cap ($CAP s from the first card command) passes the window's last end"
[ -e "$LOCK" ] || nodev "no card lock file $LOCK (the host makes it at boot; never created here)"
FD=${E200_FIRSTDIR:-}
[ "$FD" = "build/e200/first-s$SIT-$FIRST" ] || nodev "E200_FIRSTDIR '$FD' is not step 7's folder of this sitting (build/e200/first-s$SIT-$FIRST)"
[ -d "$FD" ] && [ -s "$FD/config.out" ] || nodev "step 7's folder $FD holds no config read (config.out): step 7 first"
fv=$(python3 -I -B - "$FD" <<'PY'
import glob, json, os, sys
d = sys.argv[1]
recs = []
for p in sorted(glob.glob(os.path.join(d, "fwgate-aifoundry2-c0-*.json"))):
    try:
        j = json.load(open(p))
    except (OSError, ValueError):
        print("UNREADABLE " + os.path.basename(p)); sys.exit(0)
    recs.append((j.get("read_epoch") or 0, j.get("verdict"), os.path.basename(p), j.get("boot_epoch")))
if not recs:
    print("NONE"); sys.exit(0)
bad = [r for r in recs if r[1] != "EQUAL"]
if bad:
    print("NOT-EQUAL " + " ".join("%s:%s" % (r[2], r[1]) for r in bad)); sys.exit(0)
r = max(recs)
print("EQUAL %s %s" % (r[2], r[3]))
PY
)
case "${E200_FWGATE:-}" in
  continuity)
    [ "$fv" = NONE ] || nodev "E200_FWGATE reads continuity but step 7's folder holds fwgate's records ($fv)"
    fwtxt="continuity: fwgate's look read CONTINUITY (a committed record after this boot): no read on this sitting" ;;
  read)
    case "$fv" in "EQUAL "*) ;; *) nodev "E200_FWGATE reads read but step 7's folder $FD does not hold fwgate's records all EQUAL, one at least ($fv): the firmware identity is not shown (fwgate's own guard is step 9's)" ;; esac
    bt=$(awk '/^btime / {print $2}' /proc/stat 2>/dev/null)
    [ -n "$bt" ] && [ "$(echo "$fv" | cut -d' ' -f3)" = "$bt" ] || nodev "fwgate's record in $FD was read on another boot (its boot $(echo "$fv" | cut -d' ' -f3), this boot ${bt:-unread})"
    fwtxt="fwgate's read of this sitting: $(echo "$fv" | cut -d' ' -f1-2) (on this boot)" ;;
  *) nodev "no E200_FWGATE (read or continuity): step 9 passes the firmware identity step 7 and fwgate's guard read" ;;
esac
mkdir -p "$OUTD/first" && cp -a "$FD/." "$OUTD/first/" || nodev "cannot copy step 7's folder $FD"
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner.Worker$'
i=0
while :; do   # the free check, re-read while every holder line is a reader of ours on the management node (our live collector)
  i=$((i + 1))
  o=$(timeout 30 et-who --check 2>&1); wrc=$?
  p=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
  [ "$p" -eq 0 ] || notfree "$p device process(es) of another user"
  [ "$wrc" -eq 0 ] && break
  [ "$wrc" -eq 1 ] || notfree "et-who --check exit $wrc"
  hl=$(printf '%s\n' "$o" | grep -E '^(/dev/et|lock:)')
  nh=$(printf '%s\n' "$hl" | grep -c .)
  ours=$(printf '%s\n' "$hl" | awk -v me="$(id -un)" '$1 == "/dev/et0_mgmt" && $2 == me {n++} END {print n+0}')
  if [ "$nh" -gt 0 ] && [ "$ours" -eq "$nh" ] && [ "$i" -lt 4 ]; then
    say "the free check, read $i: $nh holder line(s), every one a reader of ours on /dev/et0_mgmt (our live collector's read in flight): read again in 2 s"
    sleep 2; continue
  fi
  notfree "et-who --check exit $wrc ($nh holder lines, $ours of them a reader of ours on /dev/et0_mgmt; read $i)"
done
exec 9< "$LOCK"; flock -n -E 75 9; lrc=$?; exec 9<&-
[ "$lrc" -eq 0 ] || notfree "the card lock is held (probe exit $lrc)"
echo "$FIRST" > "$OUTD/first-card-command.txt"
say "the firmware identity: $fwtxt; step 7's folder copied into first/ ($(ls "$OUTD/first" | wc -l | tr -d ' ') files)"
# ---- THE DIE GATE (E200.md 9): after the first card command, before the session ---------------------------------------------------
DS=$(date +%s); k=0; dok=0
while :; do
  k=$((k + 1))
  dout=$(flock -n /run/lock/etsoc-shire0.lock timeout 10 bash "$GUARD" sample --seconds 1 --every-ms 200 < /dev/null 2> "$OUTD/diegate-$k.err"); drc=$?
  printf '%s\n' "$dout" > "$OUTD/diegate-$k.jsonl"
  dv=$(python3 -I -B - "$OUTD/diegate-$k.jsonl" "$DIE_C" <<'PY'
import json, sys
vals = []
for ln in open(sys.argv[1], errors="replace"):
    ln = ln.strip()
    if not (ln.startswith("{") and ln.endswith("}")):
        continue
    try:
        j = json.loads(ln)
        v = j["temp_c"]["minshire"][0]
    except (ValueError, KeyError, IndexError, TypeError):
        continue
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        vals.append(float(v))
lim = float(sys.argv[2])
if not vals:
    print("NONE 0 -")
else:
    print("%s %d %g" % ("OK" if max(vals) <= lim else "WARM", len(vals), max(vals)))
PY
)
  set -- $dv
  say "the die gate, read $k (rc $drc): $2 sample(s), the highest minshire[0] ${3} C: $1 (the gate: every sample at or below $DIE_C C)"
  [ "$1" = OK ] && { dok=1; break; }
  [ $(( $(date +%s) - DS + DIE_POLL )) -le "$DIE_MAX" ] || break
  sleep "$DIE_POLL"
done
if [ "$dok" -ne 1 ]; then
  say "GATE-STOP: the die gate: the shires' mean did not read $DIE_C C or less within $DIE_MAX s of reads after the first card command (E200.md 9): no sitting today, no train run"
  say "session end (T0 $T0)"; finish_files 12; exit 12
fi
NOW=$(date +%s)
CAPS=$((CAP - DLM + 60 - (NOW - FIRST)))
WCAP=$((LE - 180 + 60 - NOW)); [ "$WCAP" -lt "$CAPS" ] && CAPS=$WCAP
if [ "$CAPS" -lt 300 ]; then
  say "GATE-STOP: too little of the cap is left for a block after the die gate ($CAPS s): no train run"
  say "session end (T0 $T0)"; finish_files 12; exit 12
fi
export CAP_S=$CAPS
say "the first card command at $(date -d @"$FIRST" '+%H:%M:%S %Z') (step 7's); the die gate passed after $((NOW - DS)) s; the cap $CAP s, at $(date -d @$((FIRST + CAP)) '+%H:%M:%S %Z'); CAP_S $CAPS s, the runner's deadline at about $(date -d @$((NOW + CAPS - 60)) '+%H:%M:%S %Z') (the first card command + the cap - $DLM s); the end-stop at $(date -d @$((FIRST + CAP - 30)) '+%H:%M:%S %Z')"
python3 -I -B "$KIT/watch_e200.py" "$OUTD/run" --first "$FIRST" --cap "$CAP" --host "$H" --log-dir "$OUTD" --session-log "$LOG" > "$OUTD/watch.out" 2>&1 < /dev/null &
WATCH=$!
bash "$OUTD/ref/run_session.sh" "$OUTD/run" "$PLAN" > "$OUTD/run_session.out" 2>&1 < /dev/null &
RS=$!
stopw() {  # stopw <why>: the registered stop file, created once with O_EXCL (set -C): the first writer's reason stands
  ( set -C; printf '{"by": "session_e200", "why": "%s", "t_ms": %s, "card": false}\n' "$1" "$(date +%s%3N)" > "$OUTD/run/STOP" ) 2> /dev/null || :
}
trap 'stopw "a signal to the wrapper: the launch in flight finishes"; say "signal: STOP written; waiting for the session to end"' TERM INT HUP
say "running: run_session.sh $PLAN (pid $RS), watch_e200.py (pid $WATCH)"
while kill -0 "$RS" 2>/dev/null; do
  if ! kill -0 "$WATCH" 2>/dev/null && [ ! -e "$OUTD/run/SESSION_DONE" ] && [ ! -e "$OUTD/run/STOP" ]; then
    stopw "the kit's watch is gone"; say "the kit's watch is gone: STOP written"
  fi
  sleep 1
done
wait "$RS"; rc=$?
if [ ! -e "$OUTD/run/SESSION_DONE" ]; then   # E192's fix 1: run_session.sh exited before its EXIT trap wrote it
  printf '{"by": "session_e200", "why": "run_session.sh exited (rc %s) before its own end marker: written by the wrapper so the watch ends", "t_ms": %s}\n' \
    "$rc" "$(date +%s%3N)" > "$OUTD/run/SESSION_DONE"
  say "run_session.sh exited (rc $rc) before its own end marker (its EXIT trap writes SESSION_DONE): the wrapper wrote run/SESSION_DONE"
fi
trap - TERM INT HUP
wait "$WATCH" 2>/dev/null
END=$(date +%s)
if [ ! -e "$OUTD/run/telemetry.jsonl" ]; then
  say "the configuration at the sitting's end: not made (the session's sampler never started)"
elif grep -q 'HUNG: ' "$LOG" 2>/dev/null; then
  say "the configuration at the sitting's end: not made (a host was seen hung: nothing more is sent to the card)"
else
  co=$(timeout 30 et-who --check 2>&1); cwrc=$?
  if [ "$cwrc" -ne 0 ]; then
    say "the configuration at the sitting's end: not made (et-who --check exit $cwrc: the card is not free)"
  else
    flock -n /run/lock/etsoc-shire0.lock timeout 10 bash "$GUARD" config < /dev/null > "$OUTD/config-end.out" 2> "$OUTD/config-end.err"; crc=$?
    cl=$(python3 -I -B "$K194/e194_common.py" --config-line "$OUTD/config-end.out" 2>> "$OUTD/config-end.err")
    say "the configuration at the sitting's end (reported, never a gate): rc $crc; ${cl:-no configuration object read}"
  fi
fi
say "run_session.sh rc $rc; its log's last lines: $(tail -n 2 "$OUTD/run/session.log" 2>/dev/null | tr '\n' ' ' | cut -c1-300)"
python3 -I -B "$KIT/check_e200.py" summary "$OUTD/run" --plan "$PLAN" --watch "$OUTD/watch.jsonl" > "$OUTD/summary.txt" 2>&1
nodevtxt=""
[ -e "$OUTD/run/telemetry.jsonl" ] || [ -e "$OUTD/run/runs.jsonl" ] || [ -e "$OUTD/run/marks.jsonl" ] || nodevtxt=" (no device opened by the session's run: only step 7's and the die gate's reads came before it)"
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
