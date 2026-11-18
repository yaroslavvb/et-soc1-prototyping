#!/usr/bin/env bash
# E213 (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): the desk test of E213's runbook with a FAKE ssh and rsync on stand-in
# aifoundry3 and aifoundry1 boxes, E211's rb/selftest_rb_e211.sh form (landed in 2b7f261f) with E206's second box, for E213's two arms. Its scratch
# repository is a shared, sparse clone of the lab clone this test runs from (its HEAD holds E213's registration as a commit, as on the card day)
# with the kit's files committed on top as one stand-in kit commit, the kit's list a stand-in made here and pinned in the scratch copy of step 2's
# KITPIN line (the one line this test changes in a copy), and stand-in desk-test logs (this test's own log is not final while it runs). The stand-in
# boxes are aifoundry3's ~/aifoundry and aifoundry1's ~/nekko, rsync targets under the scratch; the stand-in ssh serves them with `bash -s` (and
# `true`) and refuses any other host or command; the stand-in rsync rewrites its paths; each box's hostname, uptime, et-who, et-lab-manifest and
# pgrep are stand-ins, and each box tree holds a stand-in reader at build/ettelem/ettelem (the doubles' config and sampler, the box's arm) and
# aifoundry3's E128's guard (k6's step 7 runs it there; arm B's step 7 runs E213's guard with ET_DEVICES=1); cmake, the compilers and /opt/et are
# this desk's REAL ones (the build is the real build_e213.sh). Step 6n's scan reads the scratch repository at its HEAD as the lab and a stand-in
# folder as the round's lanes (E213_ROUND_OUT). No lab box is reached. When the lab clone's history holds the kit commit (the commit that added
# KIT.md: the readiness lane), the scratch repository is built at that commit's PARENT and the kit's files are taken from HEAD, its main following
# a local branch at that parent; otherwise (the kit lane) the untracked files and the lab clone's HEAD. Cases:
#   A / AB  the dry listing, each arm: every step exits 0, no call reaches the stand-ins
#   K   step 2 with no window: 10       W1 a window written for the other arm: 10      W2 a window written for another runbook: 10
#   W3  step 1 for another day: 10      W4 step 1 with an unknown arm: 10              G  step 2 without RB_GITLOCK: 10
#   N   step 2 inside the lab-git lock (nested): 16 naming the pull
#   P1 / P1B  step 2 on the scratch repository, each arm: 0 (the lists at their pins, HISTORY OK, the registration and the kit found by content,
#       MM1-v3's land an ancestor, the registration's checks, the scorer's three self-checks byte-identical, the preflight GO, the desk tests' logs)
#   P2  in one step-2 run (each run takes about 2 minutes): the registration's list one line short, the kit's list one line short and a desk
#       test's log without its PASS line (that log is in the kit's list, so the kit's list reads one entry not OK too): 16, the failure list
#       naming all three
#   H1  a committed edit of a registration file: 16 by the history check      H2 a committed tools/claims-v3/e213/json.py (a shadow): 16
#   DA  arm A's data committed: step 2 refuses arm A (16) and goes on for arm B (0), which reports the other arm's data commit
#   GS  in one step-2 run: an E213 gate stop's record committed (step 2 reports it) and a FILE whose name holds 'e213' committed under
#       docs/reports/data (E175's design tile ...0e213f.bin's form: no datum, no other arm's datum): step 2 goes on (0)
#   S0  THE STEP-0 CHECKS (rb/s00_step0_e213.sh) on the scratch repository with a stand-in GitHub main: (a) no sealed record: "sealed 0 of 0", both
#       arms as stated; (b) a record whose sealed sha256 the note at HEAD registers: 1 of 1; (c) a record listing a sha256 the note does not
#       register: NOT AS STATED (S1), exit 1; (d) arm B with GitHub main BEFORE the registration commit: F1 NOT AS STATED, exit 1; (e) arm A's
#       data committed: arm A D0 NOT AS STATED, arm B D0 as stated (the other arm's REPORTED)
#   O   the look on each stand-in box (k6's s05, unchanged): FREE, our login recorded for the scrub
#   OL  E213's ours_live: a shell whose command string names session_e213.sh is not a session; a session_e213.sh run as a script is
#   SY / SYB  step 5 on each box: the rsync, HARNESS OK on the box     L1 a login link on a read: 11, "<HH:MM:SS> aifoundry3 needs a check" appended
#       to RB_LOCK, nothing retried      L2 a read that hangs (the read class's bound 3 s for this call): 13
#   T   NO-THIRD-BUILD: two starts recorded on aifoundry3 today: a third start is refused with 16
#   BA  step 6 on aifoundry3: start, wait (17 while it builds, then 0): the REAL build of both kernels, KERNEL OK on each, the record (arm A), the
#       harness, the preflight GO and both self-checks read on the box; RB_OUT/e213-built-A.txt
#   BB  step 6 on aifoundry1: the REAL build on this desk's stock device layer stops at the ET_DEVICES gate: the wait reads 16, no e213-built-B.txt
#   NR  STEP 6n, THE NEVER-RUN SEARCH REPEATED (the registration's scanner over the scratch repository and a stand-in lanes folder): arm A: a
#       record of a039's token in a card-a3 lane folder dated BEFORE arm A's freeze line: 'ran before', labelled (a039 and a040, the token's two
#       points), the labels LABELS-OK; arm B: a record of k03's token in a card-a1c1 lane folder dated AFTER the registration commit: REPORTED and
#       kept, no label; E213's own card lane folders (card-e213a, card-e213b) subtracted
#   R7 / R7B  STEP 7 ONLY WITH A FRESH NEVER-RUN REPORT AND ONLY ONCE THE REST HAS OPENED: no report: 10; a report 31 minutes old: 10; a session of
#       ours ended 10 minutes ago: 10; in none of the three is the stand-in reader called; then 0, the reader called once (arm A k6's read, TDP 0 W
#       / 65 C / 600 MHz; arm B E206's card-1 read through E213's guard with ET_DEVICES=1: TDP 65 W, 499 mV, /dev/et1_mgmt, ID 1)
#   D / DB  step 8 on each box (the doubles there): 0, and THE SCRUB CHECK on the dry pass's copy reads CLEAN (the box's home masked)
#   DS  THE SCRUB CHECK REFUSES BEFORE THE SESSION: a file with another home's path (/home/<someone else>/...) in the dry pass's folder: the wait
#       reads 16 (SCRUB-CHECK LEFT), no session that day
#   HG  THE HUNG MARKER: a session log of ours on aifoundry3 with a HUNG line: step 9 refuses (10), nothing launched
#   SD  THE SAME-DAY RULE: an E213 arm A session that opened the card earlier today: step 9 refuses (10)
#   LS  THE LAST START passed with the last end still far: step 9 refuses (16) and sends nothing to the box
#   NS  no never-run report from today in RB_OUT (step 6n): step 9 refuses (10) and sends nothing to the box
#   LA  step 9 launches the REAL session_e213.sh and run_e213.py on the stand-in aifoundry3, which stop at their box check before any device (the
#       desk's own hostname): "refused, no device opened"; step 10 reads GATE-STOPPED (16) with the manifest written
#   W10 step 10's readings on stand-in logs: a running session_e213.sh with no end 17 (RUN-RUNNING); none running 14 (RUN-GONE); a HUNG line 16
#       (HUNG); a K1 stop 16 (K1-STOPPED); a CRASH line 16 (CRASHED); an ended session (rc 0) with a STOP line 0
#   C   step 11 on LA's session: COPY-BACK EXACT 0; step 12: the gate stop's record under docs/reports/gate-stops/ (COLLECTED-GATE-STOP), the
#       desk-path gate, HISTORY OK: 0; step 13 refuses a gate stop's record: 10      C2 one byte of a box file changed after the manifest:
#       COPY-BACK NOT EXACT 16
#   CD / CDB  a session that ran on each box (step 8's dry session copied as a session): step 11 0 (the box's home in every form read), step 12
#       the data directory (docs/reports/data/<today>-e213-blind-matmul-<aifoundry3 | aifoundry1-c1>) with data-e213.json (the reducer), step 6n's
#       report, judgement and labels (in SHA256SUMS) and the scrub clean: 0; after a stand-in data commit, step 13 runs the FROZEN scorer on it,
#       arm A WITH step 6n's labels (LABELS-OK first): 0
#   Z   no process of this test left running
#   bash tools/claims-v3/e213/rb/selftest_rb_e213.sh <scratch dir> > logs/selftest-rb-e213.txt   (prints SELFTEST-RB-E213 <n> of <m> PASS or FAIL)
# On a box with a card (aifoundry2) run it ONLY inside a sandbox with no /dev/et* and an empty /run/lock: case LA runs the real runner.
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK RB_DRY RB_WAIT_LOOP_S; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
# E211's fix kept: the stand-in boxes are this desk, so ours_live reads the desk's real process table; the test runs itself once more in a private
# PID namespace (bubblewrap), where it sees only its own processes; E213_RB_PIDNS=1 marks that inner run.
if [ -z "${E213_RB_PIDNS:-}" ]; then
  command -v bwrap > /dev/null || { echo "no bwrap: the runbook test runs in a private PID namespace"; exit 2; }
  echo "(the runbook test: re-run in a private PID namespace, so that no other lane's process on this desk is read as a session of ours)"
  exec /usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- env E213_RB_PIDNS=1 bash "$SRC/tools/claims-v3/e213/rb/selftest_rb_e213.sh" "$@"
