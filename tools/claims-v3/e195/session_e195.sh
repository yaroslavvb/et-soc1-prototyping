#!/usr/bin/env bash
# E195's kit (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): THE CARD SESSION on aifoundry3 card 0, a LAB PORT of the
# registered proposal/src/session_x09.sh (itself the lab's E139 session and queue with E183's gates). It keeps every arm, value, order,
# pass, window rule and stop of the registered session: the smoke block 901 of anchor_pi, x9_rd_rnd, x9_wr_u4, x9_wrh_rnd, x9_wrh_nst and
# its registered gate (smoke_gate_x09.py, unchanged); passes 910-917 (910 the registered warm-up), each one block; no pass after the
# session's 38th minute, none when now + the longest pass so far (360 s until one has run) + 60 s for the close would pass X9_DEADLINE; a
# pass in flight never cut; a pass that fails ends the queue; 15 s between passes; the board-power watcher (watch_x09.py, unchanged; no
# block starts while it is not running) and the runner's die stop at 70 C; the session's config reads through E128's guard at both ends,
# each only while et-who --check reads the card free (the registered cfg(), session_x09.sh lines 70-73).
# What the port changes, each for the reason named (KIT.md section 1):
#   - the blocks are block_e195.sh (block_x09.sh with lib_e195.sh: no SIGKILL of a sampler; runitems_e195.py: the record read whole);
#   - the kits' session form: its files in <tree>/build/e195/T<T0>/ (the box's tree ~/aifoundry, where every rest rule of ours reads
#     build/e*/T*/session.log; "session start", "session end (T0 <T0>)"), MANIFEST.sha256 last (every file of the session's directory and
#     of its data folder, paths from the tree's top), session.rc after it; each session's data in its own folder of E195's root,
#     build/claims-v3/aifoundry3/x09-T<T0>/p<pass>/ (X9_EXPN, a knob of the registered scripts), so no earlier session's pass is ever
#     skipped as "already done" by lib.sh's block_begin;
#   - refusals before anything (exit 8, "refused, no device opened"): the host's name aifoundry3; USER this login; the window
#     (X9_LATEST_START, X9_DEADLINE: no session after the first, the smoke must fit before the second); no stop file; harness-e195.json at
#     the sha256 the launch passes and every file of it at its pin (HARNESS OK); today's build record and the host, kernel and the box's
#     two tools at its hashes; this T0's data folder new; then the device-command preflight (preflight_e195.sh: dmcmd_audit GO, exit 3);
#   - THE FIRST CARD COMMAND is the holder check (lib.sh's two ps rules and et-who --check), stamped as it starts: the cap of 45
#     card-minutes counts from it (E195.md 6); then exactly one ops node, /dev/et0_ops (E195.md 3), and the card lock file, else no
#     session ("no device opened"); then the start config read (ET_DEVICES unset, under the card lock, timeout 10, through E128's guard):
#     TDP 0 W, 65 C, minion 600 MHz as found, else no pass (GATE-STOP);
#   - the deadline is the earlier of X9_DEADLINE (step 9 sets it to the earlier of the window's last end and the launch + 45 minutes) and
#     the first card command + 45 minutes;
#   - THE KIT'S SMOKE GATE beside the registered one (E195.md 5, the lab's choice): the smoke's highest board reading, its heater bursts
#     included, below 65 W and its highest die reading below 65 C (check_e195.py smoke), else no pass;
#   - a signal (TERM, INT, HUP) writes the session's stop file and the running pass's STOP, waits for the block (never a kill), and closes;
#   - a sampler left stuck by lib_e195.sh (it ignored SIGTERM: never killed) stops the queue, and the closing config read is skipped
#     (nothing may open the management node beside it);
#   - THE CLOSING CONFIG READ ONLY WHILE THE CARD READS FREE (Q191, lane fix-e195, Sun 15 Nov 2026, before any E195 datum; verify-e195's
#     finding 1): the registered cfg() reads at both ends only while `et-who --check` reads the card free (request.md 8.3 and 9); the
#     port kept that at the start (the holder check) and keeps it at the end too: `timeout 20 et-who --check` first, its lines in
#     etwho-check-end.txt; when it does not read free (any exit but 0) the log says "closing config read: not read (et-who --check does
#     not read the card free ...)" and nothing is read; a tool's stderr is never copied into the session log, its file is named instead
#     (verify-e195's finding 4: the rest rule reads the session log);
#   - --dry: every refusal and pin, then each block with V3_DRY=1 (every device call printed, nothing opened), the listing checked against
#     the kit's committed listing for aifoundry3 (check_e195.py dry): "E195-DRY OK"; its files in T<T0>-dry/, every log line "DRY ...".
# Exit: 0 the queue ended by the plan (every pass, or the 38-minute or deadline rule); 1 a live stop or a failed pass ended it; 3 a gate
# (GATE-STOP); 4 a pass ended without a registered stop (runitems exit 1, a traceback: reported, nothing killed; a dated note decides);
# 8 a refusal; 2 usage.
#   E195_T0=<epoch> X9_LATEST_START=@<epoch> X9_DEADLINE=@<epoch> E195_HARNESS_SHA256=<sha> \
#     setsid nohup bash <E195's root>/tools/claims-v3/e195/session_e195.sh [--dry] > build/e195/launch-T<T0>.out 2>&1 < /dev/null &
# Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms, no firmware-revisions query.
# SPDX-License-Identifier: Apache-2.0
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)              # tools/claims-v3/e195 in E195's root
X9=$HERE/proposal/src                                                 # the registered source, byte for byte
R=$(cd "$HERE/../../.." && pwd -P)                                    # E195's root: the tree the blocks write into (X9_ROOT)
TREE=$(cd "$R/../../../.." && pwd -P)                                 # the box's tree (~/aifoundry)
cd "$TREE" || exit 2
RR=${R#"$TREE"/}
DRYF=
case "${1:-}" in "") ;; --dry) DRYF=1 ;; *) echo "usage: session_e195.sh [--dry]"; exit 2 ;; esac
T0=${E195_T0:-}
case "$T0" in ''|*[!0-9]*) echo "E195_T0 must be the launch's epoch seconds"; exit 2 ;; esac
SD=build/e195/T$T0; [ -n "$DRYF" ] && SD=$SD-dry
[ -e "$SD" ] && { echo "$SD exists: one session a T0"; exit 2; }
mkdir -p "$SD" || exit 2
LOG=$SD/session.log
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %Z') ${DRYF:+DRY }$*" >> "$LOG"; }
unset ET_DEVICES V3_DEVICE V3_DRY
export LC_ALL=C LD_LIBRARY_PATH=/opt/et/lib
LOCK=/run/lock/etsoc-shire0.lock
G=tools/claims-v3/e128/ettelem_guard.sh                              # relative to E195's root (it execs build/ettelem/ettelem there)
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$'   # lib.sh's DEV_COMM
OTHER_COMM="$DEV_COMM|^Runner.Worker$"                                                # lib.sh's OTHER_COMM
EXPN=x09-T$T0
CARD=$(hostname)
DATA=$RR/build/claims-v3/$CARD/$EXPN; [ -n "$DRYF" ] && DATA=$RR/build/claims-v3-dry/$CARD/$EXPN
SMOKE=901
SMOKE_ITEMS=anchor_pi,x9_rd_rnd,x9_wr_u4,x9_wrh_rnd,x9_wrh_nst
PASSES="910 911 912 913 914 915 916 917"
CAP_MIN=38; longest=360; SMOKE_S=150; CLOSE_S=60; CAP_S=2700
WPID=; BPID=; CUR=; CFG_OK=
finish() {  # finish <exit status>: "session end", the manifest last (the session's directory and its data folder), session.rc after it
  [ -n "$WPID" ] && { date --iso-8601=seconds > "$SD/session-end.time"; sleep 2; kill "$WPID" 2>/dev/null; wait "$WPID" 2>/dev/null; }
  for f in "$RR/build/x09-STOP" "$RR/build/claims-v3/STOP"; do [ -e "$f" ] && cp "$f" "$SD/stopfile-$(basename "$f").txt"; done
  say "session end (T0 $T0)"
  { find "$SD" -type f ! -name 'MANIFEST.sha256*' ! -name session.rc
    [ -d "$DATA" ] && find "$DATA" -type f ! -name telemetry.jsonl.raw
  } | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done > "$SD/MANIFEST.sha256.tmp" && mv "$SD/MANIFEST.sha256.tmp" "$SD/MANIFEST.sha256"
  echo "$1" > "$SD/session.rc"
  exit "$1"
}
refuse() { say "refused, no device opened: $*"; finish 8; }
nodev() { say "GATE-STOP: $* (no device opened)"; finish 3; }
config_read() {  # config_read <file>: card 0's static config through E128's guard, under the card lock, timeout 10 (READ only)
  ( cd "$R" && flock -n "$LOCK" timeout 10 bash "$G" config < /dev/null 2> "$TREE/$1.err" | grep '^{' | tail -n 1 ) > "$1"
}
stuck() { [ -d "$DATA" ] && [ -n "$(find "$DATA" -name SAMPLER-STUCK 2>/dev/null | head -n 1)" ]; }
errsz() {  # errsz <file>: a tool's stderr file named with its size, never its text (verify-e195's finding 4: the rest rule reads this log)
  if [ -s "$1" ]; then echo "its stderr in $(basename "$1"), $(wc -c < "$1" | tr -d ' ') bytes"; else echo "$(basename "$1") empty"; fi
}
closing() {  # the closing config read (reported, never a gate), only while et-who --check reads the card free (the registered cfg()); et-who
  if [ -n "$DRYF" ]; then say "timeout 20 et-who --check, then, only while it reads the card free, flock -n $LOCK timeout 10 $G config (the closing config read, reported)"; return 0; fi
  local crc nh2 c2
  if stuck; then
    say "closing config read: SKIPPED: a sampler of this session ignored SIGTERM and still runs to its own bound ($(find "$DATA" -name SAMPLER-STUCK | head -n 1)); nothing may open the management node beside it"
  else
    timeout 20 et-who --check > "$SD/etwho-check-end.txt" 2>&1; crc=$?    # the registered cfg()'s rule: read only while the card reads free
    if [ "$crc" -ne 0 ]; then
      nh2=$(awk '$1 ~ /^\/dev\/et/ || $1 ~ /^lock:/ {n++} END {print n+0}' "$SD/etwho-check-end.txt")
      say "closing config read: not read (et-who --check does not read the card free: exit $crc, $nh2 holder line(s) in etwho-check-end.txt)"
    else
      config_read "$SD/config-session-end.json"
      c2=$(cat "$SD/config-session-end.json")
      if [ -z "$c2" ]; then say "closing config read: none came back (the card lock held, or the guard refused; $(errsz "$SD/config-session-end.json.err"))"
      elif echo "$c2" | grep -q '"tdp_w":0,' && echo "$c2" | grep -q '"temp_threshold_c":65,' && echo "$c2" | grep -q '"minion_mhz":600,'; then
        say "closing config read: TDP 0 W, 65 C, minion 600 MHz, as at the start (config-session-end.json)"
      else
        say "closing config read: NOT as at the start (reported; nothing was set by this session): $(echo "$c2" | cut -c1-240)"
      fi
    fi
  fi
  timeout 20 et-who > "$SD/etwho-end.txt" 2>&1
  say "et-who at the end: $(head -n 1 "$SD/etwho-end.txt" | cut -c1-160)"
}
gate() { say "GATE-STOP: $*: no pass runs"; [ -n "$CFG_OK" ] && closing; finish 3; }
on_sig() {  # a signal: the session's stop file and the running pass's STOP; the block is waited for, never killed
  say "signal: build/x09-STOP and the running pass's STOP written; the launch in flight finishes, then the session closes"
  echo "signal to the session at $(date '+%T')" >> "$RR/build/x09-STOP"
  [ -n "$CUR" ] && [ -d "$DATA/p$CUR" ] && echo "signal to the session at $(date '+%T')" >> "$DATA/p$CUR/STOP"
}
bg_wait() {  # bg_wait <pid>: its exit status; a trapped signal interrupts the shell's wait, so wait again while it lives
  local pid=$1 rc r2
  while :; do
    wait "$pid"; rc=$?
    kill -0 "$pid" 2>/dev/null && continue
    if [ "$rc" -gt 128 ]; then wait "$pid" 2>/dev/null; r2=$?; [ "$r2" -ne 127 ] && rc=$r2; fi
    return "$rc"
  done
}
block() {  # block <log file> <pass> [items]: one block_e195.sh block, its output appended to <log file>
  local lg=$1; shift
  if [ -n "$DRYF" ]; then
    X9_ROOT=$R X9_EXPN=$EXPN X9_GEN=$R/tools/claims-v3/e195/gen-e195-noms X9_MAX_C=70 V3_DRY=1 bash "$RR/tools/claims-v3/e195/block_e195.sh" "$@" < /dev/null >> "$lg" 2>&1
    return $?
  fi
  X9_ROOT=$R X9_EXPN=$EXPN X9_GEN=$R/tools/claims-v3/e195/gen-e195-noms X9_MAX_C=70 bash "$RR/tools/claims-v3/e195/block_e195.sh" "$@" < /dev/null >> "$lg" 2>&1 &
  BPID=$!
  bg_wait "$BPID"; local rc=$?
  BPID=
  return "$rc"
}
trap on_sig TERM INT HUP

