#!/usr/bin/env bash
# E198 dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum): THE SESSION'S WRAPPER on aifoundry1, card 1, one
# sitting a call, on THE LAB'S RUNNER COPY. It is session_e198.sh (kit-e198, Q191, which stays as committed beside it and is not run for
# E198 after A1) with these changes and no other:
#   - the runner is tools/claims-v3/e198/run_x04_e198a1.py (E198.md.dated-amendment-A1.md: E193's runner 26d08862... with the kill path
#     changed and nothing else: each device process under a plain `timeout 10`, TERM at 10 s and never a KILL; one still running 25 s
#     after it started is reported at once, recorded as the registered stop "tell the lab admin" and LEFT RUNNING; end_device() sends
#     SIGTERM to its timeout and waits, never a KILL); it is given E193's arms.tsv by --arms, the value E193's runner takes by default
#     from its own folder (the copy sits in E198's folder); every other option as session_e198.sh passes it;
#   - the harness is harness-e198-a1.json (harness_e198a1.py), the preflight preflight_e198a1.sh, and the build record must name
#     build_e198a1.sh (A1's build, whose listing reads the lab's copy);
#   - A DEVICE PROCESS NOT ENDED: when a runner call's log holds the runner's own "device process not ended" line, the session says so at
#     once ("A DEVICE PROCESS DID NOT END ..."), sends nothing else to the card (its closing config read is skipped), kills nothing, and
#     ends as session_e198.sh would (the smoke: its gate; the main run: "main run stopped", the registered stop); step 9 (A1) then refuses
#     any further E198 sitting before a dated note, and step 10 (A1) reads DEVICE-NOT-ENDED;
#   - its start line names A1 ("kit-e198 with amendment A1").
# Everything else is session_e198.sh's, line for line: THE PRIVATE /dev (privdev_e198.sh), the warden and the watch (warden_e198.py,
# holdercheck_e198.sh), the guard shim (ettelem_guard_e198.sh through E191's guard), the runtime-line guard (x04host_e198.sh), THE IDENTITY
# GATE (a) and (b) (ident_e198.py, ident_inner_e198.sh), the first card command, the deadline, the smoke and E193's smoke gate, the main
# run, the crash rule, the manifest, and the session folder build/e198/T<T0>/ (every rest rule of ours reads its session.log).
# Exit: 0 every pass; 1 a registered stop (a device process not ended among them); 4 a crash; 3 a gate stop (no main run); 2 refused
# before anything (no device opened).
#   E198_T0=<epoch> E198_LAST_END_EPOCH=<epoch> E198_HARNESS_SHA256=<harness-e198-a1.json's sha256> bash <R>/tools/claims-v3/e198/session_e198a1.sh A|B
#   DRY=1 E198_T0=<epoch> E198_HARNESS_SHA256=<sha256> bash <R>/tools/claims-v3/e198/session_e198a1.sh A|B      (opens nothing)
# DRY=1 is the dry pass (session_e198.sh's): every device call listed by the runner's own --dry inside the private /dev, the private /dev
# listed for real (it opens nothing), the rest printed and skipped; its folder is build/e198/T<T0>-dry and every line begins "DRY ".
# There is no desk-test variable: the desk tests drive this file's real path exactly as the launch does.
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
  *) echo "usage: session_e198.sh A|B (sitting A: blocks S,D,W,T, cap 60 card-minutes; sitting B: block C, cap 50)"; exit 2 ;;
esac
DRYF=
case "${DRY-}" in "") ;; 1) DRYF=1 ;; *) echo "DRY must be 1 or unset (it is '${DRY}')"; exit 2 ;; esac
T0=${E198_T0:-}
case "$T0" in ''|*[!0-9]*) echo "E198_T0 must be the launch's epoch seconds"; exit 2 ;; esac
LAST_END=${E198_LAST_END_EPOCH:-}
if [ -z "$DRYF" ]; then
  case "$LAST_END" in ''|*[!0-9]*) echo "E198_LAST_END_EPOCH must be the window's last end, epoch seconds"; exit 2 ;; esac
