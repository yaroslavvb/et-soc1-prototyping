#!/usr/bin/env bash
# E211 (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum): the desk test of E211's runbook with a FAKE ssh and rsync on a stand-in
# aifoundry3, E206's rb/selftest_rb_e206.sh form (landed in 906699ea), as E207's kit ported it (Q199), for E211's one box and two kernels. Its scratch repository is a shared, sparse clone of the
# lab clone this test runs from (its HEAD holds E211's registration as a commit, as on the card day) with the kit's files committed on top as one
# stand-in kit commit, the kit's list a stand-in made here and pinned in the scratch copy of step 2's KITPIN line (the one line this test changes
# in a copy), and stand-in desk-test logs (this test's own log is not final while it runs). The stand-in box is aifoundry3's ~/aifoundry, an
# rsync target under the scratch; the stand-in ssh serves it with `bash -s` (and `true`) and refuses any other host or command; the stand-in
# rsync rewrites its paths; the box's hostname, uptime, et-who, et-lab-manifest and pgrep are stand-ins, and the box tree holds a stand-in reader
# at build/ettelem/ettelem (the doubles' config and sampler) and E128's guard (k6's step 7 runs it there); cmake, the compilers and /opt/et are
# this desk's REAL ones (the build is the real build_e211.sh, both kernels through THE KERNEL GATE, the hosts' refusals in its sandbox). Step 6n
# reads stand-in roots (a lab, the round's lane folders, HOME/claude/work) through E211_NR_* (RB_DESKTEST=1 only). No lab box is reached.
# When the lab clone's history holds the kit commit (the commit that added KIT.md: the readiness lane), the scratch repository is built at that
# commit's PARENT and the kit's files are taken from HEAD, its main following a local branch at that parent (so step 2's pull is up to date);
# otherwise (the kit lane) the untracked files and the lab clone's HEAD. Cases:
#   A   the dry listing: every step exits 0, no call reaches the stand-ins
#   K   step 2 with no window: 10       W1 a window written for another arm: 10      W2 a window written for another runbook: 10
#   W3  step 1 for another day: 10      W4 step 1 with the arm B: 10                G  step 2 without RB_GITLOCK: 10
#   N   step 2 inside the lab-git lock (nested): 16 naming the pull
#   P1  step 2 on the scratch repository: 0 (the lists at their pins, HISTORY OK, the registration and the kit found by content, the
#       registration's checks, the scorer's stand-in self-test byte-identical, the preflight GO, the desk tests' logs and the simulator check's)
#   P2  the registration's list one line short: 16      P3 the kit's list one line short: 16
#   P4  the simulator check's log without its AS STATED line: 16
#   H1  a committed edit of a registration file: 16 by the history check      H2 a committed tools/claims-v3/e211/json.py (a shadow): 16
#   DA  E211 data committed: step 2 refuses (16)      GS an E211 gate stop's record committed: step 2 reports it and goes on (0)
#   E7  (fix-e211, Amendment A1 clause 4) no E207 data folder at HEAD: step 2 refuses (16) with E207-data alone in its failure list; the
#       scratch repository carries one stand-in E207 data commit on the kit's for every other case (P1 reads it: E207 data folders at HEAD)
#   O   the look on the stand-in box (k6's s05, unchanged): FREE, our login recorded for the scrub
#   OL  E211's ours_live: a shell whose command string names session_e211.sh is not a session; a session_e211.sh run as a script is
#   SY  step 5: the rsync, HARNESS OK on the box     L1 a login link on a read: 11, "<HH:MM:SS> aifoundry3 needs a check" appended to RB_LOCK,
#       nothing retried      L2 a read that hangs (the read class's bound 3 s for this call): 13
#   T   NO-THIRD-BUILD: two starts recorded on aifoundry3 today: a third start is refused with 16
#   BA  step 6: start, wait (17 while it builds, then 0): the REAL build of both kernels, KERNEL OK on each, the record, the harness, the
#       preflight GO and both self-checks read on the box; RB_OUT/e211-built-A.txt
#   NR  STEP 6n, THE NEVER-RUN SEARCH REPEATED, on stand-in roots: a gemmLn record in the lab's data (as if a card had run rgm211) and one in
#       another kit's run folder on the box are found ("rgm211 on a card before E211: <keys>"), a twin's record in the lab's data is listed; a
#       gemmLn record in an E211 lane's desk test, in E211's design lane, in E211's own dry pass on the box and in the model session's folder
#       are left out by name; a simulator record on the box (ghz 0) is named apart, never a card run; the --desk-only form says "aifoundry3
#       NOT SEARCHED" and finds the lab's alone; the registration's committed report is never touched
#   R7  STEP 7 ONLY WITH A FRESH NEVER-RUN REPORT AND ONLY ONCE THE REST HAS OPENED: no report: 10; a report 31 minutes old: 10; a session of ours
#       ended 10 minutes ago: 10; in none of the three is the stand-in reader called (no config read sent); then 0, the reader called once
#   D   step 8 on the stand-in box (the doubles there): 0
#   HG  THE HUNG MARKER: a session log of ours on aifoundry3 with a HUNG line: step 9 refuses (10), nothing launched
#   SD  THE SAME-DAY RULE: an E211 session that opened the card earlier today: step 9 refuses (10)
#   LS  THE LAST START passed with the last end still far: step 9 refuses (16) and sends nothing to the box
#   NS  no never-run report from today in RB_OUT (step 6n): step 9 refuses (10) and sends nothing to the box
#   LA  step 9 launches the REAL session_e211.sh and run_e211.py on the stand-in aifoundry3, which stop at their box check before any device
#       (the desk's own hostname): "refused, no device opened"; step 10 reads GATE-STOPPED (16) with the manifest written
#   W10 step 10's readings on stand-in logs: a running session_e211.sh with no end 17 (RUN-RUNNING); none running 14 (RUN-GONE); a HUNG line
#       16 (HUNG); a K1 stop 16 (K1-STOPPED); a CRASH line 16 (CRASHED); an ended session (rc 0) with a STOP line 0
#   C   step 11 on LA's session: COPY-BACK EXACT 0; step 12: the gate stop's record under docs/reports/gate-stops/ (COLLECTED-GATE-STOP), the
#       desk-path gate, HISTORY OK: 0; step 13 refuses a gate stop's record: 10      C2 one byte of a box file changed after the manifest:
#       COPY-BACK NOT EXACT 16
#   CD  a session that ran (step 8's dry session copied as a session): step 11 0, step 12 the data directory with data-e211.json (the reducer),
#       step 6n's report (neverrun-e211-card.txt and .json, in SHA256SUMS) and the scrub clean: 0; after a stand-in data commit, step 13 runs
#       the FROZEN scorer on it: 0
#   Z   no process of this test left running
#   bash tools/claims-v3/e211/rb/selftest_rb_e211.sh <scratch dir> > logs/selftest-rb-e211.txt   (prints SELFTEST-RB-E211 <n> of <m> PASS or FAIL)
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
# fix-e211 (Tue 17 Nov 2026, before any E211 datum): the stand-in box is this desk, so ours_live (steps 5, 6, 10 and 11, and case OL) reads the
# desk's real process table, where another lane's session_eNNN.sh or queue_eNNN desk processes on aifoundry2 read as a session of ours
# (fix-e211's run t3 read 16 of 29 while kit-e209's real-path test ran eleven session_e209.sh processes). So the test runs itself once more in
# a private PID namespace (bubblewrap, as desk/realpath_e211.sh runs its test), where it sees only its own processes; E211_RB_PIDNS=1 marks
# that inner run. The sandbox's /dev (no et node, checked above) and every path are the same inside.
if [ -z "${E211_RB_PIDNS:-}" ]; then
  command -v bwrap > /dev/null || { echo "no bwrap: the runbook test runs in a private PID namespace"; exit 2; }
  echo "(the runbook test: re-run in a private PID namespace, so that no other lane's process on this desk is read as a session of ours)"
  exec /usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- env E211_RB_PIDNS=1 bash "$SRC/tools/claims-v3/e211/rb/selftest_rb_e211.sh" "$@"