say "session start (T0 $T0 = $(date -d @"$T0" '+%H:%M:%S %Z' 2>/dev/null); E195, the model session's X09, on aifoundry3 card 0; the lab port of session_x09.sh (kit-e195)${DRYF:+; DRY})"
say "box $CARD, tree $(basename "$TREE"), E195's root $RR, data $DATA; $(python3 --version 2>&1)"
[ "$CARD" = aifoundry3 ] || refuse "this is $CARD, not aifoundry3: E195 runs on aifoundry3 card 0 only (E195.md 3; the registered order is drawn on the host's name)"
case "$RR" in build/claims-v3/aifoundry3/e195) ;; *) refuse "E195's root is $RR, not build/claims-v3/aifoundry3/e195 under the box's tree" ;; esac
ME=$(id -un 2>/dev/null)
[ -n "${USER:-}" ] || export USER="$ME"
[ -n "$ME" ] && [ "$USER" = "$ME" ] || refuse "USER is '$USER', not this login: the holder checks compare with it"
[ -n "${X9_LATEST_START:-}" ] && [ -n "${X9_DEADLINE:-}" ] || refuse "X9_LATEST_START and X9_DEADLINE are required: the window of the day's go"
latest=$(date -d "$X9_LATEST_START" +%s 2>/dev/null) || refuse "X9_LATEST_START '$X9_LATEST_START' is not a date"
deadline=$(date -d "$X9_DEADLINE" +%s 2>/dev/null) || refuse "X9_DEADLINE '$X9_DEADLINE' is not a date"
t_start=$(date +%s)
[ "$t_start" -le "$latest" ] || refuse "no session starts after $(date -d @"$latest" '+%F %T %Z')"
[ $((t_start + SMOKE_S + CLOSE_S)) -le "$deadline" ] || refuse "the smoke ($SMOKE_S s) and the close would end after the deadline $(date -d @"$deadline" '+%F %T %Z')"
for f in "$RR/build/x09-STOP" "$RR/build/claims-v3/STOP"; do [ -e "$f" ] && refuse "$f exists (a stop file left from before: a dated note moves it aside first)"; done
hj=$(sha256sum "$RR/tools/claims-v3/e195/harness-e195.json" 2>/dev/null | cut -d' ' -f1)
[ -n "${E195_HARNESS_SHA256:-}" ] && [ "$hj" = "${E195_HARNESS_SHA256}" ] || refuse "harness-e195.json reads ${hj:-nothing}, not the launch's ${E195_HARNESS_SHA256:-<unset>}"
python3 -I -B "$RR/tools/claims-v3/e195/harness_e195.py" --box --root "$RR" > "$SD/harness.txt" 2>&1
grep -q '^HARNESS OK: ' "$SD/harness.txt" || refuse "the harness check failed: $(tail -n 1 "$SD/harness.txt" | cut -c1-200)"
say "$(grep -m1 '^HARNESS OK: ' "$SD/harness.txt")"
BUILT=$RR/build/x09mem-built.txt
H=$RR/build/x09mem/host/x09mem_host; K=$RR/build/x09mem/kernel/x09mem.elf
ET=$RR/build/ettelem/ettelem; SP=$RR/build/sparsity/host/sparsity_host
[ -f "$BUILT" ] && grep -q '^X09MEM-BUILT ' "$BUILT" || refuse "no build record ($BUILT): run step 6 first"
for f in "$H" "$ET" "$SP"; do [ -x "$f" ] || refuse "$f is not an executable file"; done
[ -f "$K" ] || refuse "$K is missing"
hh=$(sha256sum "$H" | cut -d' ' -f1); kh=$(sha256sum "$K" | cut -d' ' -f1); eh=$(sha256sum "$ET" | cut -d' ' -f1); ph=$(sha256sum "$SP" | cut -d' ' -f1)
grep -q "^host $hh\$" "$BUILT" && grep -q "^kernel $kh\$" "$BUILT" && grep -q "^ettelem $eh " "$BUILT" && grep -q "^sparsity_host $ph " "$BUILT" ||
  refuse "the host, the kernel, the sampler or the heater is not the one the build record names ($BUILT)"