fi
SD=build/e198/T$T0; [ -n "$DRYF" ] && SD=$SD-dry
[ -e "$SD" ] && { echo "$SD exists: one session a T0"; exit 2; }
mkdir -p "$SD" || exit 2
LOG=$SD/session.log
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %Z') ${DRYF:+DRY }$*" >> "$LOG"; }
KIT=$RR/tools/claims-v3/e198
E193K=$RR/tools/claims-v3/e193
RUNNER=$KIT/run_x04_e198a1.py                       # THE LAB'S RUNNER COPY (E198 A1); E193's runner stays as committed
ARMS=$E193K/proposal/src/arms.tsv                   # E193's arms.tsv, the value E193's runner takes by default from its folder
H=$RR/build/x04clock/host/x04clock_host
K=$RR/build/x04clock/kernel/x04clock.elf
BUILT=$RR/build/x04clock-built.txt
GTREE=tools/claims-v3/e191/ettelem_guard_e191.sh     # the tree's own copy, at its pin 6fd26f51... (harness-e198.json "tree")
READER=build/ettelem/ettelem                          # the box's reader, at its pin 8008f96f... (harness-e198.json "tree")
GSHIM=$KIT/ettelem_guard_e198.sh
HC=$KIT/holdercheck_e198.sh
WRAP=$KIT/x04host_e198.sh
PRIV=(bash "$KIT/privdev_e198.sh")
LOCK=/run/lock/etsoc-shire1.lock
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$'   # lib.sh's DEV_COMM
OTHER_COMM="$DEV_COMM|^Runner.Worker$"                                                # lib.sh's OTHER_COMM
unset ET_DEVICES V3_DEVICE V3_DRY
export LC_ALL=C E198_SESSION_T0=$T0 E198_HOST=$H E198_KIT=$KIT E198_HOLDERD=$SD/holderd
WPID=

stop_warden() {  # the warden's summary written before the manifest
  [ -n "$WPID" ] || return 0
  touch "$SD/holderd/stop"
  for _ in $(seq 1 100); do kill -0 "$WPID" 2>/dev/null || break; sleep 0.1; done
  if [ -s "$SD/holderd/summary.json" ]; then say "the warden: $(cut -c1-300 "$SD/holderd/summary.json")"
  else say "the warden wrote no summary (reported)"; fi
  WPID=
}
finish() {  # finish <exit status>: the warden stopped, "session end", the manifest last, session.rc after it
  stop_warden
  say "session end (T0 $T0)"
  ( cd "$SD" && find . -type f ! -name MANIFEST.sha256 ! -name session.rc | sed 's#^\./##' | LC_ALL=C sort |
      while IFS= read -r f; do sha256sum "$f"; done > MANIFEST.sha256 )
  echo "$1" > "$SD/session.rc"
  exit "$1"
}
CFG_OK=
nodev() { say "GATE-STOP: $* (no device opened)"; finish 3; }
gate() { say "GATE-STOP: $*: no main run"; [ -n "$CFG_OK" ] && closing; finish 3; }
config_read() {  # config_read <file>: card 1's static config through E191's guard, INSIDE the private /dev, card 1's lock, timeout 10
  env ET_DEVICES=1 "${PRIV[@]}" flock -n "$LOCK" timeout 10 "$GSHIM" config < /dev/null 2> "$1.err" > "$1.raw"
  grep '^{' "$1.raw" | tail -n 1 > "$1"
}
DNE=
dne_check() {  # dne_check <smoke|x04>: E198 A1: the runner's own line for a device process it left running (never killed)
  [ -z "$DRYF" ] || return 0
  grep -qs 'device process not ended' "$SD/$1/run.log" || return 0
  DNE=1
  say "A DEVICE PROCESS DID NOT END in the $1 run ($(grep -m1 'device process not ended' "$SD/$1/run.log" | cut -c1-200)): nothing was killed; it is left for the lab admin and nothing else is sent to the card (E198 A1); tell the owner and the lab admin at once"
}
closing() {  # the closing config read (reported, never a gate); E198 A1: skipped while a device process of the sitting did not end
  if [ -n "$DNE" ]; then
    say "closing config read: skipped: a device process of this sitting did not end (E198 A1: nothing else is sent to the card while it is there)"
    return 0
  fi
  if [ -n "$DRYF" ]; then
    say "ET_DEVICES=1 privdev_e198.sh flock -n $LOCK timeout 10 ettelem_guard_e198.sh config (the closing config read, reported)"
    return 0
  fi
  config_read "$SD/config-end.json"
  if [ ! -s "$SD/config-end.json" ]; then say "closing config read: none came back ($(head -c 160 "$SD/config-end.json.err" | tr '\n' ' '))"
  else
    python3 -I -B "$KIT/ident_e198.py" config "$SD/config-end.json" "$SD/config-end.json.err" > "$SD/ident-end.txt" 2>&1
    say "closing config read: $(head -n 1 "$SD/ident-end.txt" | cut -c1-240) (reported; nothing was set by this session)"
  fi
}

