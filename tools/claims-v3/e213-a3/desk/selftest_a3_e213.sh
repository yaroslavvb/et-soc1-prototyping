#!/usr/bin/env bash
# E213 Amendment A3 (Q219, lane a3-e213, Wed 18 Nov 2026, before any datum of E213's arm B): THE DESK TEST OF A3, in two parts.
# PART 1, A3's order, its wrapper, the runner through it and the scorer's reading by point: desk/selftest_order_a3_e213.py (cases O1-O5, R1, R2,
# S1; its docstring has them), run from the scratch repository below.
# PART 2, ARM B'S RUNBOOK AS AMENDED BY A2 AND A3, in A2's runbook-test form (tools/claims-v3/e213-a2/desk/selftest_a2_e213.sh: a FAKE ssh and
# rsync, a stand-in aifoundry1 box per case with its own tree, lock folder, ledger and RB_OUT, k6's bounded runner and the kit's and A2's own steps
# unchanged around A3's), its fwgate stand-ins as fwgate's README requires (FWGATE_DESK_TEST=1 and every stand-in); THE BOXES BOOT BEFORE E82's
# FIRMWARE READ (2026-10-26 15:18:24 PDT, A2's continuity case), so A2's step 4 passes by CONTINUITY with no read and A2's launch guard reads
# "identity ... ok" (A2's own desk test covers its other cases). The box shell carries ET_DEVICES=1. Cases:
#   Y   the kit's step 1 (window), A2's step 4 (CONTINUITY), the kit's step 5 (HARNESS OK on the stand-in box), then A3's ROW 5b: 0, the rsync
#       sent A3's three files, "A3-PINS OK 3 of 3" and "A3-ORDER OK: arm B 85 runs, ..." on the box, RB_OUT/e213-a3-sync-B.txt
#   L9  then A3's STEP 9: 0, LAUNCHED (A3's session_e213.sh), A2's guard ok, A3-PINS and A3-ORDER read in the launch call; the REAL A3
#       session_e213.sh, run_e213_a3.py and the kit's run_e213.py run on the stand-in box and stop at the runner's box check before any device
#       (the desk's own hostname): "refused, no device opened"; runner.out's first line "A3-ORDER OK"; no host process; the kit's step 10 reads
#       GATE-STOPPED (16) with the manifest written
#   W10 THE KIT'S STEPS 10 AND 11 COUNT A3'S WRAPPER BY ITS NAME: a stand-in at tools/claims-v3/e213-a3/session_e213.sh running, its log
#       without an end: step 10 17 (RUN-RUNNING); its log ended and its manifest written while it still runs: step 11 10 ("a session_e213.sh of
#       ours still runs"); once it has ended: step 10 0 (RUN-ENDED)
#   P9  A3's sequence file changed on the box after row 5b: A3's step 9 16 (A3-STOP: its pins), the session not started
#   OB  the box's points-e213.json changed after the kit's step 5: A3's row 5b 16 (A3-STOP from the wrapper's order check on the box)
#   NS  A3's step 9 with no row 5b today in RB_OUT: 10, nothing sent to the box
#   PD  A3's wrapper changed (uncommitted) in the lab clone: row 5b 16 before any call reaches the box
#   AA  arm A refused by A3's two steps (10), before any call
#   DRY A3's dry listing (rb/list_steps_e213_a3.sh): 16 steps listed, 0 exited non-zero, 0 box calls, the order under A3 exit 0
#   Z   no process of this test left running
#   bash tools/claims-v3/e213-a3/desk/selftest_a3_e213.sh <scratch dir> > logs/selftest-a3-e213.txt   (prints SELFTEST-A3-E213 <n> of <m> PASS or FAIL)
# On a box with a card (aifoundry2) run it ONLY inside a sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh), and never while THE QUIET
# DESK FLAG stands (its sessions start the doubles' hosts and scripts named session_e213.sh). SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK RB_DRY RB_WAIT_LOOP_S RB_OUT FWGATE_DESK_TEST FWGATE_CLI \
         FWGATE_ETWHO FWGATE_LOCKDIR FWGATE_LEDGER_DIR FWGATE_HOSTNAME FWGATE_BOOT_EPOCH FWGATE_BOOT_ID FWGATE_NOW_EPOCH; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test sets its own"; exit 2; }