printf 'host %s\nkernel %s\nettelem %s\nsparsity_host %s\nguard %s\nrunitems_e195 %s\nblock_e195 %s\n' "$hh" "$kh" "$eh" "$ph" \
  "$(sha256sum "$RR/$G" | cut -d' ' -f1)" "$(sha256sum "$RR/tools/claims-v3/e195/runitems_e195.py" | cut -d' ' -f1)" \
  "$(sha256sum "$RR/tools/claims-v3/e195/block_e195.sh" | cut -d' ' -f1)" > "$SD/hashes.txt"
say "binaries: host ${hh:0:16}, kernel ${kh:0:16} (as built: $(grep -m1 '^X09MEM-BUILT ' "$BUILT" | cut -c1-80)); the sampler ${eh:0:16} and the heater ${ph:0:16} as recorded"
[ -e "$DATA" ] && refuse "$DATA exists: one data folder a T0"
bash "$RR/tools/claims-v3/e195/preflight_e195.sh" > "$SD/preflight.txt" 2>&1; a=$?
say "device-command preflight rc=$a: $(grep -m1 '^dmcmd_audit:' "$SD/preflight.txt" | cut -c1-200)"
[ "$a" -eq 0 ] && grep -q '^dmcmd_audit: GO' "$SD/preflight.txt" || { say "refused, no device opened: the device-command preflight is not GO ($SD/preflight.txt)"; finish 3; }
say "passes $PASSES (910 the registered warm-up); no pass starts after $CAP_MIN min or past the deadline; the memory shires' counters not read (every x9_ item runs --no-ms: KIT.md section 4)"