say "session start (T0 $T0 = $(date -d @"$T0" '+%H:%M:%S %Z' 2>/dev/null); E198 sitting $SIT, blocks $BLOCKS, cap $((CAP_S / 60)) card-minutes; the lab's runner copy on aifoundry1 card 1 in a private /dev; kit-e198 with amendment A1 (no kill path)${DRYF:+; DRY})"
say "box $(hostname), tree $(basename "$TREE"), root $RR; $(python3 --version 2>&1)"
[ "$(hostname)" = aifoundry1 ] || nodev "this is $(hostname), not aifoundry1: E198 runs on aifoundry1 card 1 only (E198.md 3)"

# ---- 1. before anything opens a card node: the harness at its pin, every file of it, the preflight, the binaries, the reader, the guard
hj=$(sha256sum "$KIT/harness-e198-a1.json" 2>/dev/null | cut -d' ' -f1)
[ -n "${E198_HARNESS_SHA256:-}" ] && [ "$hj" = "${E198_HARNESS_SHA256}" ] ||
  nodev "harness-e198-a1.json reads ${hj:-nothing}, not the launch's ${E198_HARNESS_SHA256:-<unset>}"
python3 -I -B "$KIT/harness_e198a1.py" --box --root "$RR" > "$SD/harness.txt" 2>&1
grep -q '^HARNESS OK: ' "$SD/harness.txt" || nodev "the harness check failed: $(tail -n 1 "$SD/harness.txt" | cut -c1-200)"
say "$(grep -m1 '^HARNESS OK: ' "$SD/harness.txt")"
bash "$KIT/preflight_e198a1.sh" > "$SD/preflight.txt" 2>&1
grep -q '^dmcmd_audit: GO' "$SD/preflight.txt" || nodev "the preflight is not GO: $(head -n 1 "$SD/preflight.txt" | cut -c1-200)"
say "preflight: $(head -n 1 "$SD/preflight.txt" | cut -c1-200)"
for f in "$H" "$READER" "$GSHIM" "$HC" "$WRAP"; do [ -x "$f" ] || nodev "$f is not an executable file"; done
[ -f "$K" ] || nodev "$K is missing"
[ -f "$BUILT" ] && grep -q '^X04-BUILT ' "$BUILT" || nodev "no build record ($BUILT): run step 6 first"
grep -q '^a1 build_e198a1.sh$' "$BUILT" || nodev "the build record ($BUILT) was not written by build_e198a1.sh (E198 A1's build, whose listing reads the lab's runner copy): run step 6 (A1) first"
hh=$(sha256sum "$H" | cut -d' ' -f1); kh=$(sha256sum "$K" | cut -d' ' -f1)
grep -q "^host $hh\$" "$BUILT" && grep -q "^kernel $kh\$" "$BUILT" ||
  nodev "the host or the kernel is not the one today's build recorded ($BUILT)"
