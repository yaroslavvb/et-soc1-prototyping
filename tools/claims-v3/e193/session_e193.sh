#!/usr/bin/env bash
# E193 (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum; fixed in place before the land by lane fix-e193, the same evening):
# THE SESSION'S WRAPPER on aifoundry3, one sitting a call. Step 9
# (rb/s11_a3_session_e193.sh) starts it detached (setsid nohup) after k6's guard, THE REST RULE, today's dry pass and today's build;
# step 8 (rb/s10_a3_dry_e193.sh) runs it with DRY=1. It drives THE PROPOSAL'S RUNNER AS COMMITTED (proposal/src/run_x04.py at the
# registration's sha256, unchanged, every option at its default but those E193.md names) with the box's own tools:
#   - the holder check is the box's `et-who --check` (the runner's default --holder-check), the card lock /run/lock/etsoc-shire0.lock;
#   - the sampler is the box's build/ettelem/ettelem (the audit table's reviewed variant 'ettelem', every aifoundry3 kit's), started BY
#     THE RUNNER (--sampler) through E128's guard (tools/claims-v3/e128/ettelem_guard.sh, synced at its sha256), which refuses every word
#     but `config` and `sample --seconds N --every-ms N` and execs the reader, so the runner's one exempt holder (the sampler, by its
#     process id) is the process that holds the management node; one sampler a runner call, its file started for that call;
#   - the host is x04clock_host built on the box today from proposal/src (step 6's build, X04-BUILT, its sha256 recorded and checked here).
# What it adds, each before the runner or through the runner's own registered options, never by editing the runner (E193.md 17.2):
#   1. before anything opens a card node: harness-e193.json at the sha256 the launch passes and every file of it at its pin (the
#      registration's 29 files among them), dmcmd_audit GO (preflight_e193.sh), the binaries present and the ones today's build recorded;
#   2. THE FIRST CARD COMMAND, from which the sitting's cap counts (E193.md 6), its time stamped AS IT STARTS (before the two ps rules
#      and the holder check, so the cap counts from the holder check itself): the holder check (et-who --check exit 0), no other user's
#      device process and none of ours (lib.sh's two ps rules); then THE ONE OPS NODE: exactly /dev/et0_ops on the host (the runner's
#      and the host's one-card rule, E193.md 3), counted before anything opens a card node, else no sitting (no device opened); then the
#      start config read through the guard under the card lock (ET_DEVICES=0, the card the runner's --device 0 names; timeout 10):
#      TDP 0 W, 65 C, minion 600 MHz as found, else no sitting (k6's s09 test, the same strings);
#   3. the runner's --deadline = the first card command + the cap (sitting A 60 card-minutes, B 50; E193.md 6) - 120 s, and never past
#      the window's last end - 180 s: no run starts after it, and the in-flight run, the runner's clean-up and the closing read fit before
#      the cap;
#   4. THE SMOKE: the runner with --smoke --blocks S,D,W,T,C (E193.md 5: all five named arms, 10 device processes), then THE KIT'S SMOKE
#      GATE (check_e193.py smoke: every device process exit 0, every launch ok, the ten calls as registered, the train whole; its
#      telemetry at 600 MHz in every sample and below every stop); a failed gate ends the sitting with no main run;
#   5. THE MAIN RUN: the runner with --blocks S,D,W,T (sitting A) or C (B), 9 passes as committed; a registered stop ends it and the
#      passes done stand; a runner that exits non-zero with NO stop recorded (a crash: a traceback, a kill from outside) is written
#      "main run ended without a registered stop", never as a registered stop: E193.md 11 has no row for it, so it is reported,
#      nothing is killed, and a dated note decides whether its passes are reduced (fix-e193, verify-e193's finding 5);
#   6. the closing config read (reported; nothing is set), also after a gate stop that followed a good start read; "session end (T0
#      <T0>)" in the kits' session-log form (every rest rule of ours reads build/e193/T<T0>/session.log), MANIFEST.sha256 last (the
#      collection's exact copy-back reads it), session.rc after it.
# Exit: 0 the main run ended rc 0 (every pass); 1 the main run stopped (a registered stop: the passes done stand); 4 the main run ended
# without a registered stop (a crash: reported; a dated note decides); 3 a gate stop (no main run); 2 refused before anything (no
# device opened).
#   E193_T0=<epoch> E193_LAST_END_EPOCH=<epoch> E193_HARNESS_SHA256=<sha256> bash <R>/tools/claims-v3/e193/session_e193.sh A|B
#   DRY=1 E193_T0=<epoch> E193_HARNESS_SHA256=<sha256> bash <R>/tools/claims-v3/e193/session_e193.sh A|B      (opens nothing)
# DRY=1 is the dry pass: every device call listed (the runner's --dry), the holder check, the count of ops nodes, the config reads and the
# smoke gate printed and skipped; its directory is build/e193/T<T0>-dry and every line of its log begins "DRY " (the rest rules skip it). There is no desk-test
# variable: the desk tests drive this file's real path exactly as the launch does (the deadline's clip by a short window's last end
# stands in for a short cap).
# SPDX-License-Identifier: Apache-2.0
set -u
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)
TREE=$(cd "$R/../../../.." && pwd -P)
cd "$TREE" || exit 2
RR=${R#"$TREE"/}
SIT=${1:-}
case "$SIT" in
  A) BLOCKS=S,D,W,T; CAP_S=3600 ;;
  B) BLOCKS=C; CAP_S=3000 ;;
  *) echo "usage: session_e193.sh A|B (sitting A: blocks S,D,W,T, cap 60 card-minutes; sitting B: block C, cap 50)"; exit 2 ;;