fi
for c in timeout sha256sum flock cmake c++ rsync git; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
REAL_RSYNC=$(command -v rsync)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree box bin boxbin out; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; B=$S/box; BIN=$S/bin; BB=$S/boxbin
A3=$B/aifoundry3/aifoundry
E=tools/claims-v3/e211
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
G="git -C $T -c user.name=e211-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /workloads/ledger/ /docs/reports/data/2026-11-02-e136-large-gemm/ /docs/reports/data/2026-11-01-e119-gemm-speed/ \
  /docs/reports/data/2026-11-02-e126-gemm-arms/ /docs/reports/data/2026-11-02-e146-gemm-stores/ /docs/reports/data/2026-11-12-q166-ledger-v2/ \
  /docs/reports/data/2026-11-01-e107-gemm-placement/ /docs/reports/data/2026-11-01-e95-real-tensors-energy/ /docs/reports/data/2026-09-23-energy-manual/ \
  /docs/reports/data/2026-11-13-e190-large-gemm/ /docs/reports/data/2026-11-01-e105-gemm-layout/ /docs/reports/data/2026-10-26-load-model/ \
  /docs/reports/data/2026-11-12-q166-counter-sparseparity/ /docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/ \
  /docs/reports/data/2026-11-01-e101-real-matmul/ || return 2
# fix-e206 (verify-e206's finding 2): the kit committed in the lab clone (the readiness lane runs this test at HEAD) or not yet (the kit lane)
KITC=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/KIT.md | tail -n 1)
if [ -n "$KITC" ]; then
  BASE=$(git -C "$SRC" rev-parse "$KITC^") || return 2
  FORM="the kit committed in the lab clone (${KITC:0:12}): the scratch built at its parent ${BASE:0:12}, the kit's files from HEAD $(git -C "$SRC" rev-parse --short=12 HEAD)"
else
  BASE=$(git -C "$SRC" rev-parse HEAD) || return 2
  FORM="the kit's files untracked in the lab clone: the scratch built at its HEAD ${BASE:0:12}"
fi
$G checkout -q -B main "$BASE" || return 2
if [ -n "$KITC" ]; then      # a local upstream at the parent, so step 2's `git pull --ff-only` is up to date (the lab clone's main would diverge)
  { $G branch -q -f e211-desktest-base "$BASE" && $G branch -q --set-upstream-to=e211-desktest-base main; } || { echo "the scratch's upstream could not be set"; return 2; }
else
  $G branch -q --set-upstream-to=origin/main 2>/dev/null
fi
$G log --diff-filter=A --format=%H -- $E/E211.md | grep -q . || { echo "the registration is not in the scratch repository's history"; return 2; }
if [ -n "$KITC" ]; then      # the paths the kit commit added, at HEAD's bytes (the history check keeps them as first committed)
  git -C "$SRC" diff-tree --no-commit-id --name-only -r --diff-filter=A "$KITC" -- $E | while IFS= read -r f; do
    mkdir -p "$T/$(dirname "$f")"; git -C "$SRC" show "HEAD:$f" > "$T/$f" || exit 2; done || { echo "the kit's files could not be taken from HEAD"; return 2; }