python3 -I -B "$KIT/harness_e198a1.py" --tree --root "$RR" > "$SD/tree.txt" 2>&1
grep -q '^TREE OK: ' "$SD/tree.txt" || nodev "the box's tree files are not at their pins (the reader build/ettelem/ettelem, E191's guard; E198.md 3): $(tail -n 1 "$SD/tree.txt" | cut -c1-200)"
rh=$(sha256sum "$READER" | cut -d' ' -f1); gh=$(sha256sum "$GTREE" | cut -d' ' -f1)
printf 'host %s\nkernel %s\nreader %s\nguard %s\nrunner %s\n' "$hh" "$kh" "$rh" "$gh" "$(sha256sum "$RUNNER" | cut -d' ' -f1)" > "$SD/hashes.txt"
say "binaries: host ${hh:0:16}, kernel ${kh:0:16} (as built: $(grep -m1 '^X04-BUILT ' "$BUILT" | cut -c1-80)); reader ${rh:0:16}, E191's guard ${gh:0:16}"

# ---- 2. THE FIRST CARD COMMAND: the holder rules, the two-card box, the private /dev shown, the start config read: identity (a)
FIRST=$(date +%s)                                     # stamped as the first card command starts: the cap counts from its start
if [ -n "$DRYF" ]; then
  say "lib.sh's two ps rules and et-who --check (the holder check: the first card command; the cap counts from its start)"
  say "the host's ops nodes: exactly /dev/et0_ops /dev/et1_ops (the two-card box), else no sitting (no device opened)"
else
  echo "$FIRST" > "$SD/first-card-command.txt"
  PO=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n+0}')
  PX=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
  timeout 30 et-who --check > "$SD/etwho-start.txt" 2>&1; wrc=$?
  nh=$(awk '$1 ~ /^\/dev\/et/ || $1 ~ /^lock:/ {n++} END {print n+0}' "$SD/etwho-start.txt")
  [ "$PX" -eq 0 ] || nodev "another user's device process is running ($PX)"
  [ "$PO" -eq 0 ] || nodev "a device process of ours is running ($PO)"
  case "$wrc" in
    0) ;;
    1) nodev "a card is held: et-who --check lists $nh holder line(s) (either card)" ;;
    *) nodev "the holder check failed (et-who --check exit $wrc)" ;;
  esac
  OPS=$(ls -1d /dev/et*_ops 2>/dev/null | grep -E '^/dev/et[0-9]+_ops$' | sort | tr '\n' ' '); OPS=${OPS% }
  [ "$OPS" = "/dev/et0_ops /dev/et1_ops" ] || nodev "the host shows ops node(s) [${OPS:-none}], not /dev/et0_ops /dev/et1_ops: not the two-card box E198.md 3 registers"
  say "the first card command (the holder check): free on both cards (et-who --check exit 0; other users' device processes 0, ours 0); the host's ops nodes $OPS; the cap counts from the holder check's start"
fi
"${PRIV[@]}" /bin/ls -1 /dev > "$SD/privdev-dev.txt" 2> "$SD/privdev-dev.err"; prc=$?
inside=$(grep -E '^et[0-9]' "$SD/privdev-dev.txt" | LC_ALL=C sort | tr '\n' ' '); inside=${inside% }
[ "$prc" -eq 0 ] && [ "$inside" = "et1_mgmt et1_ops" ] ||
  nodev "the private /dev is not card 1's two nodes only (rc $prc; card nodes inside: [${inside:-none}]; $(head -c 160 "$SD/privdev-dev.err" | tr '\n' ' '))"
say "the private /dev (privdev_e198.sh, a listing inside it, nothing opened): card nodes inside [$inside], $(grep -c . "$SD/privdev-dev.txt") entries; the box's real /run/lock, /proc and /sys"
if [ -n "$DRYF" ]; then
  say "ET_DEVICES=1 privdev_e198.sh flock -n $LOCK timeout 10 ettelem_guard_e198.sh config (the start config read; THE IDENTITY GATE (a): TDP 65 W, 65 C, 600 MHz, PCIe target /dev/et1_mgmt, device ID 1, minion_mv in (450, 510))"