esac
DRYF=
case "${DRY-}" in "") ;; 1) DRYF=1 ;; *) echo "DRY must be 1 or unset (it is '${DRY}')"; exit 2 ;; esac
T0=${E193_T0:-}
case "$T0" in ''|*[!0-9]*) echo "E193_T0 must be the launch's epoch seconds"; exit 2 ;; esac
LAST_END=${E193_LAST_END_EPOCH:-}
if [ -z "$DRYF" ]; then
  case "$LAST_END" in ''|*[!0-9]*) echo "E193_LAST_END_EPOCH must be the window's last end, epoch seconds"; exit 2 ;; esac
fi
SD=build/e193/T$T0; [ -n "$DRYF" ] && SD=$SD-dry
[ -e "$SD" ] && { echo "$SD exists: one session a T0"; exit 2; }
mkdir -p "$SD" || exit 2
LOG=$SD/session.log
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %Z') ${DRYF:+DRY }$*" >> "$LOG"; }
KIT=$RR/tools/claims-v3/e193
SRC=$KIT/proposal/src
RUNNER=$SRC/run_x04.py
H=$RR/build/x04clock/host/x04clock_host
K=$RR/build/x04clock/kernel/x04clock.elf
BUILT=$RR/build/x04clock-built.txt
G=$RR/tools/claims-v3/e128/ettelem_guard.sh
SAMPLER=build/ettelem/ettelem
LOCK=/run/lock/etsoc-shire0.lock
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$'   # lib.sh's DEV_COMM
OTHER_COMM="$DEV_COMM|^Runner.Worker$"                                                # lib.sh's OTHER_COMM
unset ET_DEVICES V3_DEVICE V3_DRY
export LC_ALL=C

finish() {  # finish <exit status>: "session end", the manifest last, session.rc after it
  say "session end (T0 $T0)"
  ( cd "$SD" && find . -type f ! -name MANIFEST.sha256 ! -name session.rc | sed 's#^\./##' | LC_ALL=C sort |
      while IFS= read -r f; do sha256sum "$f"; done > MANIFEST.sha256 )
  echo "$1" > "$SD/session.rc"
  exit "$1"
}
CFG_OK=
nodev() { say "GATE-STOP: $* (no device opened)"; finish 3; }
gate() { say "GATE-STOP: $*: no main run"; [ -n "$CFG_OK" ] && closing; finish 3; }
config_read() {  # config_read <file>: card 0's static config through E128's guard, under the card lock, timeout 10 (READ only)
  ET_DEVICES=0 flock -n "$LOCK" timeout 10 "$G" config < /dev/null 2> "$1.err" | grep '^{' | tail -n 1 > "$1"
}
closing() {  # the closing config read (reported, never a gate): after the main run, or after a gate stop that followed a good start read
  if [ -n "$DRYF" ]; then
    say "ET_DEVICES=0 flock -n $LOCK timeout 10 $G config (the closing config read, reported)"
    return 0
  fi
  config_read "$SD/config-end.json"
  c2=$(cat "$SD/config-end.json")
  if [ -z "$c2" ]; then say "closing config read: none came back ($(head -c 160 "$SD/config-end.json.err"))"
  elif echo "$c2" | grep -q '"tdp_w":0,' && echo "$c2" | grep -q '"temp_threshold_c":65,' && echo "$c2" | grep -q '"minion_mhz":600,'; then
    say "closing config read: TDP 0 W, 65 C, minion 600 MHz, as at the start (config-end.json)"
  else
    say "closing config read: NOT as at the start (reported; nothing was set by this session): $(echo "$c2" | cut -c1-240)"
  fi
}