fi
for c in timeout sha256sum flock cmake c++ rsync git; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
REAL_RSYNC=$(command -v rsync)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree box bin boxbin out; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; B=$S/box; BIN=$S/bin; BB=$S/boxbin
A3=$B/aifoundry3/aifoundry
A1=$B/aifoundry1/nekko
E=tools/claims-v3/e213
mkdir -p "$A3" "$A1" "$BIN" "$BB"
sedi() { local f=${!#} t; t=$(mktemp "$S/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
main() {
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" 2>/dev/null && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
# ---- the scratch repository: a shared sparse clone of the lab clone's HEAD (the registration in it), the kit's files as one stand-in commit
git clone -q --shared --no-checkout "$SRC" "$T" || return 2
G="git -C $T -c user.name=e213-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/ /docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/ \
  /docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/ /docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/ || return 2
KITC=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/KIT.md | tail -n 1)
if [ -n "$KITC" ]; then
  BASE=$(git -C "$SRC" rev-parse "$KITC^") || return 2
  FORM="the kit committed in the lab clone (${KITC:0:12}): the scratch built at its parent ${BASE:0:12}, the kit's files from HEAD $(git -C "$SRC" rev-parse --short=12 HEAD)"
else
  BASE=$(git -C "$SRC" rev-parse HEAD) || return 2
  FORM="the kit's files untracked in the lab clone: the scratch built at its HEAD ${BASE:0:12}"
fi
$G checkout -q -B main "$BASE" || return 2
{ $G branch -q -f e213-desktest-base "$BASE" && $G branch -q --set-upstream-to=e213-desktest-base main; } || { echo "the scratch's upstream could not be set"; return 2; }
REGC=$($G log --diff-filter=A --format=%H -- $E/E213.md | tail -n 1)
[ -n "$REGC" ] || { echo "the registration is not in the scratch repository's history"; return 2; }
if [ -n "$KITC" ]; then
  git -C "$SRC" diff-tree --no-commit-id --name-only -r --diff-filter=A "$KITC" -- $E | while IFS= read -r f; do
    mkdir -p "$T/$(dirname "$f")"; git -C "$SRC" show "HEAD:$f" > "$T/$f" || exit 2; done || { echo "the kit's files could not be taken from HEAD"; return 2; }
else
  ( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E ) | sort -u | while IFS= read -r f; do
    [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
fi
mkdir -p "$T/$E/logs"
for spec in "selftest-run-e213.txt SELFTEST-RUN-E213 0 of 0 PASS" "realpath-e213.txt REALPATH-E213 0 of 0 PASS" "realbytes-e213.txt REALBYTES-E213 0 of 0 PASS" \
            "desktest-build-e213.txt DESKTEST-BUILD-E213 0 of 0 PASS" "selftest-rb-e213.txt SELFTEST-RB-E213 0 of 0 PASS" \
            "dry-listing-e213-A.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dry-listing-e213-B.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" \
            "dmcmd-audit-e213.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"
done
( cd "$T" && /usr/bin/python3 -I -B $E/check_e213.py --make > /dev/null )
mklist() {  # the kit's stand-in list: every file this stand-in commit adds under E213's folder, but the list itself and step 2
  ( cd "$T" && git ls-files --others --exclude-standard -- $E | grep -v -x -e "$E/SHA256SUMS-e213-kit" -e "$E/rb/s03_desk_e213.sh" |
      LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/kit-standin.txt"
  KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e213-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^KITPIN=$E/SHA256SUMS-e213-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e213-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e213.sh"
  grep -q "^KITPIN=$E/SHA256SUMS-e213-kit:$KITN:$KITH:top" "$T/$E/rb/s03_desk_e213.sh"
}
mklist || { echo "the scratch step 2's KITPIN was not set"; return 2; }
$G add -A $E && $G commit -q -m "E213 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; return 2; }
KIT=$($G rev-parse HEAD)
echo "scratch repository: a shared sparse clone of the lab clone ($FORM; the registration ${REGC:0:12} in it), the kit as one stand-in commit ${KIT:0:12}; the kit's stand-in list $KITN files"
[ "$KITN" -gt 0 ] || { echo "the kit's stand-in list is empty"; return 2; }
# ---- the stand-ins
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3|aifoundry1) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; cat > /dev/null; echo "To authenticate, visit: https://login.tailscale.com/a/e213desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'bash -s' and 'true' are served (got: \$cmd)" >&2; exit 97; }
cd "$B/\$host" || exit 1
exec env HOME="$B/\$host" STANDIN_HOST="\$host" STANDIN_S="$S" PATH="$BB:\$PATH" bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3|aifoundry1) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho "scp refused by the desk test" >&2\nexit 97\n' > "$BIN/scp"
printf '#!/bin/sh\necho "${STANDIN_HOST:-desk}"\n' > "$BB/hostname"
cat > "$BB/uptime" <<'EOF'
#!/bin/sh
if [ "${1:-}" = -s ] && [ -n "${STANDIN_HOST:-}" ]; then echo "2026-10-26 15:18:24"; exit 0; fi
exec /usr/bin/uptime "$@"
EOF
cat > "$BB/et-who" <<EOF
#!/bin/sh
if [ -s "$S/etwho-lines-\${STANDIN_HOST:-x}" ]; then cat "$S/etwho-lines-\${STANDIN_HOST:-x}"; exit 0; fi
echo "No process holds an ET-SoC-1 device node or card lock."
EOF
printf '#!/bin/sh\necho "et-lab-manifest (desk-test stand-in): no device opened"\n' > "$BB/et-lab-manifest"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$BB/python3"
REAL_PGREP=$(command -v pgrep)
cat > "$BB/pgrep" <<EOF
#!/bin/bash
anc=" "; p=\$\$
while [ -n "\$p" ] && [ "\$p" -gt 1 ]; do anc="\$anc\$p "; p=\$(ps -o ppid= -p "\$p" 2>/dev/null | tr -d ' '); done
"$REAL_PGREP" "\$@" | while IFS= read -r x; do case "\$anc" in *" \${x%% *} "*) ;; *) echo "\$x" ;; esac; done
EOF
chmod +x "$BIN"/* "$BB"/*
for spec in "$A3:A" "$A1:B"; do       # each box's own reader stand-in (counting its calls), the box's arm
  bt=${spec%%:*}; arm=${spec#*:}
  mkdir -p "$bt/build/ettelem" "$bt/tools/claims-v3/e128"
  cat > "$bt/build/ettelem/ettelem" <<EOF
#!/bin/sh
echo "\$(date +%s) \$*" >> "$S/reader-calls-$arm.txt"
mode=ok; [ -s "$S/reader-mode-$arm" ] && mode=\$(cat "$S/reader-mode-$arm")
exec env E213_FAKE_ARM=$arm E213_FAKE_CONFIG=\$mode /usr/bin/python3 -B "$T/$E/fake_card_e213.py" "\$@"
EOF
  chmod +x "$bt/build/ettelem/ettelem"
done
cp -p "$SRC/tools/claims-v3/e128/ettelem_guard.sh" "$A3/tools/claims-v3/e128/ettelem_guard.sh"
export PATH="$BIN:$PATH" RB_LOCK="$S/rb-lock.txt"
GL=$S/lab-git.lock; : > "$GL"
TODAY=$(TZ=America/Los_Angeles date +%F)
STARTHM=23:58; ENDHM=23:59           # the window is today's last minutes: the steps' budgets are E213_DESK_BUDGET_S (60 s) here
OA=$S/outA; OB=$S/outB; mkdir -p "$OA" "$OB"
NRO=$S/nr/out
run() {  # run <arm's RB_OUT> <log> <script> [args]: a step of the scratch repository's runbook
  local o=$1 lg=$2; shift 2
  RB_OUT=$o RB_GITLOCK=$GL RB_DESKTEST=1 E213_DESK_BUDGET_S=60 E213_ROUND_OUT="$NRO" bash "$T/$E/rb/$1" "${@:2}" > "$S/$lg.txt" 2>&1
  echo $?
}
waitjob() {  # waitjob <RB_OUT> <tag> <script> <args...>: call a wait step until it says something other than 17 (at most 40 calls)
  local o=$1 tag=$2 r k; shift 2
  for k in $(seq 1 40); do r=$(run "$o" "$tag-$k" "$@"); [ "$r" = 17 ] || { cp "$S/$tag-$k.txt" "$S/$tag.txt"; echo "$r"; return; }; done; echo 17
}
rec() {  # rec <arm token> <type> <tile>: one SPARSITY record line of the lab's hosts, full chip, randn data
  printf 'SPARSITY {"test":"fma","arm":"%s","gen":"randn","type":"%s","pattern":"none","values":"%s:randn:tools/claims-v3/kinds/tiles/%s","b_stream":0,"minions":1024,"shire_mask":"0xffffffff","iters":1,"passes":1,"launch":0,"cycles_max":1,"ghz":0.6,"ok":true}\n' "$1" "$2" "$1" "$3"
}
step "A: the dry listing, arm A; AB: arm B"
mkdir -p "$S/listing-A" "$S/listing-B"
( cd "$T" && bash $E/rb/list_steps_e213.sh A "$S/listing-A" > "$S/A-A.txt" 2>&1; bash $E/rb/list_steps_e213.sh B "$S/listing-B" > "$S/A-B.txt" 2>&1 )
ok "$(grep -c 'dry listing: 15 steps listed, 0 exited non-zero, 0 box calls' "$S/A-A.txt")$(grep -c 'dry listing: 15 steps listed, 0 exited non-zero, 0 box calls' "$S/A-B.txt")" "11" "$(tail -n 1 "$S/A-A.txt"); $(tail -n 1 "$S/A-B.txt")"
step "K: step 2 with no window"
r=$(run "$OA" K s03_desk_e213.sh A); ok "$r $( [ -s "$S/calls.log" ] && echo calls || echo nocalls)" "10 nocalls" "$(grep -m1 STOP "$S/K.txt" | cut -c1-120)"
step "W1: a window written for the other arm; W2: a window written for another runbook; W3: step 1 for another day; W4: step 1 with an unknown arm"
r=$(run "$OA" W1a s02_window_e213.sh A "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_ARM=A/RB_ARM=B/' "$OA/window.env"; r1=$(run "$OA" W1 s03_desk_e213.sh A)
rm -f "$OA/window.env"; r=$(run "$OA" W2a s02_window_e213.sh A "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_PLAN=e213/RB_PLAN=e211/' "$OA/window.env"
r2=$(run "$OA" W2 s03_desk_e213.sh A)
r3=$(run "$OA" W3 s02_window_e213.sh A 2026-11-12 10:00 12:00)
rm -f "$OA/window.env"; r4=$(run "$OA" W4 s02_window_e213.sh C "$TODAY" "$STARTHM" "$ENDHM")
r=$(run "$OA" W0 s02_window_e213.sh A "$TODAY" "$STARTHM" "$ENDHM"); rb_=$(run "$OB" W0B s02_window_e213.sh B "$TODAY" "$STARTHM" "$ENDHM")
ok "$r1 $(has 'not arm A' "$S/W1.txt") $r2 $(has 'not E213' "$S/W2.txt") $r3 $r4 $(has "A (aifoundry3 card 0) or B (aifoundry1 card 1)" "$S/W4.txt") $r $rb_" "10 1 10 1 10 10 1 0 0" "$(grep -m1 STOP "$S/W1.txt" | cut -c1-100); $(grep -m1 STOP "$S/W2.txt" | cut -c1-100); $(grep -m1 STOP "$S/W4.txt" | cut -c1-90)"
step "G: step 2 without RB_GITLOCK"
r=$(RB_OUT=$OA RB_DESKTEST=1 bash "$T/$E/rb/s03_desk_e213.sh" A > "$S/G.txt" 2>&1; echo $?); ok "$r" 10 "$(grep -m1 STOP "$S/G.txt" | cut -c1-100)"
step "N: step 2 inside the lab-git lock (nested)"
r=$(RB_OUT=$OA RB_GITLOCK=$GL RB_DESKTEST=1 RB_GITLOCK_T=3 flock -n "$GL" bash "$T/$E/rb/s03_desk_e213.sh" A > "$S/N.txt" 2>&1; echo $?)
ok "$r $(has 'pull(rc 14; a nested lab-git lock exits 75)' "$S/N.txt")" "16 1" "$(stopline "$S/N.txt" | cut -c1-160)"
step "P1: step 2 on the scratch repository, arm A; P1B: arm B"
r=$(run "$OA" P1 s03_desk_e213.sh A); rb_=$(run "$OB" P1B s03_desk_e213.sh B)
ok "$r $(has 'desk check: the window written today for E213 arm A' "$S/P1.txt") $rb_ $(has 'desk check: the window written today for E213 arm B' "$S/P1B.txt")" "0 1 0 1" "$(grep -m1 'desk check:' "$S/P1.txt" | cut -c1-260)"
[ "$r" = 0 ] || tail -n 30 "$S/P1.txt"
step "P2: in one step-2 run: the registration's list one line short, the kit's list one line short, a desk test's log without its PASS line"
cp "$T/$E/SHA256SUMS-e213-registration" "$S/reg.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e213-registration"
cp "$T/$E/SHA256SUMS-e213-kit" "$S/kit.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e213-kit"
cp "$T/$E/logs/realbytes-e213.txt" "$S/rbl.bak"; echo "REALBYTES-E213 0 of 1 FAIL" > "$T/$E/logs/realbytes-e213.txt"
r=$(run "$OA" P2 s03_desk_e213.sh A)
cp "$S/reg.bak" "$T/$E/SHA256SUMS-e213-registration"; cp "$S/kit.bak" "$T/$E/SHA256SUMS-e213-kit"; cp "$S/rbl.bak" "$T/$E/logs/realbytes-e213.txt"
nreg2=$(( $(grep -c . "$S/reg.bak") - 1 )); nkit2=$(( $(grep -c . "$S/kit.bak") - 1 ))
ok "$r $(has "SHA256SUMS-e213-registration($nreg2 OK of $nreg2" "$S/P2.txt") $(has "SHA256SUMS-e213-kit($((nkit2 - 1)) OK of $nkit2; pinned $KITN" "$S/P2.txt") $(has ' realbytes-e213' "$S/P2.txt")" "16 1 1 1" "$(stopline "$S/P2.txt" | cut -c1-220)"
step "H1: a committed edit of a registration file; H2: a committed shadowing addition (tools/claims-v3/e213/json.py)"
echo "an edit" >> "$T/$E/E213.md"; $G commit -q -am "desk test: an edit of E213.md"
r=$(run "$OA" H1 s03_desk_e213.sh A); $G reset -q --hard "$KIT"
echo "# a shadow" > "$T/$E/json.py"; $G add "$E/json.py"; $G commit -q -m "desk test: a shadow"
r2=$(run "$OA" H2 s03_desk_e213.sh A); /usr/bin/python3 -I -B "$T/$E/rb/check_history_e213.py" tree > "$S/H2b.txt" 2>&1; $G reset -q --hard "$KIT"
ok "$r $(has 'history' "$S/H1.txt") $r2 $(has 'json.py' "$S/H2b.txt")" "16 1 16 1" "$(stopline "$S/H1.txt" | cut -c1-150); $(head -c 150 "$S/H2b.txt")"
step "DA: arm A's data committed: step 2 refuses arm A and goes on for arm B; GS: a gate stop's record and a FILE named *e213* under docs/reports/data (E175's form): reported, no datum, 0"
DD="docs/reports/data/$TODAY-e213-blind-matmul-aifoundry3"
mkdir -p "$T/$DD"; echo "stand-in" > "$T/$DD/README.md"
$G add --sparse -f "$DD/README.md"; $G commit -q -m "desk test: E213 arm A data (stand-in)"
r=$(run "$OA" DA s03_desk_e213.sh A); rb_=$(run "$OB" DAB s03_desk_e213.sh B); $G reset -q --hard "$KIT"
mkdir -p "$T/docs/reports/gate-stops/$TODAY-e213-blind-matmul-T1-aifoundry3"; echo "stand-in" > "$T/docs/reports/gate-stops/$TODAY-e213-blind-matmul-T1-aifoundry3/README.md"
$G add --sparse -f "docs/reports/gate-stops/$TODAY-e213-blind-matmul-T1-aifoundry3/README.md"; $G commit -q -m "desk test: an E213 gate stop's record (stand-in)"
F175="docs/reports/data/2026-11-05-q143g-e175-design/candidates/tiles/fp16/fp16.e5c92_ar_k_t7_0e213f.bin"
mkdir -p "$T/$(dirname "$F175")"; echo "stand-in tile" > "$T/$F175"; $G add --sparse -f "$F175"; $G commit -q -m "desk test: a file named *e213* (E175's form)"
rg=$(run "$OA" GS s03_desk_e213.sh A); $G reset -q --hard "$KIT"
ok "$r $(has 'E213-arm-A-has-data(1 commit(s))' "$S/DA.txt") $rb_ $(has "the other arm's data commits: 1" "$S/DAB.txt") $rg $(has 'E213 gate-stop commits: 1' "$S/GS.txt") $(has "the other arm's data commits: 0" "$S/GS.txt")" "16 1 0 1 0 1 1" \
   "arm A: $(stopline "$S/DA.txt" | cut -c1-120); arm B goes on; a gate stop and E175's file: rc $rg, $(grep -o "the other arm's data commits: [0-9]*; E213 gate-stop commits: [0-9]*" "$S/GS.txt" | head -n 1)"
step "S0: THE STEP-0 CHECKS on the scratch repository (a stand-in GitHub main = its HEAD)"
SR=$S/sealed; mkdir -p "$SR"
s0() { RB_DESKTEST=1 E213_S0_LAB="$T" E213_S0_MAIN="${2:-$($G rev-parse HEAD)}" E213_SEALED="$1" bash "$T/$E/rb/s00_step0_e213.sh" "$3" > "$S/S0-$4.txt" 2>&1; echo $?; }
a=$(s0 "$SR/none.txt" "" A a); b=$(s0 "$SR/none.txt" "" B b)
SHA=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
mkdir -p "$T/tools/claims-v3/sealed-e213"; printf '# E213 freeze lines (desk-test stand-in)\nsha256 %s\n' "$SHA" > "$T/tools/claims-v3/sealed-e213/e213-freeze-lines.md"
$G add tools/claims-v3/sealed-e213; $G commit -q -m "desk test: a sealed-forecast note (stand-in)"
printf '# record\nE213 %s #99 2026-11-18 00:00:00 PST -- stand-in\n' "$SHA" > "$SR/one.txt"
c=$(s0 "$SR/one.txt" "" B c)
printf '# record\nE213 %s #99 2026-11-18 00:00:00 PST -- stand-in\nE213 %s #98 2026-11-18 00:01:00 PST -- not registered\n' "$SHA" "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210" > "$SR/two.txt"
d=$(s0 "$SR/two.txt" "" A d)
$G reset -q --hard "$KIT"
e=$(s0 "$SR/none.txt" "$($G rev-parse "$REGC^")" B e)
mkdir -p "$T/$DD"; echo "stand-in" > "$T/$DD/README.md"; $G add --sparse -f "$DD/README.md"; $G commit -q -m "desk test: E213 arm A data (stand-in)"
f=$(s0 "$SR/none.txt" "" A f); g=$(s0 "$SR/none.txt" "" B g); $G reset -q --hard "$KIT"
ok "$a $b $(has 'sealed 0 of 0' "$S/S0-a.txt") $(has 'STEP0-E213 arm A: 5 of 5 as stated' "$S/S0-a.txt") $(has 'STEP0-E213 arm B: 5 of 5 as stated' "$S/S0-b.txt") $c $(has 'sealed 1 of 1' "$S/S0-c.txt") $d $(has 'S1 NOT AS STATED: sealed 1 of 2' "$S/S0-d.txt") $e $(has 'F1 NOT AS STATED' "$S/S0-e.txt") $f $(has 'D0 NOT AS STATED' "$S/S0-f.txt") $g $(has 'D0 as stated' "$S/S0-g.txt")" \
   "0 0 1 1 1 0 1 1 1 1 1 1 1 0 1" "no record: $(tail -n 1 "$S/S0-a.txt" | cut -c1-70); a registered seal: $(grep -m1 '^S1' "$S/S0-c.txt" | cut -c1-60); an unregistered one: $(grep -m1 '^S1' "$S/S0-d.txt" | cut -c1-80); main before the registration: $(grep -m1 '^F1' "$S/S0-e.txt" | cut -c1-80)"
step "O: the look on each stand-in box (k6's s05)"
r3=$(RB_OUT=$OA bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry3 > "$S/O3.txt" 2>&1; echo $?)
r1=$(RB_OUT=$OB bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry1 > "$S/O1.txt" 2>&1; echo $?)
ok "$r3 $( [ -s "$OA/box-login-aifoundry3.txt" ] && echo login) $r1 $( [ -s "$OB/box-login-aifoundry1.txt" ] && echo login)" "0 login 0 login" "aifoundry3: $(grep -m1 'FREE\|HELD' "$S/O3.txt" | cut -c1-70); aifoundry1: $(grep -m1 'FREE\|HELD' "$S/O1.txt" | cut -c1-70)"
step "OL: E213's ours_live counts a session_e213.sh by its own script, never by a command string"
mkdir -p "$S/ol"; printf '#!/bin/bash\nsleep 25\n' > "$S/ol/session_e213.sh"
( . "$T/$E/rb/rb_e213.sh" > /dev/null 2>&1; e213_live_text ) > "$S/ol/live.sh"
printf '. "%s"\necho "$(ours_live session_e213.sh) $(ours_live)"\n' "$S/ol/live.sh" > "$S/ol/count.sh"
printf '#!/bin/bash\nsleep 25\n: tools/claims-v3/e213/session_e213.sh\n' > "$S/ol/decoy.sh"
n0=$(bash "$S/ol/count.sh")
setsid bash "$S/ol/decoy.sh" session_e213.sh < /dev/null > /dev/null 2>&1 &
p1=$!
n1=$(sleep 1; bash "$S/ol/count.sh")
setsid bash "$S/ol/session_e213.sh" < /dev/null > /dev/null 2>&1 &
p2=$!
n2=$(sleep 1; bash "$S/ol/count.sh")
kill "$p1" "$p2" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do [ "$(bash "$S/ol/count.sh")" = "0 0" ] && break; sleep 0.5; done
n3=$(bash "$S/ol/count.sh")
ok "$n0|$n1|$n2|$n3" "0 0|0 0|1 1|0 0" "before: $n0; a script whose arguments and text name session_e213.sh: $n1; a session_e213.sh run as a script: $n2; after it ended: $n3"
step "SY: step 5 on aifoundry3; SYB: on aifoundry1"
ra=$(run "$OA" SYA s07_sync_e213.sh A); rb_=$(run "$OB" SYB s07_sync_e213.sh B)
ok "$ra $(has 'HARNESS OK on the box' "$S/SYA.txt") $rb_ $(has 'HARNESS OK on the box' "$S/SYB.txt")" "0 1 0 1" "$(grep -m1 'synced to' "$S/SYA.txt" | cut -c1-120); $(grep -m1 'synced to' "$S/SYB.txt" | cut -c1-120)"
step "L1: a login link on a read (step 5's first read); L2: a read that hangs (the read class's bound 3 s for this call)"
touch "$S/ssh-login"; n0=$(grep -c . "$RB_LOCK" 2>/dev/null || echo 0)
r=$(run "$OA" L1 s07_sync_e213.sh A); n1=$(grep -c 'aifoundry3 needs a check' "$RB_LOCK" 2>/dev/null || echo 0)
touch "$S/ssh-hang"
r2=$(RB_READ_S=3 RB_OUT=$OA RB_DESKTEST=1 bash "$T/$E/rb/s07_sync_e213.sh" A > "$S/L2.txt" 2>&1; echo $?); rm -f "$S/ssh-hang"
ok "$r $((n1 - n0)) $r2" "11 1 13" "$(stopline "$S/L1.txt" | cut -c1-120); $(stopline "$S/L2.txt" | cut -c1-100)"
step "T: NO-THIRD-BUILD on aifoundry3"
mkdir -p "$A3/build"; for k in 1 2; do echo "$TODAY 01:0$k:00 PST a3-build-e213 started" >> "$A3/build/e213-build-attempts.txt"; done
r=$(run "$OA" T s08_build_e213.sh A start); rm -f "$A3/build/e213-build-attempts.txt"
ok "$r $(has NO-THIRD-BUILD "$S/T.txt")" "16 1" "$(stopline "$S/T.txt" | cut -c1-140)"
step "BA: step 6 on aifoundry3: the real build; BB: step 6 on aifoundry1: the real build stops at the ET_DEVICES gate (this desk's device layer)"
r=$(run "$OA" BA1 s08_build_e213.sh A start); r2=$(waitjob "$OA" BA2 s08_build_e213.sh A wait)
rb1=$(run "$OB" BB1 s08_build_e213.sh B start); rb2=$(waitjob "$OB" BB2 s08_build_e213.sh B wait)
ok "$r $r2 $(has 'KERNEL OK: ' "$S/BA2.txt")$(cat "$OA/e213-built-A.txt" 2>/dev/null) $rb1 $rb2 $(has 'RGM-BUILD-FAILED: ET_DEVICES: a host has no ET_DEVICES' "$S/BB2.txt") $( [ -e "$OB/e213-built-B.txt" ] && echo built || echo none)" "0 0 1rgm 0 16 1 none" \
   "$(grep -m1 'built today on' "$S/BA2.txt" | cut -c1-140); arm B: $(stopline "$S/BB2.txt" | cut -c1-100)"
[ "$r2" = 0 ] || tail -n 25 "$S/BA2.txt"
step "NR: step 6n, the never-run search repeated (the registration's scanner over the scratch repository and a stand-in lanes folder)"
mkdir -p "$NRO/card-a3-desktest/runs/1" "$NRO/card-a1c1-desktest/runs/1" "$NRO/card-e213a/runs/1" "$NRO/kit-e213x/work"
rec gemmL4x5x1 int8 int8/full.bin > "$NRO/card-a3-desktest/runs/1/proc-00.out"        # a039's token on aifoundry3, dated before arm A's freeze line
touch -d '2026-11-17 20:00:00 PST' "$NRO/card-a3-desktest/runs/1/proc-00.out"
rec gemmL4x1x2 int8 int8/full.bin > "$NRO/card-a1c1-desktest/runs/1/proc-00.out"      # k03's token on card 1, dated now (after the registration)
rec gemmL3x1x9 fp32 fp32/randn.bin > "$NRO/card-e213a/runs/1/proc-00.out"              # E213's own card lane: subtracted
rec gemmL1x1x13 fp32 fp32/randn.bin > "$NRO/kit-e213x/work/proc.out"                   # a desk lane: not read
ra=$(run "$OA" NRA s06n_neverrun_e213.sh A); rb_=$(run "$OB" NRB s06n_neverrun_e213.sh B)
nrda=$(cat "$OA/e213-neverrun-dir-A.txt" 2>/dev/null); nrdb=$(cat "$OB/e213-neverrun-dir-B.txt" 2>/dev/null)
la=$(/usr/bin/python3 -I -B -c "import json, sys; print(json.load(open(sys.argv[1]))['A']['ran_before_points'])" "$nrda/labels-e213-A.json" 2>/dev/null)
lb=$(/usr/bin/python3 -I -B -c "import json, sys; print(json.load(open(sys.argv[1]))['B']['ran_before_points'])" "$nrdb/labels-e213-B.json" 2>/dev/null)
ck=$( (cd "$T" && /usr/bin/python3 -I -B $E/desk/neverrun_card_e213.py check-labels "$nrda/labels-e213-A.json") 2>&1 | tail -n 1)
ok "$ra $rb_ $la $lb $ck $(has 'ran after it (REPORTED, kept): k03' "$S/NRB.txt") $( [ -s "$OA/e213-neverrun-A.txt" ] && echo report)" "0 0 ['a039', 'a040'] [] LABELS-OK 1 report" \
   "$(grep -m1 'NEVER-RUN-E213 arm A' "$S/NRA.txt" | cut -c1-230); $(grep -m1 'NEVER-RUN-E213 arm B' "$S/NRB.txt" | cut -c1-200)"
step "R7: STEP 7 needs a fresh never-run report and the rest (arm A); R7B: arm B's card-1 read"
O5=$S/out5; mkdir -p "$O5"; cp "$OA/window.env" "$O5/"; touch "$O5/window.env"
c0=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
ra=$(run "$O5" R7a s09_reads_e213.sh A)
cp "$OA/e213-neverrun-A.txt" "$O5/"; touch -d '-31 min' "$O5/e213-neverrun-A.txt"
rb_=$(run "$O5" R7b s09_reads_e213.sh A)
mkdir -p "$A3/build/e185/T1"
{ echo "$(date -d '-14 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-10 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-10 min' "$A3/build/e185/T1/session.log"
rc_=$(run "$OA" R7c s09_reads_e213.sh A); c1=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
{ echo "$(date -d '-50 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-45 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-45 min' "$A3/build/e185/T1/session.log"
rd=$(run "$OA" R7d s09_reads_e213.sh A); c2=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
b0=$(grep -c . "$S/reader-calls-B.txt" 2>/dev/null || echo 0)
re=$(run "$OB" R7e s09_reads_e213.sh B); b1=$(grep -c . "$S/reader-calls-B.txt" 2>/dev/null || echo 0)
ok "$ra $(has 'no never-run report' "$S/R7a.txt") $rb_ $(has 'minutes old (more than 30)' "$S/R7b.txt") $rc_ $(has 'the rest has not run' "$S/R7c.txt") $((c1 - c0)) $rd $((c2 - c1)) $(has 'config TDP 0 W / 65 C / 600 MHz, et-who clean' "$S/R7d.txt") $re $((b1 - b0)) $(has 'aifoundry1 card 1: config TDP 65 W / 65 C / 600 MHz, minion_mv 499; identity /dev/et1_mgmt, physical device ID 1' "$S/R7e.txt")" \
   "10 1 10 1 10 1 0 0 1 1 0 1 1" "no report: $(stopline "$S/R7a.txt" | cut -c1-80); 31 min: $(stopline "$S/R7b.txt" | cut -c1-80); 10 min after a session: $(stopline "$S/R7c.txt" | cut -c1-80) (reader calls $((c1 - c0))); arm B: $(grep -m1 'aifoundry1 card 1:' "$S/R7e.txt" | cut -c1-100)"
step "D: step 8 on aifoundry3 (the dry pass and THE SCRUB CHECK); DB: on aifoundry1; DS: the scrub check refusing another home's path"
ra=$(run "$OA" DA1 s10_dry_e213.sh A start); ra2=$(waitjob "$OA" DA2 s10_dry_e213.sh A wait)
rb1=$(run "$OB" DB1 s10_dry_e213.sh B start); rb2=$(waitjob "$OB" DB2 s10_dry_e213.sh B wait)
ddb=$(ls -d "$A1"/build/e213/T*-B-dry 2>/dev/null | tail -n 1)
mkdir -p "$ddb/zz"; echo '{"path": "/home/someoneelse/work/x"}' > "$ddb/zz/other-home.json"
rs=$(waitjob "$OB" DS s10_dry_e213.sh B wait); rm -rf "${ddb:?}/zz"
ok "$ra $ra2 $(has 'SCRUB-CHECK CLEAN: ' "$S/DA2.txt") $rb1 $rb2 $(has 'SCRUB-CHECK CLEAN: ' "$S/DB2.txt") $rs $(has 'SCRUB-CHECK LEFT' "$S/DS.txt")" "0 0 1 0 0 1 16 1" \
   "$(grep -m1 'E213-DRY' "$S/DA2.txt" | cut -c1-80); $(grep -m1 'SCRUB-CHECK' "$S/DA2.txt" | cut -c1-90); arm B: $(grep -m1 'SCRUB-CHECK' "$S/DB2.txt" | cut -c1-80); another home: $(stopline "$S/DS.txt" | cut -c1-80)"
step "HG: a HUNG marker in a session log of ours on aifoundry3: step 9 refuses"
mkdir -p "$A3/build/e204/T1794800000"
printf '%s session start (T0 1794800000; desk test)\n%s HUNG: a device process did not end after its timeout TERM (desk test)\n%s session end (T0 1794800000)\n' \
  "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" > "$A3/build/e204/T1794800000/session.log"
touch -d '-3 hours' "$A3/build/e204/T1794800000/session.log"
r=$(run "$OA" HG s11_session_e213.sh A); rm -rf "${A3:?}/build/e204"
ok "$r $(has 'REFUSED: a HUNG marker of ours on the box' "$S/HG.txt") $(ls "$A3/build/e213" 2>/dev/null | grep -c '^T[0-9]*-A$')" "10 1 0" "$(grep -m1 'REFUSED' "$S/HG.txt" | cut -c1-140)"
step "SD: the same-day rule: an E213 arm A session that opened the card earlier today"
mkdir -p "$A3/build/e213/T1700000000-A"
printf '%s session start (T0 1700000000; desk test)\n%s the first card command: the start config read through the guard\n%s session end (T0 1700000000)\n' \
  "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-45 min' '+%F %T %Z')" > "$A3/build/e213/T1700000000-A/session.log"
if [ "$(TZ=America/Los_Angeles date -d '-45 min' +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then touch -d '-45 min' "$A3/build/e213/T1700000000-A/session.log"
else TZ=America/Los_Angeles touch -d "$(TZ=America/Los_Angeles date +%F) 00:00:01" "$A3/build/e213/T1700000000-A/session.log"; fi
r=$(run "$OA" SD s11_session_e213.sh A); rm -rf "${A3:?}/build/e213/T1700000000-A"
ok "$r $(has 'REFUSED: the same-day rule' "$S/SD.txt")" "10 1" "$(grep -m1 'REFUSED' "$S/SD.txt" | cut -c1-140)"
step "LS: THE LAST START passed (the window's last end still far): step 9 refuses (16) before anything is sent"
O6=$S/out6; mkdir -p "$O6"; cp "$OA/window.env" "$OA/e213-built-A.txt" "$O6/"
sedi -e "s/^RB_LAST_START_EPOCH=.*/RB_LAST_START_EPOCH=$(( $(date +%s) - 60 ))/" "$O6/window.env"; touch "$O6/window.env" "$O6/e213-built-A.txt"
n0=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
r=$(run "$O6" LS s11_session_e213.sh A); n1=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
ok "$r $(has "past the round's last start" "$S/LS.txt") $((n1 - n0))" "16 1 0" "$(stopline "$S/LS.txt" | cut -c1-140); box calls $((n1 - n0))"
step "NS: no never-run report from today in RB_OUT: step 9 refuses (10) before anything is sent"
O7=$S/out7; mkdir -p "$O7"; cp "$OA/window.env" "$OA/e213-built-A.txt" "$O7/"; touch "$O7/window.env" "$O7/e213-built-A.txt"
n0=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
r=$(run "$O7" NS s11_session_e213.sh A); n1=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
ok "$r $(has 'no never-run report from today' "$S/NS.txt") $((n1 - n0))" "10 1 0" "$(stopline "$S/NS.txt" | cut -c1-140); box calls $((n1 - n0))"
step "LA: step 9 launches the REAL session_e213.sh, which stops at its box check (the desk's own hostname); step 10 reads the gate"
r=$(run "$OA" LA s11_session_e213.sh A); r2=$(waitjob "$OA" LA2 s20_wait_e213.sh A)
t0=$(cat "$OA/e213-T0-A.txt" 2>/dev/null)
sd=$A3/build/e213/T$t0-A
procs=$(find "$sd" -name 'proc*.out' 2>/dev/null | wc -l | tr -d ' ')
ok "$r $r2 $(has 'refused, no device opened: the box or the build is not the registered one (this host is' "$sd/session.log") $(has '"rc": 16' "$sd/queue.json") $( [ -s "$sd/MANIFEST.sha256" ] && echo manifest) $procs $(has 'GATE-STOPPED e213 arm A' "$S/LA2.txt")" \
   "0 16 1 1 manifest 0 1" "$(grep -m1 'no device opened' "$sd/session.log" | cut -c1-200)"