else
  config_read "$SD/config-start.json"
  [ -s "$SD/config-start.json" ] || gate "no start config read came back (card 1's lock held, the guard refused, or the private /dev did not open card 1): $(head -c 200 "$SD/config-start.json.err" | tr '\n' ' ')"
  python3 -I -B "$KIT/ident_e198.py" config "$SD/config-start.json" "$SD/config-start.json.err" > "$SD/ident-a.txt" 2>&1 ||
    gate "THE IDENTITY GATE (a): $(head -n 1 "$SD/ident-a.txt" | cut -c1-240)"
  say "start config read (inside the private /dev): $(head -n 1 "$SD/ident-a.txt" | cut -c1-240)"
fi
CFG_OK=1

# ---- 3. THE WARDEN outside, then THE IDENTITY GATE (b) with the identity sampler inside the private /dev
if [ -n "$DRYF" ]; then
  say "warden_e198.py $SD/holderd (outside: et-who --check for the holder check inside; the watch on every process of the sitting)"
  say "ET_DEVICES=1 privdev_e198.sh bash ident_inner_e198.sh (the identity sampler, 10 s); et-who outside once it has sampled; THE IDENTITY GATE (b)"
else
  mkdir -p "$SD/holderd"
  python3 -I -B "$KIT/warden_e198.py" "$SD/holderd" --t0 "$T0" --session-pid "$$" --stop "$SD/smoke/STOP" --stop "$SD/x04/STOP" \
    > "$SD/warden.out" 2>&1 < /dev/null &
  WPID=$!
  for _ in $(seq 1 100); do [ -e "$SD/holderd/ready" ] && break; sleep 0.1; done
  [ -e "$SD/holderd/ready" ] || gate "the warden did not start ($(head -c 160 "$SD/warden.out" | tr '\n' ' '))"
  mkdir -p "$SD/ident"
  env ET_DEVICES=1 "${PRIV[@]}" bash "$KIT/ident_inner_e198.sh" "$SD/ident" "$GSHIM" "$HC" > "$SD/ident/inner.out" 2>&1 < /dev/null &
  ip=$!
  for _ in $(seq 1 100); do [ -s "$SD/ident/ident-first-sample" ] && break; sleep 0.1; done   # the identity sampler's first sample (at most 10 s)
  sleep 1
  sp=$(cat "$SD/ident/ident-sampler.pid" 2>/dev/null)
  timeout 30 et-who > "$SD/etwho-identity.txt" 2>&1; irc=$?
  python3 -I -B "$KIT/ident_e198.py" nodes "${sp:-0}" > "$SD/ident/sampler-nodes.json" 2>&1
  for _ in $(seq 1 200); do kill -0 "$ip" 2>/dev/null || break; sleep 0.1; done
  wait "$ip" 2>/dev/null
  python3 -I -B "$KIT/ident_e198.py" etwho "$SD/etwho-identity.txt" --rc "$irc" --me "$(id -un)" --pid "${sp:-0}" \
    --nodes "$SD/ident/sampler-nodes.json" --client "$SD/ident/ident-client.out" --client-rc "$(cat "$SD/ident/ident-client.rc" 2>/dev/null || echo 2)" \
    > "$SD/ident-b.txt" 2>&1 || gate "THE IDENTITY GATE (b): $(head -n 1 "$SD/ident-b.txt" | cut -c1-300)"
  say "identity read with the sampler running: $(head -n 1 "$SD/ident-b.txt" | cut -c1-300); $(tail -n 1 "$SD/ident/inner.out" | cut -c1-120)"
fi
DEADLINE=$((FIRST + CAP_S - 120))
if [ -z "$DRYF" ] && [ $((LAST_END - 180)) -lt "$DEADLINE" ]; then DEADLINE=$((LAST_END - 180)); fi
say "the runner's deadline: $(date -d @"$DEADLINE" '+%H:%M:%S %Z') (epoch $DEADLINE: the first card command + $CAP_S s - 120 s, never past the window's last end - 180 s); no run starts after it"
COMMON=(--arms "$ARMS" --host "$WRAP" --sampler "$GSHIM" --device 1 --holder-check "$HC" --deadline "$DEADLINE")
[ -n "$DRYF" ] && COMMON+=(--dry)