say "session start (T0 $T0 = $(date -d @"$T0" '+%H:%M:%S %Z' 2>/dev/null); E193 sitting $SIT, blocks $BLOCKS, cap $((CAP_S / 60)) card-minutes; the proposal's runner as committed, driven with the box's tools; kit-e193${DRYF:+; DRY})"
say "box $(hostname), tree $(basename "$TREE"), root $RR; $(python3 --version 2>&1)"
[ "$(hostname)" = aifoundry3 ] || nodev "this is $(hostname), not aifoundry3: E193 runs on aifoundry3 card 0 only (E193.md 3)"

# ---- 1. before anything opens a card node: the harness at its pin, every file of it, the preflight, the binaries
hj=$(sha256sum "$KIT/harness-e193.json" 2>/dev/null | cut -d' ' -f1)
[ -n "${E193_HARNESS_SHA256:-}" ] && [ "$hj" = "${E193_HARNESS_SHA256}" ] ||
  nodev "harness-e193.json reads ${hj:-nothing}, not the launch's ${E193_HARNESS_SHA256:-<unset>}"
python3 -I -B "$KIT/harness_e193.py" --box --root "$RR" > "$SD/harness.txt" 2>&1
grep -q '^HARNESS OK: ' "$SD/harness.txt" || nodev "the harness check failed: $(tail -n 1 "$SD/harness.txt" | cut -c1-200)"
say "$(grep -m1 '^HARNESS OK: ' "$SD/harness.txt")"
bash "$KIT/preflight_e193.sh" > "$SD/preflight.txt" 2>&1
grep -q '^dmcmd_audit: GO' "$SD/preflight.txt" || nodev "the preflight is not GO: $(head -n 1 "$SD/preflight.txt" | cut -c1-200)"
say "preflight: $(head -n 1 "$SD/preflight.txt" | cut -c1-200)"
for f in "$H" "$G" "$SAMPLER"; do [ -x "$f" ] || nodev "$f is not an executable file"; done
[ -f "$K" ] || nodev "$K is missing"
[ -f "$BUILT" ] && grep -q '^X04-BUILT ' "$BUILT" || nodev "no build record ($BUILT): run step 6 first"
hh=$(sha256sum "$H" | cut -d' ' -f1); kh=$(sha256sum "$K" | cut -d' ' -f1); sh=$(sha256sum "$SAMPLER" | cut -d' ' -f1)
grep -q "^host $hh\$" "$BUILT" && grep -q "^kernel $kh\$" "$BUILT" ||
  nodev "the host or the kernel is not the one today's build recorded ($BUILT)"
printf 'host %s\nkernel %s\nsampler %s\nguard %s\nrunner %s\n' "$hh" "$kh" "$sh" "$(sha256sum "$G" | cut -d' ' -f1)" \
  "$(sha256sum "$RUNNER" | cut -d' ' -f1)" > "$SD/hashes.txt"
say "binaries: host ${hh:0:16}, kernel ${kh:0:16} (as built: $(grep -m1 '^X04-BUILT ' "$BUILT" | cut -c1-80)); sampler build/ettelem/ettelem ${sh:0:16}"

# ---- 2. THE FIRST CARD COMMAND: the holder rules, the one ops node, then the start config read under the card lock
if [ -n "$DRYF" ]; then
  FIRST=$(date +%s)
  say "lib.sh's two ps rules and et-who --check (the holder check: the first card command; the cap counts from its start)"
  say "count /dev/et*_ops: exactly /dev/et0_ops, else no sitting (no device opened)"
  say "ET_DEVICES=0 flock -n $LOCK timeout 10 $G config (the start config read; gate: TDP 0 W, 65 C, minion 600 MHz)"
else
  FIRST=$(date +%s)                                   # stamped as the first card command starts: the cap counts from its start
  echo "$FIRST" > "$SD/first-card-command.txt"
  PO=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
  PX=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
  timeout 30 et-who --check > "$SD/etwho-start.txt" 2>&1; wrc=$?
  nh=$(awk '$1 ~ /^\/dev\/et/ || $1 ~ /^lock:/ {n++} END {print n+0}' "$SD/etwho-start.txt")
  [ "$PX" -eq 0 ] || nodev "another user's device process is running ($PX)"
  [ "$PO" -eq 0 ] || nodev "a device process of ours is running ($PO)"
  case "$wrc" in
    0) ;;
    1) nodev "the card is held: et-who --check lists $nh holder line(s)" ;;
    *) nodev "the holder check failed (et-who --check exit $wrc)" ;;
  esac
  OPS=$(ls -1d /dev/et*_ops 2>/dev/null | grep -E '^/dev/et[0-9]+_ops$' | sort | tr '\n' ' ')   # the runner's ops_nodes(), before any card read
  OPS=${OPS% }
  [ "$OPS" = /dev/et0_ops ] || nodev "the host shows ops node(s) [${OPS:-none}], not exactly /dev/et0_ops: E193 runs on one card, card 0 (E193.md 3)"
  say "the first card command (the holder check): free (et-who --check exit 0; other users' device processes 0, ours 0); the one ops node /dev/et0_ops; the cap counts from the holder check's start"
  config_read "$SD/config-start.json"
  cfg=$(cat "$SD/config-start.json")
  [ -n "$cfg" ] || gate "no start config read came back (the card lock held, or the guard refused): $(head -c 200 "$SD/config-start.json.err")"
  echo "$cfg" | grep -q '"tdp_w":0,' && echo "$cfg" | grep -q '"temp_threshold_c":65,' && echo "$cfg" | grep -q '"minion_mhz":600,' ||
    gate "the start config is not TDP 0 W / 65 C / 600 MHz as found: $(echo "$cfg" | cut -c1-240)"
  say "start config read: TDP 0 W, 65 C, minion 600 MHz as found (config-start.json)"
