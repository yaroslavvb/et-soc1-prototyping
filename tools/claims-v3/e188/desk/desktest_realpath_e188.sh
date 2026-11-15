#!/usr/bin/env bash
# E188 (Q182, the kit's dated note 2, KIT.md.dated-note-2.md, Sun 15 Nov 2026, before any E188 datum): THE REAL-PATH DESK TEST, E183's lesson
# (its kit note 6, 977c63d1: both E183 days were lost to a check that runs only on the REAL path, which no dry-path desk test could see).
# E188's kit (726a6b64, Thu 12 Nov) predates that lesson: its dry pass (dry_intel_e188.sh) runs every block under V3_DRY, where the session
# skips its config reads and its smoke gate, lib.sh takes no card lock and starts no sampler, and both runners print instead of launching.
# This test runs session_e188.sh's REAL path, V3_DRY unset, at the desk, against stand-ins for every device tool, and never near a card:
#   - it runs inside its own bubblewrap sandbox (a private /dev with no /dev/et*, a private /run/lock holding the sandbox's own empty card
#     lock file, a private PID namespace, the hostname aifoundry3), re-executing itself there, and refuses if any /dev/et* node is visible;
#     run it inside the round's no-device sandbox too (aifoundry2 has a card of its own);
#   - EVERY BINARY THE SESSION RUNS IS A REAL BUILD on the recording mock runtime, in its 600 MHz form (desk/mock_rt_e188_clock.cpp:
#     desk/mock_rt_e188.cpp, device memory host memory and every device-layer and runtime call appended to E188_DEVICE_RECORD, with each
#     FMA launch lasting its cycles at the card's pinned 600 MHz, so the host's own clock reading is the card's and the smoke gate's
#     clock check can pass at the desk; with the committed mock's fixed 40 ms a launch it read 0.06-3.1 GHz and the gate failed on the
#     clock alone, this note's first run of this test; the train host is built with MOCK_C_SKIP, which stores no C, since the engine's C at
#     a train's iters takes seconds a tile and would put a train process past its timeout 10, and no step of the session reads it), with
#     the accum engine
#     (rtl-sim/fma_toggle_v2/accum.c) as MOCK_ACCUM: E78's host (build/sparsity/host/sparsity_host, also aifoundry3's heater), the
#     C-logging host (build/ccheck/b/host/sparsity_host: patch_host_ccheck's patch alone) and the train host, built by build_host_e188.sh's
#     REAL path with the kit's stand-in cmake (rb/fake_cmake_gcc_e188.sh: g++-13 at -O2); the kernel is a stand-in file (the mock never
#     reads it); the tree's harness-e188.json pins these four stand-in binaries, as the runbook desk test pins its stand-in box's;
#   - the telemetry reader build/ettelem/ettelem is a stand-in (E183's form) that answers E128's guard's two words, `config` (the box's
#     config line) and `sample --seconds N --every-ms M` (10 Hz lines in the box's form: board 30 W, minshire[0] 50 C, 600 MHz; a board
#     level, a stall and a later hot board are test knobs); the holder readers (et-who, and `sudo -n /usr/local/sbin/et-holders`, which D1's
#     rule calls) are stand-ins that answer "No process holds ..." and name the sandbox's own card lock as this login's; timeout and flock are
#     the system's behind stand-ins that log each call; ssh, scp and rsync refuse; USER is the login, as aifoundry3's ssh login sets it.
# The cases:
#   0   the sandbox; the three builds (TRAIN-CHANGE OK read from the train host's behaviour, no device call); HARNESS OK 79 with the
#       binaries (check_e188.py's real form) and 72 without them; the device-command preflight GO;
#   P   THE REAL PATH: session_e188.sh FULL with the trains, V3_DRY unset, the operator's stop (build/e188/STOP) written before the launch so
#       the queue stops before its first block: the harness with the binaries, the train host's behaviour, the preflight, et-who, the start
#       config read under the card lock and timeout 10 through E128's guard, the stop-path test 18802 (each of its three stops fires on a
#       live sample), the smoke 18801 (its thirteen kinds items and two B05 train processes, every launch through the C wrapper), BOTH smoke
#       gates on the real smoke (smoke_gate_e188.py --part kinds and --part train: never run under V3_DRY), "smoke gate passed: queue
#       starts", the queue's STOP before p18820, the closing config read, et-who, "session end", blocks.txt and MANIFEST.sha256 over the
#       session's files and both blocks; the real calls counted;
#   P6  the smoke gate's clock check bites: P's smoke copied, every launch record's ghz moved 1% off 0.6: smoke_gate_e188.py --part kinds
#       reads FAIL on the clock (as it did on the committed mock's fixed-sleep clock);
#   P5  step 10 (rb/s20_wait_e188.sh, unchanged) on that real passing session, through a stand-in ssh that serves the sandbox's tree as
#       aifoundry3's ~/aifoundry: RUN-ENDED with its manifest (0), no GATE-STOPPED (E190's lesson, on a real passing log);
#   A1  D1's other-user rule on the real path: another user's holder line on card 0: the block exits 3 before anything, no device call;
#   A2  the card lock held by another process: the block exits 3 at lib.sh's lock, no device call;
#   A3  a live board stop (the stand-in board at 66 W): the smoke's runner stops before its first launch (its in-run watcher writes the
#       board stop into STOP, so the runner ends EXIT_STOP 8, or its own check EXIT_HOT 6), the block fails (1), no host run;
#   A4  the sampler stalls: the runner stops at its stale check (EXIT_STALL), the block fails (1);
#   A6  a changed C-logging host binary: the session stops at its harness check (9, "no device opened"); the block refuses in its preflight
#       (2); without the binaries (the dry form) the harness passes;
#   A8  the session's start gate past the latest start: 8, the real log, no device opened;
#   A9  lib.sh's skip of a block whose block.json reads ok (the smoke again after P): "already done", 0, no device call;
#   A10 D1 and USER (E183's kit note 6, section 6, carried): with another user's holder line and USER unset, block_e188.sh's own D1 reads no
#       holder and goes on (to its block-number check, 2, before any device), where with USER set it exits 3: E188's sessions rely on the
#       ssh login's USER, as E183's first sessions did; no E188 file gates it (reported, a carried gap; nothing here changes a box file);
#   Z   no process of the test left; no network call; no /dev/et* through the run.
#   bash tools/claims-v3/e188/desk/desktest_realpath_e188.sh <scratch dir outside the repository> > <log>
# Prints DESKTEST-REALPATH-E188 PASS or FAIL (<n> of <m>); exit 0 or 1. It needs bubblewrap, g++-13, a C compiler, GNU coreutils and
# /usr/bin/python3 with numpy. A few minutes (the smoke's thirteen items and two train processes at their real lengths).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
case "$S" in *session_e18*|*queue_e18*|*block_e18*) echo "the scratch directory's path must not name a session, a queue or a block"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible here: run this test only inside a no-device sandbox"; exit 2; }
if [ "${E188RP_INNER:-}" != 1 ]; then
  [ -x /usr/bin/bwrap ] || { echo "no /usr/bin/bwrap (bubblewrap)"; exit 2; }
  mkdir -p "$S" || exit 2
  SELF=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")
  E188RP_INNER=1 exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --unshare-pid --proc /proc --unshare-uts \
    --hostname aifoundry3 --die-with-parent -- /bin/bash "$SELF" "$S"