if [ -n "$DRYF" ]; then
  FIRST=$(date +%s)
  say "lib.sh's two ps rules and et-who --check (the holder check: the first card command; the cap counts from its start)"
  say "count /dev/et*_ops: exactly /dev/et0_ops, and the card lock file, else no session (no device opened)"
  say "flock -n $LOCK timeout 10 $G config (the start config read; gate: TDP 0 W, 65 C, minion 600 MHz)"
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
  OPS=$(ls -1d /dev/et*_ops 2>/dev/null | grep -E '^/dev/et[0-9]+_ops$' | sort | tr '\n' ' ')   # the host's own rule, before any card read
  OPS=${OPS% }
  [ "$OPS" = /dev/et0_ops ] || nodev "the host shows ops node(s) [${OPS:-none}], not exactly /dev/et0_ops: E195 runs on one card, card 0 (E195.md 3)"
  [ -e "$LOCK" ] || nodev "no card lock file $LOCK"
  say "the first card command (the holder check): free (et-who --check exit 0; other users' device processes 0, ours 0); the one ops node /dev/et0_ops; the cap counts from the holder check's start"
  config_read "$SD/config-session-start.json"
  cfg=$(cat "$SD/config-session-start.json")
  [ -n "$cfg" ] || gate "no start config read came back (the card lock held, or the guard refused; $(errsz "$SD/config-session-start.json.err"))"
  echo "$cfg" | grep -q '"tdp_w":0,' && echo "$cfg" | grep -q '"temp_threshold_c":65,' && echo "$cfg" | grep -q '"minion_mhz":600,' ||
    gate "the start config is not TDP 0 W / 65 C / 600 MHz as found: $(echo "$cfg" | cut -c1-240)"
  say "start config read: TDP 0 W, 65 C, minion 600 MHz as found (config-session-start.json)"