fi
CFG_OK=1
DEADLINE=$((FIRST + CAP_S - 120))
if [ -z "$DRYF" ] && [ $((LAST_END - 180)) -lt "$DEADLINE" ]; then DEADLINE=$((LAST_END - 180)); fi
say "the runner's deadline: $(date -d @"$DEADLINE" '+%H:%M:%S %Z') (epoch $DEADLINE: the first card command + $CAP_S s - 120 s, never past the window's last end - 180 s); no run starts after it"
RUNCMD=(python3 -I -B "$RUNNER")
COMMON=(--host "$H" --sampler "$G" --device 0 --deadline "$DEADLINE")
[ -n "$DRYF" ] && COMMON+=(--dry)

# ---- 4. THE SMOKE, then the kit's smoke gate
[ -e "$SD/STOP" ] && gate "the operator's stop file ($SD/STOP) is present before the smoke"
say "smoke start: run_x04.py $SD/smoke --smoke --blocks S,D,W,T,C (the five named arms, 10 device processes)"
"${RUNCMD[@]}" "$SD/smoke" "${COMMON[@]}" --smoke --blocks S,D,W,T,C > "$SD/smoke-runner.out" 2>&1 < /dev/null
src=$?
say "smoke end: runner rc $src; $(python3 -I -B "$KIT/check_e193.py" stopreason "$SD/smoke" 2>&1 | tail -n 1 | cut -c1-200)"
if [ -n "$DRYF" ]; then
  say "check_e193.py smoke $SD/smoke --rc $src (the kit's smoke gate) would read the smoke's X04 lines and telemetry: skipped; listed $(grep -c '^DRY ET_DEVICES=' "$SD/smoke-runner.out") device calls"
else
  python3 -I -B "$KIT/check_e193.py" smoke "$SD/smoke" --rc "$src" > "$SD/smoke-gate.txt" 2>&1
  grep -q '^SMOKE GO' "$SD/smoke-gate.txt" || gate "the smoke gate failed: $(grep -m1 -E '^SMOKE' "$SD/smoke-gate.txt" | cut -c1-240)"
  say "$(grep -m1 '^SMOKE GO' "$SD/smoke-gate.txt" | cut -c1-240)"
fi

# ---- 5. THE MAIN RUN
[ -e "$SD/STOP" ] && gate "the operator's stop file ($SD/STOP) is present before the main run"
say "main run start: run_x04.py $SD/x04 --blocks $BLOCKS (9 passes, pass 0 the registered warm-up)"
"${RUNCMD[@]}" "$SD/x04" "${COMMON[@]}" --blocks "$BLOCKS" > "$SD/runner.out" 2>&1 < /dev/null
mrc=$?
why=$(python3 -I -B "$KIT/check_e193.py" stopreason "$SD/x04" 2>&1 | tail -n 1 | cut -c1-240)
CRASH=
if [ -n "$DRYF" ]; then
  say "main run end: runner rc $mrc; listed $(grep -c '^DRY ET_DEVICES=' "$SD/runner.out") device calls"
elif [ "$mrc" -eq 0 ]; then
  say "main run end: runner rc 0, every pass ($why)"
elif [ "${why#stop: }" != "$why" ]; then
  say "main run stopped: runner rc $mrc; $why; the passes done stand (E193.md 11)"
else
  CRASH=1
  say "main run ended without a registered stop: runner rc $mrc; $why: a crash, not a registered stop (E193.md 11 has no row for it): reported, nothing killed; a dated note decides whether its passes are reduced"
fi

# ---- 6. the closing config read (reported), session end, the manifest
closing
rc=0; [ -z "$DRYF" ] && [ "$mrc" -ne 0 ] && rc=1
[ -n "$CRASH" ] && rc=4
finish "$rc"