step "W10: step 10's readings on stand-in logs (a running session, none, HUNG, K1, CRASH, an ended session with a STOP line)"
O3=$S/out3; mkdir -p "$O3"; cp "$OA/window.env" "$OA/box-login-aifoundry3.txt" "$O3/"; touch "$O3/window.env"; echo 7 > "$O3/e213-T0-A.txt"
mkdir -p "$A3/build/q141k"; echo 7 > "$A3/build/q141k/e213A.T0"; W7=$A3/build/e213/T7-A; mkdir -p "$W7"
mkdir -p "$S/wv"; printf '#!/bin/bash\nsleep 30\n' > "$S/wv/session_e213.sh"
wr() { RB_OUT=$O3 RB_DESKTEST=1 RB_WAIT_LOOP_S=4 bash "$T/$E/rb/s20_wait_e213.sh" A > "$S/W10-$1.txt" 2>&1; echo $?; }
echo "$(date '+%F %T %Z') session start (T0 7; desk-test stand-in, no end)" > "$W7/session.log"
setsid bash "$S/wv/session_e213.sh" < /dev/null > /dev/null 2>&1 &
p3=$!
sleep 1
rv=$(wr V)
kill "$p3" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$p3" 2>/dev/null || break; sleep 0.5; done
rg=$(wr G)
printf '%s session start (T0 7; desk test)\n%s HUNG: a device process (the host of 002-pass1-a039 (proc-00); its `timeout` pid 9) still runs\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"
rh=$(wr H)
printf '%s session start (T0 7; desk test)\n%s STOP: K1: a launch of run 002-pass1-a039 did not finish (the host'"'"'s words): it may leave a hung hart: nothing further started\n%s session end (T0 7)\n' \
  "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo "x  session.log" > "$W7/MANIFEST.sha256"; echo 0 > "$W7/runner.rc"