fi
CFG_OK=1
[ $((FIRST + CAP_S)) -lt "$deadline" ] && deadline=$((FIRST + CAP_S))
say "the deadline: $(date -d @"$deadline" '+%H:%M:%S %Z') (epoch $deadline: the earlier of X9_DEADLINE and the first card command + $CAP_S s)"

if [ -z "$DRYF" ]; then
  python3 -I -B "$X9/watch_x09.py" --root "$TREE/$DATA" --stop-w 70 --n 3 --session-stop "$R/build/x09-STOP" \
    --end-flag "$TREE/$SD/session-end.time" --max-s $((deadline - t_start + 600)) >> "$SD/watch.log" 2>&1 &
  WPID=$!
  sleep 2
  kill -0 "$WPID" 2>/dev/null || { WPID=; gate "the board-power watcher did not start (watch.log)"; }
  say "the board-power watcher runs (pid $WPID): a stop at 70 W on 3 samples in a row, on every pass's live telemetry"
fi
watching() { [ -n "$DRYF" ] || kill -0 "$WPID" 2>/dev/null; }

CUR=$SMOKE
block "$SD/smoke.log" "$SMOKE" "$SMOKE_ITEMS"; rc=$?
CUR=
say "smoke rc=$rc"
if [ -n "$DRYF" ]; then
  say "the smoke gates (smoke_gate_x09.py and the kit's 65 W / 65 C) need a real smoke: not run"
