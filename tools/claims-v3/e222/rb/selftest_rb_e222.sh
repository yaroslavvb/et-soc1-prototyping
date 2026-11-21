#!/usr/bin/env bash
# E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST that day): the desk test of E222's runbook with a FAKE ssh and rsync on a stand-in
# aifoundry3, E218's rb/selftest_rb_e218.sh (kit 5582edfc), itself E215 arm A's (8bde0182), for E222's one arm (arm B's cases, its aifoundry1
# box and its A2 form are not carried: E222 runs on aifoundry3 card 0 only). Its scratch repository is a shared, sparse clone of the lab clone this test runs from (its
# HEAD holds E222's registration as a commit, as on the card day) with the kit's files committed on top as one stand-in kit commit, the kit's
# list a stand-in made here and pinned in the scratch copy of step 2's KITPIN line (the one line this test changes in a copy), and stand-in
# desk-test logs (this test's own log is not final while it runs). The stand-in box is aifoundry3's ~/aifoundry, an rsync target under the
# scratch; the stand-in ssh serves it with `bash -s` (and `true`) and refuses any other host or command; the stand-in rsync rewrites its paths;
# the box's hostname, uptime (THE STAND-IN BOX BOOTED AFTER THE FIRMWARE READ: 2026-11-17 16:46:07, the real aifoundry3's boot as kit-e222's
# look read it at 15:05:22 PST Fri 20 Nov 2026, after E82's read of 31 Oct 2026; the lesson of E213 arm B's day), et-who, et-lab-manifest and
# pgrep are stand-ins, and the box tree holds a stand-in reader at build/ettelem/ettelem
# (the doubles' config and sampler, arm A) and E128's guard (k6's step 7 runs it there); cmake, the compilers and /opt/et are this desk's REAL
# ones (the build is the real build_e222.sh). Step 6n's scan reads the scratch repository at its HEAD as the lab and a stand-in folder as the
# round's lanes (E222_ROUND_OUT). No lab box is reached. When the lab clone's history holds the kit commit (the commit that added KIT.md: the
# readiness lane), the scratch repository is built at that commit's PARENT and the kit's files are taken from HEAD, its main following a local
# branch at that parent; otherwise (the kit lane) the untracked files and the lab clone's HEAD. Cases:
#   A   the dry listing: every step exits 0 (15 steps), no call reaches the stand-ins
#   K   step 2 with no window: 10       W1 a window written for another arm: 10      W2 a window written for another runbook: 10
#   W3  step 1 for another day: 10      W4 step 1 with an unknown arm (B): 10, naming E222's one arm      G  step 2 without RB_GITLOCK: 10
#   N   step 2 inside the lab-git lock (nested): 16 naming the pull
#   P1  step 2 on the scratch repository: 0 (the lists at their pins, HISTORY OK, the registration and the kit found by content, MM1-v3.2's
#       land and the three candidates' lands ancestors, the registration's four checks in their --check form, the scorer's two self-tests
#       written in RB_OUT and byte-identical, the sized timeout, the no-kill audit, the preflight GO, the desk tests' logs, nothing written)
#   P1W STEP 2 WROTE NOTHING in the scratch repository's work tree: no file outside .git newer than a marker made before P1, the registered
#       forecast files' (forecast-e222.json, .csv, .txt) times and inodes unchanged; the scorer's two self-tests' files, which step 2 put in
#       RB_OUT (scorer-check-A/), byte-identical to the committed selftest-standins.json and selftest-real.json
#   P1X STEP 2 SEES A REWRITE WITH THE SAME BYTES, which git status cannot: a stand-in preflight (in place of preflight_e222.sh, a kit file) that
#       rewrites two registered files with their own bytes - forecast-e222.csv under E222's folder and MM1-v3.2's mm1_v32_params.json, which the
#       forecasts read in place (the form of a registration check run in its writing form) - then prints the preflight's GO line: 16 naming
#       wrote-in-lab and both files (beside the changed kit file's own failures); the files' bytes unchanged; the files restored from HEAD
#   P2  in one step-2 run: the registration's list one line short, the kit's list one line short and a desk test's log without its PASS line
#       (that log is in the kit's list, so the kit's list reads one entry not OK too): 16, the failure list naming all three
#   H1  a committed edit of a registration file: 16 by the history check      H2 a committed tools/claims-v3/e222/json.py (a shadow): 16
#   DA  arm A's data committed (a docs/reports/data folder named <day>-e222-blind-matmul-aifoundry3): step 2 refuses (16, E222-has-data)
#   GS  in one step-2 run: an E222 gate stop's record committed (step 2 reports it) and a stand-in FILE whose name holds 'e222' committed under
#       docs/reports/data (E175's design tile-name form, ...0e222f.bin: no tile so named exists at HEAD; a file is not a datum): 0
#   S0  THE STEP-0 CHECKS (rb/s00_step0_e222.sh) on the scratch repository with a stand-in GitHub main and a stand-in record of the freeze post
#       (the round's form: FROZEN.txt and the three forecast files' sha256): (a) no sealed record: "sealed 0 of 0", 8 of 8 as stated; (b) a record
#       whose sealed sha256 the note at HEAD (tools/claims-v3/sealed-e222/e222-freeze-lines.md) registers: 1 of 1; (c) a record listing a sha256
#       the note does not register: S1 NOT AS STATED, exit 1; (d) GitHub main = the registration's parent: F1 and F1C as stated, F1R and F2 NOT AS
#       STATED, exit 1; (e) GitHub main before MM1-v3.2's land: F1 and F1C NOT AS STATED; (f) arm A's data committed: D0 NOT AS STATED; (g) an
#       untracked file in the lab clone: G1 NOT AS STATED; (h) a post record without FROZEN.txt's line: F0 NOT AS STATED; (i) a committed edit of
#       forecast-e222.txt: F0 NOT AS STATED (its sha256 at HEAD is not the posted one); (j) E222_FROZEN naming a file that is not FROZEN.txt: F0
#       NOT AS STATED
#   O   the look on the stand-in aifoundry3 (k6's s05, unchanged): FREE, our login recorded for the scrub
#   OB  THE STAND-IN aifoundry3 BOOTED AFTER THE FIRMWARE READ (its uptime -s 2026-11-17 16:46:07, the whole test's): the look reads FREE and
#       names no identity line (k6's identity-by-continuity rule is aifoundry1's alone; no E222 step gates on the boot)
#   OL  E222's ours_live: a shell whose command string names session_e222.sh is not a session; a session_e222.sh run as a script is
#   SY  step 5: the rsync, HARNESS OK on the box     L1 a login link on a read: 11, "<HH:MM:SS> aifoundry3 needs a check" appended to RB_LOCK,
#       nothing retried      L2 a read that hangs (the read class's bound 3 s for this call): 13
#   T   NO-THIRD-BUILD: two starts recorded on aifoundry3 today: a third start is refused with 16
#   BA  step 6: start, wait (17 while it builds, then 0): the REAL build of both trees, rgm136 KERNEL OK and rgm211's tree KERNEL OK, the record,
#       the harness, the preflight GO and both self-checks read on the box; RB_OUT/e222-built-A.txt
#   NR  STEP 6n, THE NEVER-RUN SEARCH REPEATED (the registration's scanner over the scratch repository and a stand-in lanes folder), dated note 1's
#       reading: a session record (runs/<n>/proc-00.out) of k01's token (gemmLnc2x6x12, family G3: the token) and one of q01a's token at its mask
#       (gemmL1x8x8 at 0xa0000000, family Y3: token and masks) in a card-a3 lane folder: k01, q01a and q01b (q01a's token) labelled 'ran before';
#       wn01's token (gemmLnc1x6x48) in a folder naming no card (data-desktest/work/): NOT labelled (desk copies never count; the literal reading
#       REPORTED reads it run); E222's own card lane folder (card-e222, b01's token there) never opened; a desk lane (kit-e222x, b02's token) not
#       read; FAMILY R printed "RAN (exempt by family name: same-card repeats, REPORTED only)" and THE POSITIVE CONTROL 4 of 4 RAN (E218's data
#       folder in the scratch); the labels in the scorer's form, LABELS-OK
#   NRP THE POSITIVE CONTROL FAILING: the scratch's sparse checkout without E218's data folder (the scan cannot see this card's own session):
#       step 6n stops with 16 ("POSITIVE CONTROL FAILED"), no report for step 7; the checkout restored
#   R7  STEP 7 ONLY WITH A FRESH NEVER-RUN REPORT AND ONLY ONCE THE REST HAS OPENED: no report: 10; a report 31 minutes old: 10; a session of ours
#       ended 10 minutes ago: 10; in none of the three is the stand-in reader called; then 0, the reader called once (k6's read: TDP 0 W / 65 C /
#       600 MHz); R7f the card's threshold reading 70 C (the doubles' thr70): 16, the config not as registered
#   D   step 8 (the doubles on the box): 0, and THE SCRUB CHECK on the dry pass's copy reads CLEAN (the box's home masked)
#   DS  THE SCRUB CHECK REFUSES BEFORE THE SESSION: a file with another home's path (/home/<someone else>/...) in the dry pass's folder: the wait
#       reads 16 (SCRUB-CHECK LEFT), no session that day
#   HG  THE HUNG MARKER: a session log of ours on aifoundry3 with a HUNG line: step 9 refuses (10), nothing launched
#   SD  THE SAME-DAY RULE: an E222 arm A session that opened the card earlier today: step 9 refuses (10)
#   LS  THE LAST START passed with the last end still far: step 9 refuses (16) and sends nothing to the box
#   NS  no never-run report from today in RB_OUT (step 6n): step 9 refuses (10) and sends nothing to the box
#   LA  step 9 launches the REAL session_e222.sh and run_e222.py on the stand-in aifoundry3, which stop at their box check before any device (the
#       desk's own hostname): "refused, no device opened"; step 10 reads GATE-STOPPED (16) with the manifest written
#   W10 step 10's readings on stand-in logs: a running session_e222.sh with no end 17 (RUN-RUNNING); none running 14 (RUN-GONE); a HUNG line 16
#       (HUNG); a K1 stop 16 (K1-STOPPED); a CRASH line 16 (CRASHED); an ended session (rc 0) with a STOP line 0
#   C   step 11 on LA's session: COPY-BACK EXACT 0; step 12: the gate stop's record under docs/reports/gate-stops/ (COLLECTED-GATE-STOP), the
#       desk-path gate, HISTORY OK: 0; step 13 refuses a gate stop's record: 10      C2 one byte of a box file changed after the manifest:
#       COPY-BACK NOT EXACT 16
#   CD  a session that ran (step 8's dry session copied as a session): step 11 0 (the box's home in every form read), step 12 the data directory
#       (docs/reports/data/<today>-e222-blind-matmul-aifoundry3) with data-e222.json (the reducer), step 6n's report, judgement and labels (in
#       SHA256SUMS) and the scrub clean: 0; after a stand-in data commit, step 13 runs the FROZEN scorer on it in its registered form (--a <data>
#       --a-tag A --out <dir>) WITH step 6n's labels (LABELS-OK first): 0, scores-e222-A.json and .txt with R0 and SEL, CX PENDING E220 DATA
#   Z   no process of this test left running
#   bash tools/claims-v3/e222/rb/selftest_rb_e222.sh <scratch dir> > logs/selftest-rb-e222.txt   (prints SELFTEST-RB-E222 <n> of <m> PASS or FAIL)
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
# PID namespace (bubblewrap), where it sees only its own processes; E222_RB_PIDNS=1 marks that inner run.
if [ -z "${E222_RB_PIDNS:-}" ]; then
  command -v bwrap > /dev/null || { echo "no bwrap: the runbook test runs in a private PID namespace"; exit 2; }
  echo "(the runbook test: re-run in a private PID namespace, so that no other lane's process on this desk is read as a session of ours)"
  exec /usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- env E222_RB_PIDNS=1 bash "$SRC/tools/claims-v3/e222/rb/selftest_rb_e222.sh" "$@"