rk=$(wr K)
printf '%s session start (T0 7; desk test)\n%s CRASH: KeyError: b99\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 1 > "$W7/runner.rc"
rc_=$(wr C)
printf '%s session start (T0 7; desk test)\n%s STOP: board 71.2 W above 70 W on 3 samples in a row: nothing further started\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 0 > "$W7/runner.rc"
re=$(wr E)
rm -rf "${A3:?}/build/e213/T7-A"; echo "$t0" > "$A3/build/q141k/e213A.T0"
ok "$rv $rg $rh $rk $rc_ $re $(has 'RUN-RUNNING' "$S/W10-V.txt")$(has 'RUN-GONE' "$S/W10-G.txt")$(has 'KILL NOTHING' "$S/W10-H.txt")$(has 'K1' "$S/W10-K.txt")$(has 'crashed' "$S/W10-C.txt")$(has 'read its STOP line' "$S/W10-E.txt")" \
   "17 14 16 16 16 0 111111" "running $rv, gone $rg, HUNG $rh, K1 $rk, CRASH $rc_, ended with a STOP line $re"
step "C: step 11 on LA's session, step 12 (the gate stop's record), step 13 refuses it; C2: a byte changed after the manifest"
r=$(run "$OA" C1 s22_collect_e213.sh A); r2=$(run "$OA" C2s s23_data_e213.sh A); r3=$(run "$OA" C3s s24_score_e213.sh A)
gs=$(cat "$OA/e213-data-dir-A.txt" 2>/dev/null)
ok "$r $r2 $(has 'COLLECTED-GATE-STOP docs/reports/gate-stops/' "$S/C2s.txt") $(grep -rl '/home/' "$T/$gs" 2>/dev/null | wc -l | tr -d ' ') $r3" "0 0 1 0 10" \
   "$(grep -m1 'COLLECTED' "$S/C2s.txt" | cut -c1-140); step 13: $(stopline "$S/C3s.txt" | cut -c1-100)"
