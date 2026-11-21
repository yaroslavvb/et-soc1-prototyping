#!/usr/bin/env bash
# E224 ARM A (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): the desk test of arm A's runbook with a FAKE ssh and rsync on a
# stand-in AIFOUNDRY1 (card 1), E218's rb/selftest_rb_e218.sh (E215's form) made arm A's box's with E215's arm B cases (rb/selftest_rb_e215.sh:
# OB, BB, R7B). Its scratch repository is a shared, sparse clone of the lab clone this test runs from (its HEAD holds E224's registration as a
# commit, as on the card day) with the kit's files committed on top as one stand-in kit commit, the kit's list (SHA256SUMS-e224-kit, both arms'
# files, both step 2s outside it) a stand-in made here and pinned in the scratch copy of step 2's KITPIN line (the one line this test changes in
# a copy), and stand-in desk-test logs (this test's own log is not final while it runs). The stand-in box is aifoundry1's ~/nekko, an rsync
# target under the scratch; the stand-in ssh serves it with `bash -s` (and `true`) and refuses any other host or command; the stand-in rsync
# rewrites its paths; the box's hostname, uptime, et-who, et-lab-manifest and pgrep are stand-ins, and the box tree holds a stand-in reader at
# build/ettelem/ettelem (the doubles' config and sampler: card 1's TDP 65 W / 65 C / 600 MHz, 499 mV) behind arm A's own guard
# (ettelem_guard_e224a.sh with ET_DEVICES=1, step 7); cmake, the compilers and /opt/et are this desk's REAL ones (the build is the real
# build_e224a.sh, which this desk's device layer stops at its ET_DEVICES gate: case BB; the later cases run on a stand-in BUILT record beside the
# real ELFs and hosts). Step 6n's scan reads the scratch repository at its HEAD as the lab and a stand-in folder as the round's lanes
# (E224A_ROUND_OUT). No lab box is reached. When the lab clone's history holds the kit commit (the commit that added KIT.md: the
# readiness lane), the scratch repository is built at that commit's PARENT and the kit's files are taken from HEAD, its main following a local
# branch at that parent; otherwise (the kit lane) the untracked files and the lab clone's HEAD. Cases:
#   A   the dry listing: every step exits 0 (15 steps), no call reaches the stand-ins
#   K   step 2 with no window: 10       W1 a window written for another arm: 10      W2 a window written for another runbook: 10
#   W3  step 1 for another day: 10      W4 step 1 with another arm (B): 10, naming arm A's card      G  step 2 without RB_GITLOCK: 10
#   N   step 2 inside the lab-git lock (nested): 16 naming the pull
#   P1  step 2 on the scratch repository: 0 (the lists at their pins, HISTORY OK, the registration and the kit found by content, MM1-v3.2's
#       land an ancestor, the registration's five checks in their --check form, the scorer's two self-tests byte-identical, its forecasts print
#       (print only), the preflight GO, the desk tests' logs, nothing written)
#   P1W STEP 2 WROTE NOTHING in the scratch repository's work tree: no file outside .git newer than a marker made before P1, the registered
#       forecast files' (forecast-e224.txt, forecast-e224.csv, forecast-e224.json) times and inodes unchanged; the frozen scorer's two
#       self-tests' outputs, which step 2 put in RB_OUT (rb/scorer_check_e224.py), and its one PASS line
#   P1X STEP 2 SEES A REWRITE WITH THE SAME BYTES, which git status cannot: a stand-in preflight (in place of preflight_e224a.sh, a kit file) that
#       rewrites two registered files with their own bytes - forecast-e224.csv and forecast-e224.json under E224's folder (the
#       form of a registration check run in its writing form) - then prints the preflight's GO line: 16 naming wrote-in-lab and both files
#       (beside the changed kit file's own failures); the files' bytes unchanged; the files restored from the scratch's HEAD
#   P2  in one step-2 run: the registration's list one line short, the kit's list one line short and a desk test's log without its PASS line
#       (that log is in the kit's list, so the kit's list reads one entry not OK too): 16, the failure list naming all three
#   H1  a committed edit of a registration file: 16 by the history check      H2 a committed tools/claims-v3/e224/json.py (a shadow): 16
#   DA  arm A's data committed (a docs/reports/data folder named <day>-e224a-blind-matmul-aifoundry1): step 2 refuses (16, E224-has-data)
#   GS  in one step-2 run: an E224 gate stop's record committed (step 2 reports it) and a stand-in FILE whose name holds 'e224a' committed under
#       docs/reports/data (E175's design tile-name form, ...0e224af.bin: no tile so named exists at HEAD; a file is not a datum): 0
#   S0  THE STEP-0 CHECKS (rb/s00_step0_e224a.sh) on the scratch repository with a stand-in GitHub main: (a) no sealed record: "sealed 0 of 0",
#       6 of 6 as stated; (b) a record whose sealed sha256 the note at HEAD (tools/claims-v3/sealed-e224/e224-freeze-lines.md) registers: 1 of 1;
#       (c) a record listing a sha256 the note does not register: S1 NOT AS STATED, exit 1; (d) GitHub main = the registration's parent: F1 (the
#       freeze line) as stated, F1R and F2 NOT AS STATED, exit 1; (e) GitHub main before MM1-v3.2's land: F1 NOT AS STATED; (f) arm A's data
#       committed: D0 NOT AS STATED; (g) an untracked file in the lab clone: G1 NOT AS STATED
#   O   the look on the stand-in aifoundry1 booted BEFORE E82's firmware read (k6's s05, unchanged): FREE, our login recorded for the scrub
#   OB  THE STAND-IN BOOTED AFTER E82'S FIRMWARE READ (aifoundry1's boot now, 2026-11-17 16:46:32 PST): k6's look stops at its identity by
#       continuity (16): the reason arm A's step 4 is the A2 form's (fwgate's identity gate on this boot), whose own desk test boots its
#       stand-in box there (a2/desk/selftest_a2_e224a.sh)
#   OL  E224's ours_live: a shell whose command string names session_e224a.sh is not a session; a session_e224a.sh run as a script is
#   SY  step 5: the rsync, HARNESS OK on the box     L1 a login link on a read: 11, "<HH:MM:SS> aifoundry1 needs a check" appended to RB_LOCK,
#       nothing retried      L2 a read that hangs (the read class's bound 3 s for this call): 13
#   T   NO-THIRD-BUILD: two starts recorded on aifoundry1 today: a third start is refused with 16
#   BB  step 6 on aifoundry1: start, wait: the REAL build of both trees on this desk's stock device layer stops at THE ET_DEVICES GATE (the
#       wait reads 16, RGM-BUILD-FAILED 'ET_DEVICES: a host has no ET_DEVICES', no RB_OUT/e224a-built-A.txt): E215 arm B's BB; the later cases
#       run on a stand-in BUILT record (the real ELFs' and hosts' sha256, the ET_DEVICES reading) and RB_OUT/e224a-built-A.txt written here
#   NR  STEP 6n, THE NEVER-RUN SEARCH REPEATED (the registration's scanner over the scratch repository and a stand-in lanes folder): a record of
#       g08's token (gemmLnc2x14x16, family G: the token on aifoundry1 card 1) in a card-a3 lane folder dated BEFORE the freeze line, and a record
#       of y06b's configuration (gemmL2x8x24 at mask 0x3030, family Y: the shape at its mask) dated now: both labelled 'ran before' (E224.md 4,
#       whatever the date; each file's date against the freeze line REPORTED), y06a (the same token at mask 0xf) not; E224's own card lane
#       folder (card-e224a, f01's token there) SUBTRACTED; a desk lane (kit-e224ax, f02's token there) not read; the labels LABELS-OK
#   R7  STEP 7 ONLY WITH A FRESH NEVER-RUN REPORT AND ONLY ONCE THE REST HAS OPENED: no report: 10; a report 31 minutes old: 10; a session of ours
#       ended 10 minutes ago: 10; R7e THE REST RULE on the model session's folders: a write under ~/claude/work/ee-desktest/ on the box 10
#       minutes ago: 10; in none of these is the stand-in reader called; then (both 45 minutes back) 0, the reader called once (card 1's read
#       through arm A's guard with ET_DEVICES=1: TDP 65 W / 65 C / 600 MHz, 499 mV); R7f the card's threshold reading 70 C (thr70): 16
#   D   step 8 (the doubles on the box): 0, and THE SCRUB CHECK on the dry pass's copy reads CLEAN (the box's home masked)
#   DS  THE SCRUB CHECK REFUSES BEFORE THE SESSION: a file with another home's path (/home/<someone else>/...) in the dry pass's folder: the wait
#       reads 16 (SCRUB-CHECK LEFT), no session that day
#   HG  THE HUNG MARKER: a session log of ours on aifoundry1 with a HUNG line: step 9 refuses (10), nothing launched
#   SD  THE SAME-DAY RULE: an E224 arm A session that opened the card earlier today: step 9 refuses (10)
#   LS  THE LAST START passed with the last end still far: step 9 refuses (16) and sends nothing to the box
#   NS  no never-run report from today in RB_OUT (step 6n): step 9 refuses (10) and sends nothing to the box
#   LA  step 9 launches the REAL session_e224a.sh and run_e224a.py on the stand-in aifoundry1, which stop at their box check before any device (the
#       desk's own hostname): "refused, no device opened"; step 10 reads GATE-STOPPED (16) with the manifest written
#   W10 step 10's readings on stand-in logs: a running session_e224a.sh with no end 17 (RUN-RUNNING); none running 14 (RUN-GONE); a HUNG line 16
#       (HUNG); a K1 stop 16 (K1-STOPPED); a CRASH line 16 (CRASHED); an ended session (rc 0) with a STOP line 0
#   C   step 11 on LA's session: COPY-BACK EXACT 0; step 12: the gate stop's record under docs/reports/gate-stops/ (COLLECTED-GATE-STOP), the
#       desk-path gate, HISTORY OK: 0; step 13 refuses a gate stop's record: 10      C2 one byte of a box file changed after the manifest:
#       COPY-BACK NOT EXACT 16
#   CD  a session that ran (step 8's dry session copied as a session): step 11 0 (the box's home in every form read), step 12 the data directory
#       (docs/reports/data/<today>-e224a-blind-matmul-aifoundry1) with data-e224a.json (the reducer), step 6n's report, judgement and labels (in
#       SHA256SUMS) and the scrub clean: 0; after a stand-in data commit, step 13 runs the FROZEN scorer on it WITH step 6n's labels (LABELS-OK
#       first): 0, the labels applied
#   Z   no process of this test left running
#   bash tools/claims-v3/e224/rb/selftest_rb_e224a.sh <scratch dir> > logs/selftest-rb-e224a.txt   (prints SELFTEST-RB-E224A <n> of <m> PASS or FAIL)
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
# E211's fix kept: the stand-in box is this desk, so ours_live reads the desk's real process table; the test runs itself once more in a private
# PID namespace (bubblewrap), where it sees only its own processes; E224A_RB_PIDNS=1 marks that inner run.
if [ -z "${E224A_RB_PIDNS:-}" ]; then
  command -v bwrap > /dev/null || { echo "no bwrap: the runbook test runs in a private PID namespace"; exit 2; }
  echo "(the runbook test: re-run in a private PID namespace, so that no other lane's process on this desk is read as a session of ours)"
  exec /usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- env E224A_RB_PIDNS=1 bash "$SRC/tools/claims-v3/e224/rb/selftest_rb_e224a.sh" "$@"