else
  ( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E ) | sort -u | while IFS= read -r f; do
    [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
fi
mkdir -p "$T/$E/logs"
for spec in "selftest-run-e211.txt SELFTEST-RUN-E211 0 of 0 PASS" "realpath-e211.txt REALPATH-E211 0 of 0 PASS" "realbytes-e211.txt REALBYTES-E211 0 of 0 PASS" \
            "desktest-build-e211.txt DESKTEST-BUILD-E211 0 of 0 PASS" "selftest-rb-e211.txt SELFTEST-RB-E211 0 of 0 PASS" \
            "dry-listing-e211.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e211.txt dmcmd_audit: GO (stand-in)" \
            "simcheck-e211.txt SIMCHECK-E211 0 of 0 AS STATED"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"
done
( cd "$T" && /usr/bin/python3 -I -B $E/check_e211.py --make > /dev/null )
mklist() {  # the kit's stand-in list: every file this stand-in commit adds under E211's folder, but the list itself and step 2
  ( cd "$T" && git ls-files --others --exclude-standard -- $E | grep -v -x -e "$E/SHA256SUMS-e211-kit" -e "$E/rb/s03_desk_e211.sh" |
      LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/kit-standin.txt"
  KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e211-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^KITPIN=$E/SHA256SUMS-e211-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e211-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e211.sh"
  grep -q "^KITPIN=$E/SHA256SUMS-e211-kit:$KITN:$KITH:top" "$T/$E/rb/s03_desk_e211.sh"
}
mklist || { echo "the scratch step 2's KITPIN was not set"; return 2; }
$G add -A $E && $G commit -q -m "E211 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; return 2; }
KITS=$($G rev-parse HEAD)
# fix-e211 (Tue 17 Nov 2026, Amendment A1 clause 4): step 2 refuses while no E207 data folder is at HEAD, so the scratch repository gets one
# stand-in E207 data commit on top of the kit's; every case that resets to KIT keeps it, and case E7 removes every E207 data folder at HEAD
E7D="docs/reports/data/$(TZ=America/Los_Angeles date +%F)-e207-desktest-standin-aifoundry3"
mkdir -p "$T/$E7D"; echo "stand-in (E211's runbook desk test): E207's data folder" > "$T/$E7D/README.md"
{ $G add --sparse -f "$E7D/README.md" && $G commit -q -m "E211 runbook desk test: E207's data folder (stand-in)"; } || { echo "the scratch E207 stand-in commit failed"; return 2; }
KIT=$($G rev-parse HEAD)
echo "scratch repository: a shared sparse clone of the lab clone ($FORM; the registration in it), the kit as one stand-in commit ${KITS:0:12} and a stand-in E207 data commit ${KIT:0:12} on it; the kit's stand-in list $KITN files"
[ "$KITN" -gt 0 ] || { echo "the kit's stand-in list is empty"; return 2; }
# ---- the stand-ins
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; cat > /dev/null; echo "To authenticate, visit: https://login.tailscale.com/a/e211desktest" >&2; sleep 30; exit 1; fi
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
cat > "$BB/uptime" <<'EOF'
#!/bin/sh
if [ "${1:-}" = -s ] && [ "${STANDIN_HOST:-}" = aifoundry3 ]; then echo "2026-10-26 15:18:24"; exit 0; fi
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
for spec in "$A3:A"; do       # the box's own tools: a stand-in reader (counting its calls), and the E128 guard (k6's step 7 runs it)
  bt=${spec%%:*}; arm=${spec#*:}
  mkdir -p "$bt/build/ettelem" "$bt/tools/claims-v3/e128"
  cat > "$bt/build/ettelem/ettelem" <<EOF
#!/bin/sh
echo "\$(date +%s) \$*" >> "$S/reader-calls-$arm.txt"
mode=ok; [ -s "$S/reader-mode-$arm" ] && mode=\$(cat "$S/reader-mode-$arm")
exec env E211_FAKE_ARM=$arm E211_FAKE_CONFIG=\$mode /usr/bin/python3 -B "$T/$E/fake_card_e211.py" "\$@"
EOF
  chmod +x "$bt/build/ettelem/ettelem"
done
cp -p "$SRC/tools/claims-v3/e128/ettelem_guard.sh" "$A3/tools/claims-v3/e128/ettelem_guard.sh"
export PATH="$BIN:$PATH" RB_LOCK="$S/rb-lock.txt"
GL=$S/lab-git.lock; : > "$GL"
TODAY=$(TZ=America/Los_Angeles date +%F)
STARTHM=23:58; ENDHM=23:59           # the window is today's last minutes: the steps' budgets are E211_DESK_BUDGET_S (60 s) here
OA=$S/outA; mkdir -p "$OA"
run() {  # run <arm's RB_OUT> <log> <script> [args]: a step of the scratch repository's runbook
  local o=$1 lg=$2; shift 2
  RB_OUT=$o RB_GITLOCK=$GL RB_DESKTEST=1 E211_DESK_BUDGET_S=60 E211_ROUND_OUT="$NRO" E211_NR_LAB="$NRL" E211_NR_OUT="$NRO" E211_NR_HOMEW="$NRH" \
    E211_NR_ARMS="$NRH/ee-1116-mmsweep/src/arms.json" bash "$T/$E/rb/$1" "${@:2}" > "$S/$lg.txt" 2>&1
  echo $?
}
waitjob() {  # waitjob <RB_OUT> <tag> <script> <args...>: call a wait step until it says something other than 17 (at most 40 calls)
  local o=$1 tag=$2 r k; shift 2
  for k in $(seq 1 40); do r=$(run "$o" "$tag-$k" "$@"); [ "$r" = 17 ] || { cp "$S/$tag-$k.txt" "$S/$tag.txt"; echo "$r"; return; }; done; echo 17
}
# ---- the never-run step's stand-in roots (a lab, the round's lane folders, HOME/claude/work), read through E211_NR_* (RB_DESKTEST=1 only)
NRL=$S/nr/lab; NRO=$S/nr/out; NRH=$S/nr/homew
rec() {  # rec <arm> <type> <tile> [ghz]: one SPARSITY record line of the lab's hosts, full chip, randn data (ghz 0 is a simulator's)
  printf 'SPARSITY {"test":"fma","arm":"%s","gen":"randn","type":"%s","pattern":"none","values":"%s:randn:tools/claims-v3/kinds/tiles/%s","b_stream":0,"minions":1024,"shire_mask":"0xffffffff","iters":1,"passes":1,"launch":0,"cycles_max":1,"ghz":%s,"ok":true}\n' "$1" "$2" "$1" "$3" "${4:-0.6}"
}
mkdir -p "$NRL/docs/reports/data/2026-11-01-x-aifoundry3" "$NRO/kit-e211/work/t" "$NRO/mm-kernel2/work" "$NRO/other-lane" "$NRH/ee-1116-mmsweep/src"
rec gemmLn3x6x6 fp32 fp32/randn.bin > "$NRL/docs/reports/data/2026-11-01-x-aifoundry3/proc.out"      # w07n's arm, as if a card had run rgm211
rec gemmL2x8x4 fp32 fp32/randn.bin >> "$NRL/docs/reports/data/2026-11-01-x-aifoundry3/proc.out"     # w04m's twin, a card record
rec gemmLn1x5x5 fp32 fp32/randn.bin > "$NRO/kit-e211/work/t/proc.out"                                  # an E211 lane's desk test (left out)
rec gemmLnc2x3x2 fp32 fp32/randn.bin > "$NRO/mm-kernel2/work/plan.out"                                # E211's design lane (left out)
echo "nothing here" > "$NRO/other-lane/notes.txt"
rec gemmLn4x3x6 fp32 fp32/randn.bin > "$NRH/ee-1116-mmsweep/src/session.out"                          # the model session's folder (left out)
step "A: the dry listing"
mkdir -p "$S/listing-A"
( cd "$T" && bash $E/rb/list_steps_e211.sh "$S/listing-A" > "$S/A-A.txt" 2>&1 )
ok "$(grep -c 'dry listing: 15 steps listed, 0 exited non-zero, 0 box calls' "$S/A-A.txt")" "1" "$(tail -n 1 "$S/A-A.txt")"
step "K: step 2 with no window"
r=$(run "$OA" K s03_desk_e211.sh A); ok "$r $( [ -s "$S/calls.log" ] && echo calls || echo nocalls)" "10 nocalls" "$(grep -m1 STOP "$S/K.txt" | cut -c1-120)"
step "W1: a window written for another arm; W2: a window written for another runbook; W3: step 1 for another day; W4: step 1 with the arm B"
r=$(run "$OA" W1a s02_window_e211.sh A "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_ARM=A/RB_ARM=B/' "$OA/window.env"; r1=$(run "$OA" W1 s03_desk_e211.sh A)
rm -f "$OA/window.env"; r=$(run "$OA" W2a s02_window_e211.sh A "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_PLAN=e211/RB_PLAN=e206/' "$OA/window.env"
r2=$(run "$OA" W2 s03_desk_e211.sh A)
r3=$(run "$OA" W3 s02_window_e211.sh A 2026-11-12 10:00 12:00)
rm -f "$OA/window.env"; r4=$(run "$OA" W4 s02_window_e211.sh B "$TODAY" "$STARTHM" "$ENDHM")
r=$(run "$OA" W0 s02_window_e211.sh A "$TODAY" "$STARTHM" "$ENDHM")
ok "$r1 $(has 'not E211' "$S/W1.txt") $r2 $(has 'not E211' "$S/W2.txt") $r3 $r4 $(has "E211's one arm" "$S/W4.txt") $r" "10 1 10 1 10 10 1 0" "$(grep -m1 STOP "$S/W1.txt" | cut -c1-100); $(grep -m1 STOP "$S/W2.txt" | cut -c1-100); $(grep -m1 STOP "$S/W4.txt" | cut -c1-90)"
step "G: step 2 without RB_GITLOCK"
r=$(RB_OUT=$OA RB_DESKTEST=1 bash "$T/$E/rb/s03_desk_e211.sh" A > "$S/G.txt" 2>&1; echo $?); ok "$r" 10 "$(grep -m1 STOP "$S/G.txt" | cut -c1-100)"
step "N: step 2 inside the lab-git lock (nested)"
r=$(RB_OUT=$OA RB_GITLOCK=$GL RB_DESKTEST=1 RB_GITLOCK_T=3 flock -n "$GL" bash "$T/$E/rb/s03_desk_e211.sh" A > "$S/N.txt" 2>&1; echo $?)
ok "$r $(has 'pull(rc 14; a nested lab-git lock exits 75)' "$S/N.txt")" "16 1" "$(stopline "$S/N.txt" | cut -c1-160)"
step "P1: step 2 on the scratch repository"
r=$(run "$OA" P1 s03_desk_e211.sh A)
ok "$r $(has 'desk check: the window written today for E211' "$S/P1.txt")" "0 1" "$(grep -m1 'desk check:' "$S/P1.txt" | cut -c1-300)"
[ "$r" = 0 ] || tail -n 30 "$S/P1.txt"
step "P2: the registration's list one line short; P3: the kit's list one line short; P4: the simulator check's log without its line"
cp "$T/$E/SHA256SUMS-e211-registration" "$S/reg.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e211-registration"
r=$(run "$OA" P2 s03_desk_e211.sh A); cp "$S/reg.bak" "$T/$E/SHA256SUMS-e211-registration"
cp "$T/$E/SHA256SUMS-e211-kit" "$S/kit.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e211-kit"
r3=$(run "$OA" P3 s03_desk_e211.sh A); cp "$S/kit.bak" "$T/$E/SHA256SUMS-e211-kit"
cp "$T/$E/logs/simcheck-e211.txt" "$S/sim.bak"; echo "SIMCHECK-E211 0 of 1 NOT AS STATED" > "$T/$E/logs/simcheck-e211.txt"
r4=$(run "$OA" P4 s03_desk_e211.sh A); cp "$S/sim.bak" "$T/$E/logs/simcheck-e211.txt"
# fix-e211 (Tue 17 Nov 2026): the list one line short reads <its count - 1> OK of <its count - 1>, the count read from the list itself (38 entries
# since Amendment A1 added power-a1-e211.json; this line read a fixed 36, the 37-entry list's, and failed when the list grew)
nreg2=$(( $(grep -c . "$S/reg.bak") - 1 ))
ok "$r $(has "SHA256SUMS-e211-registration($nreg2 OK of $nreg2" "$S/P2.txt") $r3 $(has 'SHA256SUMS-e211-kit(' "$S/P3.txt") $r4 $(has 'simcheck-e211' "$S/P4.txt")" "16 1 16 1 16 1" "$(stopline "$S/P2.txt" | cut -c1-160)"
step "H1: a committed edit of a registration file; H2: a committed shadowing addition (tools/claims-v3/e211/json.py)"
echo "an edit" >> "$T/$E/E211.md"; $G commit -q -am "desk test: an edit of E211.md"
r=$(run "$OA" H1 s03_desk_e211.sh A); $G reset -q --hard "$KIT"
echo "# a shadow" > "$T/$E/json.py"; $G add "$E/json.py"; $G commit -q -m "desk test: a shadow"
r2=$(run "$OA" H2 s03_desk_e211.sh A); /usr/bin/python3 -I -B "$T/$E/rb/check_history_e211.py" tree > "$S/H2b.txt" 2>&1; $G reset -q --hard "$KIT"
ok "$r $(has 'history' "$S/H1.txt") $r2 $(has 'json.py' "$S/H2b.txt")" "16 1 16 1" "$(stopline "$S/H1.txt" | cut -c1-150); $(head -c 150 "$S/H2b.txt")"
step "DA: E211 data committed: step 2 refuses; GS: a gate stop's record committed: step 2 reports it and goes on"
mkdir -p "$T/docs/reports/data/$TODAY-e211-second-kernel-aifoundry3"; echo "stand-in" > "$T/docs/reports/data/$TODAY-e211-second-kernel-aifoundry3/README.md"
$G add --sparse -f "docs/reports/data/$TODAY-e211-second-kernel-aifoundry3/README.md"; $G commit -q -m "desk test: E211 data (stand-in)"
r=$(run "$OA" DA s03_desk_e211.sh A); $G reset -q --hard "$KIT"
mkdir -p "$T/docs/reports/gate-stops/$TODAY-e211-second-kernel-T1-aifoundry3"; echo "stand-in" > "$T/docs/reports/gate-stops/$TODAY-e211-second-kernel-T1-aifoundry3/README.md"
$G add --sparse -f "docs/reports/gate-stops/$TODAY-e211-second-kernel-T1-aifoundry3/README.md"; $G commit -q -m "desk test: an E211 gate stop's record (stand-in)"
rg=$(run "$OA" GS s03_desk_e211.sh A); $G reset -q --hard "$KIT"
ok "$r $(has 'E211-has-data(1 commit(s))' "$S/DA.txt") $rg $(has 'gate-stop commits (reported): 1' "$S/GS.txt")" "16 1 0 1" "$(stopline "$S/DA.txt" | cut -c1-140); $(grep -m1 'gate-stop commits' "$S/GS.txt" | sed 's/.*E211 data commits/E211 data commits/' | cut -c1-120)"
step "E7: no E207 data folder at HEAD (fix-e211, A1 clause 4): step 2 refuses (16) with E207-data alone in its failure list; with it: 0"
for d7 in $(git -C "$T" ls-tree -d --name-only HEAD docs/reports/data/ | grep '^docs/reports/data/[^/]*e207'); do $G rm -r -q --sparse --cached -- "$d7"; done
$G commit -q -m "desk test: no E207 data folder at HEAD"
r=$(run "$OA" E7 s03_desk_e211.sh A); $G reset -q --hard "$KIT"
n7=$(git -C "$T" ls-tree -d --name-only HEAD docs/reports/data/ | grep -c '^docs/reports/data/[^/]*e207')
ok "$r $(has 'the desk check failed: E207-data(no docs/reports/data/' "$S/E7.txt") $(has 'E207 data folders at HEAD: [1-9]' "$S/P1.txt") $( [ "$n7" -gt 0 ] && echo restored)" "16 1 1 restored" "$(stopline "$S/E7.txt" | cut -c1-200); P1: $(grep -o 'E207 data folders at HEAD: [0-9]*' "$S/P1.txt" | head -n 1)"
step "O: the look on the stand-in box (k6's s05)"
r3=$(RB_OUT=$OA bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry3 > "$S/O3.txt" 2>&1; echo $?)
ok "$r3 $( [ -s "$OA/box-login-aifoundry3.txt" ] && echo login)" "0 login" "aifoundry3: $(grep -m1 'FREE\|HELD' "$S/O3.txt" | cut -c1-80)"
step "OL: E211's ours_live counts a session_e211.sh by its own script, never by a command string"
mkdir -p "$S/ol"; printf '#!/bin/bash\nsleep 25\n' > "$S/ol/session_e211.sh"
( . "$T/$E/rb/rb_e211.sh" > /dev/null 2>&1; e211_live_text ) > "$S/ol/live.sh"
printf '. "%s"\necho "$(ours_live session_e211.sh) $(ours_live)"\n' "$S/ol/live.sh" > "$S/ol/count.sh"
printf '#!/bin/bash\nsleep 25\n: tools/claims-v3/e211/session_e211.sh\n' > "$S/ol/decoy.sh"
n0=$(bash "$S/ol/count.sh")
setsid bash "$S/ol/decoy.sh" session_e211.sh < /dev/null > /dev/null 2>&1 &
p1=$!
n1=$(sleep 1; bash "$S/ol/count.sh")
setsid bash "$S/ol/session_e211.sh" < /dev/null > /dev/null 2>&1 &
p2=$!
n2=$(sleep 1; bash "$S/ol/count.sh")
kill "$p1" "$p2" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do [ "$(bash "$S/ol/count.sh")" = "0 0" ] && break; sleep 0.5; done
n3=$(bash "$S/ol/count.sh")
ok "$n0|$n1|$n2|$n3" "0 0|0 0|1 1|0 0" "before: $n0; a script whose arguments and text name session_e211.sh: $n1; a session_e211.sh run as a script: $n2; after it ended: $n3"
step "SY: step 5 on the stand-in box"
ra=$(run "$OA" SYA s07_sync_e211.sh A)
ok "$ra $(has 'HARNESS OK on the box' "$S/SYA.txt")" "0 1" "$(grep -m1 'synced to' "$S/SYA.txt" | cut -c1-140)"
step "L1: a login link on a read (step 5's first read); L2: a read that hangs (the read class's bound 3 s for this call)"
touch "$S/ssh-login"; n0=$(grep -c . "$RB_LOCK" 2>/dev/null || echo 0)
r=$(run "$OA" L1 s07_sync_e211.sh A); n1=$(grep -c 'aifoundry3 needs a check' "$RB_LOCK" 2>/dev/null || echo 0)
touch "$S/ssh-hang"
r2=$(RB_READ_S=3 RB_OUT=$OA RB_DESKTEST=1 bash "$T/$E/rb/s07_sync_e211.sh" A > "$S/L2.txt" 2>&1; echo $?); rm -f "$S/ssh-hang"
ok "$r $((n1 - n0)) $r2" "11 1 13" "$(stopline "$S/L1.txt" | cut -c1-120); $(stopline "$S/L2.txt" | cut -c1-100)"
step "T: NO-THIRD-BUILD on aifoundry3"
mkdir -p "$A3/build"; for k in 1 2; do echo "$TODAY 01:0$k:00 PST a3-build-e211 started" >> "$A3/build/e211-build-attempts.txt"; done
r=$(run "$OA" T s08_build_e211.sh A start); rm -f "$A3/build/e211-build-attempts.txt"
ok "$r $(has NO-THIRD-BUILD "$S/T.txt")" "16 1" "$(stopline "$S/T.txt" | cut -c1-140)"
step "BA: step 6 on aifoundry3: the real build"
r=$(run "$OA" BA1 s08_build_e211.sh A start); r2=$(waitjob "$OA" BA2 s08_build_e211.sh A wait)
ok "$r $r2 $(has 'KERNEL OK: ' "$S/BA2.txt")$(cat "$OA/e211-built-A.txt" 2>/dev/null)" "0 0 1rgm" "$(grep -m1 'built today on' "$S/BA2.txt" | cut -c1-160)"
[ "$r2" = 0 ] || tail -n 25 "$S/BA2.txt"
step "NR: step 6n, the never-run search repeated, on stand-in roots: rgm211 found in the lab's data and in another kit's box folder; the left-out folders; a simulator record apart"
mkdir -p "$A3/build/e999/T5" "$A3/build/e211/T1-A-dry/runs/004-X-x01n" "$B/aifoundry3/claude/work/q204-kit-e211/runs/sim-W" "$B/aifoundry3/claude/work/ee-x"
rec gemmLn6x6x6 fp32 fp32/randn.bin > "$A3/build/e999/T5/proc.out"                                          # another kit's folder on the box: found
rec gemmLn1x5x5 fp32 fp32/randn.bin > "$A3/build/e211/T1-A-dry/runs/004-X-x01n/proc-00.out"                  # E211's own dry pass: left out
rec gemmLn2x2x1 fp32 fp32/randn.bin 0.0000 > "$B/aifoundry3/claude/work/q204-kit-e211/runs/sim-W/out.json"   # the simulator check: apart
rec gemmLn3x1x8 fp32 fp32/randn.bin > "$B/aifoundry3/claude/work/ee-x/proc.out"                              # the model session's: left out
cp "$T/$E/desk/neverrun-e211.json" "$S/reg-neverrun.bak"
r=$(run "$OA" NR1 s06n_neverrun_e211.sh A); r2=$(run "$OA" NR2 s06n_neverrun_e211.sh A --desk-only)
rm -rf "${A3:?}/build/e999" "${A3:?}/build/e211/T1-A-dry" "${B:?}/aifoundry3/claude"
nrd=$(cat "$OA/e211-neverrun-dir.txt" 2>/dev/null)
ok "$r $(has 'NEVER-RUN-E211 rgm211 on a card before E211: gemmLn3x6x6|fp32|random|1024|0xffffffff, gemmLn6x6x6|fp32|random|1024|0xffffffff; gemmLn/gemmLnc configurations found 3 (simulator records 1); twins with a card record: 1 of 13; aifoundry3 searched$' "$S/NR1.txt") $r2 $(has 'NEVER-RUN-E211 rgm211 on a card before E211: gemmLn3x6x6|fp32|random|1024|0xffffffff; gemmLn/gemmLnc configurations found 1 (simulator records 0); twins with a card record: 1 of 13; aifoundry3 NOT SEARCHED$' "$S/NR2.txt") $( [ -s "$OA/e211-neverrun.txt" ] && [ -s "$nrd/neverrun-e211-card.json" ] && echo report) $(cmp -s "$T/$E/desk/neverrun-e211.json" "$S/reg-neverrun.bak" && echo kept)" \
   "0 1 0 1 report kept" "$(grep -m1 'NEVER-RUN' "$S/NR1.txt" | cut -c1-200); desk-only: $(grep -m1 'NEVER-RUN' "$S/NR2.txt" | cut -c1-160)"
step "R7: STEP 7 needs a fresh never-run report and the rest: (a) no report: 10, no config read; (b) a report 31 minutes old: 10; (c) the rest not run (a session ended 10 minutes ago): 10; (d) both: 0, the reader called once"
O5=$S/out5; mkdir -p "$O5"; cp "$OA/window.env" "$O5/"; touch "$O5/window.env"
c0=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
ra=$(run "$O5" R7a s09_reads_e211.sh A)
cp "$OA/e211-neverrun.txt" "$O5/"; touch -d '-31 min' "$O5/e211-neverrun.txt"
rb=$(run "$O5" R7b s09_reads_e211.sh A)
mkdir -p "$A3/build/e185/T1"
{ echo "$(date -d '-14 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-10 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-10 min' "$A3/build/e185/T1/session.log"
rc_=$(run "$OA" R7c s09_reads_e211.sh A); c1=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
{ echo "$(date -d '-50 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-45 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-45 min' "$A3/build/e185/T1/session.log"
rd=$(run "$OA" R7d s09_reads_e211.sh A); c2=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
ok "$ra $(has 'no never-run report' "$S/R7a.txt") $rb $(has 'minutes old (more than 30)' "$S/R7b.txt") $rc_ $(has 'the rest has not run' "$S/R7c.txt") $((c1 - c0)) $rd $((c2 - c1)) $(has 'config TDP 0 W / 65 C / 600 MHz, et-who clean' "$S/R7d.txt")" \
   "10 1 10 1 10 1 0 0 1 1" "no report: $(stopline "$S/R7a.txt" | cut -c1-90); 31 min: $(stopline "$S/R7b.txt" | cut -c1-90); 10 min after a session: $(stopline "$S/R7c.txt" | cut -c1-90) (reader calls $((c1 - c0))); then: $(grep -m1 'aifoundry3:' "$S/R7d.txt" | cut -c1-90)"
step "D: step 8 on the stand-in box"
ra=$(run "$OA" DA1 s10_dry_e211.sh A start); ra2=$(waitjob "$OA" DA2 s10_dry_e211.sh A wait)
ok "$ra $ra2" "0 0" "$(grep -m1 'E211-DRY' "$S/DA2.txt")"
step "HG: a HUNG marker in a session log of ours on aifoundry3: step 9 refuses"
mkdir -p "$A3/build/e204/T1794800000"
printf '%s session start (T0 1794800000; desk test)\n%s HUNG: a device process did not end after its timeout TERM (desk test)\n%s session end (T0 1794800000)\n' \
  "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" > "$A3/build/e204/T1794800000/session.log"
touch -d '-3 hours' "$A3/build/e204/T1794800000/session.log"
r=$(run "$OA" HG s11_session_e211.sh A); rm -rf "${A3:?}/build/e204"
ok "$r $(has 'REFUSED: a HUNG marker of ours on the box' "$S/HG.txt") $(ls "$A3/build/e211" 2>/dev/null | grep -c '^T[0-9]*-A$')" "10 1 0" "$(grep -m1 'REFUSED' "$S/HG.txt" | cut -c1-140)"
step "SD: the same-day rule: an E211 session that opened the card earlier today"
mkdir -p "$A3/build/e211/T1700000000-A"
printf '%s session start (T0 1700000000; desk test)\n%s the first card command: the start config read through the guard\n%s session end (T0 1700000000)\n' \
  "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-45 min' '+%F %T %Z')" > "$A3/build/e211/T1700000000-A/session.log"
# the same-day rule reads the log's last write by its Pacific date, the rest rule its "session end" line: the write is dated inside today (45
# minutes ago, or 00:00:01 today when that was yesterday), so the case holds at every hour of the day (verify-e207's finding 5, fix-e207's form)
if [ "$(TZ=America/Los_Angeles date -d '-45 min' +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then touch -d '-45 min' "$A3/build/e211/T1700000000-A/session.log"
else TZ=America/Los_Angeles touch -d "$(TZ=America/Los_Angeles date +%F) 00:00:01" "$A3/build/e211/T1700000000-A/session.log"; fi
r=$(run "$OA" SD s11_session_e211.sh A); rm -rf "${A3:?}/build/e211/T1700000000-A"
ok "$r $(has 'REFUSED: the same-day rule' "$S/SD.txt")" "10 1" "$(grep -m1 'REFUSED' "$S/SD.txt" | cut -c1-140)"
step "LS: THE LAST START passed (the window's last end still far): step 9 refuses (16) before anything is sent"
O6=$S/out6; mkdir -p "$O6"; cp "$OA/window.env" "$OA/e211-built-A.txt" "$O6/"
sedi -e "s/^RB_LAST_START_EPOCH=.*/RB_LAST_START_EPOCH=$(( $(date +%s) - 60 ))/" "$O6/window.env"; touch "$O6/window.env" "$O6/e211-built-A.txt"
n0=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
r=$(run "$O6" LS s11_session_e211.sh A); n1=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
ok "$r $(has "past the round's last start" "$S/LS.txt") $((n1 - n0))" "16 1 0" "$(stopline "$S/LS.txt" | cut -c1-140); box calls $((n1 - n0))"
step "NS: no never-run report from today in RB_OUT: step 9 refuses (10) before anything is sent"
O7=$S/out7; mkdir -p "$O7"; cp "$OA/window.env" "$OA/e211-built-A.txt" "$O7/"; touch "$O7/window.env" "$O7/e211-built-A.txt"
n0=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
r=$(run "$O7" NS s11_session_e211.sh A); n1=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
ok "$r $(has 'no never-run report from today' "$S/NS.txt") $((n1 - n0))" "10 1 0" "$(stopline "$S/NS.txt" | cut -c1-140); box calls $((n1 - n0))"
step "LA: step 9 launches the REAL session_e211.sh, which stops at its box check (the desk's own hostname); step 10 reads the gate"
r=$(run "$OA" LA s11_session_e211.sh A); r2=$(waitjob "$OA" LA2 s20_wait_e211.sh A)
t0=$(cat "$OA/e211-T0-A.txt" 2>/dev/null)
sd=$A3/build/e211/T$t0-A
procs=$(find "$sd" -name 'proc*.out' 2>/dev/null | wc -l | tr -d ' ')
ok "$r $r2 $(has 'refused, no device opened: the box or the build is not the registered one (this host is' "$sd/session.log") $(has '"rc": 16' "$sd/queue.json") $( [ -s "$sd/MANIFEST.sha256" ] && echo manifest) $procs $(has 'GATE-STOPPED e211 arm A' "$S/LA2.txt")" \
   "0 16 1 1 manifest 0 1" "$(grep -m1 'no device opened' "$sd/session.log" | cut -c1-200)"
step "W10: step 10's readings on stand-in logs (a running session, none, HUNG, K1, CRASH, an ended session with a STOP line)"
O3=$S/out3; mkdir -p "$O3"; cp "$OA/window.env" "$OA/box-login-aifoundry3.txt" "$O3/"; touch "$O3/window.env"; echo 7 > "$O3/e211-T0-A.txt"
mkdir -p "$A3/build/q141k"; echo 7 > "$A3/build/q141k/e211A.T0"; W7=$A3/build/e211/T7-A; mkdir -p "$W7"
mkdir -p "$S/wv"; printf '#!/bin/bash\nsleep 30\n' > "$S/wv/session_e211.sh"
wr() { RB_OUT=$O3 RB_DESKTEST=1 RB_WAIT_LOOP_S=4 bash "$T/$E/rb/s20_wait_e211.sh" A > "$S/W10-$1.txt" 2>&1; echo $?; }
echo "$(date '+%F %T %Z') session start (T0 7; desk-test stand-in, no end)" > "$W7/session.log"
setsid bash "$S/wv/session_e211.sh" < /dev/null > /dev/null 2>&1 &
p3=$!
sleep 1
rv=$(wr V)
kill "$p3" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$p3" 2>/dev/null || break; sleep 0.5; done
rg=$(wr G)
printf '%s session start (T0 7; desk test)\n%s HUNG: a device process (the host of 004-X-x01n (proc-00); its `timeout` pid 9) still runs\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"
rh=$(wr H)
printf '%s session start (T0 7; desk test)\n%s STOP: K1: a launch of run 004-X-x01n did not finish (the host'"'"'s words): it may leave a hung hart: nothing further started\n%s session end (T0 7)\n' \
  "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo "x  session.log" > "$W7/MANIFEST.sha256"; echo 0 > "$W7/runner.rc"
rk=$(wr K)
printf '%s session start (T0 7; desk test)\n%s CRASH: KeyError: b99\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 1 > "$W7/runner.rc"
rc_=$(wr C)
printf '%s session start (T0 7; desk test)\n%s STOP: board 71.2 W above 70 W on 3 samples in a row: nothing further started\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 0 > "$W7/runner.rc"
re=$(wr E)
rm -rf "${A3:?}/build/e211/T7-A"; echo "$t0" > "$A3/build/q141k/e211A.T0"
ok "$rv $rg $rh $rk $rc_ $re $(has 'RUN-RUNNING' "$S/W10-V.txt")$(has 'RUN-GONE' "$S/W10-G.txt")$(has 'KILL NOTHING' "$S/W10-H.txt")$(has 'K1' "$S/W10-K.txt")$(has 'crashed' "$S/W10-C.txt")$(has 'read its STOP line' "$S/W10-E.txt")" \
   "17 14 16 16 16 0 111111" "running $rv, gone $rg, HUNG $rh, K1 $rk, CRASH $rc_, ended with a STOP line $re"
step "C: step 11 on LA's session, step 12 (the gate stop's record), step 13 refuses it; C2: a byte changed after the manifest"
r=$(run "$OA" C1 s22_collect_e211.sh A); r2=$(run "$OA" C2s s23_data_e211.sh A); r3=$(run "$OA" C3s s24_score_e211.sh A)
gs=$(cat "$OA/e211-data-dir-A.txt" 2>/dev/null)
ok "$r $r2 $(has 'COLLECTED-GATE-STOP docs/reports/gate-stops/' "$S/C2s.txt") $(grep -rl '/home/' "$T/$gs" 2>/dev/null | wc -l | tr -d ' ') $r3" "0 0 1 0 10" \
   "$(grep -m1 'COLLECTED' "$S/C2s.txt" | cut -c1-140); step 13: $(stopline "$S/C3s.txt" | cut -c1-100)"
O2=$S/out2; mkdir -p "$O2"; cp "$OA"/window.env "$OA"/e211-T0-A.txt "$OA"/box-login-aifoundry3.txt "$O2/"; touch "$O2/window.env"
echo "x" >> "$sd/session.log"
r=$(RB_OUT=$O2 RB_DESKTEST=1 bash "$T/$E/rb/s22_collect_e211.sh" A > "$S/C2.txt" 2>&1; echo $?)
ok "$r $(has 'COPY-BACK NOT EXACT' "$S/C2.txt")" "16 1" "$(stopline "$S/C2.txt" | cut -c1-140)"
step "CD: a session that ran (step 8's dry session copied as a session): steps 11, 12 and, after a stand-in data commit, 13 (the FROZEN scorer)"
dd=$(ls -d "$A3"/build/e211/T*-A-dry 2>/dev/null | tail -n 1)
O4=$S/out4; mkdir -p "$O4"; cp "$OA"/window.env "$OA"/box-login-aifoundry3.txt "$OA"/e211-neverrun-dir.txt "$O4/"; touch "$O4/window.env"; echo 8 > "$O4/e211-T0-A.txt"
cp -a "$dd" "$A3/build/e211/T8-A"; rm -f "${A3:?}/build/e211/T8-A/dry.lock"     # a dry session keeps its lock file beside its manifest
r=$(run "$O4" CD1 s22_collect_e211.sh A); rm -rf "${T:?}/docs/reports/data/$TODAY-e211-second-kernel-aifoundry3"; r2=$(run "$O4" CD2 s23_data_e211.sh A)
dd2=$(cat "$O4/e211-data-dir-A.txt" 2>/dev/null)
$G add --sparse -f "$dd2" > /dev/null 2>&1; $G commit -q -m "desk test: a data commit (stand-in)" > /dev/null 2>&1
r3=$(run "$O4" CD3 s24_score_e211.sh A)
ok "$r $r2 $(has "COLLECTED docs/reports/data/$TODAY-e211-second-kernel-aifoundry3" "$S/CD2.txt") $( [ -s "$T/$dd2/data-e211.json" ] && echo data) $(grep -c '  neverrun-e211-card\.\(txt\|json\)$' "$T/$dd2/SHA256SUMS" 2>/dev/null) $r3 $( [ -s "$O4/scores-e211-A.json" ] && echo scored)" \
   "0 0 1 data 2 0 scored" "$(grep -m1 'COLLECTED' "$S/CD2.txt" | cut -c1-140); $(grep -m1 'scored arm A' "$S/CD3.txt" | cut -c1-120); R0 in the scorer's words: $(grep -m1 '^R0 ' "$O4/scores-e211-A.txt" 2>/dev/null | cut -c1-60)"
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
echo "SELFTEST-RB-E211 $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
}
main