rm -rf "${T:?}/$gs"
O2=$S/out2; mkdir -p "$O2"; cp "$OA"/window.env "$OA"/e213-T0-A.txt "$OA"/box-login-aifoundry3.txt "$O2/"; touch "$O2/window.env"
echo "x" >> "$sd/session.log"
r=$(RB_OUT=$O2 RB_DESKTEST=1 bash "$T/$E/rb/s22_collect_e213.sh" A > "$S/C2.txt" 2>&1; echo $?)
ok "$r $(has 'COPY-BACK NOT EXACT' "$S/C2.txt")" "16 1" "$(stopline "$S/C2.txt" | cut -c1-140)"
step "CD: arm A's session that ran (step 8's dry session copied as a session): steps 11, 12 and, after a stand-in data commit, 13 WITH step 6n's labels; CDB: arm B's"
for arm in A B; do
  if [ "$arm" = A ]; then bx=$A3; O=$S/out4; src=$OA; box=aifoundry3; suf=aifoundry3; else bx=$A1; O=$S/out4b; src=$OB; box=aifoundry1; suf=aifoundry1-c1; fi
  dd=$(ls -d "$bx"/build/e213/T*-$arm-dry 2>/dev/null | tail -n 1)
  mkdir -p "$O"; cp "$src"/window.env "$src"/box-login-$box.txt "$src"/e213-neverrun-dir-$arm.txt "$O/"; touch "$O/window.env"; echo 8 > "$O/e213-T0-$arm.txt"
  mkdir -p "$bx/build/q141k"; cp -a "$dd" "$bx/build/e213/T8-$arm"; rm -f "${bx:?}/build/e213/T8-$arm/dry.lock"
  r=$(run "$O" CD1$arm s22_collect_e213.sh $arm); r2=$(run "$O" CD2$arm s23_data_e213.sh $arm)
  dd2=$(cat "$O/e213-data-dir-$arm.txt" 2>/dev/null)
  $G add --sparse -f "$dd2" > /dev/null 2>&1; $G commit -q -m "desk test: a data commit (stand-in, arm $arm)" > /dev/null 2>&1
  r3=$(run "$O" CD3$arm s24_score_e213.sh $arm)
  nh=$(grep -c . "$O/box-home-$arm.txt" 2>/dev/null)
  if [ "$arm" = A ]; then
    ok "$r $r2 $(has "COLLECTED docs/reports/data/$TODAY-e213-blind-matmul-$suf" "$S/CD2$arm.txt") $( [ -s "$T/$dd2/data-e213.json" ] && echo data) $(grep -c '  \(neverrun-e213-card\.\(txt\|json\)\|judge-e213-card\.\(txt\|json\)\|labels-e213\.json\)$' "$T/$dd2/SHA256SUMS" 2>/dev/null) $(has 'LABELS-OK' "$S/CD3$arm.txt") $r3 $( [ -s "$O/scores-e213-$arm.json" ] && echo scored) $( [ "$nh" -ge 1 ] && echo homes)" \
       "0 0 1 data 5 1 0 scored homes" "$(grep -m1 'COLLECTED' "$S/CD2$arm.txt" | cut -c1-130); $(grep -m1 'scored arm' "$S/CD3$arm.txt" | cut -c1-80); labels applied: $(/usr/bin/python3 -I -B -c "import json, sys; print(json.load(open(sys.argv[1])).get('labels_applied'))" "$O/scores-e213-A.json" 2>/dev/null | cut -c1-80)"
  else
    ok "$r $r2 $(has "COLLECTED docs/reports/data/$TODAY-e213-blind-matmul-$suf" "$S/CD2$arm.txt") $( [ -s "$T/$dd2/data-e213.json" ] && echo data) $(grep -c '  labels-e213\.json$' "$T/$dd2/SHA256SUMS" 2>/dev/null) $r3 $( [ -s "$O/scores-e213-$arm.json" ] && echo scored)" \
       "0 0 1 data 1 0 scored" "$(grep -m1 'COLLECTED' "$S/CD2$arm.txt" | cut -c1-130); $(grep -m1 'scored arm' "$S/CD3$arm.txt" | cut -c1-80)"
  fi
done
$G reset -q --hard "$KIT"
step "Z: nothing of this test left running"
left=0
for p in /proc/[0-9]*; do
  c=$(readlink "$p/cwd" 2>/dev/null) || continue
  case "$c" in "$S"|"$S"/*) [ "${p#/proc/}" = "$$" ] || left=$((left + 1)) ;; esac
done
ok "$left" 0 "processes whose working directory is under the scratch directory (the stand-in boxes' jobs, sessions, builds)"
echo
echo "box calls the stand-ins served: $(grep -c . "$S/calls.log" 2>/dev/null || echo 0) (all to the stand-in boxes; no lab box was reached)"
echo "SELFTEST-RB-E213 $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
}
main