fi
for c in timeout sha256sum flock cmake c++ rsync git; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
REAL_RSYNC=$(command -v rsync)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree box bin boxbin out; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; B=$S/box; BIN=$S/bin; BB=$S/boxbin
A3=$B/aifoundry1/nekko        # (E218's variable name kept: the stand-in box is aifoundry1's ~/nekko, arm A's tree)
E=tools/claims-v3/e224
FZ=4e386f7519a236fb0bf8c43d26f8303be57e09a2       # the points' and forecasts' freeze line: MM1-v3.2's land
MMF=$E/forecast-e224.json     # E224's registered forecasts (forecast_e224.py writes forecast-e224.json, .csv and .txt)
mkdir -p "$A3" "$BIN" "$BB"
sedi() { local f=${!#} t; t=$(mktemp "$S/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
main() {
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" 2>/dev/null && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
# ---- the scratch repository: a shared sparse clone of the lab clone's HEAD (the registration in it), the kit's files as one stand-in commit
git clone -q --shared --no-checkout "$SRC" "$T" || return 2
G="git -C $T -c user.name=e224a-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/ /docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/ \
  /docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/ /docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/ \
  /docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/ /docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/ \
  /docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/ /docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/ \
  /docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2/ /docs/reports/data/2026-11-16-e208-mmsweep-a2c0-S1/ \
  /docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry1-c1/ /docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry2/ /workloads/nocbench/analyze.py || return 2     # the data folders step 2's checks read (plan_e224,
# rules_e224 through run_v32, the scorer's real-bytes self-test) and the mesh map MM1-v3.2's layout module reads (through E215's v01_map.py)
KITC=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/KIT.md | tail -n 1)
if [ -n "$KITC" ]; then
  BASE=$(git -C "$SRC" rev-parse "$KITC^") || return 2
  FORM="the kit committed in the lab clone (${KITC:0:12}): the scratch built at its parent ${BASE:0:12}, the kit's files from HEAD $(git -C "$SRC" rev-parse --short=12 HEAD)"
else
  BASE=$(git -C "$SRC" rev-parse HEAD) || return 2
  FORM="the kit's files untracked in the lab clone: the scratch built at its HEAD ${BASE:0:12}"
fi
$G checkout -q -B main "$BASE" || return 2
{ $G branch -q -f e224a-desktest-base "$BASE" && $G branch -q --set-upstream-to=e224a-desktest-base main; } || { echo "the scratch's upstream could not be set"; return 2; }
REGC=$($G log --diff-filter=A --format=%H -- $E/E224.md | tail -n 1)
[ -n "$REGC" ] || { echo "the registration is not in the scratch repository's history"; return 2; }
if [ -n "$KITC" ]; then
  git -C "$SRC" diff-tree --no-commit-id --name-only -r --diff-filter=A "$KITC" -- $E | while IFS= read -r f; do
    mkdir -p "$T/$(dirname "$f")"; git -C "$SRC" show "HEAD:$f" > "$T/$f" || exit 2; done || { echo "the kit's files could not be taken from HEAD"; return 2; }
else
  ( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E ) | sort -u | while IFS= read -r f; do
    [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
fi
[ -s "$T/$E/KIT.md" ] || { echo "no KIT.md among the kit's files: step 2 finds the kit commit by it"; return 2; }
mkdir -p "$T/$E/logs"
for spec in "selftest-run-e224a.txt SELFTEST-RUN-E224A 0 of 0 PASS" "realpath-e224a.txt REALPATH-E224A 0 of 0 PASS" "realbytes-e224a.txt REALBYTES-E224A 0 of 0 PASS" \
            "desktest-build-e224a.txt DESKTEST-BUILD-E224A 0 of 0 PASS" "selftest-rb-e224a.txt SELFTEST-RB-E224A 0 of 0 PASS" \
            "dry-listing-e224a-A.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e224a.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"
done
mkdir -p "$T/$E/a2/logs"
printf '%s\n' "SELFTEST-A2-E224A 0 of 0 PASS" > "$T/$E/a2/logs/selftest-a2-e224a.txt"
printf '%s\n' "dry listing (A2, arm A): 0 steps listed, 0 exited non-zero, 0 box calls" > "$T/$E/a2/logs/dry-listing-a2-A.txt"
( cd "$T" && /usr/bin/python3 -I -B $E/check_e224a.py --make > /dev/null )
mklist() {  # the kit's stand-in list: every file this stand-in commit adds under E224's folder, but the list itself and step 2
  ( cd "$T" && git ls-files --others --exclude-standard -- $E | grep -v -x -e "$E/SHA256SUMS-e224-kit" -e "$E/rb/s03_desk_e224a.sh" -e "$E/rb/s03_desk_e224b.sh" |
      LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/kit-standin.txt"
  KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e224-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^KITPIN=$E/SHA256SUMS-e224-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e224-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e224a.sh"
  grep -q "^KITPIN=$E/SHA256SUMS-e224-kit:$KITN:$KITH:top" "$T/$E/rb/s03_desk_e224a.sh"
}
mklist || { echo "the scratch step 2's KITPIN was not set"; return 2; }
$G add -A $E && $G commit -q -m "E224 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; return 2; }
KIT=$($G rev-parse HEAD)
echo "scratch repository: a shared sparse clone of the lab clone ($FORM; the registration ${REGC:0:12} in it), the kit as one stand-in commit ${KIT:0:12}; the kit's stand-in list $KITN files"
[ "$KITN" -gt 0 ] || { echo "the kit's stand-in list is empty"; return 2; }
# ---- the stand-ins
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry1) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; cat > /dev/null; echo "To authenticate, visit: https://login.tailscale.com/a/e224adesktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'bash -s' and 'true' are served (got: \$cmd)" >&2; exit 97; }
cd "$B/\$host" || exit 1
exec env HOME="$B/\$host" STANDIN_HOST="\$host" STANDIN_S="$S" PATH="$BB:\$PATH" bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry1) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho "scp refused by the desk test" >&2\nexit 97\n' > "$BIN/scp"
printf '#!/bin/sh\necho "${STANDIN_HOST:-desk}"\n' > "$BB/hostname"
cat > "$BB/uptime" <<EOF
#!/bin/sh
if [ "\${1:-}" = -s ] && [ -n "\${STANDIN_HOST:-}" ]; then
  if [ -s "$S/boot-\${STANDIN_HOST}" ]; then cat "$S/boot-\${STANDIN_HOST}"; else echo "2026-10-26 15:18:24"; fi; exit 0
fi
exec /usr/bin/uptime "\$@"
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
mkdir -p "$A3/build/ettelem" "$A3/tools/claims-v3/e128"       # the box's reader stand-in (counting its calls), arm A's doubles
cat > "$A3/build/ettelem/ettelem" <<EOF
#!/bin/sh
echo "\$(date +%s) \$*" >> "$S/reader-calls-A.txt"
mode=ok; [ -s "$S/reader-mode-A" ] && mode=\$(cat "$S/reader-mode-A")
exec env E224A_FAKE_ARM=A E224A_FAKE_CONFIG=\$mode /usr/bin/python3 -B "$T/$E/fake_card_e224a.py" "\$@"
EOF
chmod +x "$A3/build/ettelem/ettelem"
cp -p "$SRC/tools/claims-v3/e128/ettelem_guard.sh" "$A3/tools/claims-v3/e128/ettelem_guard.sh"     # (k6's; arm A's step 7 runs the kit's own guard, synced by step 5)
export PATH="$BIN:$PATH" RB_LOCK="$S/rb-lock.txt"
GL=$S/lab-git.lock; : > "$GL"
TODAY=$(TZ=America/Los_Angeles date +%F)
STARTHM=23:58; ENDHM=23:59           # the window is today's last minutes: the steps' budgets are E224A_DESK_BUDGET_S (60 s) here
OA=$S/outA; mkdir -p "$OA"
NRO=$S/nr/out
run() {  # run <RB_OUT> <log> <script> [args]: a step of the scratch repository's runbook
  local o=$1 lg=$2; shift 2
  RB_OUT=$o RB_GITLOCK=$GL RB_DESKTEST=1 E224A_DESK_BUDGET_S=60 E224A_ROUND_OUT="$NRO" bash "$T/$E/rb/$1" "${@:2}" > "$S/$lg.txt" 2>&1
  echo $?
}
waitjob() {  # waitjob <RB_OUT> <tag> <script> <args...>: call a wait step until it says something other than 17 (at most 40 calls)
  local o=$1 tag=$2 r k; shift 2
  for k in $(seq 1 40); do r=$(run "$o" "$tag-$k" "$@"); [ "$r" = 17 ] || { cp "$S/$tag-$k.txt" "$S/$tag.txt"; echo "$r"; return; }; done; echo 17
}
rec() {  # rec <arm token> <type> <tile> <mask>: one SPARSITY record line of the lab's hosts, randn data
  printf 'SPARSITY {"test":"fma","arm":"%s","gen":"randn","type":"%s","pattern":"none","values":"%s:randn:tools/claims-v3/kinds/tiles/%s","b_stream":0,"minions":1024,"shire_mask":"%s","iters":1,"passes":1,"launch":0,"cycles_max":1,"ghz":0.6,"ok":true}\n' "$1" "$2" "$1" "$3" "$4"
}
step "A: the dry listing"
mkdir -p "$S/listing-A"
( cd "$T" && bash $E/rb/list_steps_e224a.sh A "$S/listing-A" > "$S/A-A.txt" 2>&1 )
ok "$(grep -c 'dry listing: 15 steps listed, 0 exited non-zero, 0 box calls' "$S/A-A.txt")" "1" "$(tail -n 1 "$S/A-A.txt")"
step "K: step 2 with no window"
r=$(run "$OA" K s03_desk_e224a.sh A); ok "$r $( [ -s "$S/calls.log" ] && echo calls || echo nocalls)" "10 nocalls" "$(grep -m1 STOP "$S/K.txt" | cut -c1-120)"
step "W1: a window written for another arm; W2: a window written for another runbook; W3: step 1 for another day; W4: step 1 with an unknown arm"
r=$(run "$OA" W1a s02_window_e224a.sh A "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_ARM=A/RB_ARM=B/' "$OA/window.env"; r1=$(run "$OA" W1 s03_desk_e224a.sh A)
rm -f "$OA/window.env"; r=$(run "$OA" W2a s02_window_e224a.sh A "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_PLAN=e224a/RB_PLAN=e215/' "$OA/window.env"
r2=$(run "$OA" W2 s03_desk_e224a.sh A)
r3=$(run "$OA" W3 s02_window_e224a.sh A 2026-11-12 10:00 12:00)
rm -f "$OA/window.env"; r4=$(run "$OA" W4 s02_window_e224a.sh B "$TODAY" "$STARTHM" "$ENDHM")
r=$(run "$OA" W0 s02_window_e224a.sh A "$TODAY" "$STARTHM" "$ENDHM")
ok "$r1 $(has 'not arm A' "$S/W1.txt") $r2 $(has 'not E224' "$S/W2.txt") $r3 $r4 $(has "A .aifoundry1 card 1, E224 arm A's runbook" "$S/W4.txt") $r" "10 1 10 1 10 10 1 0" "$(grep -m1 STOP "$S/W1.txt" | cut -c1-100); $(grep -m1 STOP "$S/W2.txt" | cut -c1-100); $(grep -m1 STOP "$S/W4.txt" | cut -c1-90)"
step "G: step 2 without RB_GITLOCK"
r=$(RB_OUT=$OA RB_DESKTEST=1 bash "$T/$E/rb/s03_desk_e224a.sh" A > "$S/G.txt" 2>&1; echo $?); ok "$r" 10 "$(grep -m1 STOP "$S/G.txt" | cut -c1-100)"
step "N: step 2 inside the lab-git lock (nested)"
r=$(RB_OUT=$OA RB_GITLOCK=$GL RB_DESKTEST=1 RB_GITLOCK_T=3 flock -n "$GL" bash "$T/$E/rb/s03_desk_e224a.sh" A > "$S/N.txt" 2>&1; echo $?)
ok "$r $(has 'pull(rc 14; a nested lab-git lock exits 75)' "$S/N.txt")" "16 1" "$(stopline "$S/N.txt" | cut -c1-160)"
step "P1: step 2 on the scratch repository"
FCF="$E/forecast-e224.txt $E/forecast-e224.csv $MMF"
touch "$S/p1-before.marker"; fcs0=$(cd "$T" && stat -c '%y %i' $FCF | tr '\n' ' ')
r=$(run "$OA" P1 s03_desk_e224a.sh A)
ok "$r $(has 'desk check: the window written today for E224 arm A' "$S/P1.txt")" "0 1" "$(grep -m1 'desk check:' "$S/P1.txt" | cut -c1-260)"
[ "$r" = 0 ] || tail -n 30 "$S/P1.txt"
step "P1W: P1 wrote nothing in the scratch repository's work tree; the registered forecast files untouched; the frozen scorer's two self-tests (rb/scorer_check_e224.py) in RB_OUT, byte-identical"
find "$T" -path "$T/.git" -prune -o -type f -newer "$S/p1-before.marker" -print > "$S/P1W-newer.txt" 2>&1
fcs1=$(cd "$T" && stat -c '%y %i' $FCF | tr '\n' ' ')
nf=$(ls "$OA/scorer-check-A/selftest-standins-e224-check.json" "$OA/scorer-check-A/selftest-real-e224-check.json" 2>/dev/null | wc -l | tr -d ' '); gv=$(grep -c 'SCORER-CHECK-E224: stand-ins PASS' "$S/P1.txt")
ok "$(grep -c . "$S/P1W-newer.txt") $([ "$fcs0" = "$fcs1" ] && echo same || echo changed) $nf $gv" "0 same 2 1" \
   "files written in the scratch's work tree by P1: $(grep -c . "$S/P1W-newer.txt")$(head -n 3 "$S/P1W-newer.txt" | sed "s#^$T/# #" | tr -d '\n'); the three forecast files' times and inodes $([ "$fcs0" = "$fcs1" ] && echo unchanged || echo changed); the print $nf lines, its last: $(tail -n 1 "$OA/forecasts-e224a-check.txt" 2>/dev/null | cut -c1-90)"
step "P1X: a stand-in preflight that rewrites two registered files with their own bytes: step 2 refuses naming wrote-in-lab and both files"
cat > "$T/$E/preflight_e224a.sh" <<'EOF'
#!/usr/bin/env bash
# the runbook desk test's case P1X only (never committed): a stand-in for preflight_e224a.sh that rewrites two registered files with their own bytes
# (the form of a registration check run in its writing form), then prints the preflight's GO line
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
for f in tools/claims-v3/e224/forecast-e224.csv tools/claims-v3/e224/forecast-e224.json; do
  /usr/bin/python3 -I -B - "$R/$f" <<'PY'
import sys
b = open(sys.argv[1], "rb").read()
open(sys.argv[1], "wb").write(b)
PY
done
echo "dmcmd_audit: GO (stand-in: two registered files rewritten with their own bytes)"
EOF
r=$(run "$OA" P1X s03_desk_e224a.sh A)
fcx=bytes-same
for f in "$E/forecast-e224.csv" "$MMF"; do $G show "HEAD:$f" > "$S/P1X-committed.bin"; cmp -s "$T/$f" "$S/P1X-committed.bin" || fcx=bytes-changed; done
$G checkout -q -- "$E/preflight_e224a.sh" "$E/forecast-e224.csv" "$MMF"
ok "$r $(has "wrote-in-lab(rc 0; 2 file(s):" "$S/P1X.txt")$(has "wrote-in-lab(rc 0; 2 file(s):.*forecast-e224.csv" "$S/P1X.txt")$(has "wrote-in-lab(rc 0; 2 file(s):.*forecast-e224.json" "$S/P1X.txt") $fcx $($G status --porcelain --untracked-files=all | grep -c .)" "16 111 bytes-same 0" \
   "$(grep -ao 'wrote-in-lab([^;]*;[^:]*:[^)]*)' "$S/P1X.txt" | head -n 1); the two files $fcx; the scratch restored from its HEAD: $($G status --porcelain --untracked-files=all | grep -c .) path(s) changed"
step "P2: in one step-2 run: the registration's list one line short, the kit's list one line short, a desk test's log without its PASS line"
cp "$T/$E/SHA256SUMS-e224-registration" "$S/reg.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e224-registration"
cp "$T/$E/SHA256SUMS-e224-kit" "$S/kit.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e224-kit"
cp "$T/$E/logs/realbytes-e224a.txt" "$S/rbl.bak"; echo "REALBYTES-E224A 0 of 1 FAIL" > "$T/$E/logs/realbytes-e224a.txt"
r=$(run "$OA" P2 s03_desk_e224a.sh A)
cp "$S/reg.bak" "$T/$E/SHA256SUMS-e224-registration"; cp "$S/kit.bak" "$T/$E/SHA256SUMS-e224-kit"; cp "$S/rbl.bak" "$T/$E/logs/realbytes-e224a.txt"
nreg2=$(( $(grep -c . "$S/reg.bak") - 1 )); nkit2=$(( $(grep -c . "$S/kit.bak") - 1 ))
ok "$r $(has "SHA256SUMS-e224-registration($nreg2 OK of $nreg2" "$S/P2.txt") $(has "SHA256SUMS-e224-kit($((nkit2 - 1)) OK of $nkit2; pinned $KITN" "$S/P2.txt") $(has ' realbytes-e224a' "$S/P2.txt")" "16 1 1 1" "$(stopline "$S/P2.txt" | cut -c1-220)"
step "H1: a committed edit of a registration file; H2: a committed shadowing addition (tools/claims-v3/e224/json.py)"
echo "an edit" >> "$T/$E/E224.md"; $G commit -q -am "desk test: an edit of E224.md"
r=$(run "$OA" H1 s03_desk_e224a.sh A); $G reset -q --hard "$KIT"
echo "# a shadow" > "$T/$E/json.py"; $G add "$E/json.py"; $G commit -q -m "desk test: a shadow"
r2=$(run "$OA" H2 s03_desk_e224a.sh A); /usr/bin/python3 -I -B "$T/$E/rb/check_history_e224a.py" tree > "$S/H2b.txt" 2>&1; $G reset -q --hard "$KIT"
ok "$r $(has 'history' "$S/H1.txt") $r2 $(has 'json.py' "$S/H2b.txt")" "16 1 16 1" "$(stopline "$S/H1.txt" | cut -c1-150); $(head -c 150 "$S/H2b.txt")"
step "DA: arm A's data committed: step 2 refuses; GS: a gate stop's record and a stand-in FILE named *e224a* under docs/reports/data: reported, no datum, 0"
DD="docs/reports/data/$TODAY-e224-blind-matmul-aifoundry1-c1"
mkdir -p "$T/$DD"; echo "stand-in" > "$T/$DD/README.md"
$G add --sparse -f "$DD/README.md"; $G commit -q -m "desk test: E224 arm A data (stand-in)"
r=$(run "$OA" DA s03_desk_e224a.sh A); $G reset -q --hard "$KIT"
mkdir -p "$T/docs/reports/gate-stops/$TODAY-e224-blind-matmul-T1-aifoundry1-c1"; echo "stand-in" > "$T/docs/reports/gate-stops/$TODAY-e224-blind-matmul-T1-aifoundry1-c1/README.md"
$G add --sparse -f "docs/reports/gate-stops/$TODAY-e224-blind-matmul-T1-aifoundry1-c1/README.md"; $G commit -q -m "desk test: an E224 gate stop's record (stand-in)"
F175="docs/reports/data/2026-11-05-q143g-e175-design/candidates/tiles/fp16/fp16.e5c92_ar_k_t7_0e224af.bin"
mkdir -p "$T/$(dirname "$F175")"; echo "stand-in tile" > "$T/$F175"; $G add --sparse -f "$F175"; $G commit -q -m "desk test: a file named *e224a* (E175's tile-name form)"
rg=$(run "$OA" GS s03_desk_e224a.sh A); $G reset -q --hard "$KIT"
ok "$r $(has 'E224-has-data(1 commit(s))' "$S/DA.txt") $rg $(has 'E224 gate-stop commits: 1' "$S/GS.txt")" "16 1 0 1" \
   "arm A's data: $(stopline "$S/DA.txt" | cut -c1-120); a gate stop and a file named *e224a*: rc $rg, $(grep -o 'E224 gate-stop commits: [0-9]*; sealed-forecast note commits: [0-9]*' "$S/GS.txt" | head -n 1)"
step "S0: THE STEP-0 CHECKS on the scratch repository (a stand-in GitHub main: its HEAD unless named)"
SR=$S/sealed; mkdir -p "$SR"
s0() { RB_DESKTEST=1 E224A_S0_LAB="$T" E224A_S0_MAIN="${2:-$($G rev-parse HEAD)}" E224A_SEALED="$1" bash "$T/$E/rb/s00_step0_e224a.sh" A > "$S/S0-$3.txt" 2>&1; echo $?; }
a=$(s0 "$SR/none.txt" "" a)
SHA=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
mkdir -p "$T/tools/claims-v3/sealed-e224"; printf '# E224 freeze lines (desk-test stand-in)\nsha256 %s\n' "$SHA" > "$T/tools/claims-v3/sealed-e224/e224-freeze-lines.md"
$G add tools/claims-v3/sealed-e224; $G commit -q -m "desk test: a sealed-forecast note (stand-in)"
printf '# record\nE224 %s #99 2026-11-19 22:00:00 PST -- stand-in\n' "$SHA" > "$SR/one.txt"
b=$(s0 "$SR/one.txt" "" b)
printf '# record\nE224 %s #99 2026-11-19 22:00:00 PST -- stand-in\nE224 %s #98 2026-11-19 22:01:00 PST -- not registered\n' "$SHA" "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210" > "$SR/two.txt"
c=$(s0 "$SR/two.txt" "" c)
$G reset -q --hard "$KIT"
d=$(s0 "$SR/none.txt" "$($G rev-parse "$REGC^")" d)
e=$(s0 "$SR/none.txt" "$($G rev-parse "$FZ^")" e)
mkdir -p "$T/$DD"; echo "stand-in" > "$T/$DD/README.md"; $G add --sparse -f "$DD/README.md"; $G commit -q -m "desk test: E224 arm A data (stand-in)"
f=$(s0 "$SR/none.txt" "" f); $G reset -q --hard "$KIT"
echo "an untracked file" > "$T/$E/untracked-s0.txt"; g=$(s0 "$SR/none.txt" "" g); rm -f "$T/$E/untracked-s0.txt"
ok "$a $(has 'sealed 0 of 0' "$S/S0-a.txt") $(has 'STEP0-E224 arm A: 6 of 6 as stated' "$S/S0-a.txt") $b $(has 'sealed 1 of 1' "$S/S0-b.txt") $c $(has 'S1 NOT AS STATED: sealed 1 of 2' "$S/S0-c.txt") $d $(has '^F1 as stated' "$S/S0-d.txt")$(has '^F1R NOT AS STATED' "$S/S0-d.txt")$(has '^F2 NOT AS STATED' "$S/S0-d.txt") $e $(has '^F1 NOT AS STATED' "$S/S0-e.txt") $f $(has '^D0 NOT AS STATED' "$S/S0-f.txt") $g $(has "^G1 NOT AS STATED: the lab clone's status: 1 line" "$S/S0-g.txt")" \
   "0 1 1 0 1 1 1 1 111 1 1 1 1 1 1" "no record: $(tail -n 1 "$S/S0-a.txt" | cut -c1-70); a registered seal: $(grep -m1 '^S1' "$S/S0-b.txt" | cut -c1-60); an unregistered one: $(grep -m1 '^S1' "$S/S0-c.txt" | cut -c1-80); main at the registration's parent: $(grep -m1 '^F1R' "$S/S0-d.txt" | cut -c1-80); main before MM1-v3.2's land: $(grep -m1 '^F1 ' "$S/S0-e.txt" | cut -c1-80)"
step "O: the look on the stand-in aifoundry1 booted before E82's firmware read (k6's s05)"
r3=$(RB_OUT=$OA bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry1 > "$S/O3.txt" 2>&1; echo $?)
ok "$r3 $( [ -s "$OA/box-login-aifoundry1.txt" ] && echo login)" "0 login" "aifoundry1: $(grep -m1 'FREE\|HELD' "$S/O3.txt" | cut -c1-70)"
step "OB: the stand-in aifoundry1 BOOTED AFTER E82'S FIRMWARE READ (2026-11-17 16:46:32 PST, aifoundry1's boot now): k6's look stops at its identity by continuity (16); arm A's step 4 is the A2 form's"
echo "2026-11-17 16:46:32" > "$S/boot-aifoundry1"
O6B=$S/outOB; mkdir -p "$O6B"
r=$(RB_OUT=$O6B bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry1 > "$S/OB.txt" 2>&1; echo $?)
rm -f "$S/boot-aifoundry1"
ok "$r $(has "aifoundry1 booted after E82's firmware read: STOP" "$S/OB.txt")" "16 1" "$(stopline "$S/OB.txt" | cut -c1-160)"
step "OL: E224's ours_live counts a session_e224a.sh by its own script, never by a command string"
mkdir -p "$S/ol"; printf '#!/bin/bash\nsleep 25\n' > "$S/ol/session_e224a.sh"
( . "$T/$E/rb/rb_e224a.sh" > /dev/null 2>&1; e224a_live_text ) > "$S/ol/live.sh"
printf '. "%s"\necho "$(ours_live session_e224a.sh) $(ours_live)"\n' "$S/ol/live.sh" > "$S/ol/count.sh"
printf '#!/bin/bash\nsleep 25\n: tools/claims-v3/e224/session_e224a.sh\n' > "$S/ol/decoy.sh"
n0=$(bash "$S/ol/count.sh")
setsid bash "$S/ol/decoy.sh" session_e224a.sh < /dev/null > /dev/null 2>&1 &
p1=$!
n1=$(sleep 1; bash "$S/ol/count.sh")
setsid bash "$S/ol/session_e224a.sh" < /dev/null > /dev/null 2>&1 &
p2=$!
n2=$(sleep 1; bash "$S/ol/count.sh")
kill "$p1" "$p2" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do [ "$(bash "$S/ol/count.sh")" = "0 0" ] && break; sleep 0.5; done
n3=$(bash "$S/ol/count.sh")
ok "$n0|$n1|$n2|$n3" "0 0|0 0|1 1|0 0" "before: $n0; a script whose arguments and text name session_e224a.sh: $n1; a session_e224a.sh run as a script: $n2; after it ended: $n3"
step "SY: step 5 on aifoundry1"
ra=$(run "$OA" SYA s07_sync_e224a.sh A)
ok "$ra $(has 'HARNESS OK on the box' "$S/SYA.txt")" "0 1" "$(grep -m1 'synced to' "$S/SYA.txt" | cut -c1-120)"
step "L1: a login link on a read (step 5's first read); L2: a read that hangs (the read class's bound 3 s for this call)"
touch "$S/ssh-login"; n0=$(grep -c . "$RB_LOCK" 2>/dev/null || echo 0)
r=$(run "$OA" L1 s07_sync_e224a.sh A); n1=$(grep -c 'aifoundry1 needs a check' "$RB_LOCK" 2>/dev/null || echo 0)
touch "$S/ssh-hang"
r2=$(RB_READ_S=3 RB_OUT=$OA RB_DESKTEST=1 bash "$T/$E/rb/s07_sync_e224a.sh" A > "$S/L2.txt" 2>&1; echo $?); rm -f "$S/ssh-hang"
ok "$r $((n1 - n0)) $r2" "11 1 13" "$(stopline "$S/L1.txt" | cut -c1-120); $(stopline "$S/L2.txt" | cut -c1-100)"
step "T: NO-THIRD-BUILD on aifoundry1"
mkdir -p "$A3/build"; for k in 1 2; do echo "$TODAY 01:0$k:00 PST a1-build-e224a started" >> "$A3/build/e224a-build-attempts.txt"; done
r=$(run "$OA" T s08_build_e224a.sh A start); rm -f "$A3/build/e224a-build-attempts.txt"
ok "$r $(has NO-THIRD-BUILD "$S/T.txt")" "16 1" "$(stopline "$S/T.txt" | cut -c1-140)"
step "BB: step 6 on aifoundry1: the REAL build stops at THE ET_DEVICES GATE (this desk's device layer carries no ET_DEVICES)"
r=$(run "$OA" BA1 s08_build_e224a.sh A start); r2=$(waitjob "$OA" BA2 s08_build_e224a.sh A wait)
ok "$r $r2 $(has 'RGM-BUILD-FAILED: ET_DEVICES: a host has no ET_DEVICES' "$S/BA2.txt") $(grep -c 'KERNEL OK: ' "$S/BA2.txt" | sed 's/^[1-9][0-9]*$/gated/') $( [ -e "$OA/e224a-built-A.txt" ] && echo built || echo none)" "0 16 1 gated none" \
   "$(stopline "$S/BA2.txt" | cut -c1-160)"
# the later cases run on a STAND-IN BUILT record beside the real ELFs and hosts the refused build left (aifoundry1's own build reads the
# ET_DEVICES reading: E215 arm B's), the job's verdict line, and RB_OUT/e224a-built-A.txt as step 6's wait writes it
JBN=a1-build-e224a       # rb_e224a.sh's e224a_jobs: J=a1 (arm A's jobs word), JOB_BUILD=$J-build-e224a
/usr/bin/python3 -I -B - "$A3" "$TODAY" <<'PY'
import hashlib, json, os, sys, time
a3, day = sys.argv[1], sys.argv[2]
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
ks = {}
for k in ("rgm136", "rgm211"):
    ks[k] = {"kernel_sha256": sha(os.path.join(a3, f"build/e224argm/{k}/kernel/sparsity.elf")), "host_sha256": sha(os.path.join(a3, f"build/e224argm/{k}/host/sparsity_host")),
             "kernel_gate": "KERNEL OK: (the real build's gate, case BB)"}
rec = {"box": "aifoundry1", "arm": "A", "day": day, "epoch": int(time.time()), "verdict": "BUILT", "builder": "build_e224a.sh", "kernels": ks,
       "host_checks": ["stand-in"], "et_devices": "the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES",
       "what": "the runbook desk test's stand-in record after case BB (the real ELFs and hosts; aifoundry1's own build reads the ET_DEVICES reading)"}
json.dump(rec, open(os.path.join(a3, "build/e224argm/BUILD-e224a.json"), "w"), indent=1)
PY
[ -n "$JBN" ] && echo "RGM-BUILT rc=0 (the runbook desk test's stand-in verdict after case BB)" >> "$A3/build/q141k/jobs/$JBN.out"
echo rgm > "$OA/e224a-built-A.txt"
step "NR: step 6n, the never-run search repeated (the registration's scanner over the scratch repository and a stand-in lanes folder)"
mkdir -p "$NRO/card-a1c1-desktest/runs/1" "$NRO/card-a1c1-desktest/runs/2" "$NRO/card-e224a/runs/1" "$NRO/kit-e224ax/work"
rec gemmLnc3x6x12 fp32 fp32/randn.bin 0xffffffff > "$NRO/card-a1c1-desktest/runs/1/proc-00.out"   # g01's token (L-AF4; g01t reads it too) on aifoundry1 card 1
touch -d '2026-11-19 19:00:00 PST' "$NRO/card-a1c1-desktest/runs/1/proc-00.out"
rec gemmL1x7x8 fp32 fp32/randn.bin 0x6000 > "$NRO/card-a1c1-desktest/runs/2/proc-00.out"               # the posimb pair y1a/y1b's token (read by token), dated now
rec gemmL4x2x3 fp32 fp32/randn.bin 0xffffffff > "$NRO/card-e224a/runs/1/proc-00.out"               # e01's token in E224's own card lane: never opened
rec gemmL3x2x4 fp32 fp32/randn.bin 0xffffffff > "$NRO/kit-e224ax/work/proc.out"                    # e02's token in a desk lane: not read
ra=$(run "$OA" NRA s06n_neverrun_e224a.sh A)
nrda=$(cat "$OA/e224a-neverrun-dir-A.txt" 2>/dev/null)
la=$(/usr/bin/python3 -I -B -c "import json, sys; print(json.load(open(sys.argv[1]))['ran_before_points']['A'])" "$nrda/labels-e224-A.json" 2>/dev/null)
ck=$( (cd "$T" && /usr/bin/python3 -I -B $E/desk/neverrun_card_e224.py check-labels "$nrda/labels-e224-A.json" --arm A) 2>&1 | tail -n 1 | cut -d: -f1)
ev=$(/usr/bin/python3 -I -B -c "import json, sys; e = json.load(open(sys.argv[1]))['evidence']; print(''.join('1' if 'card-a1c1-desktest' in json.dumps(e.get(k)) else '0' for k in ('g01', 'y1a')))" "$nrda/judge-e224-A.json" 2>/dev/null)
sub=$(grep -c 'card-e224a/runs\|kit-e224ax' "$nrda/judge-e224-A.json" 2>/dev/null)
ok "$ra $la $ck $ev $sub $( [ -s "$OA/e224a-neverrun-A.txt" ] && echo report)" "0 ['g01', 'g01t', 'y1a', 'y1b'] LABELS-OK 11 0 report" \
   "$(grep -m1 'NEVER-RUN-E224 arm A' "$S/NRA.txt" | cut -c1-260)"
step "R7: STEP 7 needs a fresh never-run report and the rest (ours, and the model session's ~/claude/work/ee-*/); R7f: a threshold of 70 C read: refused"
O5=$S/out5; mkdir -p "$O5"; cp "$OA/window.env" "$O5/"; touch "$O5/window.env"
c0=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
ra=$(run "$O5" R7a s09_reads_e224a.sh A)
cp "$OA/e224a-neverrun-A.txt" "$O5/"; touch -d '-31 min' "$O5/e224a-neverrun-A.txt"
rb_=$(run "$O5" R7b s09_reads_e224a.sh A)
mkdir -p "$A3/build/e185/T1"
{ echo "$(date -d '-14 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-10 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-10 min' "$A3/build/e185/T1/session.log"
rc_=$(run "$OA" R7c s09_reads_e224a.sh A)
{ echo "$(date -d '-50 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-45 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-45 min' "$A3/build/e185/T1/session.log"
EEW=$B/aifoundry1/claude/work/ee-desktest; mkdir -p "$EEW"; echo "a model-session sweep's file (desk-test stand-in)" > "$EEW/sweep.log"; touch -d '-10 min' "$EEW/sweep.log" "$EEW"
re7=$(run "$OA" R7e s09_reads_e224a.sh A); touch -d '-45 min' "$EEW/sweep.log" "$EEW"
c1=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
{ echo "$(date -d '-50 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-45 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-45 min' "$A3/build/e185/T1/session.log"
rd=$(run "$OA" R7d s09_reads_e224a.sh A); c2=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
echo thr70 > "$S/reader-mode-A"
rf=$(run "$OA" R7f s09_reads_e224a.sh A); c3=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
rm -f "$S/reader-mode-A"
ok "$ra $(has 'no never-run report' "$S/R7a.txt") $rb_ $(has 'minutes old (more than 30)' "$S/R7b.txt") $rc_ $(has 'the rest has not run' "$S/R7c.txt") $re7 $(has 'the rest has not run' "$S/R7e.txt") $((c1 - c0)) $rd $((c2 - c1)) $(has 'aifoundry1 card 1: config TDP 65 W / 65 C / 600 MHz, minion_mv 499; identity /dev/et1_mgmt, physical device ID 1' "$S/R7d.txt") $rf $((c3 - c2)) $(has "aifoundry1 card 1's config is not TDP 65 W / 65 C / 600 MHz" "$S/R7f.txt")" \
   "10 1 10 1 10 1 10 1 0 0 1 1 16 1 1" "no report: $(stopline "$S/R7a.txt" | cut -c1-80); 31 min: $(stopline "$S/R7b.txt" | cut -c1-80); 10 min after a session: $(stopline "$S/R7c.txt" | cut -c1-80); a write under ee-* 10 min ago: $(stopline "$S/R7e.txt" | cut -c1-80) (reader calls $((c1 - c0))); a 70 C threshold: $(stopline "$S/R7f.txt" | cut -c1-100)"
step "D: step 8 on aifoundry1 (the dry pass and THE SCRUB CHECK); DS: the scrub check refusing another home's path"
ra=$(run "$OA" DA1 s10_dry_e224a.sh A start); ra2=$(waitjob "$OA" DA2 s10_dry_e224a.sh A wait)
dda=$(ls -d "$A3"/build/e224a/T*-A-dry 2>/dev/null | tail -n 1)
mkdir -p "$dda/zz"; echo '{"path": "/home/someoneelse/work/x"}' > "$dda/zz/other-home.json"
rs=$(waitjob "$OA" DS s10_dry_e224a.sh A wait); rm -rf "${dda:?}/zz"
ok "$ra $ra2 $(has 'SCRUB-CHECK CLEAN: ' "$S/DA2.txt") $(has 'E224-DRY arm A rc=0 runs=3' "$S/DA2.txt") $rs $(has 'SCRUB-CHECK LEFT' "$S/DS.txt")" "0 0 1 1 16 1" \
   "$(grep -m1 'E224-DRY' "$S/DA2.txt" | cut -c1-80); $(grep -m1 'SCRUB-CHECK' "$S/DA2.txt" | cut -c1-90); another home: $(stopline "$S/DS.txt" | cut -c1-80)"
[ "$ra2" = 0 ] || tail -n 25 "$S/DA2.txt"
step "HG: a HUNG marker in a session log of ours on aifoundry1: step 9 refuses"
mkdir -p "$A3/build/e204/T1794800000"
printf '%s session start (T0 1794800000; desk test)\n%s HUNG: a device process did not end after its timeout TERM (desk test)\n%s session end (T0 1794800000)\n' \
  "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" > "$A3/build/e204/T1794800000/session.log"
touch -d '-3 hours' "$A3/build/e204/T1794800000/session.log"
r=$(run "$OA" HG s11_session_e224a.sh A); rm -rf "${A3:?}/build/e204"
ok "$r $(has 'REFUSED: a HUNG marker of ours on the box' "$S/HG.txt") $(ls "$A3/build/e224a" 2>/dev/null | grep -c '^T[0-9]*-A$')" "10 1 0" "$(grep -m1 'REFUSED' "$S/HG.txt" | cut -c1-140)"
step "SD: the same-day rule: an E224 arm A session that opened the card earlier today"
mkdir -p "$A3/build/e224a/T1700000000-A"
printf '%s session start (T0 1700000000; desk test)\n%s the first card command: the start config read through the guard\n%s session end (T0 1700000000)\n' \
  "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-45 min' '+%F %T %Z')" > "$A3/build/e224a/T1700000000-A/session.log"
if [ "$(TZ=America/Los_Angeles date -d '-45 min' +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then touch -d '-45 min' "$A3/build/e224a/T1700000000-A/session.log"
else TZ=America/Los_Angeles touch -d "$(TZ=America/Los_Angeles date +%F) 00:00:01" "$A3/build/e224a/T1700000000-A/session.log"; fi
r=$(run "$OA" SD s11_session_e224a.sh A); rm -rf "${A3:?}/build/e224a/T1700000000-A"
ok "$r $(has 'REFUSED: the same-day rule' "$S/SD.txt")" "10 1" "$(grep -m1 'REFUSED' "$S/SD.txt" | cut -c1-140)"
step "LS: THE LAST START passed (the window's last end still far): step 9 refuses (16) before anything is sent"
O6=$S/out6; mkdir -p "$O6"; cp "$OA/window.env" "$OA/e224a-built-A.txt" "$O6/"
sedi -e "s/^RB_LAST_START_EPOCH=.*/RB_LAST_START_EPOCH=$(( $(date +%s) - 60 ))/" "$O6/window.env"; touch "$O6/window.env" "$O6/e224a-built-A.txt"
n0=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
r=$(run "$O6" LS s11_session_e224a.sh A); n1=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
ok "$r $(has "past the round's last start" "$S/LS.txt") $((n1 - n0))" "16 1 0" "$(stopline "$S/LS.txt" | cut -c1-140); box calls $((n1 - n0))"
step "NS: no never-run report from today in RB_OUT: step 9 refuses (10) before anything is sent"
O7=$S/out7; mkdir -p "$O7"; cp "$OA/window.env" "$OA/e224a-built-A.txt" "$O7/"; touch "$O7/window.env" "$O7/e224a-built-A.txt"
n0=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
r=$(run "$O7" NS s11_session_e224a.sh A); n1=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
ok "$r $(has 'no never-run report from today' "$S/NS.txt") $((n1 - n0))" "10 1 0" "$(stopline "$S/NS.txt" | cut -c1-140); box calls $((n1 - n0))"
step "LA: step 9 launches the REAL session_e224a.sh, which stops at its box check (the desk's own hostname); step 10 reads the gate"
r=$(run "$OA" LA s11_session_e224a.sh A); r2=$(waitjob "$OA" LA2 s20_wait_e224a.sh A)
t0=$(cat "$OA/e224a-T0-A.txt" 2>/dev/null)
sd=$A3/build/e224a/T$t0-A
procs=$(find "$sd" -name 'proc*.out' 2>/dev/null | wc -l | tr -d ' ')
ok "$r $r2 $(has 'refused, no device opened: the box or the build is not the registered one (this host is' "$sd/session.log") $(has '"rc": 16' "$sd/queue.json") $( [ -s "$sd/MANIFEST.sha256" ] && echo manifest) $procs $(has 'GATE-STOPPED e224a arm A' "$S/LA2.txt")" \
   "0 16 1 1 manifest 0 1" "$(grep -m1 'no device opened' "$sd/session.log" | cut -c1-200)"
step "W10: step 10's readings on stand-in logs (a running session, none, HUNG, K1, CRASH, an ended session with a STOP line)"
O3=$S/out3; mkdir -p "$O3"; cp "$OA/window.env" "$OA/box-login-aifoundry1.txt" "$O3/"; touch "$O3/window.env"; echo 7 > "$O3/e224a-T0-A.txt"
mkdir -p "$A3/build/q141k"; echo 7 > "$A3/build/q141k/e224aA.T0"; W7=$A3/build/e224a/T7-A; mkdir -p "$W7"
mkdir -p "$S/wv"; printf '#!/bin/bash\nsleep 30\n' > "$S/wv/session_e224a.sh"
wr() { RB_OUT=$O3 RB_DESKTEST=1 RB_WAIT_LOOP_S=4 bash "$T/$E/rb/s20_wait_e224a.sh" A > "$S/W10-$1.txt" 2>&1; echo $?; }
echo "$(date '+%F %T %Z') session start (T0 7; desk-test stand-in, no end)" > "$W7/session.log"
setsid bash "$S/wv/session_e224a.sh" < /dev/null > /dev/null 2>&1 &
p3=$!
sleep 1
rv=$(wr V)
kill "$p3" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$p3" 2>/dev/null || break; sleep 0.5; done
rg=$(wr G)
printf '%s session start (T0 7; desk test)\n%s HUNG: a device process (the host of 002-pass1-d25 (proc-00); its `timeout` pid 9) still runs\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"
rh=$(wr H)
printf '%s session start (T0 7; desk test)\n%s STOP: K1: a launch of run 002-pass1-d25 did not finish (the host'"'"'s words): it may leave a hung hart: nothing further started\n%s session end (T0 7)\n' \
  "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo "x  session.log" > "$W7/MANIFEST.sha256"; echo 0 > "$W7/runner.rc"
rk=$(wr K)
printf '%s session start (T0 7; desk test)\n%s CRASH: KeyError: y99\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 1 > "$W7/runner.rc"
rc_=$(wr C)
printf '%s session start (T0 7; desk test)\n%s STOP: board 71.2 W above 70 W on 3 samples in a row: nothing further started\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 0 > "$W7/runner.rc"
re=$(wr E)
rm -rf "${A3:?}/build/e224a/T7-A"; echo "$t0" > "$A3/build/q141k/e224aA.T0"
ok "$rv $rg $rh $rk $rc_ $re $(has 'RUN-RUNNING' "$S/W10-V.txt")$(has 'RUN-GONE' "$S/W10-G.txt")$(has 'KILL NOTHING' "$S/W10-H.txt")$(has 'K1' "$S/W10-K.txt")$(has 'crashed' "$S/W10-C.txt")$(has 'read its STOP line' "$S/W10-E.txt")" \
   "17 14 16 16 16 0 111111" "running $rv, gone $rg, HUNG $rh, K1 $rk, CRASH $rc_, ended with a STOP line $re"
step "C: step 11 on LA's session, step 12 (the gate stop's record), step 13 refuses it; C2: a byte changed after the manifest"
r=$(run "$OA" C1 s22_collect_e224a.sh A); r2=$(run "$OA" C2s s23_data_e224a.sh A); r3=$(run "$OA" C3s s24_score_e224a.sh A)
gs=$(cat "$OA/e224a-data-dir-A.txt" 2>/dev/null)
ok "$r $r2 $(has 'COLLECTED-GATE-STOP docs/reports/gate-stops/' "$S/C2s.txt") $(grep -rl '/home/' "$T/$gs" 2>/dev/null | wc -l | tr -d ' ') $r3" "0 0 1 0 10" \
   "$(grep -m1 'COLLECTED' "$S/C2s.txt" | cut -c1-140); step 13: $(stopline "$S/C3s.txt" | cut -c1-100)"
[ -n "$gs" ] && rm -rf "${T:?}/${gs:?}"
O2=$S/out2; mkdir -p "$O2"; cp "$OA"/window.env "$OA"/e224a-T0-A.txt "$OA"/box-login-aifoundry1.txt "$O2/"; touch "$O2/window.env"
echo "x" >> "$sd/session.log"
r=$(RB_OUT=$O2 RB_DESKTEST=1 bash "$T/$E/rb/s22_collect_e224a.sh" A > "$S/C2.txt" 2>&1; echo $?)
ok "$r $(has 'COPY-BACK NOT EXACT' "$S/C2.txt")" "16 1" "$(stopline "$S/C2.txt" | cut -c1-140)"
step "CD: a session that ran (step 8's dry session copied as a session): steps 11, 12 and, after a stand-in data commit, 13 WITH step 6n's labels"
O=$S/out4
dd=$(ls -d "$A3"/build/e224a/T*-A-dry 2>/dev/null | tail -n 1)
mkdir -p "$O"; cp "$OA"/window.env "$OA"/box-login-aifoundry1.txt "$OA"/e224a-neverrun-dir-A.txt "$O/"; touch "$O/window.env"; echo 8 > "$O/e224a-T0-A.txt"
cp -a "$dd" "$A3/build/e224a/T8-A"; rm -f "${A3:?}/build/e224a/T8-A/dry.lock"
r=$(run "$O" CD1 s22_collect_e224a.sh A); r2=$(run "$O" CD2 s23_data_e224a.sh A)
dd2=$(cat "$O/e224a-data-dir-A.txt" 2>/dev/null)
$G add --sparse -f "$dd2" > /dev/null 2>&1; $G commit -q -m "desk test: a data commit (stand-in)" > /dev/null 2>&1
r3=$(run "$O" CD3 s24_score_e224a.sh A)
nh=$(grep -c . "$O/box-home-A.txt" 2>/dev/null)
lap=$(/usr/bin/python3 -I -B -c "import json, sys; m = json.load(open(sys.argv[1]))['arms']['A']['measured']; print(sorted(k for k, v in m.items() if v.get('ran_before')))" "$O/scores-e224-A.json" 2>/dev/null)
ok "$r $r2 $(has "COLLECTED docs/reports/data/$TODAY-e224-blind-matmul-aifoundry1-c1" "$S/CD2.txt") $( [ -s "$T/$dd2/data-e224a.json" ] && echo data) $(grep -c '  \(neverrun-e224-card\.\(txt\|json\)\|judge-e224-card\.\(txt\|json\)\|labels-e224\.json\)$' "$T/$dd2/SHA256SUMS" 2>/dev/null) $(has 'LABELS-OK' "$S/CD3.txt") $r3 $( [ -s "$O/scores-e224-A.json" ] && echo scored) $( [ "${nh:-0}" -ge 1 ] && echo homes)" \
   "0 0 1 data 5 1 0 scored homes" "$(grep -m1 'COLLECTED' "$S/CD2.txt" | cut -c1-130); $(grep -m1 'scored E224' "$S/CD3.txt" | cut -c1-80); labels applied: $(echo "$lap" | cut -c1-80)"
[ "$r3" = 0 ] || tail -n 20 "$S/CD3.txt"
$G reset -q --hard "$KIT"
step "Z: nothing of this test left running"
left=0
for p in /proc/[0-9]*; do
  c=$(readlink "$p/cwd" 2>/dev/null) || continue
  case "$c" in "$S"|"$S"/*) [ "${p#/proc/}" = "$$" ] || left=$((left + 1)) ;; esac
done
ok "$left" 0 "processes whose working directory is under the scratch directory (the stand-in box's jobs, sessions, builds)"
echo
echo "box calls the stand-ins served: $(grep -c . "$S/calls.log" 2>/dev/null || echo 0) (all to the stand-in box; no lab box was reached)"
echo "SELFTEST-RB-E224A $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
}
main