fi
for c in timeout sha256sum flock cmake c++ rsync git; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
REAL_RSYNC=$(command -v rsync)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree box bin boxbin out; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; B=$S/box; BIN=$S/bin; BB=$S/boxbin
A3=$B/aifoundry3/aifoundry
E=tools/claims-v3/e222
FZ=4e386f7519a236fb0bf8c43d26f8303be57e09a2       # MM1-v3.2's land (the baseline the forecasts read in place; step 0's F1)
MMF=tools/matmul/mm1/v3.2/out/mm1_v32_params.json  # MM1-v3.2's constants, read in place by the forecasts' check (P1X's second file)
POSTS_LINE="#1.30.1.2.1.1.1 2026-11-20 13:51:12 PST: reg-e222 (desk-test stand-in of the round's record) FROZEN 13:50:25 PST: FROZEN.txt 172ed079a4a5640a381c984dd7adc1bb1a63cbb024373c0a1f8f9c0c40d9369f; forecast-e222.json c4630d19554ab0daacd9eacd83f74fb1d8bd0df851bcbd1cfc02d3ac715314a8; forecast-e222.csv 223f943e32c01544063de6b1dc925712e0701ba43f4c99f97ff622e8c5b835cb; forecast-e222.txt f2d8047f1e1136924939250da1207cecd4a48a047a07ec678ce30417913ec910"
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
G="git -C $T -c user.name=e222-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
SPARSE="/tools/ /docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/ /docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/ \
  /docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/ /docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/ \
  /docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/ /docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/ /workloads/nocbench/analyze.py"
$G sparse-checkout set --no-cone $SPARSE || return 2     # the data folders step 2's checks read (the forecasts' and rules' checks through MM1-v3.2,
# the scorer's real-bytes self-test and the timeout sizing: E218's, E215 arm A's and E213 arm A's on aifoundry3), step 6n's positive control reads
# (E218's) and the mesh map MM1-v3.2's layout module reads (through E215's v01_map.py)
KITC=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/KIT.md | tail -n 1)
if [ -n "$KITC" ]; then
  BASE=$(git -C "$SRC" rev-parse "$KITC^") || return 2
  FORM="the kit committed in the lab clone (${KITC:0:12}): the scratch built at its parent ${BASE:0:12}, the kit's files from HEAD $(git -C "$SRC" rev-parse --short=12 HEAD)"
else
  BASE=$(git -C "$SRC" rev-parse HEAD) || return 2
  FORM="the kit's files untracked in the lab clone: the scratch built at its HEAD ${BASE:0:12}"
fi
$G checkout -q -B main "$BASE" || return 2
{ $G branch -q -f e222-desktest-base "$BASE" && $G branch -q --set-upstream-to=e222-desktest-base main; } || { echo "the scratch's upstream could not be set"; return 2; }
REGC=$($G log --diff-filter=A --format=%H -- $E/E222.md | tail -n 1)
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
for spec in "selftest-run-e222.txt SELFTEST-RUN-E222 0 of 0 PASS" "realpath-e222.txt REALPATH-E222 0 of 0 PASS" "realbytes-e222.txt REALBYTES-E222 0 of 0 PASS" \
            "desktest-build-e222.txt DESKTEST-BUILD-E222 0 of 0 PASS" "selftest-rb-e222.txt SELFTEST-RB-E222 0 of 0 PASS" \
            "dry-listing-e222-A.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e222.txt dmcmd_audit: GO (stand-in)" \
            "nokill-e222.txt NOKILL-E222: 0 lines that could send SIGKILL toward a device process (stand-in)" "timeouts-e222.txt TIMEOUT-E222 CHECK PASS (stand-in)"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"
