#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): THE REAL-PATH DESK TEST. E183's
# first session (aifoundry3 card 0, Fri 13 Nov 2026, T0 13:14:18 PST) stopped at its smoke gate on a check that runs only on the REAL path:
# block_e183_v2.sh runs check_e183.py block after every real block, the smoke included, and under V3_DRY it skips that check, so the kit's
# dry pass and every desk test passed while the first real smoke could not. This test runs the session's REAL path, V3_DRY unset, at the
# desk, against stand-ins for every device tool, and never near a card:
#   - it runs inside its own bubblewrap sandbox (a private /dev with no /dev/et*, an empty private /run/lock, a private PID namespace, the
#     hostname aifoundry3), re-executing itself there, and refuses if any /dev/et* node is visible; run it inside the round's no-device
#     sandbox too (aifoundry2 has a card of its own);
#   - THE TRAIN HOST IS A REAL BUILD: build_host_e183_v2.sh, on its real path, with a stand-in cmake (rb/fake_cmake_gcc_e183.sh, unchanged)
#     that compiles the patched main.cpp by g++-13 at -O2 against E184's desk stubs, with a Constants.h whose kernel path is the stand-in
#     tree's (as the box's configure writes it), linked with desk/mock_runtime_e183_v2.cpp: the device layer and the runtime are the mock,
#     each launch sleeps 400 ms (E183_MOCK_LAUNCH_MS: the 0.4 s window at 600 MHz), and every device call is appended to a record
#     (E183_DEVICE_RECORD), so the record counts the host processes that reached the device layer;
#   - the telemetry reader build/ettelem/ettelem is a stand-in that answers E128's guard's two words: config (the box's config line) and
#     sample --seconds --every-ms (10 Hz lines in the box's form, board 30 W, minshire[0] 50 C, 600 MHz); the holder readers (et-who, and
#     sudo -n /usr/local/sbin/et-holders, which D1's rule calls) are stand-ins that answer "No process holds ..." and name this test's own
#     card lock as its own; the card lock is the sandbox's own /run/lock/etsoc-shire0.lock; timeout and flock are the system's, behind
#     stand-ins that log each call; ssh, scp and rsync refuse. The operator's stop (build/e183/STOP) is written by the holder stand-in once
#     block 18310 has begun, so the queue runs that one train block to its end and stops before the next (about six minutes, not FULL's
#     hour).
# The cases:
#   0   the stand-in tree; the train host built by build v2's real path (BUILD OK, BUILD-E183.json, TRAIN-CHANGE OK); harness v3 with the
#       binaries; the sandbox (no /dev/et*, aifoundry3, a private PID namespace);
#   N1  THE NEGATIVE CONTROL: session_e183_v2.sh on the real path stops as aifoundry3 did: the stop-path test passes, the smoke's own gate
#       reads SMOKE GO, block v2's post-block check crashes with KeyError: 'block 18301 is not a planned train block (18310-18315)', the
#       smoke ends rc 1, and the gate line reads "smoke gate failed (stop test rc 0, smoke rc 1, gate 0): no train block runs";
#   N2  the same smoke under V3_DRY: block v2 reads rc 0 (the dry path never runs the check: why no desk test saw it);
#   W   without an aside: block v3's stop-path test rewrites the earlier stop test's directory in place, and its smoke moves the earlier
#       smoke to p18301.attempt-<epoch> inside e183-smoke/ (which step 11 copies whole): why note 6 moves the first session's two
#       directories aside before a second session;
#   P   THE REAL PATH: session_e183_v3.sh (harness v3 with the binaries, preflight v3, the config reads under the card lock, the stop-path
#       test, the smoke and its gate, queue v3 and block v3 18310 with all 52 train processes and its four anchors, the post-block check,
#       the closing config read): the stop test fires both stops on live samples; the smoke reads ok with no post-block check and its gate
#       SMOKE GO; block 18310's post-block check reads ok, 52 of 52 processes, 676 launch records by the schedule; the queue stops before
#       18311 at the operator's stop; 62 host processes reached the mock device layer (the smoke's 6, the block's 56), the train checks none;
#   A1-A11  each branch the dry path skips, on its real path: A1 D1's other-user rule (another user's holder line: block v3 exits 3, no
#       device call); A2 the card lock held by another process (exit 3); A3 a live stop (board 66 W: the block's status "stop", stop.json,
#       exit 5, no host run); A4 the sampler stalls (the runner exits 4, the block "fail", one anchor ran); A5 the runner's own check of the
#       registration's list (a changed file: exit 2 on the real path, rc 0 under --dry); A6 the session's harness with the binaries (a
#       changed host binary: exit 9, no device opened; the dry harness passes); A7 the block's preflight harness with the binaries (exit 2);
#       A8 the session's start gate on the real path (exit 8, the real log, no device opened); A9 lib.sh's skip of a train block whose
#       block.json exists (block v3 18310 again: "already done", exit 0, no device call); A10 D1's rule reads $USER: unset (as in this
#       test's own sandbox before it set USER as the box's ssh login does), its holder lines read empty and another user's holder passes
#       (the runner's --check-others exits 0, not 3), and session v3's new gate refuses first (exit 8, no device opened); A3b a live stop
#       during a launch (the board crosses 65 W inside the first anchor burst: the in-run watcher SIGTERMs the host, exit 5); A11 lib.sh's
#       ours_running (a device process of ours left running: exit 3);
#   Z   no process of the test left; no network call; no /dev/et* through the run.
#   bash tools/claims-v3/e183/desk/desktest_realpath_e183.sh <scratch dir outside the repository> > <log>
# Prints DESKTEST-REALPATH-E183 PASS or FAIL (<n> of <m>); exit 0 or 1. It needs bubblewrap, g++-13, GNU coreutils and python3 with numpy.
# About 12 minutes, most of it block 18310's 52 train processes at the mock's 0.4 s a launch.
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible here: run this test only inside a no-device sandbox"; exit 2; }
if [ "${E183RP_INNER:-}" != 1 ]; then
  [ -x /usr/bin/bwrap ] || { echo "no /usr/bin/bwrap (bubblewrap)"; exit 2; }
  mkdir -p "$S" || exit 2
  SELF=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")
  E183RP_INNER=1 exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --unshare-pid --proc /proc --unshare-uts \
    --hostname aifoundry3 --die-with-parent -- /bin/bash "$SELF" "$S"