# ---- 5. THE SMOKE, then E193's smoke gate and the watch
[ -e "$SD/STOP" ] && gate "the operator's stop file ($SD/STOP) is present before the smoke"
say "smoke start: run_x04_e198a1.py $SD/smoke --smoke --blocks S,D,W,T,C (the five named arms, 10 device processes), in the private /dev"
env E198_RAWDIR="$SD/smoke-hostraw" "${PRIV[@]}" python3 -I -B "$RUNNER" "$SD/smoke" "${COMMON[@]}" --smoke --blocks S,D,W,T,C > "$SD/smoke-runner.out" 2>&1 < /dev/null
src=$?
say "smoke end: runner rc $src; $(python3 -I -B "$E193K/check_e193.py" stopreason "$SD/smoke" 2>&1 | tail -n 1 | cut -c1-200)"
dne_check smoke
if [ -n "$DRYF" ]; then
  say "check_e193.py smoke $SD/smoke --rc $src (E193's smoke gate) would read the smoke's X04 lines and telemetry: skipped; listed $(grep -c '^DRY ET_DEVICES=' "$SD/smoke-runner.out") device calls"
else
  [ ! -e "$SD/holderd/WATCH-STOP" ] || gate "the watch saw a card node other than card 1's: $(head -n 1 "$SD/holderd/WATCH-STOP" | cut -c1-200)"
  python3 -I -B "$E193K/check_e193.py" smoke "$SD/smoke" --rc "$src" > "$SD/smoke-gate.txt" 2>&1
  grep -q '^SMOKE GO' "$SD/smoke-gate.txt" || gate "the smoke gate failed: $(grep -m1 -E '^SMOKE' "$SD/smoke-gate.txt" | cut -c1-240)"
  say "$(grep -m1 '^SMOKE GO' "$SD/smoke-gate.txt" | cut -c1-240); the host's runtime lines: $(env -u LD_LIBRARY_PATH python3 -I -B "$KIT/dropruntime_e198.py" facts "$SD/smoke-hostraw/index.jsonl" | cut -c1-200)"
fi

# ---- 6. THE MAIN RUN
[ -e "$SD/STOP" ] && gate "the operator's stop file ($SD/STOP) is present before the main run"
say "main run start: run_x04_e198a1.py $SD/x04 --blocks $BLOCKS (9 passes, pass 0 the registered warm-up), in the private /dev"
env E198_RAWDIR="$SD/x04-hostraw" "${PRIV[@]}" python3 -I -B "$RUNNER" "$SD/x04" "${COMMON[@]}" --blocks "$BLOCKS" > "$SD/runner.out" 2>&1 < /dev/null
mrc=$?
why=$(python3 -I -B "$E193K/check_e193.py" stopreason "$SD/x04" 2>&1 | tail -n 1 | cut -c1-240)
CRASH=
if [ -n "$DRYF" ]; then
  say "main run end: runner rc $mrc; listed $(grep -c '^DRY ET_DEVICES=' "$SD/runner.out") device calls"
elif [ "$mrc" -eq 0 ]; then
  say "main run end: runner rc 0, every pass ($why)"
elif [ "${why#stop: }" != "$why" ]; then
  say "main run stopped: runner rc $mrc; $why; the passes done stand (E198.md 13)"
else
  CRASH=1
  say "main run ended without a registered stop: runner rc $mrc; $why: a crash, not a registered stop (E198.md 13 has no row for it): reported, nothing killed; a dated note decides whether its passes are reduced"
fi
dne_check x04
[ -z "$DRYF" ] && [ -e "$SD/holderd/WATCH-STOP" ] && say "the watch: $(head -n 1 "$SD/holderd/WATCH-STOP" | cut -c1-200)"
[ -z "$DRYF" ] && say "the host's runtime lines in the main run: $(env -u LD_LIBRARY_PATH python3 -I -B "$KIT/dropruntime_e198.py" facts "$SD/x04-hostraw/index.jsonl" | cut -c1-200)"

# ---- 7. the closing config read (reported), the warden, session end, the manifest
closing
rc=0; [ -z "$DRYF" ] && [ "$mrc" -ne 0 ] && rc=1
[ -n "$CRASH" ] && rc=4
finish "$rc"