else
  python3 -I -B "$X9/smoke_gate_x09.py" "$DATA/p$SMOKE" "$SMOKE_ITEMS" > "$SD/smoke-gate.txt" 2>&1; g=$?
  python3 -I -B "$RR/tools/claims-v3/e195/check_e195.py" smoke "$DATA/p$SMOKE" > "$SD/smoke-peak.txt" 2>&1; g2=$?
  say "$(tail -n 1 "$SD/smoke-gate.txt" | cut -c1-240)"
  say "$(tail -n 1 "$SD/smoke-peak.txt" | cut -c1-240)"
  if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ] || [ "$g2" -ne 0 ] || [ -e "$RR/build/x09-STOP" ]; then
    gate "the smoke gate failed or a stop is set (block rc $rc, registered gate $g, the kit's 65 W / 65 C gate $g2)"
  fi
  say "smoke gate passed: the passes start"
fi

done_n=0; why="every pass"; rc_end=0
for p in $PASSES; do
  stop=
  for f in "$RR/build/x09-STOP" "$RR/build/claims-v3/STOP"; do [ -e "$f" ] && stop=$f; done
  if [ -n "$stop" ]; then why="$stop exists: stopping before p$p"; rc_end=1; break; fi
  if ! watching; then why="the board-power watcher is not running: stopping before p$p"; rc_end=1; break; fi
  now=$(date +%s)
  el=$(( (now - t_start) / 60 ))
  if [ "$el" -ge "$CAP_MIN" ]; then why="$el min into the session: no pass starts after $CAP_MIN (before p$p)"; break; fi
  if [ $((now + longest + CLOSE_S)) -gt "$deadline" ]; then
    why="deadline: p$p would end after $(date -d @"$deadline" '+%T %Z') (longest pass $longest s + $CLOSE_S s)"; break
  fi
  t0=$(date +%s)
  CUR=$p
  block "$SD/passes.log" "$p"; rc=$?
  CUR=
  d=$(( $(date +%s) - t0 ))
  [ "$d" -gt "$longest" ] && longest=$d
  say "p$p rc=$rc ($d s)"
  if [ "$rc" -ne 0 ]; then
    note=$(sed -n 's/.*"note":"\([^"]*\)".*/\1/p' "$DATA/p$p/block.json" 2>/dev/null | head -n 1)
    if [ "$rc" -eq 1 ] && [ "$note" = "runitems exit 1" ]; then
      why="p$p ended without a registered stop (block rc 1, $note: a traceback in the runner): reported, nothing killed; a dated note decides whether its passes are reduced"
      rc_end=4
    else
      why="stopping after p$p (block rc $rc${note:+, $note})"; rc_end=1
    fi
    break
  fi
  done_n=$((done_n + 1))
  stuck && { why="a sampler of p$p ignored SIGTERM (never killed): stopping after p$p"; rc_end=1; break; }
  sleep 15
done
say "queue end: $why; passes complete: $done_n of 8 (910 the warm-up)"
[ -n "$DRYF" ] && {
  python3 -I -B "$RR/tools/claims-v3/e195/check_e195.py" dry "$SD" "$RR/tools/claims-v3/e195/desk/dry-e195-noms-aifoundry3.txt" > "$SD/dry-check.txt" 2>&1
  say "$(tail -n 1 "$SD/dry-check.txt" | cut -c1-240)"
  grep -q '^E195-DRY OK' "$SD/dry-check.txt" || rc_end=1
}
closing
finish "$rc_end"