done
( cd "$T" && /usr/bin/python3 -I -B $E/check_e222.py --make > /dev/null )
mklist() {  # the kit's stand-in list: every file this stand-in commit adds under E222's folder, but the list itself and step 2
  ( cd "$T" && git ls-files --others --exclude-standard -- $E | grep -v -x -e "$E/SHA256SUMS-e222-kit" -e "$E/rb/s03_desk_e222.sh" |
      LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/kit-standin.txt"
  KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e222-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^KITPIN=$E/SHA256SUMS-e222-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e222-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e222.sh"
  grep -q "^KITPIN=$E/SHA256SUMS-e222-kit:$KITN:$KITH:top" "$T/$E/rb/s03_desk_e222.sh"
}
mklist || { echo "the scratch step 2's KITPIN was not set"; return 2; }
$G add -A $E && $G commit -q -m "E222 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; return 2; }
KIT=$($G rev-parse HEAD)
echo "scratch repository: a shared sparse clone of the lab clone ($FORM; the registration ${REGC:0:12} in it), the kit as one stand-in commit ${KIT:0:12}; the kit's stand-in list $KITN files"
[ "$KITN" -gt 0 ] || { echo "the kit's stand-in list is empty"; return 2; }
# ---- the stand-ins
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; cat > /dev/null; echo "To authenticate, visit: https://login.tailscale.com/a/e222desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'bash -s' and 'true' are served (got: \$cmd)" >&2; exit 97; }
cd "$B/\$host" || exit 1
exec env HOME="$B/\$host" STANDIN_HOST="\$host" STANDIN_S="$S" PATH="$BB:\$PATH" bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho "scp refused by the desk test" >&2\nexit 97\n' > "$BIN/scp"
printf '#!/bin/sh\necho "${STANDIN_HOST:-desk}"\n' > "$BB/hostname"
cat > "$BB/uptime" <<EOF
#!/bin/sh
if [ "\${1:-}" = -s ] && [ -n "\${STANDIN_HOST:-}" ]; then
  if [ -s "$S/boot-\${STANDIN_HOST}" ]; then cat "$S/boot-\${STANDIN_HOST}"; else echo "2026-11-17 16:46:07"; fi; exit 0
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
exec env E222_FAKE_ARM=A E222_FAKE_CONFIG=\$mode /usr/bin/python3 -B "$T/$E/fake_card_e222.py" "\$@"
EOF
chmod +x "$A3/build/ettelem/ettelem"
cp -p "$SRC/tools/claims-v3/e128/ettelem_guard.sh" "$A3/tools/claims-v3/e128/ettelem_guard.sh"
export PATH="$BIN:$PATH" RB_LOCK="$S/rb-lock.txt"
GL=$S/lab-git.lock; : > "$GL"
TODAY=$(TZ=America/Los_Angeles date +%F)
STARTHM=23:58; ENDHM=23:59           # the window is today's last minutes: the steps' budgets are E222_DESK_BUDGET_S (60 s) here
OA=$S/outA; mkdir -p "$OA"
NRO=$S/nr/out
run() {  # run <RB_OUT> <log> <script> [args]: a step of the scratch repository's runbook
  local o=$1 lg=$2; shift 2
  RB_OUT=$o RB_GITLOCK=$GL RB_DESKTEST=1 E222_DESK_BUDGET_S=60 E222_ROUND_OUT="$NRO" bash "$T/$E/rb/$1" "${@:2}" > "$S/$lg.txt" 2>&1
  echo $?
}
waitjob() {  # waitjob <RB_OUT> <tag> <script> <args...>: call a wait step until it says something other than 17 (at most 40 calls)
  local o=$1 tag=$2 r k; shift 2
  for k in $(seq 1 40); do r=$(run "$o" "$tag-$k" "$@"); [ "$r" = 17 ] || { cp "$S/$tag-$k.txt" "$S/$tag.txt"; echo "$r"; return; }; done; echo 17
}
rec() {  # rec <arm token> <type> <tile> <mask>: one SPARSITY record line of the lab's hosts, randn data
  printf 'SPARSITY {"test":"fma","arm":"%s","gen":"randn","type":"%s","pattern":"none","values":"%s:randn:tools/claims-v3/kinds/tiles/%s","b_stream":0,"minions":1024,"shire_mask":"%s","iters":1,"passes":1,"launch":0,"cycles_max":1,"ghz":0.6,"ok":true}\n' "$1" "$2" "$1" "$3" "$4"
}
cat > "$S/labels_of.py" <<'PY'
import json, sys
print(",".join(json.load(open(sys.argv[1]))["ran_before_points"]["A"]) or "none")
PY
cat > "$S/literal_has.py" <<'PY'
import json, sys
j = json.load(open(sys.argv[1]))
pid = sys.argv[2]
lab = pid in j.get("ran_before_labelled", [])
lit = pid in (j.get("literal_reading_REPORTED") or {}).get("ran", [])
print("literal-only" if lit and not lab else ("labelled" if lab else "neither"))
PY
step "A: the dry listing"
mkdir -p "$S/listing-A"
( cd "$T" && bash $E/rb/list_steps_e222.sh A "$S/listing-A" > "$S/A-A.txt" 2>&1 )
ok "$(grep -c 'dry listing: 15 steps listed, 0 exited non-zero, 0 box calls' "$S/A-A.txt")" "1" "$(tail -n 1 "$S/A-A.txt")"
step "K: step 2 with no window"
r=$(run "$OA" K s03_desk_e222.sh A); ok "$r $( [ -s "$S/calls.log" ] && echo calls || echo nocalls)" "10 nocalls" "$(grep -m1 STOP "$S/K.txt" | cut -c1-120)"
step "W1: a window written for another arm; W2: a window written for another runbook; W3: step 1 for another day; W4: step 1 with an unknown arm"
r=$(run "$OA" W1a s02_window_e222.sh A "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_ARM=A/RB_ARM=B/' "$OA/window.env"; r1=$(run "$OA" W1 s03_desk_e222.sh A)
rm -f "$OA/window.env"; r=$(run "$OA" W2a s02_window_e222.sh A "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_PLAN=e222/RB_PLAN=e215/' "$OA/window.env"
r2=$(run "$OA" W2 s03_desk_e222.sh A)
r3=$(run "$OA" W3 s02_window_e222.sh A 2026-11-12 10:00 12:00)
rm -f "$OA/window.env"; r4=$(run "$OA" W4 s02_window_e222.sh B "$TODAY" "$STARTHM" "$ENDHM")
r=$(run "$OA" W0 s02_window_e222.sh A "$TODAY" "$STARTHM" "$ENDHM")
ok "$r1 $(has 'not arm A' "$S/W1.txt") $r2 $(has 'not E222' "$S/W2.txt") $r3 $r4 $(has "A (aifoundry3 card 0, E222's one arm)" "$S/W4.txt") $r" "10 1 10 1 10 10 1 0" "$(grep -m1 STOP "$S/W1.txt" | cut -c1-100); $(grep -m1 STOP "$S/W2.txt" | cut -c1-100); $(grep -m1 STOP "$S/W4.txt" | cut -c1-90)"
step "G: step 2 without RB_GITLOCK"
r=$(RB_OUT=$OA RB_DESKTEST=1 bash "$T/$E/rb/s03_desk_e222.sh" A > "$S/G.txt" 2>&1; echo $?); ok "$r" 10 "$(grep -m1 STOP "$S/G.txt" | cut -c1-100)"
step "N: step 2 inside the lab-git lock (nested)"
r=$(RB_OUT=$OA RB_GITLOCK=$GL RB_DESKTEST=1 RB_GITLOCK_T=3 flock -n "$GL" bash "$T/$E/rb/s03_desk_e222.sh" A > "$S/N.txt" 2>&1; echo $?)
ok "$r $(has 'pull(rc 14; a nested lab-git lock exits 75)' "$S/N.txt")" "16 1" "$(stopline "$S/N.txt" | cut -c1-160)"
step "P1: step 2 on the scratch repository"
FCF="$E/forecast-e222.json $E/forecast-e222.csv $E/forecast-e222.txt"
touch "$S/p1-before.marker"; fcs0=$(cd "$T" && stat -c '%y %i' $FCF | tr '\n' ' ')
r=$(run "$OA" P1 s03_desk_e222.sh A)
ok "$r $(has 'desk check: the window written today for E222 arm A' "$S/P1.txt")" "0 1" "$(grep -m1 'desk check:' "$S/P1.txt" | cut -c1-260)"
[ "$r" = 0 ] || tail -n 30 "$S/P1.txt"
step "P1W: P1 wrote nothing in the scratch repository's work tree; the registered forecast files untouched; the scorer's two self-tests' files in RB_OUT, byte-identical to the committed"
find "$T" -path "$T/.git" -prune -o -type f -newer "$S/p1-before.marker" -print > "$S/P1W-newer.txt" 2>&1
fcs1=$(cd "$T" && stat -c '%y %i' $FCF | tr '\n' ' ')
sc1=$(cmp -s "$OA/scorer-check-A/selftest-standins-e222-check.json" "$T/$E/selftest-standins.json" && echo same || echo differ)
sc2=$(cmp -s "$OA/scorer-check-A/selftest-real-e222-check.json" "$T/$E/selftest-real.json" && echo same || echo differ)
ok "$(grep -c . "$S/P1W-newer.txt") $([ "$fcs0" = "$fcs1" ] && echo same || echo changed) $sc1 $sc2" "0 same same same" \
   "files written in the scratch's work tree by P1: $(grep -c . "$S/P1W-newer.txt")$(head -n 3 "$S/P1W-newer.txt" | sed "s#^$T/# #" | tr -d '\n'); the three forecast files' times and inodes $([ "$fcs0" = "$fcs1" ] && echo unchanged || echo changed); the scorer's self-tests in RB_OUT: stand-ins $sc1, real bytes $sc2"
step "P1X: a stand-in preflight that rewrites two registered files with their own bytes: step 2 refuses naming wrote-in-lab and both files"
cat > "$T/$E/preflight_e222.sh" <<'EOF'
#!/usr/bin/env bash
# the runbook desk test's case P1X only (never committed): a stand-in for preflight_e222.sh that rewrites two registered files with their own bytes
# (the form of a registration check run in its writing form), then prints the preflight's GO line
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
for f in tools/claims-v3/e222/forecast-e222.csv tools/matmul/mm1/v3.2/out/mm1_v32_params.json; do
  /usr/bin/python3 -I -B - "$R/$f" <<'PY'
import sys
b = open(sys.argv[1], "rb").read()
open(sys.argv[1], "wb").write(b)
PY
done
echo "dmcmd_audit: GO (stand-in: two registered files rewritten with their own bytes)"
EOF
r=$(run "$OA" P1X s03_desk_e222.sh A)
fcx=bytes-same
for f in "$E/forecast-e222.csv" "$MMF"; do $G show "HEAD:$f" > "$S/P1X-committed.bin"; cmp -s "$T/$f" "$S/P1X-committed.bin" || fcx=bytes-changed; done
$G checkout -q -- "$E/preflight_e222.sh" "$E/forecast-e222.csv" "$MMF"
ok "$r $(has "wrote-in-lab(rc 0; 2 file(s): $E/forecast-e222.csv $MMF)" "$S/P1X.txt") $fcx $($G status --porcelain --untracked-files=all | grep -c .)" "16 1 bytes-same 0" \
   "$(grep -ao 'wrote-in-lab([^;]*;[^:]*:[^)]*)' "$S/P1X.txt" | head -n 1); the two files $fcx; the scratch restored from its HEAD: $($G status --porcelain --untracked-files=all | grep -c .) path(s) changed"
step "P2: in one step-2 run: the registration's list one line short, the kit's list one line short, a desk test's log without its PASS line"
cp "$T/$E/SHA256SUMS-e222-registration" "$S/reg.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e222-registration"
cp "$T/$E/SHA256SUMS-e222-kit" "$S/kit.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e222-kit"
cp "$T/$E/logs/realbytes-e222.txt" "$S/rbl.bak"; echo "REALBYTES-E222 0 of 1 FAIL" > "$T/$E/logs/realbytes-e222.txt"
r=$(run "$OA" P2 s03_desk_e222.sh A)
cp "$S/reg.bak" "$T/$E/SHA256SUMS-e222-registration"; cp "$S/kit.bak" "$T/$E/SHA256SUMS-e222-kit"; cp "$S/rbl.bak" "$T/$E/logs/realbytes-e222.txt"
nreg2=$(( $(grep -c . "$S/reg.bak") - 1 )); nkit2=$(( $(grep -c . "$S/kit.bak") - 1 ))
ok "$r $(has "SHA256SUMS-e222-registration($nreg2 OK of $nreg2" "$S/P2.txt") $(has "SHA256SUMS-e222-kit($((nkit2 - 1)) OK of $nkit2; pinned $KITN" "$S/P2.txt") $(has ' realbytes-e222' "$S/P2.txt")" "16 1 1 1" "$(stopline "$S/P2.txt" | cut -c1-220)"
step "H1: a committed edit of a registration file; H2: a committed shadowing addition (tools/claims-v3/e222/json.py)"
echo "an edit" >> "$T/$E/E222.md"; $G commit -q -am "desk test: an edit of E222.md"
r=$(run "$OA" H1 s03_desk_e222.sh A); $G reset -q --hard "$KIT"
echo "# a shadow" > "$T/$E/json.py"; $G add "$E/json.py"; $G commit -q -m "desk test: a shadow"
r2=$(run "$OA" H2 s03_desk_e222.sh A); /usr/bin/python3 -I -B "$T/$E/rb/check_history_e222.py" tree > "$S/H2b.txt" 2>&1; $G reset -q --hard "$KIT"
ok "$r $(has 'history' "$S/H1.txt") $r2 $(has 'json.py' "$S/H2b.txt")" "16 1 16 1" "$(stopline "$S/H1.txt" | cut -c1-150); $(head -c 150 "$S/H2b.txt")"
step "DA: arm A's data committed: step 2 refuses; GS: a gate stop's record and a stand-in FILE named *e222* under docs/reports/data: reported, no datum, 0"
DD="docs/reports/data/$TODAY-e222-blind-matmul-aifoundry3"
mkdir -p "$T/$DD"; echo "stand-in" > "$T/$DD/README.md"
$G add --sparse -f "$DD/README.md"; $G commit -q -m "desk test: E222 arm A data (stand-in)"
r=$(run "$OA" DA s03_desk_e222.sh A); $G reset -q --hard "$KIT"
mkdir -p "$T/docs/reports/gate-stops/$TODAY-e222-blind-matmul-T1-aifoundry3"; echo "stand-in" > "$T/docs/reports/gate-stops/$TODAY-e222-blind-matmul-T1-aifoundry3/README.md"
$G add --sparse -f "docs/reports/gate-stops/$TODAY-e222-blind-matmul-T1-aifoundry3/README.md"; $G commit -q -m "desk test: an E222 gate stop's record (stand-in)"
F175="docs/reports/data/2026-11-05-q143g-e175-design/candidates/tiles/fp16/fp16.e5c92_ar_k_t7_0e222f.bin"
mkdir -p "$T/$(dirname "$F175")"; echo "stand-in tile" > "$T/$F175"; $G add --sparse -f "$F175"; $G commit -q -m "desk test: a file named *e222* (E175's tile-name form)"
rg=$(run "$OA" GS s03_desk_e222.sh A); $G reset -q --hard "$KIT"
ok "$r $(has 'E222-has-data(1 commit(s))' "$S/DA.txt") $rg $(has 'E222 gate-stop commits: 1' "$S/GS.txt")" "16 1 0 1" \
   "arm A's data: $(stopline "$S/DA.txt" | cut -c1-120); a gate stop and a file named *e222*: rc $rg, $(grep -o 'E222 gate-stop commits: [0-9]*; sealed-forecast note commits: [0-9]*' "$S/GS.txt" | head -n 1)"
step "S0: THE STEP-0 CHECKS on the scratch repository (a stand-in GitHub main: its HEAD unless named; a stand-in record of the freeze post)"
SR=$S/sealed; mkdir -p "$SR"
printf '# the round'"'"'s freeze lines for E222 (desk-test stand-in)\n%s\n' "$POSTS_LINE" > "$SR/posts.txt"
s0() { RB_DESKTEST=1 E222_S0_LAB="$T" E222_S0_MAIN="${2:-$($G rev-parse HEAD)}" E222_SEALED="$1" E222_FROZEN_POSTS="${4:-$SR/posts.txt}" bash "$T/$E/rb/s00_step0_e222.sh" A > "$S/S0-$3.txt" 2>&1; echo $?; }
a=$(s0 "$SR/none.txt" "" a)
SHA=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
mkdir -p "$T/tools/claims-v3/sealed-e222"; printf '# E222 freeze lines (desk-test stand-in)\nsha256 %s\n' "$SHA" > "$T/tools/claims-v3/sealed-e222/e222-freeze-lines.md"
$G add tools/claims-v3/sealed-e222; $G commit -q -m "desk test: a sealed-forecast note (stand-in)"
printf '# record\nE222 %s #99 2026-11-20 22:00:00 PST -- stand-in\n' "$SHA" > "$SR/one.txt"
b=$(s0 "$SR/one.txt" "" b)
printf '# record\nE222 %s #99 2026-11-20 22:00:00 PST -- stand-in\nE222 %s #98 2026-11-20 22:01:00 PST -- not registered\n' "$SHA" "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210" > "$SR/two.txt"
c=$(s0 "$SR/two.txt" "" c)
$G reset -q --hard "$KIT"
d=$(s0 "$SR/none.txt" "$($G rev-parse "$REGC^")" d)
e=$(s0 "$SR/none.txt" "$($G rev-parse "$FZ^")" e)
mkdir -p "$T/$DD"; echo "stand-in" > "$T/$DD/README.md"; $G add --sparse -f "$DD/README.md"; $G commit -q -m "desk test: E222 arm A data (stand-in)"
f=$(s0 "$SR/none.txt" "" f); $G reset -q --hard "$KIT"
echo "an untracked file" > "$T/$E/untracked-s0.txt"; g=$(s0 "$SR/none.txt" "" g); rm -f "$T/$E/untracked-s0.txt"
printf '# a record of other posts only\n#1.30.1.2 2026-11-20 05:00:00 PST: another post\n' > "$SR/noposts.txt"
h=$(s0 "$SR/none.txt" "" h "$SR/noposts.txt")
echo "an edit" >> "$T/$E/forecast-e222.txt"; $G commit -q -am "desk test: an edit of forecast-e222.txt"
i=$(s0 "$SR/none.txt" "" i); $G reset -q --hard "$KIT"
echo "not FROZEN.txt" > "$SR/frozen-wrong.txt"
j=$(RB_DESKTEST=1 E222_S0_LAB="$T" E222_S0_MAIN="$($G rev-parse HEAD)" E222_SEALED="$SR/none.txt" E222_FROZEN_POSTS="$SR/posts.txt" E222_FROZEN="$SR/frozen-wrong.txt" bash "$T/$E/rb/s00_step0_e222.sh" A > "$S/S0-j.txt" 2>&1; echo $?)
ok "$a $(has 'sealed 0 of 0' "$S/S0-a.txt") $(has 'STEP0-E222 arm A: 8 of 8 as stated' "$S/S0-a.txt") $b $(has 'sealed 1 of 1' "$S/S0-b.txt") $c $(has 'S1 NOT AS STATED: sealed 1 of 2' "$S/S0-c.txt") $d $(has '^F1 as stated' "$S/S0-d.txt")$(has '^F1C as stated' "$S/S0-d.txt")$(has '^F1R NOT AS STATED' "$S/S0-d.txt")$(has '^F2 NOT AS STATED' "$S/S0-d.txt") $e $(has '^F1 NOT AS STATED' "$S/S0-e.txt")$(has '^F1C NOT AS STATED' "$S/S0-e.txt") $f $(has '^D0 NOT AS STATED' "$S/S0-f.txt") $g $(has "^G1 NOT AS STATED: the lab clone's status: 1 line" "$S/S0-g.txt") $h $(has '^F0 NOT AS STATED: the posted freeze line: no post line names FROZEN.txt' "$S/S0-h.txt") $i $(has '^F0 NOT AS STATED: .*forecast-e222.txt at HEAD is' "$S/S0-i.txt") $j $(has '^F0 NOT AS STATED: .*FROZEN.txt' "$S/S0-j.txt")" \
   "0 1 1 0 1 1 1 1 1111 1 11 1 1 1 1 1 1 1 1 1 1" "no record: $(tail -n 1 "$S/S0-a.txt" | cut -c1-70); a registered seal: $(grep -m1 '^S1' "$S/S0-b.txt" | cut -c1-60); an unregistered one: $(grep -m1 '^S1' "$S/S0-c.txt" | cut -c1-80); main at the registration's parent: $(grep -m1 '^F1R' "$S/S0-d.txt" | cut -c1-80); main before MM1-v3.2's land: $(grep -m1 '^F1 ' "$S/S0-e.txt" | cut -c1-80); no post line: $(grep -m1 '^F0' "$S/S0-h.txt" | cut -c1-90); an edited forecast: $(grep -m1 '^F0' "$S/S0-i.txt" | cut -c1-120); a wrong FROZEN.txt: $(grep -m1 '^F0' "$S/S0-j.txt" | cut -c1-120)"
step "O: the look on the stand-in aifoundry3 (k6's s05)"
r3=$(RB_OUT=$OA bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry3 > "$S/O3.txt" 2>&1; echo $?)
ok "$r3 $( [ -s "$OA/box-login-aifoundry3.txt" ] && echo login)" "0 login" "aifoundry3: $(grep -m1 'FREE\|HELD' "$S/O3.txt" | cut -c1-70)"
step "OB: the stand-in aifoundry3 booted after the firmware read (uptime -s 2026-11-17 16:46:07, the real box's): the look reads FREE and no identity line"
echo "2026-11-17 16:46:07" > "$S/boot-aifoundry3"
rb3=$(RB_OUT=$OA bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry3 > "$S/OB.txt" 2>&1; echo $?)
ok "$rb3 $(has 'booted 2026-11-17 16:46:07' "$S/OB.txt") $(has 'identity:' "$S/OB.txt")" "0 1 0" "the stand-in's boot $(grep -m1 -o 'booted [0-9: -]*' "$S/OB.txt"); $(grep -m1 'FREE\|HELD' "$S/OB.txt" | cut -c1-70)"
step "OL: E222's ours_live counts a session_e222.sh by its own script, never by a command string"
mkdir -p "$S/ol"; printf '#!/bin/bash\nsleep 25\n' > "$S/ol/session_e222.sh"
( . "$T/$E/rb/rb_e222.sh" > /dev/null 2>&1; e222_live_text ) > "$S/ol/live.sh"
printf '. "%s"\necho "$(ours_live session_e222.sh) $(ours_live)"\n' "$S/ol/live.sh" > "$S/ol/count.sh"
printf '#!/bin/bash\nsleep 25\n: tools/claims-v3/e222/session_e222.sh\n' > "$S/ol/decoy.sh"
n0=$(bash "$S/ol/count.sh")
setsid bash "$S/ol/decoy.sh" session_e222.sh < /dev/null > /dev/null 2>&1 &
p1=$!
n1=$(sleep 1; bash "$S/ol/count.sh")
setsid bash "$S/ol/session_e222.sh" < /dev/null > /dev/null 2>&1 &
p2=$!
n2=$(sleep 1; bash "$S/ol/count.sh")
kill "$p1" "$p2" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do [ "$(bash "$S/ol/count.sh")" = "0 0" ] && break; sleep 0.5; done
n3=$(bash "$S/ol/count.sh")
ok "$n0|$n1|$n2|$n3" "0 0|0 0|1 1|0 0" "before: $n0; a script whose arguments and text name session_e222.sh: $n1; a session_e222.sh run as a script: $n2; after it ended: $n3"
step "SY: step 5 on aifoundry3"
ra=$(run "$OA" SYA s07_sync_e222.sh A)
ok "$ra $(has 'HARNESS OK on the box' "$S/SYA.txt")" "0 1" "$(grep -m1 'synced to' "$S/SYA.txt" | cut -c1-120)"
step "L1: a login link on a read (step 5's first read); L2: a read that hangs (the read class's bound 3 s for this call)"
touch "$S/ssh-login"; n0=$(grep -c . "$RB_LOCK" 2>/dev/null || echo 0)
r=$(run "$OA" L1 s07_sync_e222.sh A); n1=$(grep -c 'aifoundry3 needs a check' "$RB_LOCK" 2>/dev/null || echo 0)
touch "$S/ssh-hang"
r2=$(RB_READ_S=3 RB_OUT=$OA RB_DESKTEST=1 bash "$T/$E/rb/s07_sync_e222.sh" A > "$S/L2.txt" 2>&1; echo $?); rm -f "$S/ssh-hang"
ok "$r $((n1 - n0)) $r2" "11 1 13" "$(stopline "$S/L1.txt" | cut -c1-120); $(stopline "$S/L2.txt" | cut -c1-100)"
step "T: NO-THIRD-BUILD on aifoundry3"
mkdir -p "$A3/build"; for k in 1 2; do echo "$TODAY 01:0$k:00 PST a3-build-e222 started" >> "$A3/build/e222-build-attempts.txt"; done
r=$(run "$OA" T s08_build_e222.sh A start); rm -f "$A3/build/e222-build-attempts.txt"
ok "$r $(has NO-THIRD-BUILD "$S/T.txt")" "16 1" "$(stopline "$S/T.txt" | cut -c1-140)"
step "BA: step 6 on aifoundry3: the real build (rgm136's kernel gate, rgm211's tree gate)"
r=$(run "$OA" BA1 s08_build_e222.sh A start); r2=$(waitjob "$OA" BA2 s08_build_e222.sh A wait)
ok "$r $r2 $(has 'KERNEL OK: ' "$S/BA2.txt")$(cat "$OA/e222-built-A.txt" 2>/dev/null)" "0 0 1rgm" "$(grep -m1 'built today on' "$S/BA2.txt" | cut -c1-160)"
[ "$r2" = 0 ] || tail -n 25 "$S/BA2.txt"
step "NR: step 6n, the never-run search repeated (the registration's scanner over the scratch repository and a stand-in lanes folder; dated note 1's reading)"
mkdir -p "$NRO/card-a3-desktest/runs/1" "$NRO/card-a3-desktest/runs/2" "$NRO/data-desktest/work" "$NRO/card-e222/runs/1" "$NRO/kit-e222x/work"
rec gemmLnc2x6x12 fp32 fp32/randn.bin 0xffffffff > "$NRO/card-a3-desktest/runs/1/proc-00.out"   # k01's token (family G3, the token) in a session record on aifoundry3
rec gemmL1x8x8 fp32 fp32/randn.bin 0xa0000000 > "$NRO/card-a3-desktest/runs/2/proc-00.out"       # q01a's token at its mask (Y3: token and masks): q01a and q01b
rec gemmLnc1x6x48 fp32 fp32/randn.bin 0xffffffff > "$NRO/data-desktest/work/copy.txt"            # wn01's token in a folder naming no card: a desk copy, never a label
rec gemmL6x1x2 fp32 fp32/randn.bin 0xffffffff > "$NRO/card-e222/runs/1/proc-00.out"              # b01's token in E222's own card lane: never opened
rec gemmL3x1x5 fp32 fp32/randn.bin 0xffffffff > "$NRO/kit-e222x/work/proc.out"                   # b02's token in a desk lane: not read
ra=$(run "$OA" NRA s06n_neverrun_e222.sh A)
nrda=$(cat "$OA/e222-neverrun-dir-A.txt" 2>/dev/null)
la=$(/usr/bin/python3 -I -B "$S/labels_of.py" "$nrda/labels-e222-A.json" 2>/dev/null)
ck=$( (cd "$T" && /usr/bin/python3 -I -B $E/desk/neverrun_card_e222.py check-labels "$nrda/labels-e222-A.json") 2>&1 | tail -n 1 | cut -c1-9)
jk=$(grep -cE '^  k01 G3 gemmLnc2x6x12 0xffffffff: RAN BEFORE .*card-a3-desktest/runs/1/proc-00.out' "$nrda/judge-e222-A.txt" 2>/dev/null)
jq=$(grep -cE '^  q01a Y3 gemmL1x8x8 0xa0000000: RAN BEFORE .*card-a3-desktest/runs/2/proc-00.out' "$nrda/judge-e222-A.txt" 2>/dev/null)
jr=$(grep -c ' R gemm.*: RAN (exempt by family name: same-card repeats, REPORTED only); the positive control ([a-z (),]*): RAN ' "$nrda/judge-e222-A.txt" 2>/dev/null)
pc=$(grep -c 'the positive control (R.s exemption lifted, the same scan): 4 of 4 RAN' "$OA/e222-neverrun-A.txt" 2>/dev/null)
lw=$(/usr/bin/python3 -I -B "$S/literal_has.py" "$nrda/judge-e222-A.json" wn01 2>/dev/null)
sub=$(grep -c 'card-e222/runs\|kit-e222x' "$nrda/judge-e222-A.txt" "$nrda/judge-e222-A.json" 2>/dev/null | awk -F: '{s += $NF} END {print s + 0}')
ok "$ra $la $ck $jk$jq $jr $pc $lw $sub $( [ -s "$OA/e222-neverrun-A.txt" ] && echo report)" "0 k01,q01a,q01b LABELS-OK 11 4 1 literal-only 0 report" \
   "$(grep -m1 'NEVER-RUN-E222 arm A' "$S/NRA.txt" | cut -c1-300)"
step "NRP: the positive control failing (the scratch's sparse checkout without E218's data folder): step 6n stops with 16, no report"
OP=$S/outP; mkdir -p "$OP"; cp "$OA/window.env" "$OP/"; touch "$OP/window.env"
$G sparse-checkout set --no-cone $(echo $SPARSE | tr ' ' '\n' | grep -v 'e218-blind-matmul-aifoundry3') || echo "the sparse checkout could not be narrowed"
gone=$([ -d "$T/docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3" ] && echo present || echo absent)
rp=$(run "$OP" NRP s06n_neverrun_e222.sh A)
$G sparse-checkout set --no-cone $SPARSE || echo "the sparse checkout could not be restored"
back=$([ -d "$T/docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3" ] && echo restored || echo missing)
ok "$gone $rp $(has 'POSITIVE CONTROL FAILED' "$S/NRP.txt") $( [ -s "$OP/e222-neverrun-A.txt" ] && echo report || echo noreport) $back" "absent 16 1 noreport restored" \
   "$(stopline "$S/NRP.txt" | cut -c1-200)"
step "R7: STEP 7 needs a fresh never-run report and the rest; R7f: a threshold of 70 C read: refused"
O5=$S/out5; mkdir -p "$O5"; cp "$OA/window.env" "$O5/"; touch "$O5/window.env"
c0=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
ra=$(run "$O5" R7a s09_reads_e222.sh A)
cp "$OA/e222-neverrun-A.txt" "$O5/"; touch -d '-31 min' "$O5/e222-neverrun-A.txt"
rb_=$(run "$O5" R7b s09_reads_e222.sh A)
mkdir -p "$A3/build/e185/T1"
{ echo "$(date -d '-14 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-10 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-10 min' "$A3/build/e185/T1/session.log"
rc_=$(run "$OA" R7c s09_reads_e222.sh A); c1=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
{ echo "$(date -d '-50 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-45 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-45 min' "$A3/build/e185/T1/session.log"
rd=$(run "$OA" R7d s09_reads_e222.sh A); c2=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
echo thr70 > "$S/reader-mode-A"
rf=$(run "$OA" R7f s09_reads_e222.sh A); c3=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
rm -f "$S/reader-mode-A"
ok "$ra $(has 'no never-run report' "$S/R7a.txt") $rb_ $(has 'minutes old (more than 30)' "$S/R7b.txt") $rc_ $(has 'the rest has not run' "$S/R7c.txt") $((c1 - c0)) $rd $((c2 - c1)) $(has 'config TDP 0 W / 65 C / 600 MHz, et-who clean' "$S/R7d.txt") $rf $((c3 - c2)) $(has "aifoundry3's config is not TDP 0 W / 65 C / 600 MHz" "$S/R7f.txt")" \
   "10 1 10 1 10 1 0 0 1 1 16 1 1" "no report: $(stopline "$S/R7a.txt" | cut -c1-80); 31 min: $(stopline "$S/R7b.txt" | cut -c1-80); 10 min after a session: $(stopline "$S/R7c.txt" | cut -c1-80) (reader calls $((c1 - c0))); a 70 C threshold: $(stopline "$S/R7f.txt" | cut -c1-100)"
step "D: step 8 on aifoundry3 (the dry pass and THE SCRUB CHECK); DS: the scrub check refusing another home's path"
ra=$(run "$OA" DA1 s10_dry_e222.sh A start); ra2=$(waitjob "$OA" DA2 s10_dry_e222.sh A wait)
dda=$(ls -d "$A3"/build/e222/T*-A-dry 2>/dev/null | tail -n 1)
mkdir -p "$dda/zz"; echo '{"path": "/home/someoneelse/work/x"}' > "$dda/zz/other-home.json"
rs=$(waitjob "$OA" DS s10_dry_e222.sh A wait); rm -rf "${dda:?}/zz"
ok "$ra $ra2 $(has 'SCRUB-CHECK CLEAN: ' "$S/DA2.txt") $(has 'E222-DRY arm A rc=0 runs=3' "$S/DA2.txt") $rs $(has 'SCRUB-CHECK LEFT' "$S/DS.txt")" "0 0 1 1 16 1" \
   "$(grep -m1 'E222-DRY' "$S/DA2.txt" | cut -c1-80); $(grep -m1 'SCRUB-CHECK' "$S/DA2.txt" | cut -c1-90); another home: $(stopline "$S/DS.txt" | cut -c1-80)"
[ "$ra2" = 0 ] || tail -n 25 "$S/DA2.txt"
step "HG: a HUNG marker in a session log of ours on aifoundry3: step 9 refuses"
mkdir -p "$A3/build/e204/T1794800000"
printf '%s session start (T0 1794800000; desk test)\n%s HUNG: a device process did not end after its timeout TERM (desk test)\n%s session end (T0 1794800000)\n' \
  "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" > "$A3/build/e204/T1794800000/session.log"
touch -d '-3 hours' "$A3/build/e204/T1794800000/session.log"
r=$(run "$OA" HG s11_session_e222.sh A); rm -rf "${A3:?}/build/e204"
ok "$r $(has 'REFUSED: a HUNG marker of ours on the box' "$S/HG.txt") $(ls "$A3/build/e222" 2>/dev/null | grep -c '^T[0-9]*-A$')" "10 1 0" "$(grep -m1 'REFUSED' "$S/HG.txt" | cut -c1-140)"
step "SD: the same-day rule: an E222 arm A session that opened the card earlier today"
mkdir -p "$A3/build/e222/T1700000000-A"
printf '%s session start (T0 1700000000; desk test)\n%s the first card command: the start config read through the guard\n%s session end (T0 1700000000)\n' \
  "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-45 min' '+%F %T %Z')" > "$A3/build/e222/T1700000000-A/session.log"
if [ "$(TZ=America/Los_Angeles date -d '-45 min' +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then touch -d '-45 min' "$A3/build/e222/T1700000000-A/session.log"
else TZ=America/Los_Angeles touch -d "$(TZ=America/Los_Angeles date +%F) 00:00:01" "$A3/build/e222/T1700000000-A/session.log"; fi
r=$(run "$OA" SD s11_session_e222.sh A); rm -rf "${A3:?}/build/e222/T1700000000-A"
ok "$r $(has 'REFUSED: the same-day rule' "$S/SD.txt")" "10 1" "$(grep -m1 'REFUSED' "$S/SD.txt" | cut -c1-140)"
step "LS: THE LAST START passed (the window's last end still far): step 9 refuses (16) before anything is sent"
O6=$S/out6; mkdir -p "$O6"; cp "$OA/window.env" "$OA/e222-built-A.txt" "$O6/"
sedi -e "s/^RB_LAST_START_EPOCH=.*/RB_LAST_START_EPOCH=$(( $(date +%s) - 60 ))/" "$O6/window.env"; touch "$O6/window.env" "$O6/e222-built-A.txt"
n0=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
r=$(run "$O6" LS s11_session_e222.sh A); n1=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
ok "$r $(has "past the round's last start" "$S/LS.txt") $((n1 - n0))" "16 1 0" "$(stopline "$S/LS.txt" | cut -c1-140); box calls $((n1 - n0))"
step "NS: no never-run report from today in RB_OUT: step 9 refuses (10) before anything is sent"
O7=$S/out7; mkdir -p "$O7"; cp "$OA/window.env" "$OA/e222-built-A.txt" "$O7/"; touch "$O7/window.env" "$O7/e222-built-A.txt"
n0=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
r=$(run "$O7" NS s11_session_e222.sh A); n1=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
ok "$r $(has 'no never-run report from today' "$S/NS.txt") $((n1 - n0))" "10 1 0" "$(stopline "$S/NS.txt" | cut -c1-140); box calls $((n1 - n0))"
step "LA: step 9 launches the REAL session_e222.sh, which stops at its box check (the desk's own hostname); step 10 reads the gate"
r=$(run "$OA" LA s11_session_e222.sh A); r2=$(waitjob "$OA" LA2 s20_wait_e222.sh A)
t0=$(cat "$OA/e222-T0-A.txt" 2>/dev/null)
sd=$A3/build/e222/T$t0-A
procs=$(find "$sd" -name 'proc*.out' 2>/dev/null | wc -l | tr -d ' ')
ok "$r $r2 $(has 'refused, no device opened: the box or the build is not the registered one (this host is' "$sd/session.log") $(has '"rc": 16' "$sd/queue.json") $( [ -s "$sd/MANIFEST.sha256" ] && echo manifest) $procs $(has 'GATE-STOPPED e222 arm A' "$S/LA2.txt")" \
   "0 16 1 1 manifest 0 1" "$(grep -m1 'no device opened' "$sd/session.log" | cut -c1-200)"
step "W10: step 10's readings on stand-in logs (a running session, none, HUNG, K1, CRASH, an ended session with a STOP line)"
O3=$S/out3; mkdir -p "$O3"; cp "$OA/window.env" "$OA/box-login-aifoundry3.txt" "$O3/"; touch "$O3/window.env"; echo 7 > "$O3/e222-T0-A.txt"
mkdir -p "$A3/build/q141k"; echo 7 > "$A3/build/q141k/e222A.T0"; W7=$A3/build/e222/T7-A; mkdir -p "$W7"
mkdir -p "$S/wv"; printf '#!/bin/bash\nsleep 30\n' > "$S/wv/session_e222.sh"
wr() { RB_OUT=$O3 RB_DESKTEST=1 RB_WAIT_LOOP_S=4 bash "$T/$E/rb/s20_wait_e222.sh" A > "$S/W10-$1.txt" 2>&1; echo $?; }
echo "$(date '+%F %T %Z') session start (T0 7; desk-test stand-in, no end)" > "$W7/session.log"
setsid bash "$S/wv/session_e222.sh" < /dev/null > /dev/null 2>&1 &
p3=$!
sleep 1
rv=$(wr V)
kill "$p3" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$p3" 2>/dev/null || break; sleep 0.5; done
rg=$(wr G)
printf '%s session start (T0 7; desk test)\n%s HUNG: a device process (the host of 002-pass1-wn07t (proc-00); its `timeout` pid 9) still runs\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"
rh=$(wr H)
printf '%s session start (T0 7; desk test)\n%s STOP: K1: a launch of run 002-pass1-wn07t did not finish (the host'"'"'s words): it may leave a hung hart: nothing further started\n%s session end (T0 7)\n' \
  "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo "x  session.log" > "$W7/MANIFEST.sha256"; echo 0 > "$W7/runner.rc"
rk=$(wr K)
printf '%s session start (T0 7; desk test)\n%s CRASH: KeyError: y99\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 1 > "$W7/runner.rc"
rc_=$(wr C)
printf '%s session start (T0 7; desk test)\n%s STOP: board 71.2 W above 70 W on 3 samples in a row: nothing further started\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 0 > "$W7/runner.rc"
re=$(wr E)
rm -rf "${A3:?}/build/e222/T7-A"; echo "$t0" > "$A3/build/q141k/e222A.T0"
ok "$rv $rg $rh $rk $rc_ $re $(has 'RUN-RUNNING' "$S/W10-V.txt")$(has 'RUN-GONE' "$S/W10-G.txt")$(has 'KILL NOTHING' "$S/W10-H.txt")$(has 'K1' "$S/W10-K.txt")$(has 'crashed' "$S/W10-C.txt")$(has 'read its STOP line' "$S/W10-E.txt")" \
   "17 14 16 16 16 0 111111" "running $rv, gone $rg, HUNG $rh, K1 $rk, CRASH $rc_, ended with a STOP line $re"
step "C: step 11 on LA's session, step 12 (the gate stop's record), step 13 refuses it; C2: a byte changed after the manifest"
r=$(run "$OA" C1 s22_collect_e222.sh A); r2=$(run "$OA" C2s s23_data_e222.sh A); r3=$(run "$OA" C3s s24_score_e222.sh A)
gs=$(cat "$OA/e222-data-dir-A.txt" 2>/dev/null)
ok "$r $r2 $(has 'COLLECTED-GATE-STOP docs/reports/gate-stops/' "$S/C2s.txt") $(grep -rl '/home/' "$T/$gs" 2>/dev/null | wc -l | tr -d ' ') $r3" "0 0 1 0 10" \
   "$(grep -m1 'COLLECTED' "$S/C2s.txt" | cut -c1-140); step 13: $(stopline "$S/C3s.txt" | cut -c1-100)"
[ -n "$gs" ] && rm -rf "${T:?}/${gs:?}"
O2=$S/out2; mkdir -p "$O2"; cp "$OA"/window.env "$OA"/e222-T0-A.txt "$OA"/box-login-aifoundry3.txt "$O2/"; touch "$O2/window.env"
echo "x" >> "$sd/session.log"
r=$(RB_OUT=$O2 RB_DESKTEST=1 bash "$T/$E/rb/s22_collect_e222.sh" A > "$S/C2.txt" 2>&1; echo $?)
ok "$r $(has 'COPY-BACK NOT EXACT' "$S/C2.txt")" "16 1" "$(stopline "$S/C2.txt" | cut -c1-140)"
step "CD: a session that ran (step 8's dry session copied as a session): steps 11, 12 and, after a stand-in data commit, 13 WITH step 6n's labels"
O=$S/out4
dd=$(ls -d "$A3"/build/e222/T*-A-dry 2>/dev/null | tail -n 1)
mkdir -p "$O"; cp "$OA"/window.env "$OA"/box-login-aifoundry3.txt "$OA"/e222-neverrun-dir-A.txt "$O/"; touch "$O/window.env"; echo 8 > "$O/e222-T0-A.txt"
cp -a "$dd" "$A3/build/e222/T8-A"; rm -f "${A3:?}/build/e222/T8-A/dry.lock"
r=$(run "$O" CD1 s22_collect_e222.sh A); r2=$(run "$O" CD2 s23_data_e222.sh A)
dd2=$(cat "$O/e222-data-dir-A.txt" 2>/dev/null)
$G add --sparse -f "$dd2" > /dev/null 2>&1; $G commit -q -m "desk test: a data commit (stand-in)" > /dev/null 2>&1
r3=$(run "$O" CD3 s24_score_e222.sh A)
nh=$(grep -c . "$O/box-home-A.txt" 2>/dev/null)
lap=$(grep -c '"ran_before": true' "$O/scores-e222-A.json" 2>/dev/null)
ok "$r $r2 $(has "COLLECTED docs/reports/data/$TODAY-e222-blind-matmul-aifoundry3" "$S/CD2.txt") $( [ -s "$T/$dd2/data-e222.json" ] && echo data) $(grep -c '  \(neverrun-e222-card\.\(txt\|json\)\|judge-e222-card\.\(txt\|json\)\|labels-e222\.json\)$' "$T/$dd2/SHA256SUMS" 2>/dev/null) $(has 'LABELS-OK' "$S/CD3.txt") $r3 $( [ -s "$O/scores-e222-A.json" ] && echo scored) $(grep -c '^SEL: \|^R0: \|^CX: PENDING E220 DATA' "$O/scores-e222-A.txt" 2>/dev/null) $( [ "${nh:-0}" -ge 1 ] && echo homes)" \
   "0 0 1 data 5 1 0 scored 3 homes" "$(grep -m1 'COLLECTED' "$S/CD2.txt" | cut -c1-130); $(grep -m1 'scored E222' "$S/CD3.txt" | cut -c1-80); points measured with a 'ran before' label: $lap (the labelled points did not run in the dry pass)"
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
echo "SELFTEST-RB-E222 $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
}
main