fi
for c in g++-13 timeout flock gzip sha256sum rsync; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
/usr/bin/python3 -c 'import numpy' 2> /dev/null || { echo "/usr/bin/python3 has no numpy"; exit 2; }
S=$(cd "$S" && pwd)
T=$S/tree
B=$S/bin
REC=$S/device-record.txt
CALLS=$S/calls.log
ME=$(id -un)
main() {
rm -rf "${S:?}/tree" "${S:?}/bin" "${S:?}/stubs" "${S:?}/aside" "${S:?}/a5-out" "${S:?}/host.orig"
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B" "$S/stubs" "$S/aside"
rsync -a --delete --exclude __pycache__ "$SRC/tools/claims-v3/" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/enercat ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" -eq 0 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
nrec() { if [ -f "$REC" ]; then grep -c '^MOCKDEV createPcieDeviceLayer$' "$REC"; else echo 0; fi; }
nall() { if [ -f "$REC" ]; then grep -c . "$REC"; else echo 0; fi; }
fresh_t0() { local t; t=$(date +%s); while [ "$(date +%s)" -eq "$t" ]; do sleep 0.1; done; date +%s; }   # a session's own T0 (one log per T0)
DR=$T/build/claims-v3/aifoundry3
# ---- the stand-ins (PATH first): the holder readers, sudo for et-holders alone, logging timeout and flock, no network
cat > "$B/et-holders" <<'EOF'
#!/bin/bash
# desk stand-in for /usr/local/sbin/et-holders (its two line forms); never a real holder read
echo "et-holders $*" >> "$E183RP_DIR/calls.log"
if [ -n "${E183RP_STOP_DURING:-}" ] && [ -d "build/claims-v3/aifoundry3/e183/p$E183RP_STOP_DURING" ] && [ ! -e build/e183/STOP ]; then
  mkdir -p build/e183 && : > build/e183/STOP && echo "STOP written during p$E183RP_STOP_DURING (the operator's stop, by the stand-in)" >> "$E183RP_DIR/calls.log"
fi
n=0
if [ -n "${E183RP_OTHER_HOLDER:-}" ]; then printf '%-14s %s\n' /dev/et0_ops "otheruser 4242 00:10 ./other_host (desk stand-in)"; n=1; fi
if [ -e /run/lock/etsoc-shire0.lock ] && ! /usr/bin/flock -n /run/lock/etsoc-shire0.lock true 2> /dev/null; then
  printf '%-14s %s\n' lock:etsoc-shire0.lock "$(id -un) 1 00:01 bash (this test's own card lock, desk stand-in)"; n=1
fi
[ "$n" -eq 0 ] && echo "No process holds an ET-SoC-1 device node or card lock."
exit 0
EOF
cat > "$B/sudo" <<EOF
#!/bin/bash
echo "sudo \$*" >> "$CALLS"
[ "\$*" = "-n /usr/local/sbin/et-holders" ] && exec "$B/et-holders"
echo "STAND-IN SUDO: refused (only -n /usr/local/sbin/et-holders): \$*" >&2; exit 1
EOF
cat > "$B/et-who" <<EOF
#!/bin/bash
echo "et-who \$*" >> "$CALLS"
exec "$B/et-holders"
EOF
for n in timeout flock; do printf '#!/bin/bash\necho "%s $*" >> "%s"\nexec /usr/bin/%s "$@"\n' "$n" "$CALLS" "$n" > "$B/$n"; done
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$B/python3"
for n in ssh scp rsync; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/network-calls.log" "$n" > "$B/$n"; done
cp -p "$SRC/tools/claims-v3/e183/rb/fake_cmake_gcc_e183.sh" "$B/cmake"
chmod +x "$B"/*
mkdir -p "$T/build/ettelem"
cat > "$T/build/ettelem/ettelem" <<'EOF'
#!/usr/bin/python3
# desk stand-in for the telemetry reader (E128's guard execs it): config, and sample --seconds N --every-ms M in the box's line form
import json, math, os, sys, time
sys.dont_write_bytecode = True
d = os.environ.get("E183RP_DIR", "")
if d:
    open(os.path.join(d, "calls.log"), "a").write("ettelem " + " ".join(sys.argv[1:]) + "\n")
a = sys.argv[1:]
if a == ["config"]:
    print(json.dumps({"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600,
                      "minion_mv": 523}, separators=(",", ":")), flush=True)
    sys.exit(0)
if len(a) != 5 or a[0] != "sample" or a[1] != "--seconds" or a[3] != "--every-ms":
    print("ettelem stand-in: refused " + " ".join(a), file=sys.stderr)
    sys.exit(97)
secs, every = float(a[2]), float(a[4]) / 1000.0
board, die = float(os.environ.get("E183RP_BOARD_W", "30.0")), int(os.environ.get("E183RP_DIE_C", "50"))
stall = int(os.environ.get("E183RP_STALL_AFTER", "0"))
hot = float(os.environ.get("E183RP_HOT_AFTER", "0"))
t0, i = time.time(), 0
while time.time() - t0 < secs:
    if stall and i >= stall:
        time.sleep(0.5)
        continue
    w = round((66.0 if hot and time.time() - t0 >= hot else board) + 0.2 * math.sin(i / 7.0), 2)
    s = {"t_ms": int(time.time() * 1000), "took_ms": 21, "since_reset_ms": -1, "board_w": w,
         "sp": {"board_avg_w": w, "board_min_w": w, "board_max_w": w, "minion_w": [6.7, 5.8, 7.0], "sram_w": [1.9, 1.7, 2.0],
                "noc_w": [2.1, 1.7, 2.2], "minion_mv": [523, 517, 527], "sram_mv": [698, 694, 700], "noc_mv": [484, 482, 487],
                "minion_c": [die, die - 2, die + 4], "system_c": [0, 0, 0], "minion_mhz": [600, 600, 600], "noc_mhz": [400, 400, 400]},
         "temp_c": {"pmic": die, "ioshire": [die, die - 2, die + 4], "minshire": [die, die - 4, die + 6]},
         "die_mv": {"minion": 523}, "reg_mv": {"minion": 525}, "mhz": {"minion": 600, "noc": 400, "ddr": 933}}
    print(json.dumps(s, separators=(",", ":")), flush=True)
    i += 1
    time.sleep(max(0.0, t0 + i * every - time.time()))
EOF
chmod +x "$T/build/ettelem/ettelem"
# the desk stubs with the stand-in tree's kernel path in Constants.h (the box's configure writes the build tree's own path there)
cp -rp "$SRC/tools/claims-v3/e184/desk/stubs/." "$S/stubs/"
sed "s#^\#define KERNEL_ELF .*#\#define KERNEL_ELF \"$T/build/enercat-e183/kernel/enercat.elf\"#" "$SRC/tools/claims-v3/e184/desk/stubs/Constants.h" > "$S/stubs/Constants.h"
: > "$CALLS"; : > "$S/network-calls.log"; rm -f "$REC"
export PATH="$B:$PATH" E183RP_DIR="$S" E183_DEVICE_RECORD="$REC" E183_MOCK_LAUNCH_MS=400 USER="$ME" LOGNAME="$ME" \
  FAKE_CMAKE_STUBS="$S/stubs" FAKE_CMAKE_MOCK="$SRC/tools/claims-v3/e183/desk/mock_runtime_e183_v2.cpp" FAKE_CMAKE_CXX=g++-13
unset V3_DRY V3_DEVICE ET_DEVICES V3_FORCE E183_PROCESSES E183_SEQ E183_BLOCK E183_BUDGET_S E183_GAP_S E183_RESERVE_S E183_PLAN \
  E183RP_STOP_DURING E183RP_OTHER_HOLDER E183RP_BOARD_W E183RP_STALL_AFTER E183RP_HOT_AFTER
cd "$T" || return 2

step "0a. the sandbox: no /dev/et*, the hostname aifoundry3, a private PID namespace, the card lock the sandbox's own"
: > /run/lock/etsoc-shire0.lock
np=$(ps -e --no-headers | wc -l); hn=$(hostname); de=$(ls /dev/et* 2> /dev/null | wc -l)
echo "processes visible: $np; hostname $hn; /dev/et* nodes $de; /run/lock: $(ls /run/lock | tr '\n' ' ')"
[ "$de" -eq 0 ] && [ "$hn" = aifoundry3 ] && [ "$np" -lt 30 ]; ok $? "0a the sandbox"
step "0b. the train host by build_host_e183_v2.sh's REAL path (the stand-in cmake: g++-13 -O2, E184's stubs, the recording mock)"
bash tools/claims-v3/e183/build_host_e183_v2.sh > "$S/build.log" 2>&1; r=$?
tail -n 4 "$S/build.log"
echo "device record lines after the build (its train check): $(nall)"
[ "$r" -eq 0 ] && grep -q '^BUILD OK' "$S/build.log" && grep -q '^TRAIN-CHANGE OK' "$S/build.log" && [ -f build/enercat-e183/BUILD-E183.json ] \
  && [ "$(nall)" -eq 0 ]; ok $? "0b BUILD OK on the real path, TRAIN-CHANGE OK, no device call"
step "0c. harness v3 with the binaries (the real path's form) and the preflight v3"
python3 -B tools/claims-v3/e183/harness_e183_v3.py --binaries; r1=$?
bash tools/claims-v3/e183/preflight_e183_v3.sh | grep -m1 '^dmcmd_audit:'; r2=${PIPESTATUS[0]}
[ "$r1" -eq 0 ] && [ "$r2" -eq 0 ]; ok $? "0c HARNESS OK with the binaries; dmcmd_audit GO"

step "N1. THE NEGATIVE CONTROL: session_e183_v2.sh (block v2, check_e183.py block on the smoke) on the real path"
r0=$(nrec); t0=$(fresh_t0)
E183_T0=$t0 E183_LATEST_START="$(date -d '+1 hour' '+%F %T')" E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
  bash tools/claims-v3/e183/session_e183_v2.sh > "$S/n1.out" 2>&1; rc=$?
L=build/e183/session-t$t0.log
cut -d' ' -f4- "$L" | grep -E 'session start|stop-path|smoke|SMOKE|gate|queue|session end' | cut -c1-230
echo "check.err's last line: $(tail -n 1 "$DR/e183-smoke/p18301/check.err" 2>/dev/null)"
echo "the smoke's block.json: $(cat "$DR/e183-smoke/p18301/block.json" 2>/dev/null | cut -c1-400)"
echo "host processes that reached the device layer: $(( $(nrec) - r0 )) (the smoke's 4 bursts and 2 train processes)"
KE="KeyError: 'block 18301 is not a planned train block (18310-18315)'"
[ "$rc" -eq 0 ] && grep -q 'stop-path test rc=0' "$L" && grep -q 'smoke rc=1' "$L" && grep -q '^SMOKE GO: 4 bursts' "$L" \
  && grep -q 'smoke gate failed (stop test rc 0, smoke rc 1, gate 0): no train block runs' "$L" && tail -n 1 "$L" | grep -q "session end (T0 $t0)" \
  && [ "$(tail -n 1 "$DR/e183-smoke/p18301/check.err")" = "$KE" ] && grep -q "\"status\":\"fail\",\"note\":\"post-block check crashed: KeyError: 'block 18301 is not a planned train block (18310-18315)'\"" "$DR/e183-smoke/p18301/block.json" \
  && [ ! -e "$DR/e183-stoptest/p18302/check.err" ] && [ ! -e "build/e183/queue-t$t0.out" ] && [ "$(( $(nrec) - r0 ))" -eq 6 ]
ok $? "N1 session v2 stops at its smoke gate on the KeyError, as aifoundry3 did"
step "N2. the same smoke under V3_DRY: block v2 never runs the post-block check there"
r0=$(nall)
V3_DRY=1 bash tools/claims-v3/e183/block_e183_v2.sh 18301 --smoke > "$S/n2.out" 2>&1; rc=$?
tail -n 1 "$S/n2.out" | cut -c1-200
[ "$rc" -eq 0 ] && grep -q 'dry run (runner rc 0)' "$S/n2.out" && [ "$(nall)" -eq "$r0" ]; ok $? "N2 the dry smoke reads rc 0 (the check is skipped), no device call"

step "W. without an aside: block v3's stop test writes into the earlier p18302, and its smoke moves the earlier p18301 inside e183-smoke/"
j0=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["t0_ms"])' "$DR/e183-stoptest/p18302/block.json")
bash tools/claims-v3/e183/block_e183_v3.sh 18302 --stoptest > "$S/w1.out" 2>&1; r1=$?
j1=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["t0_ms"])' "$DR/e183-stoptest/p18302/block.json")
bash tools/claims-v3/e183/block_e183_v3.sh 18301 --smoke > "$S/w2.out" 2>&1; r2=$?
echo "e183-stoptest holds: $(ls "$DR/e183-stoptest" | tr '\n' ' '); its block.json t0_ms $j0 then $j1"
echo "e183-smoke holds: $(ls "$DR/e183-smoke" | sed 's/attempt-[0-9]*/attempt-<epoch>/' | tr '\n' ' ')"
[ "$r1" -eq 0 ] && [ "$r2" -eq 0 ] && [ "$(ls "$DR/e183-stoptest")" = p18302 ] && [ "$j1" -gt "$j0" ] \
  && [ "$(ls -d "$DR"/e183-smoke/p18301.attempt-* 2> /dev/null | wc -l)" -eq 1 ] && [ -f "$DR"/e183-smoke/p18301.attempt-*/check.err ]
ok $? "W the earlier stop test is overwritten in place and the earlier smoke kept inside e183-smoke/: an aside is needed"
mv "$DR/e183-smoke" "$S/aside/e183-smoke" && mv "$DR/e183-stoptest" "$S/aside/e183-stoptest"     # the test's own aside, out of the data root

step "P. THE REAL PATH: session_e183_v3.sh, V3_DRY unset; the operator's stop once block 18310 has begun"
r0=$(nrec); t0=$(fresh_t0); : > "$CALLS"
E183RP_STOP_DURING=18310 E183_T0=$t0 E183_LATEST_START="$(date -d '+1 hour' '+%F %T')" E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
  bash tools/claims-v3/e183/session_e183_v3.sh > "$S/p.out" 2>&1; rc=$?
L=build/e183/session-t$t0.log; Q=build/e183/queue-t$t0.out
cut -d' ' -f4- "$L" | grep -v '^\s*$' | cut -c1-230
echo "-- the queue:"; cut -c1-200 "$Q"
B10=$DR/e183/p18310
nruns=$(zcat "$B10/runs.jsonl.gz" | grep -c '^{'); ntr=$(zcat "$B10/train.jsonl.gz" | grep -c '^{')
echo "-- block 18310: block.json $(cut -c1-300 "$B10/block.json")"
echo "   check.json: $(python3 -c 'import json,sys; c=json.load(open(sys.argv[1])); print(c["status"], c["processes_good"], "of", c["processes_planned"], "processes good;", c["anchors_with_launches"], "anchors;", len(c["train_faults"]), "train faults;", c["train_samples_off_600"], "train samples off 600 MHz")' "$B10/check.json")"
echo "   anchor launch records $nruns; train launch records $ntr"
echo "-- the smoke: block.json $(cut -c1-300 "$DR/e183-smoke/p18301/block.json"); check.err present: $([ -e "$DR/e183-smoke/p18301/check.err" ] && echo yes || echo no)"
echo "-- the stop test: $(cat "$DR/e183-stoptest/p18302/board/stoptest.json" | python3 -c 'import json,sys; print("board:", json.load(sys.stdin)["result"])'); $(cat "$DR/e183-stoptest/p18302/die/stoptest.json" | python3 -c 'import json,sys; print("die:", json.load(sys.stdin)["result"])')"
ncfg=$(grep -c '^flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config$' "$CALLS")
nlock=$(grep -c '^flock -n 9$' "$CALLS"); nd1=$(grep -c '^sudo -n /usr/local/sbin/et-holders$' "$CALLS")
nsamp=$(grep -c '^ettelem sample --seconds [0-9]* --every-ms 100$' "$CALLS"); nhost=$(grep -c '^timeout 10 build/enercat-e183/host/enercat_host --pattern' "$CALLS")
echo "-- calls: config reads under the card lock $ncfg; block locks $nlock; D1 holder reads $nd1; 10 Hz samplers $nsamp; host runs under timeout 10 $nhost"
echo "-- host processes that reached the device layer: $(( $(nrec) - r0 )) (want 62: the smoke's 4 + 2, the block's 4 anchors + 52)"
[ "$rc" -eq 0 ] && grep -q 'kit note 6; plan FULL' "$L" && grep -q '^HARNESS OK: 132 files' "$L" && grep -q 'dmcmd_audit preflight rc=0 (dmcmd_audit: GO' "$L" \
  && grep -q 'config config-t'"$t0"'-start.json: {"tdp_w":0' "$L" && grep -q 'stop-path test rc=0' "$L" && grep -q 'smoke rc=0' "$L" \
  && grep -q '^SMOKE GO: 4 bursts' "$L" && grep -q 'smoke gate passed: queue starts (plan FULL)' "$L" && tail -n 1 "$L" | grep -q "session end (T0 $t0)" \
  && grep -q 'p18310 rc=0' "$Q" && grep -q 'STOP: stopping before p18311' "$Q" && grep -q 'done, 1 items' "$Q" ; ok $? "P1 session v3 ran its real path: harness, preflight, config reads, stop test, smoke, gate, queue, closing read"
python3 -c 'import json,sys; c=json.load(open(sys.argv[1])); sys.exit(0 if (c["status"], c["processes_good"], c["processes_planned"], c["anchors_with_launches"], c["train_faults"], c["train_samples_off_600"]) == ("ok", 52, 52, 4, [], 0) else 1)' "$B10/check.json" \
  && grep -q '"status":"ok"' "$B10/block.json" && [ "$ntr" -eq 676 ] && [ "$nruns" -ge 24 ]; ok $? "P2 block 18310's post-block check ran on the real path: ok, 52 of 52 processes, 676 launch records, 4 anchors"
grep -q '"status":"ok","note":"smoke: no post-block check' "$DR/e183-smoke/p18301/block.json" && [ ! -e "$DR/e183-smoke/p18301/check.err" ] \
  && [ ! -e "$DR/e183-smoke/p18301/check.json" ] && grep -q '"result": "both fired"' "$DR/e183-stoptest/p18302/board/stoptest.json" \
  && grep -q '"result": "both fired"' "$DR/e183-stoptest/p18302/die/stoptest.json"; ok $? "P3 the smoke reads ok with no post-block check (its gate decides); the stop test fired both stops"
[ "$ncfg" -eq 2 ] && [ "$nlock" -eq 3 ] && [ "$nd1" -ge 65 ] && [ "$nsamp" -eq 3 ] && [ "$nhost" -eq 62 ] && [ "$(( $(nrec) - r0 ))" -eq 62 ] \
  && [ ! -e "build/e183/session-dry-t$t0.log" ]; ok $? "P4 the real calls: 2 locked config reads, 3 block locks, D1 before every run, 3 samplers, 62 host runs, 62 device-layer opens"
rm -f "${T:?}/build/e183/STOP"

step "A1. D1's other-user rule on the real path: another user's holder line on card 0"
r0=$(nall)
E183RP_OTHER_HOLDER=1 bash tools/claims-v3/e183/block_e183_v3.sh 18311 > "$S/a1.out" 2>&1; rc=$?
grep -m1 'others present' "$S/a1.out" | cut -d' ' -f3- | cut -c1-200
[ "$rc" -eq 3 ] && [ "$(nall)" -eq "$r0" ] && [ ! -e "$DR/e183/p18311" ]; ok $? "A1 block v3 exits 3 before anything, no device call"
step "A2. the card lock held by another process (the real block_begin; under V3_DRY lib.sh takes no lock)"
r0=$(nall)
/usr/bin/flock -n /run/lock/etsoc-shire0.lock bash tools/claims-v3/e183/block_e183_v3.sh 18311 > "$S/a2.out" 2>&1; rc=$?
grep -m1 'card lock' "$S/a2.out" | cut -d' ' -f3- | cut -c1-200
[ "$rc" -eq 3 ] && [ "$(nall)" -eq "$r0" ]; ok $? "A2 block v3 exits 3 at the card lock, no device call"
step "A3. a live stop on the real path (the stand-in board at 66 W, over E171's 65 W)"
r0=$(nall)
E183RP_BOARD_W=66 bash tools/claims-v3/e183/block_e183_v3.sh 18312 > "$S/a3.out" 2>&1; rc=$?
echo "block.json: $(cut -c1-260 "$DR/e183/p18312/block.json")"
[ "$rc" -eq 5 ] && grep -q '"status":"stop"' "$DR/e183/p18312/block.json" && grep -q 'W >= 65 W' "$DR/e183/p18312/stop.json" && [ "$(nall)" -eq "$r0" ]
ok $? "A3 the runner's check before the first burst stops the block (exit 5, stop.json), no host run"
step "A3b. a live stop DURING a launch (the stand-in board crosses 65 W 17 s after the sampler starts, inside the first anchor burst)"
r0=$(nrec)
E183RP_HOT_AFTER=17 bash tools/claims-v3/e183/block_e183_v3.sh 18315 > "$S/a3b.out" 2>&1; rc=$?
grep -m1 'STOP ' "$DR/e183/p18315/run.log" | cut -c1-200
echo "block.json: $(cut -c1-200 "$DR/e183/p18315/block.json"); host processes that reached the device layer: $(( $(nrec) - r0 ))"
[ "$rc" -eq 5 ] && grep -q '"status":"stop"' "$DR/e183/p18315/block.json" && grep -q 'STOP e183/fadd.ps/zeros/h2@b18315-open: board' "$DR/e183/p18315/run.log" \
  && [ "$(( $(nrec) - r0 ))" -eq 1 ] && grep -q '"rc": -15\|"rc": 124\|"rc": 143' "$DR/e183/p18315/marks.jsonl"
ok $? "A3b the in-run watcher stops the burst in flight (its host SIGTERMed), the block reads stop, exit 5"
step "A4. the sampler stalls on the real path (it writes 30 lines, then nothing)"
r0=$(nrec)
E183RP_STALL_AFTER=30 bash tools/claims-v3/e183/block_e183_v3.sh 18313 > "$S/a4.out" 2>&1; rc=$?
echo "block.json: $(cut -c1-260 "$DR/e183/p18313/block.json")"
[ "$rc" -eq 1 ] && grep -q 'the sampler stopped writing' "$DR/e183/p18313/block.json" && [ "$(( $(nrec) - r0 ))" -eq 1 ]
ok $? "A4 the runner exits 4 at the next check, the block reads fail, one anchor ran"
step "A5. the runner's own check of the registration's list (real path) against --dry, with one registered file changed"
cp -p tools/claims-v3/e183/E183.md "$S/E183.md.orig"; echo "desk change" >> tools/claims-v3/e183/E183.md
r0=$(nall)
python3 -B tools/claims-v3/e183/run_e183.py "$S/a5-out" --root "$T" --block 18315 --tel-live "$S/a5-tel" > "$S/a5.out" 2>&1; r1=$?
python3 -B tools/claims-v3/e183/run_e183.py "$S/a5-out-dry" --root "$T" --block 18315 --tel-live "$S/a5-tel" --dry > "$S/a5d.out" 2>&1; r2=$?
cp -p "$S/E183.md.orig" tools/claims-v3/e183/E183.md
grep -m1 refusing "$S/a5.out" | cut -c1-160
[ "$r1" -eq 2 ] && grep -q 'changed tools/claims-v3/e183/E183.md' "$S/a5.out" && [ "$r2" -eq 0 ] && [ "$(nall)" -eq "$r0" ]
ok $? "A5 the real runner refuses (2) before any host run; the dry runner reads rc 0"
step "A6-A7. the harness with the binaries (real path) against a changed host binary: the session (9) and the block's preflight (2)"
cp -p build/enercat-e183/host/enercat_host "$S/host.orig"; printf 'x' >> build/enercat-e183/host/enercat_host
r0=$(nall); t0=$(fresh_t0)
E183_T0=$t0 E183_LATEST_START="$(date -d '+1 hour' '+%F %T')" E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
  bash tools/claims-v3/e183/session_e183_v3.sh > "$S/a6.out" 2>&1; r6=$?
grep -m1 'harness check failed' "build/e183/session-t$t0.log" | cut -d' ' -f4-
python3 -B tools/claims-v3/e183/harness_e183_v3.py > "$S/a6-dryharness.out" 2>&1; rh=$?
bash tools/claims-v3/e183/block_e183_v3.sh 18314 > "$S/a7.out" 2>&1; r7=$?
grep -m1 'preflight: harness' "$S/a7.out" | cut -c1-200
cp -p "$S/host.orig" build/enercat-e183/host/enercat_host
[ "$r6" -eq 9 ] && grep -q 'harness check failed: no device opened' "build/e183/session-t$t0.log" && [ "$rh" -eq 0 ] && [ "$r7" -eq 2 ] \
  && grep -q 'differs from BUILD-E183.json' "$S/a7.out" && [ "$(nall)" -eq "$r0" ] && [ ! -e "$DR/e183/p18314" ]
ok $? "A6-A7 the session stops (9) and the block refuses (2) before any device call; the harness without the binaries passes"
step "A8. the session's start gate on the real path (a past latest start)"
r0=$(nall); t0=$(fresh_t0)
E183_T0=$t0 E183_LATEST_START="$(date -d '-1 minute' '+%F %T')" E183_DEADLINE="$(date -d '+1 hour' '+%F %T')" \
  bash tools/claims-v3/e183/session_e183_v3.sh > /dev/null 2>&1; rc=$?
cut -d' ' -f4- "build/e183/session-t$t0.log"
[ "$rc" -eq 8 ] && grep -q 'no device opened' "build/e183/session-t$t0.log" && ! grep -q 'HARNESS' "build/e183/session-t$t0.log" && [ "$(nall)" -eq "$r0" ]
ok $? "A8 exit 8 with the real log, no device opened"
step "A9. lib.sh's skip of a train block whose block.json exists (block 18310 again after P)"
r0=$(nall)
bash tools/claims-v3/e183/block_e183_v3.sh 18310 > "$S/a9.out" 2>&1; rc=$?
grep -m1 'already done' "$S/a9.out" | cut -d' ' -f3-
[ "$rc" -eq 0 ] && grep -q 'e183 p18310 already done' "$S/a9.out" && [ "$(nall)" -eq "$r0" ]; ok $? "A9 'already done', exit 0, no device call"

step "A11. lib.sh's ours_running on the real path: a device process of ours still running (a stand-in named ettelem)"
mkdir -p "$S/leftover"; printf '#!/bin/bash\necho $$ > "%s/leftover/pid"\nwhile :; do sleep 1; done\n' "$S" > "$S/leftover/ettelem"; chmod +x "$S/leftover/ettelem"
setsid -f "$S/leftover/ettelem" < /dev/null > /dev/null 2>&1
for j in 1 2 3 4 5 6 7 8 9 10; do [ -s "$S/leftover/pid" ] && break; sleep 0.2; done
r0=$(nall)
bash tools/claims-v3/e183/block_e183_v3.sh 18311 > "$S/a11.out" 2>&1; rc=$?
kill "$(cat "$S/leftover/pid")" 2> /dev/null; sleep 1.5
grep -m1 'still running' "$S/a11.out" | cut -d' ' -f3- | cut -c1-160
[ "$rc" -eq 3 ] && grep -q 'one of our own device processes on this card is still running' "$S/a11.out" && [ "$(nall)" -eq "$r0" ]
ok $? "A11 block v3 exits 3 beside our own leftover device process, no device call"

step "A10. USER unset (the sandbox's own environment had none): D1's holder read sees no line; session v3 refuses before any device"
r0=$(nall)
E183RP_OTHER_HOLDER=1 python3 -B tools/claims-v3/e183/run_e183.py /dev/null --root "$T" --check-others > "$S/a10a.out" 2>&1; ra=$?
E183RP_OTHER_HOLDER=1 env -u USER python3 -B tools/claims-v3/e183/run_e183.py /dev/null --root "$T" --check-others > "$S/a10b.out" 2>&1; rb=$?
t0=$(fresh_t0)
E183_T0=$t0 E183_LATEST_START="$(date -d '+1 hour' '+%F %T')" E183_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
  env -u USER bash tools/claims-v3/e183/session_e183_v3.sh > /dev/null 2>&1; rs=$?
echo "D1 once with another user's holder line: USER set, runner exit $ra ($(cut -c1-90 "$S/a10a.out")); USER unset, exit $rb ($(head -c 90 "$S/a10b.out"))"
grep -m1 'USER is' "build/e183/session-t$t0.log" | cut -d' ' -f4- | cut -c1-160
[ "$ra" -eq 3 ] && [ "$rb" -eq 0 ] && [ "$rs" -eq 8 ] && grep -q "USER is '', not this login" "build/e183/session-t$t0.log" \
  && ! grep -q 'HARNESS' "build/e183/session-t$t0.log" && [ "$(nall)" -eq "$r0" ]
ok $? "A10 D1 fails open without USER (exit 0 against 3); session v3's USER gate stops it first (exit 8, no device opened)"

step "Z. no process of this test left; no network call; no /dev/et* through the run"
left=$(pgrep -c -f 'session_e183|queue_e183|block_e183|run_e183\.py|ettelem|enercat_host|sleep ')
nn=$(grep -c . "$S/network-calls.log"); de=$(ls /dev/et* 2> /dev/null | wc -l)
echo "processes left: $left; network calls: $nn; /dev/et* nodes: $de; device record: $(nall) lines, $(nrec) device-layer opens"
[ "$left" -eq 0 ] && [ "$nn" -eq 0 ] && [ "$de" -eq 0 ]; ok $? "Z"
echo
echo "DESKTEST-REALPATH-E183 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase): the session's real path at the desk (V3_DRY unset), a real GCC -O2 train host on the recording mock, no card"
return "$fail"
}
main 2>&1 | sed "s#$T#<tree>#g; s#$S#<scratch>#g; s#$SRC#<repo>#g; s#$HOME#<home>#g; s#\\b$ME\\b#<login>#g"
exit "${PIPESTATUS[0]}"