fi
for c in g++-13 cc timeout flock gzip sha256sum rsync; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
/usr/bin/python3 -c 'import numpy' 2> /dev/null || { echo "/usr/bin/python3 has no numpy"; exit 2; }
date --version 2> /dev/null | head -n 1 | grep -q 'GNU coreutils' || { echo "this test needs GNU date as date (the box's forms)"; exit 2; }
for v in RB_DRY RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
S=$(cd "$S" && pwd)
BOXH=$S/box; T=$BOXH/aifoundry; B=$S/bin
REC=$S/device-record.txt
CALLS=$S/calls.log
ME=$(id -un)
main() {
rm -rf "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/accum-b"
mkdir -p "$T/tools/claims-v3" "$B" "$S/out" "$S/accum-b"
rsync -a --delete --exclude __pycache__ "$SRC/tools/claims-v3/" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/sparsity ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
for rel in docs/reports/data/2026-10-20-bitflip-ladder/aifoundry3/hl/p1/tiles/lq_h0.b1.bin docs/reports/data/2026-10-27-e67-a-side-bit-prices/aifoundry3/hl/p750/tiles/aq_h0.b750.bin; do
  mkdir -p "$T/$(dirname "$rel")"; cp -p "$SRC/$rel" "$T/$rel"
done
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" -eq 0 ]; then npass=$((npass + 1)); echo "-> PASS ($2)"; else echo "-> FAIL ($2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
nrec() { if [ -f "$REC" ]; then grep -c '^MOCKDEV createPcieDeviceLayer$' "$REC"; else echo 0; fi; }
nall() { if [ -f "$REC" ]; then grep -c . "$REC"; else echo 0; fi; }
fresh_t0() { local t; t=$(date +%s); while [ "$(date +%s)" -eq "$t" ]; do sleep 0.1; done; date +%s; }
DR=$T/build/claims-v3/aifoundry3
# ---- the stand-ins (first on PATH): the holder readers, sudo for et-holders alone, logging timeout and flock, no network
cat > "$B/et-holders" <<'EOF'
#!/bin/bash
# desk stand-in for /usr/local/sbin/et-holders (its two line forms); never a real holder read
echo "et-holders $*" >> "$E188RP_DIR/calls.log"
n=0
if [ -n "${E188RP_OTHER_HOLDER:-}" ]; then printf '%-14s %s\n' /dev/et0_ops "otheruser 4242 00:10 ./other_host (desk stand-in)"; n=1; fi
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
cp -p "$SRC/tools/claims-v3/e188/rb/fake_cmake_gcc_e188.sh" "$B/cmake"
chmod +x "$B"/*
mkdir -p "$T/build/ettelem"
cat > "$T/build/ettelem/ettelem" <<'EOF'
#!/usr/bin/python3
# desk stand-in for the telemetry reader (E128's guard execs it): config, and sample --seconds N --every-ms M in the box's line form
import json, math, os, sys, time
sys.dont_write_bytecode = True
d = os.environ.get("E188RP_DIR", "")
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
board, die = float(os.environ.get("E188RP_BOARD_W", "30.0")), int(os.environ.get("E188RP_DIE_C", "50"))
stall = int(os.environ.get("E188RP_STALL_AFTER", "0"))
t0, i = time.time(), 0
while time.time() - t0 < secs:
    if stall and i >= stall:
        time.sleep(0.5)
        continue
    w = round(board + 0.2 * math.sin(i / 7.0), 2)
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
: > "$CALLS"; : > "$S/network-calls.log"; rm -f "$REC"
export PATH="$B:$PATH" E188RP_DIR="$S" E188_DEVICE_RECORD="$REC" MOCK_SLEEP_MS=40 USER="$ME" LOGNAME="$ME" \
  FAKE_CMAKE_MOCKRT="$T/tools/claims-v3/ccheck/mockrt" FAKE_CMAKE_MOCK="$S/mock_train.cpp" FAKE_CMAKE_CXX=g++-13
unset V3_DRY V3_DEVICE ET_DEVICES V3_FORCE E188_PLAN E188_TRAINS E188_SEQ E188_BLOCK E188_BUDGET_S E188_GAP_S E188_RESERVE_S E188_STOPTEST \
  E78_TARGET E78_PREHEAT E188RP_OTHER_HOLDER E188RP_BOARD_W E188RP_STALL_AFTER
cd "$T" || return 2

step "0a. the sandbox: no /dev/et*, the hostname aifoundry3, a private PID namespace, the card lock the sandbox's own"
: > /run/lock/etsoc-shire0.lock
np=$(ps -e --no-headers | wc -l); hn=$(hostname); de=$(ls /dev/et* 2> /dev/null | wc -l)
echo "processes visible: $np; hostname $hn; /dev/et* nodes $de; /run/lock: $(ls /run/lock | tr '\n' ' ')"
[ "$de" -eq 0 ] && [ "$hn" = aifoundry3 ] && [ "$np" -lt 30 ]; ok $? "0a the sandbox"

step "0b. the builds on the recording mock: the accum engine, E78's host, the C-logging host, and the train host by build_host_e188.sh's REAL path"
INC=$T/tools/claims-v3/ccheck/mockrt/include; MOCK=$T/tools/claims-v3/e188/desk/mock_rt_e188_clock.cpp
cc -O2 -o "$S/accum-b/accum" "$SRC/rtl-sim/fma_toggle_v2/accum.c" -lm 2> "$S/accum.err"; ra=$?
export MOCK_ACCUM=$S/accum-b/accum
mkdir -p build/sparsity/host build/sparsity/kernel build/ccheck/b/host "$S/ccsrc/host"
g++-13 -std=c++17 -O2 -I "$INC" -I workloads/sparsity workloads/sparsity/host/main.cpp "$MOCK" -o build/sparsity/host/sparsity_host 2> "$S/e78.err"; r1=$?
cp workloads/sparsity/host/main.cpp "$S/ccsrc/host/main.cpp"; cp workloads/sparsity/sparsity_args.h "$S/ccsrc/"
/usr/bin/python3 -I -B - "$T/tools/claims-v3/ccheck" "$S/ccsrc/host/main.cpp" <<'PYEOF'
import sys
sys.path.insert(0, sys.argv[1])
import patch_host_ccheck as PC
p = sys.argv[2]
text = PC.patch_text(open(p).read())
open(p, "w").write(text)
PYEOF
g++-13 -std=c++17 -O2 -I "$INC" -I "$S/ccsrc" "$S/ccsrc/host/main.cpp" "$MOCK" -o build/ccheck/b/host/sparsity_host 2> "$S/cc.err"; r2=$?
echo "desk stand-in kernel: the mock runtime never reads it" > build/sparsity/kernel/sparsity.elf
printf '// the train host'"'"'s mock (the real-path test): the 600 MHz mock with no C stored (MOCK_C_SKIP)\n#define MOCK_C_SKIP 1\n#include "%s"\n' "$MOCK" > "$S/mock_train.cpp"
bash tools/claims-v3/e188/build_host_e188.sh > "$S/build.log" 2>&1; r3=$?
tail -n 3 "$S/build.log" | cut -c1-200
echo "accum rc $ra; E78's host rc $r1; the C-logging host rc $r2; build_host_e188.sh rc $r3; device record lines after the builds: $(nall)"
[ "$ra" -eq 0 ] && [ "$r1" -eq 0 ] && [ "$r2" -eq 0 ] && [ "$r3" -eq 0 ] && grep -q '^BUILD OK' "$S/build.log" && grep -q '^TRAIN-CHANGE OK' "$S/build.log" \
  && [ -s build/e188host/SHA256 ] && [ "$(nall)" -eq 0 ]; ok $? "0b the three hosts built; the train host by its real build path, TRAIN-CHANGE OK read from its behaviour, no device call"

step "0c. the tree's harness pins the four stand-in binaries; check_e188.py with the binaries (79) and without (72); the preflight"
/usr/bin/python3 -I -B - "$T" <<'PYEOF'
import hashlib, json, os, sys
t = sys.argv[1]
p = os.path.join(t, "tools/claims-v3/e188/harness-e188.json")
h = json.load(open(p))
for rel in h["box_binaries_sha256"]:
    h["box_binaries_sha256"][rel] = hashlib.sha256(open(os.path.join(t, rel), "rb").read()).hexdigest()
open(p, "w").write(json.dumps(h, indent=1) + "\n")
print("the tree's harness-e188.json pins its four stand-in binaries")
PYEOF
python3 -B tools/claims-v3/e188/check_e188.py > "$S/ck79.out" 2>&1; c1=$?
python3 -B tools/claims-v3/e188/check_e188.py --desk > "$S/ck72.out" 2>&1; c2=$?
bash tools/claims-v3/e188/preflight_e188.sh > "$S/pf.out" 2>&1; c3=$?
grep -h -m1 '^HARNESS' "$S/ck79.out" "$S/ck72.out"; grep -m1 '^dmcmd_audit:' "$S/pf.out"
[ "$c1" -eq 0 ] && grep -q '^HARNESS OK: 79 files' "$S/ck79.out" && [ "$c2" -eq 0 ] && grep -q '^HARNESS OK: 72 files' "$S/ck72.out" && [ "$c3" -eq 0 ]
ok $? "0c HARNESS OK 79 with the binaries, 72 without; dmcmd_audit GO"

step "P. THE REAL PATH: session_e188.sh FULL with the trains, V3_DRY unset; the operator's stop written first, so the queue stops before its first block"
r0=$(nrec); t0=$(fresh_t0); : > "$CALLS"
mkdir -p build/e188; : > build/e188/STOP
E188_T0=$t0 E188_LATEST_START="$(date -d '+1 hour' '+%F %T')" E188_DEADLINE="$(date -d '+3 hour' '+%F %T')" \
  bash tools/claims-v3/e188/session_e188.sh > "$S/p.out" 2>&1; rc=$?
SD=build/e188/T$t0; L=$SD/session.log; Q=$SD/queue.out
cut -d' ' -f4- "$L" | grep -E 'session start|HARNESS|TRAIN-CHANGE|dmcmd|config |stop-path|smoke|SMOKE|gate|queue|session end|No process' | cut -c1-200
echo "-- the queue:"; cut -c1-200 "$Q"
echo "-- the stop-path test: $(tr '\n' ' ' < "$DR/e188-stoptest/p18802/stoptest.rc"); STOP files $(ls "$DR/e188-stoptest/p18802" | grep -c '^STOP\.')"
echo "-- the smoke: block.json $(cut -c1-200 "$DR/e188-smoke/p18801/block.json"); train.rc $(cat "$DR/e188-smoke/p18801/train.rc" 2>/dev/null)"
nruns=$(grep -c '^{' "$DR/e188-smoke/p18801/runs.jsonl" 2>/dev/null); ntr=$(grep -c '^{' "$DR/e188-smoke/p18801/train/train.jsonl" 2>/dev/null)
ncl=$(grep -c '^{' "$DR/e188-smoke/p18801/c-log.jsonl" 2>/dev/null)
echo "   kinds launch records $nruns; train launch records $ntr; C log lines $ncl"
echo "-- blocks.txt: $(tr '\n' ' ' < "$SD/blocks.txt"); MANIFEST.sha256 $(grep -c . "$SD/MANIFEST.sha256") files ($(grep -c 'e188-smoke/p18801/' "$SD/MANIFEST.sha256") of the smoke's, $(grep -c 'e188-stoptest/p18802/' "$SD/MANIFEST.sha256") of the stop test's)"
ncfg=$(grep -c '^flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config$' "$CALLS")
nlock=$(grep -c '^flock -n 9$' "$CALLS"); nd1=$(grep -c '^sudo -n /usr/local/sbin/et-holders$' "$CALLS")
nsamp=$(grep -c '^ettelem sample --seconds [0-9]* --every-ms 100$' "$CALLS"); nhost=$(grep -c '^timeout 10 tools/claims-v3/ccheck/sparsity_ccheck.sh --test fma' "$CALLS")
nwho=$(grep -c '^et-who' "$CALLS"); ndev=$(( $(nrec) - r0 ))
echo "-- calls: locked config reads $ncfg; block locks $nlock; D1 holder reads $nd1; 10 Hz samplers $nsamp; host runs through the wrapper under timeout 10 $nhost; et-who $nwho; host processes that reached the mock device layer $ndev"
[ "$rc" -eq 0 ] && grep -q 'session start (budget anchor' "$L" && grep -q '^HARNESS OK: 79 files' "$L" && grep -q '^TRAIN-CHANGE OK: ' "$L" \
  && grep -q 'dmcmd_audit preflight rc=0 (dmcmd_audit: GO' "$L" && grep -q 'config config-session-start.json: {"tdp_w":0' "$L" \
  && grep -q 'stop-path test rc=0' "$L" && grep -q 'smoke rc=0' "$L" && grep -q 'smoke gate passed: queue starts (plan FULL)' "$L" \
  && grep -q 'config config-session-end.json: {"tdp_w":0' "$L" && tail -n 1 "$L" | grep -q 'session end' && grep -q 'STOP: stopping before p18820' "$Q"
ok $? "P1 the session's real path: harness with the binaries, the train host's behaviour, the preflight, the locked config reads, the stop-path test, the smoke, its gates, the queue's stop, the closing read"
grep -q '^SMOKE-GATE (kinds) PASS' "$L" && grep -q '^SMOKE-GATE (train) PASS' "$L" && [ "$(tr '\n' ' ' < "$DR/e188-stoptest/p18802/stoptest.rc")" = "die:rc=6 board:rc=6 watch:rc=6 " ] \
  && grep -q '"status":"ok"' "$DR/e188-smoke/p18801/block.json" && [ "$(cat "$DR/e188-smoke/p18801/train.rc" 2>/dev/null)" = 0 ] && [ "$nruns" -ge 13 ] && [ "$ntr" -eq 28 ]
ok $? "P2 both smoke gates ran on the real smoke and passed (never run under V3_DRY); the stop-path test's three stops fired (6 each); the smoke's 13 kinds items and 2 B05 processes (28 launch records)"
[ "$(grep -c . "$SD/blocks.txt")" -eq 2 ] && grep -q 'e188-stoptest/p18802$' "$SD/blocks.txt" && grep -q 'e188-smoke/p18801$' "$SD/blocks.txt" \
  && [ "$(grep -c 'e188-smoke/p18801/' "$SD/MANIFEST.sha256")" -ge 5 ] && ( cd "$T" && sha256sum -c --quiet "$SD/MANIFEST.sha256" ) && [ -s build/e188/LAST_T0 ] \
  && [ "$(cat build/e188/LAST_T0)" = "$t0" ] && [ ! -e "build/e188/T$t0-dry" ]
ok $? "P3 the real session's own files: LAST_T0, blocks.txt naming both blocks, MANIFEST.sha256 over the session's files and both blocks' (every line reads back), no dry directory"
[ "$ncfg" -eq 2 ] && [ "$nlock" -eq 2 ] && [ "$nd1" -eq 4 ] && [ "$nsamp" -eq 2 ] && [ "$nhost" -eq 15 ] && [ "$ndev" -eq "$nhost" ] && [ "$nwho" -eq 2 ]
ok $? "P4 the real calls: 2 config reads under the card lock and timeout 10, 2 block locks, D1's holder read twice a block (before anything, and after the card lock; the runners read ps before every run, card 0 having no ET_DEVICES), 2 samplers at 10 Hz, 15 host runs (13 kinds items, 2 train processes) through the wrapper under timeout 10, each reaching the mock device layer, et-who at both ends"
cp "$L" "$S/passing-session.log"

step "P6. the smoke gate's clock check bites: P's smoke copied, every launch record's clock moved 1% off 0.6 GHz"
rm -rf "${S:?}/p6"; mkdir -p "$S/p6"; cp -rp "$DR/e188-smoke/p18801" "$S/p6/p18801"
/usr/bin/python3 -I -B - "$S/p6/p18801/runs.jsonl" <<'PYEOF'
import json, sys
p = sys.argv[1]
rows = []
for ln in open(p):
    r = json.loads(ln) if ln.strip().startswith("{") else None
    if isinstance(r, dict) and isinstance(r.get("ghz"), (int, float)):
        r["ghz"] = round(r["ghz"] * 1.01, 4)
    rows.append(json.dumps(r) if r is not None else ln.rstrip("\n"))
open(p, "w").write("\n".join(rows) + "\n")
PYEOF
python3 -B tools/claims-v3/e188/smoke_gate_e188.py "$S/p6/p18801" "$DR/e188-stoptest/p18802" --part kinds > "$S/p6.out" 2>&1; r6=$?
grep -m1 '^SMOKE-GATE' "$S/p6.out" | cut -c1-160
[ "$r6" -ne 0 ] && grep -q '^SMOKE-GATE (kinds) FAIL' "$S/p6.out" && grep -q 'outside 0.595-0.605' "$S/p6.out"
ok $? "P6 the kinds gate fails on a clock 1% off 600 MHz (its clock check reads the launch records)"

step "P5. step 10 (unchanged) on that real passing session, through a stand-in ssh that serves this tree as aifoundry3's ~/aifoundry"
mkdir -p "$S/b10"
cat > "$S/b10/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls-b10.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
[ "\$host" = aifoundry3 ] || { echo "STAND-IN SSH: refusing host \$host" >&2; exit 97; }
[ "\$cmd" = true ] && exit 0
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: refusing the command \$cmd" >&2; exit 97; }
cd "$BOXH" && HOME="$BOXH" exec bash -s
EOF
chmod +x "$S/b10/ssh"
mkdir -p build/q141k; echo "$t0" > build/q141k/e188.T0; echo "$t0" > "$S/out/e188-T0.txt"
PATH="$S/b10:$PATH" RB_OUT="$S/out" RB_LOCK="$S/lock.txt" RB_WAIT_LOOP_S=3 bash "$SRC/tools/claims-v3/e188/rb/s20_wait_e188.sh" > "$S/p5.out" 2>&1; r5=$?
grep -E '^(RUN-|GATE-|MANIFEST-)|STOP|has ended|still runs' "$S/p5.out" | cut -c1-160
[ "$r5" -eq 0 ] && grep -q '^RUN-ENDED e188' "$S/p5.out" && grep -q '^MANIFEST-WRITTEN' "$S/p5.out" && ! grep -q 'GATE-STOPPED' "$S/p5.out"
ok $? "P5 step 10 reads the real passing session RUN-ENDED with its manifest (0), no GATE-STOPPED"
rm -f "${T:?}/build/e188/STOP"
mkdir -p "$S/p-session"; mv "$DR/e188-smoke" "$S/p-session/e188-smoke"; mv "$DR/e188-stoptest" "$S/p-session/e188-stoptest"     # out of the data root

step "A1. D1's other-user rule on the real path: another user's holder line on card 0"
r0=$(nall)
E188RP_OTHER_HOLDER=1 bash tools/claims-v3/e188/block_e188.sh 18801 --smoke > "$S/a1.out" 2>&1; rc=$?
grep -m1 'others present' "$S/a1.out" | cut -d' ' -f3- | cut -c1-200
[ "$rc" -eq 3 ] && [ "$(nall)" -eq "$r0" ] && [ ! -e "$DR/e188-smoke/p18801" ]; ok $? "A1 the block exits 3 before anything, no device call"
step "A2. the card lock held by another process (the real block_begin; under V3_DRY lib.sh takes no lock)"
r0=$(nall)
/usr/bin/flock -n /run/lock/etsoc-shire0.lock bash tools/claims-v3/e188/block_e188.sh 18801 --smoke > "$S/a2.out" 2>&1; rc=$?
grep -m1 'card lock' "$S/a2.out" | cut -d' ' -f3- | cut -c1-200
[ "$rc" -eq 3 ] && [ "$(nall)" -eq "$r0" ]; ok $? "A2 the block exits 3 at the card lock, no device call"
rm -rf "${DR:?}/e188-smoke"
step "A3. a live board stop on the real path (the stand-in board at 66 W, over the registered 65 W)"
r0=$(nrec)
E188RP_BOARD_W=66 bash tools/claims-v3/e188/block_e188.sh 18801 --smoke > "$S/a3.out" 2>&1; rc=$?
grep -h -m1 'STOP' "$DR/e188-smoke/p18801/STOP" "$DR/e188-smoke/p18801/run.log" 2>/dev/null | cut -c1-180
echo "block.json: $(cut -c1-200 "$DR/e188-smoke/p18801/block.json"); host processes that reached the device layer: $(( $(nrec) - r0 ))"
[ "$rc" -eq 1 ] && grep -qE 'run_e188 or run_e188t exit [68] ' "$DR/e188-smoke/p18801/block.json" && grep -q 'board' "$DR/e188-smoke/p18801/STOP" \
  && grep -q '>= 65.0 W' "$DR/e188-smoke/p18801/STOP" && [ "$(( $(nrec) - r0 ))" -eq 0 ]
ok $? "A3 a board stop at 65 W before the first launch (the watcher's STOP, exit 8, or the runner's own, 6): the block fails (1), no host run"
rm -rf "${DR:?}/e188-smoke"
step "A4. the sampler stalls on the real path (it writes 40 lines, then nothing)"
E188RP_STALL_AFTER=40 bash tools/claims-v3/e188/block_e188.sh 18801 --smoke > "$S/a4.out" 2>&1; rc=$?
echo "block.json: $(cut -c1-200 "$DR/e188-smoke/p18801/block.json")"
grep -h -m1 -i 'stale\|stopped writing\|older than' "$DR/e188-smoke/p18801/run.log" "$S/a4.out" 2>/dev/null | cut -c1-180
[ "$rc" -eq 1 ] && grep -q '"status":"failed"' "$DR/e188-smoke/p18801/block.json"; ok $? "A4 the runner stops at its stale check, the block fails (1)"
rm -rf "${DR:?}/e188-smoke"
step "A6. a changed C-logging host binary: the session (9) and the block's preflight (2); the harness without the binaries passes"
cp -p build/ccheck/b/host/sparsity_host "$S/cc.orig"; printf 'x' >> build/ccheck/b/host/sparsity_host
r0=$(nall); t0=$(fresh_t0)
E188_T0=$t0 E188_LATEST_START="$(date -d '+1 hour' '+%F %T')" E188_DEADLINE="$(date -d '+3 hour' '+%F %T')" \
  bash tools/claims-v3/e188/session_e188.sh > "$S/a6.out" 2>&1; r6=$?
grep -m1 'harness check failed' "build/e188/T$t0/session.log" | cut -d' ' -f4-
python3 -B tools/claims-v3/e188/check_e188.py --desk > "$S/a6-desk.out" 2>&1; rh=$?
bash tools/claims-v3/e188/block_e188.sh 18801 --smoke > "$S/a7.out" 2>&1; r7=$?
grep -m1 'preflight: check_e188' "$S/a7.out" | cut -c1-160
cp -p "$S/cc.orig" build/ccheck/b/host/sparsity_host
[ "$r6" -eq 9 ] && grep -q 'harness check failed: no device opened' "build/e188/T$t0/session.log" && [ "$rh" -eq 0 ] && [ "$r7" -eq 2 ] \
  && [ "$(nall)" -eq "$r0" ] && [ ! -e "$DR/e188-smoke/p18801" ]
ok $? "A6 the session stops (9, no device opened) and the block refuses (2) before any device call; the harness without the binaries passes"
step "A8. the session's start gate on the real path (a past latest start)"
r0=$(nall); t0=$(fresh_t0)
E188_T0=$t0 E188_LATEST_START="$(date -d '-1 minute' '+%F %T')" E188_DEADLINE="$(date -d '+1 hour' '+%F %T')" \
  bash tools/claims-v3/e188/session_e188.sh > /dev/null 2>&1; rc=$?
cut -d' ' -f4- "build/e188/T$t0/session.log" | cut -c1-160
[ "$rc" -eq 8 ] && grep -q 'no device opened' "build/e188/T$t0/session.log" && ! grep -q 'HARNESS' "build/e188/T$t0/session.log" && [ "$(nall)" -eq "$r0" ]
ok $? "A8 exit 8 with the real log, no device opened"
step "A9. lib.sh's skip of a block whose block.json reads ok (P's smoke put back)"
mv "$S/p-session/e188-smoke" "$DR/e188-smoke"
r0=$(nall)
bash tools/claims-v3/e188/block_e188.sh 18801 --smoke > "$S/a9.out" 2>&1; rc=$?
grep -m1 'already done' "$S/a9.out" | cut -d' ' -f3-
[ "$rc" -eq 0 ] && grep -q 'p18801 already done' "$S/a9.out" && [ "$(nall)" -eq "$r0" ]; ok $? "A9 'already done', exit 0, no device call"
mv "$DR/e188-smoke" "$S/p-session/e188-smoke"
step "A10. D1 and USER (E183's kit note 6, section 6, carried): another user's holder line, USER set and then unset (block 18809: no E188 block, refused after D1)"
r0=$(nall)
E188RP_OTHER_HOLDER=1 bash tools/claims-v3/e188/block_e188.sh 18809 > "$S/a10a.out" 2>&1; ra=$?
E188RP_OTHER_HOLDER=1 env -u USER bash tools/claims-v3/e188/block_e188.sh 18809 > "$S/a10b.out" 2>&1; rb=$?
echo "USER set: exit $ra ($(grep -m1 -o 'others present.*' "$S/a10a.out" | cut -c1-80)); USER unset: exit $rb ($(tail -n 1 "$S/a10b.out" | cut -c1-110))"
[ "$ra" -eq 3 ] && [ "$rb" -eq 2 ] && grep -q 'no E188 block on aifoundry3' "$S/a10b.out" && [ "$(nall)" -eq "$r0" ]
ok $? "A10 block_e188.sh's D1 reads another user's holder with USER set (3) and none without it (on to the block check, 2): a carried gap, reported (no device call either way)"

step "Z. no process of this test left; no network call; no /dev/et* through the run"
left=$(pgrep -c -f 'session_e188|queue_e188|block_e188|run_e188|ettelem|sparsity_host|sleep ')
nn=$(grep -c . "$S/network-calls.log"); de=$(ls /dev/et* 2> /dev/null | wc -l)
echo "processes left: $left; network calls: $nn; /dev/et* nodes: $de; device record: $(nall) lines, $(nrec) device-layer opens"
[ "$left" -eq 0 ] && [ "$nn" -eq 0 ] && [ "$de" -eq 0 ]; ok $? "Z"
echo
echo "DESKTEST-REALPATH-E188 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase): the session's real path at the desk (V3_DRY unset), every binary a real build on the recording mock, no card"
return "$fail"
}
main 2>&1 | sed "s#$T#<tree>#g; s#$S#<scratch>#g; s#$SRC#<repo>#g; s#$HOME#<home>#g; s#\\b$ME\\b#<login>#g"
exit "${PIPESTATUS[0]}"