done
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox (W/nodev.sh)"; exit 3; }
ls /run/lock/etsoc-shire*.lock > /dev/null 2>&1 && { echo "REFUSED: a card lock file is visible in /run/lock: run this inside the sandbox (an empty /run/lock)"; exit 3; }
if [ -z "${E213A3_PIDNS:-}" ]; then
  command -v bwrap > /dev/null || { echo "no bwrap: the test runs in a private PID namespace"; exit 2; }
  echo "(A3's desk test: re-run in a private PID namespace, so that no other lane's process on this desk is read as a session of ours)"
  exec /usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- env E213A3_PIDNS=1 bash "$SRC/tools/claims-v3/e213-a3/desk/selftest_a3_e213.sh" "$@"
fi
for c in timeout sha256sum flock rsync git; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
REAL_RSYNC=$(command -v rsync)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree bin boxbin order; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; BIN=$S/bin; BB=$S/boxbin
A=tools/claims-v3/e213-a3; A2=tools/claims-v3/e213-a2; E=tools/claims-v3/e213
mkdir -p "$BIN" "$BB"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aqE -- "$1" "$2" 2>/dev/null && echo 1 || echo 0; }
cnt() { if [ -f "$1" ]; then grep -c . "$1"; else echo 0; fi; }
line() { grep -aE -- "$1" "$2" 2>/dev/null | head -n 1 | cut -c1-"${3:-200}"; }
main() {
# ---- the scratch repository: a shared sparse clone of the lab clone at its HEAD (A2's and A3's files committed in it, as on the card day)
git clone -q --shared --no-checkout "$SRC" "$T" || return 2
G="git -C $T -c user.name=e213a3-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /docs/reports/data/2026-10-31-e82-kinds-aifoundry1/ident/ || return 2
$G checkout -q -B main "$(git -C "$SRC" rev-parse HEAD)" || return 2
[ -f "$T/$A/rb/s11_session_e213_a3.sh" ] && [ -f "$T/$A2/rb/s11_session_e213_a2.sh" ] || { echo "A2's and A3's files are not committed at the lab clone's HEAD"; return 2; }
echo "scratch repository: a shared sparse clone of the lab clone at HEAD $(git -C "$T" rev-parse --short=12 HEAD) (A2's and A3's files committed in it)"

step "PART 1: A3's order, its wrapper, the runner through it and the scorer (desk/selftest_order_a3_e213.py, from the scratch repository)"
/usr/bin/python3 -B "$T/$A/desk/selftest_order_a3_e213.py" "$S/order" > "$S/order.txt" 2>&1
orc=$?
grep -E '^[A-Z][A-Z0-9]*: (PASS|FAIL) - |^SELFTEST-ORDER-A3 ' "$S/order.txt" | cut -c1-900
np=$(grep -cE '^[A-Z][A-Z0-9]*: PASS - ' "$S/order.txt"); nf=$(grep -cE '^[A-Z][A-Z0-9]*: FAIL - ' "$S/order.txt")
ncase=$((ncase + np + nf)); npass=$((npass + np)); { [ "$nf" -eq 0 ] && [ "$orc" -eq 0 ] && [ "$np" -eq 8 ]; } || { fail=1; echo "-> FAIL (part 1: rc $orc, $np PASS, $nf FAIL, want 8 PASS)"; }

step "PART 2: arm B's runbook as amended by A2 and A3, on stand-in aifoundry1 boxes"
E82A=$T/docs/reports/data/2026-10-31-e82-kinds-aifoundry1/ident/firmware_pre.txt
[ -s "$E82A" ] || { echo "E82's committed answer is not in the scratch repository"; return 2; }
cp "$E82A" "$S/answer-equal.txt"
# ---- the stand-ins (A2's desk test's, unchanged in what they serve): ssh and rsync serve aifoundry1 only, its tree in the case's own box folder
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
[ "\$host" = aifoundry1 ] || { echo "STAND-IN SSH: refusing host \$host" >&2; exit 97; }
[ "\$cmd" = true ] && exit 0
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'bash -s' and 'true' are served (got: \$cmd)" >&2; exit 97; }
R=\$(cat "$S/boxroot")
cd "\$R/\$host" || exit 1
set -a; . "$S/fwenv"; set +a
exec env HOME="\$R/\$host" STANDIN_HOST="\$host" STANDIN_S="$S" PATH="$BB:\$PATH" bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
R=\$(cat "$S/boxroot")
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; [ "\$h" = aifoundry1 ] || { echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97; }; a+=("\$R/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho "scp refused by the desk test" >&2\nexit 97\n' > "$BIN/scp"
printf '#!/bin/sh\necho "${STANDIN_HOST:-desk}"\n' > "$BB/hostname"
cat > "$BB/uptime" <<EOF
#!/bin/sh
if [ "\${1:-}" = -s ] && [ -n "\${STANDIN_HOST:-}" ]; then cat "$S/boot-text"; exit 0; fi
exec /usr/bin/uptime "\$@"
EOF
cat > "$BB/et-who" <<EOF
#!/bin/sh
if [ "\${1:-}" = --check ]; then exit "\$(cat "$S/box-etwho-check-rc" 2>/dev/null || echo 0)"; fi
echo "No process holds an ET-SoC-1 device node or card lock."
EOF
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$BB/python3"
REAL_PGREP=$(command -v pgrep)
cat > "$BB/pgrep" <<EOF
#!/bin/bash
anc=" "; p=\$\$
while [ -n "\$p" ] && [ "\$p" -gt 1 ]; do anc="\$anc\$p "; p=\$(ps -o ppid= -p "\$p" 2>/dev/null | tr -d ' '); done
"$REAL_PGREP" "\$@" | while IFS= read -r x; do case "\$anc" in *" \${x%% *} "*) ;; *) echo "\$x" ;; esac; done
EOF
chmod +x "$BIN"/* "$BB"/*
export PATH="$BIN:$PATH" RB_LOCK="$S/rb-lock.txt"
TODAY=$(TZ=America/Los_Angeles date +%F)
BEFORE_TEXT="2026-10-26 15:18:24"; BEFORE=1793053104        # a boot before E82's firmware read (A2's continuity case)
newcase() {  # newcase <tag>: a fresh box tree, lock folder, ledger, RB_OUT and window (A2's form, a boot before E82's read)
  CASE=$1; R="$S/box-$CASE"; O="$S/out-$CASE"; LD="$S/locks-$CASE"; BX="$R/aifoundry1/nekko"
  mkdir -p "$BX" "$O" "$LD"; : > "$LD/etsoc-shire0.lock"; : > "$LD/etsoc-shire1.lock"
  echo "$R" > "$S/boxroot"; echo "$BEFORE_TEXT" > "$S/boot-text"; echo 0 > "$S/box-etwho-check-rc"
  cat > "$S/fwenv" <<EOF
FWGATE_DESK_TEST=1
FWGATE_CLI=$T/tools/claims-v3/fwgate/tests/fwcli-standin
FWGATE_ETWHO=$T/tools/claims-v3/fwgate/tests/etwho-standin
FWGATE_LOCKDIR=$LD
FWGATE_LEDGER_DIR=$R/aifoundry1/.local/state/fwgate
FWGATE_HOSTNAME=aifoundry1
FWGATE_BOOT_EPOCH=$BEFORE
FWGATE_BOOT_ID=desk-$CASE-$BEFORE
FWGATE_STANDIN_LOG=$S/cli-$CASE.jsonl
FWGATE_STANDIN_LOCKS=$LD/etsoc-shire0.lock:$LD/etsoc-shire1.lock
FWGATE_STANDIN_OUT=$S/answer-equal.txt
FWGATE_STANDIN_ETWHO_LOG=$S/etwho-$CASE.log
FWGATE_STANDIN_ETWHO_RC=0
ET_DEVICES=1
EOF
  RB_OUT=$O RB_DESKTEST=1 E213_DESK_BUDGET_S=60 bash "$T/$E/rb/s02_window_e213.sh" B "$TODAY" 23:58 23:59 > "$S/$CASE-window.txt" 2>&1 || echo "window: rc $?"
}
rbs() {  # rbs <log tag> <step file under the scratch repository> [<arm>]: one runbook step in the case's RB_OUT; prints its exit
  local tag=$1 f=$2 arm=${3:-B}
  RB_OUT=$O RB_DESKTEST=1 E213_DESK_BUDGET_S=60 bash "$T/$f" "$arm" > "$S/$tag.txt" 2>&1; echo $?
}
prelaunch() {  # the box's and the desk's inputs step 9 needs besides the look and row 5b (today's build and dry pass, today's never-run report)
  echo rgm > "$O/e213-built-B.txt"
  echo "$(date '+%F %T %Z') NEVER-RUN-E213 arm B: (desk-test stand-in)" > "$O/e213-neverrun-B.txt"
  mkdir -p "$BX/build/q141k/jobs"
  echo 0 > "$BX/build/q141k/jobs/a1-dry-e213.rc"
  echo "RGM-BUILT rc=0" > "$BX/build/q141k/jobs/a1-build-e213.out"
}
upto5b() {  # upto5b <tag>: window (newcase), A2's step 4, the kit's step 5, A3's row 5b; prints the three exits
  local a b c
  a=$(rbs "$1-look" "$A2/rb/s05_look_e213_a2.sh"); b=$(rbs "$1-sync" "$E/rb/s07_sync_e213.sh"); c=$(rbs "$1-5b" "$A/rb/s07b_sync_e213_a3.sh")
  echo "$a $b $c"
}

step "Y: the window, A2's step 4 (CONTINUITY), the kit's step 5, then A3's row 5b"
newcase Y
r=$(upto5b Y)
ok "$r|$(has '^\[s07_sync_e213\] synced to aifoundry1' "$S/Y-sync.txt")|$(has '^A3-PINS OK 3 of 3$' "$S/Y-5b.txt")|$(has '^A3-ORDER OK: arm B 85 runs, ' "$S/Y-5b.txt")|$(has '^[0-9-]+ [0-9:]+ [A-Z]+ A3-SYNC-B: OK; the rsync sent 3 files' "$O/e213-a3-sync-B.txt")|$(sha256sum "$BX/$A/sequence-B-a3.json" 2>/dev/null | cut -c1-12)" \
   "0 0 0|1|1|1|1|$(sha256sum "$T/$A/sequence-B-a3.json" | cut -c1-12)" "$(line '^\[s07b_sync_a3_e213\] ' "$S/Y-5b.txt" 260)"
[ "${r%% *}" = 0 ] || tail -n 20 "$S/Y-look.txt"

step "L9: A3's step 9 launches the REAL A3 session_e213.sh, run_e213_a3.py and run_e213.py, which stop at the runner's box check; step 10 reads the gate"
prelaunch
r=$(rbs L9 "$A/rb/s11_session_e213_a3.sh")
t0=$(cat "$O/e213-T0-B.txt" 2>/dev/null); sd=$BX/build/e213/T$t0-B
k=0; while [ ! -s "$sd/runner.rc" ] && [ "$k" -lt 60 ]; do sleep 1; k=$((k + 1)); done
r2=$(RB_OUT=$O RB_DESKTEST=1 RB_WAIT_LOOP_S=20 bash "$T/$E/rb/s20_wait_e213.sh" B > "$S/L9-wait.txt" 2>&1; echo $?)
procs=$(find "$sd" -name 'proc*.out' 2>/dev/null | wc -l | tr -d ' ')
ok "$r|$(has '^LAUNCHED e213 arm B T0 [0-9]+ .*Amendment A3' "$S/L9.txt")|$(has '^identity: .*: ok$' "$S/L9.txt")|$(has '^A3-PINS OK 3 of 3$' "$S/L9.txt")|$(has '^A3-ORDER OK: ' "$S/L9.txt")|$(head -n 1 "$sd/runner.out" 2>/dev/null | cut -c1-31)|$(has 'refused, no device opened: the box or the build is not the registered one \(this host is' "$sd/session.log")|$(has '"rc": 16' "$sd/queue.json")|$( [ -s "$sd/MANIFEST.sha256" ] && echo manifest)|$(cat "$sd/runner.rc" 2>/dev/null)|$procs|$r2|$(has 'GATE-STOPPED e213 arm B' "$S/L9-wait.txt")" \
   "0|1|1|1|1|A3-ORDER OK: arm B 85 runs, the|1|1|manifest|16|0|16|1" "$(grep -m1 'no device opened' "$sd/session.log" 2>/dev/null | cut -c1-200)"
[ "${r%%|*}" = 0 ] || tail -n 30 "$S/L9.txt"

step "W10: the kit's steps 10 and 11 count A3's wrapper by its name (session_e213.sh under tools/claims-v3/e213-a3/)"
newcase W10
echo 9 > "$O/e213-T0-B.txt"; cp "$S/out-Y/box-login-aifoundry1.txt" "$O/" 2>/dev/null
mkdir -p "$BX/build/q141k" "$BX/$A"; echo 9 > "$BX/build/q141k/e213B.T0"
cat > "$BX/$A/session_e213.sh" <<'EOF'
#!/bin/bash
# A STAND-IN for A3's session_e213.sh (A3's desk test): no device; it holds while $HOME/hold-run exists, ends its log, holds while $HOME/hold-end
# exists, then writes runner.rc (each hold at most 90 s)
SD=build/e213/T${E213_T0}-B; mkdir -p "$SD"
echo "$(date '+%F %T %Z') session start (stand-in)" > "$SD/session.log"
k=0; while [ -e "$HOME/hold-run" ] && [ "$k" -lt 90 ]; do sleep 1; k=$((k + 1)); done
echo "$(date '+%F %T %Z') session end (T0 ${E213_T0})" >> "$SD/session.log"
echo "0000000000000000000000000000000000000000000000000000000000000000  session.log" > "$SD/MANIFEST.sha256"
k=0; while [ -e "$HOME/hold-end" ] && [ "$k" -lt 90 ]; do sleep 1; k=$((k + 1)); done
echo 0 > "$SD/runner.rc"
EOF
touch "$R/aifoundry1/hold-run" "$R/aifoundry1/hold-end"
( cd "$BX" && HOME="$R/aifoundry1" E213_T0=9 setsid nohup bash "$A/session_e213.sh" > /dev/null 2>&1 < /dev/null & )
sleep 2
w1=$(RB_OUT=$O RB_DESKTEST=1 RB_WAIT_LOOP_S=4 bash "$T/$E/rb/s20_wait_e213.sh" B > "$S/W10-1.txt" 2>&1; echo $?)
rm -f "$R/aifoundry1/hold-run"; k=0; while ! grep -q 'session end' "$BX/build/e213/T9-B/session.log" 2>/dev/null && [ "$k" -lt 20 ]; do sleep 1; k=$((k + 1)); done
c1=$(RB_OUT=$O RB_DESKTEST=1 bash "$T/$E/rb/s22_collect_e213.sh" B > "$S/W10-2.txt" 2>&1; echo $?)
rm -f "$R/aifoundry1/hold-end"; k=0; while [ ! -s "$BX/build/e213/T9-B/runner.rc" ] && [ "$k" -lt 20 ]; do sleep 1; k=$((k + 1)); done; sleep 2
w2=$(RB_OUT=$O RB_DESKTEST=1 RB_WAIT_LOOP_S=4 bash "$T/$E/rb/s20_wait_e213.sh" B > "$S/W10-3.txt" 2>&1; echo $?)
ok "$w1|$(has 'RUN-RUNNING e213 arm B' "$S/W10-1.txt")|$c1|$(has 'REFUSED: a session_e213.sh of ours still runs' "$S/W10-2.txt")|$w2|$(has 'RUN-ENDED e213 arm B' "$S/W10-3.txt")" \
   "17|1|10|1|0|1" "running: $(line 'RUN-' "$S/W10-1.txt" 80); step 11: $(line 'REFUSED' "$S/W10-2.txt" 120); ended: $(line 'RUN-' "$S/W10-3.txt" 60)"

step "P9: A3's sequence file changed on the box after row 5b: A3's step 9 stops with nothing launched"
newcase P9
r=$(upto5b P9); prelaunch
printf ' ' >> "$BX/$A/sequence-B-a3.json"
r9=$(rbs P9-9 "$A/rb/s11_session_e213_a3.sh")
ns=$(find "$BX/build/e213" -maxdepth 1 -type d -name 'T*-B' 2>/dev/null | wc -l | tr -d ' ')
ok "$r|$r9|$(has '^\[s11_session_a3_e213\] STOP: A3-STOP: A3.s box files are not at their pinned sha256' "$S/P9-9.txt")|$ns|$( [ -s "$O/e213-T0-B.txt" ] && echo t0 || echo no-t0)" \
   "0 0 0|16|1|0|no-t0" "$(line '\] STOP: ' "$S/P9-9.txt" 240)"

step "OB: the box's points-e213.json changed after the kit's step 5: row 5b's order check on the box stops it"
newcase OB
a=$(rbs OB-look "$A2/rb/s05_look_e213_a2.sh"); b=$(rbs OB-sync "$E/rb/s07_sync_e213.sh")
printf '\n' >> "$BX/$E/points-e213.json"
c=$(rbs OB-5b "$A/rb/s07b_sync_e213_a3.sh")
ok "$a $b $c|$(has '^A3-PINS OK 3 of 3$' "$S/OB-5b.txt")|$(has "STOP: A3-STOP: A3's order check on aifoundry1 exited 3 \(points-e213.json is not the registered file" "$S/OB-5b.txt")|$( [ -e "$O/e213-a3-sync-B.txt" ] && echo synced || echo none)" \
   "0 0 16|1|1|none" "$(line '\] STOP: ' "$S/OB-5b.txt" 240)"

step "NS: A3's step 9 with no row 5b today in RB_OUT: refused before any call reaches the box"
newcase NS
a=$(rbs NS-look "$A2/rb/s05_look_e213_a2.sh"); prelaunch
m0=$(cnt "$S/calls.log"); r9=$(rbs NS-9 "$A/rb/s11_session_e213_a3.sh"); m1=$(cnt "$S/calls.log")
ok "$a|$r9|$((m1 - m0))|$(has "A3's row 5b has not passed today in this RB_OUT" "$S/NS-9.txt")" "0|10|0|1" "$(line '\] STOP: ' "$S/NS-9.txt" 200)"

step "PD: A3's wrapper changed (uncommitted) in the lab clone: row 5b stops before any call reaches the box"
newcase PD
cp "$T/$A/run_e213_a3.py" "$S/wrapper.bak"; echo "# an uncommitted change" >> "$T/$A/run_e213_a3.py"
m0=$(cnt "$S/calls.log"); r=$(rbs PD "$A/rb/s07b_sync_e213_a3.sh"); m1=$(cnt "$S/calls.log")
cp "$S/wrapper.bak" "$T/$A/run_e213_a3.py"; $G checkout -q -- "$A/run_e213_a3.py"
ok "$r|$((m1 - m0))|$(has "A3's box files have uncommitted changes in the lab clone" "$S/PD.txt")|$(git -C "$T" status --porcelain | grep -c .)" "16|0|1|0" "$(line '\] STOP: ' "$S/PD.txt" 200)"

step "AA: arm A is refused by A3's two steps"
newcase AA
m0=$(cnt "$S/calls.log")
a=$(rbs AA1 "$A/rb/s07b_sync_e213_a3.sh" A); b=$(rbs AA2 "$A/rb/s11_session_e213_a3.sh" A)
m1=$(cnt "$S/calls.log")
ok "$a $b $((m1 - m0)) $(has "arm B's alone" "$S/AA1.txt") $(has "arm B's alone" "$S/AA2.txt")" "10 10 0 1 1" "$(line 'STOP' "$S/AA1.txt" 160)"

step "DRY: A3's dry listing (arm B as amended by A2 and A3)"
mkdir -p "$S/listing"
( cd "$T" && bash "$A/rb/list_steps_e213_a3.sh" "$S/listing" > "$S/DRY.txt" 2>&1 )
ok "$(has '^dry listing \(A2 and A3, arm B\): 16 steps listed, 0 exited non-zero, 0 box calls; the order under A3: exit 0$' "$S/DRY.txt")|$(grep -cE '^  +[0-9]+ (tie|pass1|pass2) ' "$S/DRY.txt")" "1|85" "$(tail -n 1 "$S/DRY.txt")"

step "Z: no process of this test left running"
sleep 1
left=$(ps -eo pid=,args= | grep -E 'session_e213\.sh|run_e213(_a3)?\.py|fake_card_e213|fwcli-standin|fwgate\.py|rb_run\.py' | grep -v grep | grep -c .)
ok "$left" 0 "processes left: $left"
echo
echo "the stand-ins' calls: $(grep -c '^ssh ' "$S/calls.log") ssh, $(grep -c '^rsync ' "$S/calls.log") rsync (all to the stand-in aifoundry1)"
echo "SELFTEST-A3-E213 $npass of $ncase $( [ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
}
main
