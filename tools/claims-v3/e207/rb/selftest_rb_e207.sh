#!/usr/bin/env bash
# E207 (Q199, lane kit-e207, Mon 16 Nov 2026, before any E207 datum): the desk test of E207's runbook with a FAKE ssh and rsync on a stand-in
# aifoundry3, E206's rb/selftest_rb_e206.sh form (landed in 906699ea) for E207's one box. Its scratch repository is a shared, sparse clone of the
# lab clone this test runs from (its HEAD holds E207's registration as a commit, as on the card day) with the kit's files committed on top as one
# stand-in kit commit, the kit's list a stand-in made here and pinned in the scratch copy of step 2's KITPIN line (the one line this test changes
# in a copy), and stand-in desk-test logs (this test's own log is not final while it runs). The stand-in box is aifoundry3's ~/aifoundry, an
# rsync target under the scratch; the stand-in ssh serves it with `bash -s` (and `true`) and refuses any other host or command; the stand-in
# rsync rewrites its paths; the box's hostname, uptime, et-who, et-lab-manifest and pgrep are stand-ins, and the box tree holds a stand-in reader
# at build/ettelem/ettelem (the doubles' config and sampler) and E128's guard (k6's step 7 runs it there); cmake, the compilers and /opt/et are
# this desk's REAL ones (the build is the real build_e207.sh with THE KERNEL GATE). Step 6n reads stand-in roots (a lab, the round's lane
# folders, HOME/claude/work and E208's arms) through E207_NR_* (RB_DESKTEST=1 only). No lab box is reached.
# When the lab clone's history holds the kit commit (the commit that added KIT.md: the readiness lane), the scratch repository is built at that
# commit's PARENT and the kit's files are taken from HEAD, its main following a local branch at that parent (so step 2's pull is up to date);
# otherwise (the kit lane) the untracked files and the lab clone's HEAD. Cases:
#   A   the dry listing: every step exits 0, no call reaches the stand-ins
#   K   step 2 with no window: 10       W1 a window written for another arm: 10      W2 a window written for another runbook: 10
#   W3  step 1 for another day: 10      W4 step 1 with the arm B: 10                G  step 2 without RB_GITLOCK: 10
#   N   step 2 inside the lab-git lock (nested): 16 naming the pull
#   P1  step 2 on the scratch repository: 0 (the lists at their pins, HISTORY OK, the registration and the kit found by content, the
#       registration's checks, the scorer's forecasts and self-tests byte-identical, the preflight GO, the desk tests' logs)
#   P2  the registration's list one line short: 16      P3 the kit's list one line short: 16      P4 MM1-v1's folder list one line short: 16
#   H1  a committed edit of a registration file: 16 by the history check      H2 a committed tools/claims-v3/e207/json.py (a shadow): 16
#   DA  E207 data committed: step 2 refuses (16)      GS an E207 gate stop's record committed: step 2 reports it and goes on (0)
#   O   the look on the stand-in box (k6's s05, unchanged): FREE, our login recorded for the scrub
#   OL  E207's ours_live: a shell whose command string names session_e207.sh is not a session; a session_e207.sh run as a script is
#   SY  step 5: the rsync, HARNESS OK on the box     L1 a login link on a read: 11, "<HH:MM:SS> aifoundry3 needs a check" appended to RB_LOCK,
#       nothing retried      L2 a read that hangs (the read class's bound 3 s for this call): 13
#   T   NO-THIRD-BUILD: two starts recorded on aifoundry3 today: a third start is refused with 16
#   BA  step 6: start, wait (17 while it builds, then 0): the REAL build, KERNEL OK, the record, the harness, the preflight GO and both
#       self-checks read on the box; RB_OUT/e207-built-A.txt
#   NR  STEP 6n, THE NEVER-RUN SEARCH REPEATED, on stand-in roots (fix-e207, E207.md A1 items 1-3): b10 in a lab data directory dated
#       before the freeze is RAN BEFORE; n02 in a box run folder with no session start in its path is TO DATE; b27 in a card lane's session
#       started after the freeze (its T0 in its path) is AFTER THE FREEZE (REPORTED, kept); b02 in another experiment's desk lane (kit-e209,
#       verify-e207's finding 1) is DESK-ONLY (dismissed); b30 in the model session's folder (HOME/claude/work/ee-*) is never read; b01 in an
#       E207 lane's desk test and n01 in E207's own dry pass on the box are subtracted; the --desk-only form says "aifoundry3 NOT SEARCHED"
#       and drops n02; step 6n's dating file is written; the registration's committed report is never overwritten
#   R7  STEP 7 ONLY WITH A FRESH NEVER-RUN REPORT AND ONLY ONCE THE REST HAS OPENED: no report: 10; a report 31 minutes old: 10; a session of ours
#       ended 10 minutes ago: 10; in none of the three is the stand-in reader called (no config read sent); then 0, the reader called once
#   D   step 8 on the stand-in box (the doubles there): 0
#   HG  THE HUNG MARKER: a session log of ours on aifoundry3 with a HUNG line: step 9 refuses (10), nothing launched
#   SD  THE SAME-DAY RULE: an E207 session that opened the card earlier today: step 9 refuses (10)
#   LS  THE LAST START passed with the last end still far: step 9 refuses (16) and sends nothing to the box
#   NS  no never-run report from today in RB_OUT (step 6n): step 9 refuses (10) and sends nothing to the box
#   LA  step 9 launches the REAL session_e207.sh and run_e207.py on the stand-in aifoundry3, which stop at their box check before any device
#       (the desk's own hostname): "refused, no device opened"; step 10 reads GATE-STOPPED (16) with the manifest written
#   W10 step 10's readings on stand-in logs: a running session_e207.sh with no end 17 (RUN-RUNNING); none running 14 (RUN-GONE); a HUNG line
#       16 (HUNG); a K1 stop 16 (K1-STOPPED); a CRASH line 16 (CRASHED); an ended session (rc 0) with a STOP line 0
#   C   step 11 on LA's session: COPY-BACK EXACT 0; step 12: the gate stop's record under docs/reports/gate-stops/ (COLLECTED-GATE-STOP), the
#       desk-path gate, HISTORY OK: 0; step 13 refuses a gate stop's record: 10      C2 one byte of a box file changed after the manifest:
#       COPY-BACK NOT EXACT 16
#   CD  a session that ran (step 8's dry session copied as a session): step 11 0, step 12 the data directory with data-e207.json (the reducer),
#       step 6n's report (neverrun-e207-card.txt and .json, in SHA256SUMS) and the scrub clean: 0; after a stand-in data commit, step 13 runs
#       the FROZEN scorer on it: 0; and (fix-e207, A1 item 3) step 6n's dating file in the data directory (ranbefore-e207-card.json, in
#       SHA256SUMS) and the after-score tool's registered verdicts in RB_OUT (postscore-e207-A.json, its labels from that file)
#   Z   no process of this test left running
#   bash tools/claims-v3/e207/rb/selftest_rb_e207.sh <scratch dir> > logs/selftest-rb-e207.txt   (prints SELFTEST-RB-E207 <n> of <m> PASS or FAIL)
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
for c in timeout sha256sum flock cmake c++ rsync git; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
REAL_RSYNC=$(command -v rsync)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree box bin boxbin out; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; B=$S/box; BIN=$S/bin; BB=$S/boxbin
A3=$B/aifoundry3/aifoundry
E=tools/claims-v3/e207
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
G="git -C $T -c user.name=e207-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /workloads/ledger/ /docs/reports/data/2026-11-02-e136-large-gemm/ /docs/reports/data/2026-11-01-e119-gemm-speed/ \
  /docs/reports/data/2026-11-02-e126-gemm-arms/ /docs/reports/data/2026-11-02-e146-gemm-stores/ /docs/reports/data/2026-11-12-q166-ledger-v2/ \
  /docs/reports/data/2026-11-01-e107-gemm-placement/ /docs/reports/data/2026-11-01-e95-real-tensors-energy/ /docs/reports/data/2026-09-23-energy-manual/ \
  /docs/reports/data/2026-11-13-e190-large-gemm/ /docs/reports/data/2026-11-01-e105-gemm-layout/ /docs/reports/data/2026-10-26-load-model/ \
  /docs/reports/data/2026-11-12-q166-counter-sparseparity/ /docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/ || return 2
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
  { $G branch -q -f e207-desktest-base "$BASE" && $G branch -q --set-upstream-to=e207-desktest-base main; } || { echo "the scratch's upstream could not be set"; return 2; }
else
  $G branch -q --set-upstream-to=origin/main 2>/dev/null
fi
$G log --diff-filter=A --format=%H -- $E/E207.md | grep -q . || { echo "the registration is not in the scratch repository's history"; return 2; }
if [ -n "$KITC" ]; then      # the paths the kit commit added, at HEAD's bytes (the history check keeps them as first committed)
  git -C "$SRC" diff-tree --no-commit-id --name-only -r --diff-filter=A "$KITC" -- $E | while IFS= read -r f; do
    mkdir -p "$T/$(dirname "$f")"; git -C "$SRC" show "HEAD:$f" > "$T/$f" || exit 2; done || { echo "the kit's files could not be taken from HEAD"; return 2; }
else
  ( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E ) | sort -u | while IFS= read -r f; do
    [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
fi
mkdir -p "$T/$E/logs"
for spec in "selftest-run-e207.txt SELFTEST-RUN-E207 0 of 0 PASS" "realpath-e207.txt REALPATH-E207 0 of 0 PASS" "realbytes-e207.txt REALBYTES-E207 0 of 0 PASS" \
            "desktest-build-e207.txt DESKTEST-BUILD-E207 0 of 0 PASS" "selftest-rb-e207.txt SELFTEST-RB-E207 0 of 0 PASS" \
            "dry-listing-e207.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e207.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"
done
( cd "$T" && /usr/bin/python3 -I -B $E/check_e207.py --make > /dev/null )
mklist() {  # the kit's stand-in list: every file this stand-in commit adds under E207's folder, but the list itself and step 2
  ( cd "$T" && git ls-files --others --exclude-standard -- $E | grep -v -x -e "$E/SHA256SUMS-e207-kit" -e "$E/rb/s03_desk_e207.sh" |
      LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/kit-standin.txt"
  KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e207-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^KITPIN=$E/SHA256SUMS-e207-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e207-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e207.sh"
  grep -q "^KITPIN=$E/SHA256SUMS-e207-kit:$KITN:$KITH:top" "$T/$E/rb/s03_desk_e207.sh"
}
mklist || { echo "the scratch step 2's KITPIN was not set"; return 2; }
$G add -A $E && $G commit -q -m "E207 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; return 2; }
KIT=$($G rev-parse HEAD)
echo "scratch repository: a shared sparse clone of the lab clone ($FORM; the registration in it), the kit as one stand-in commit ${KIT:0:12}; the kit's stand-in list $KITN files"
[ "$KITN" -gt 0 ] || { echo "the kit's stand-in list is empty"; return 2; }
# ---- the stand-ins
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; cat > /dev/null; echo "To authenticate, visit: https://login.tailscale.com/a/e207desktest" >&2; sleep 30; exit 1; fi
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
exec env E207_FAKE_ARM=$arm E207_FAKE_CONFIG=\$mode /usr/bin/python3 -B "$T/$E/fake_card_e207.py" "\$@"
EOF
  chmod +x "$bt/build/ettelem/ettelem"
done
cp -p "$SRC/tools/claims-v3/e128/ettelem_guard.sh" "$A3/tools/claims-v3/e128/ettelem_guard.sh"
export PATH="$BIN:$PATH" RB_LOCK="$S/rb-lock.txt"
GL=$S/lab-git.lock; : > "$GL"
TODAY=$(TZ=America/Los_Angeles date +%F)
STARTHM=23:58; ENDHM=23:59           # the window is today's last minutes: the steps' budgets are E207_DESK_BUDGET_S (60 s) here
OA=$S/outA; mkdir -p "$OA"
run() {  # run <arm's RB_OUT> <log> <script> [args]: a step of the scratch repository's runbook
  local o=$1 lg=$2; shift 2
  RB_OUT=$o RB_GITLOCK=$GL RB_DESKTEST=1 E207_DESK_BUDGET_S=60 E207_ROUND_OUT="$NRO" E207_NR_LAB="$NRL" E207_NR_OUT="$NRO" E207_NR_HOMEW="$NRH" \
    E207_NR_ARMS="$NRH/ee-1116-mmsweep/src/arms.json" bash "$T/$E/rb/$1" "${@:2}" > "$S/$lg.txt" 2>&1
  echo $?
}
waitjob() {  # waitjob <RB_OUT> <tag> <script> <args...>: call a wait step until it says something other than 17 (at most 40 calls)
  local o=$1 tag=$2 r k; shift 2
  for k in $(seq 1 40); do r=$(run "$o" "$tag-$k" "$@"); [ "$r" = 17 ] || { cp "$S/$tag-$k.txt" "$S/$tag.txt"; echo "$r"; return; }; done; echo 17
}
# ---- the never-run step's stand-in roots (a lab, the round's lane folders, HOME/claude/work), read through E207_NR_* (RB_DESKTEST=1 only)
NRL=$S/nr/lab; NRO=$S/nr/out; NRH=$S/nr/homew
rec() {  # rec <arm> <type> <tile> : one SPARSITY record line of the lab's host, full chip, randn data
  printf 'SPARSITY {"test":"fma","arm":"%s","gen":"randn","type":"%s","pattern":"none","values":"%s:randn:tools/claims-v3/kinds/tiles/%s","b_stream":0,"minions":1024,"shire_mask":"0xffffffff","iters":1,"passes":1,"launch":0,"cycles_max":1,"ghz":0.6,"ok":true}\n' "$1" "$2" "$1" "$3"
}
mkdir -p "$NRL/docs/reports/data/2026-11-01-x-aifoundry3" "$NRO/kit-e207/work/t" "$NRO/other-lane" "$NRH/ee-1116-mmsweep/src"
rec gemmL1x9x3 fp32 fp32/randn.bin > "$NRL/docs/reports/data/2026-11-01-x-aifoundry3/proc.out"       # b10's point, as if a card had run it
rec gemmL1x3x2 fp32 fp32/randn.bin > "$NRO/kit-e207/work/t/proc.out"                                   # b01's, in an E207 lane's desk test (subtracted)
echo "nothing here" > "$NRO/other-lane/notes.txt"
mkdir -p "$NRO/kit-e209/work/t" "$NRO/card-e209/rb/T1794950000-A/runs/001" "$NRH/ee-1116-mmsweep/sessions/1794900663-a2c0-S1"   # fix-e207 (A1)
rec gemmL1x3x2 int8 int8/full.bin > "$NRO/kit-e209/work/t/proc.out"                                     # b02's, another experiment's desk double (dismissed)
rec gemmL1x7x6 fp32 fp32/randn.bin > "$NRO/card-e209/rb/T1794950000-A/runs/001/proc-00.out"             # b27's, a session after the freeze (kept)
rec gemmL1x4x12 fp32 fp32/randn.bin > "$NRH/ee-1116-mmsweep/sessions/1794900663-a2c0-S1/proc.out"       # b30's, the model session's folder (never read)
printf '{"arms": [{"mb": 1, "nb": 1, "kb": 1, "type": "fp32", "kind": "rnd", "shires": "0x1"}]}\n' > "$NRH/ee-1116-mmsweep/src/arms.json"
step "A: the dry listing"
mkdir -p "$S/listing-A"
( cd "$T" && bash $E/rb/list_steps_e207.sh "$S/listing-A" > "$S/A-A.txt" 2>&1 )
ok "$(grep -c 'dry listing: 15 steps listed, 0 exited non-zero, 0 box calls' "$S/A-A.txt")" "1" "$(tail -n 1 "$S/A-A.txt")"
step "K: step 2 with no window"
r=$(run "$OA" K s03_desk_e207.sh A); ok "$r $( [ -s "$S/calls.log" ] && echo calls || echo nocalls)" "10 nocalls" "$(grep -m1 STOP "$S/K.txt" | cut -c1-120)"
step "W1: a window written for another arm; W2: a window written for another runbook; W3: step 1 for another day; W4: step 1 with the arm B"
r=$(run "$OA" W1a s02_window_e207.sh A "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_ARM=A/RB_ARM=B/' "$OA/window.env"; r1=$(run "$OA" W1 s03_desk_e207.sh A)
rm -f "$OA/window.env"; r=$(run "$OA" W2a s02_window_e207.sh A "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_PLAN=e207/RB_PLAN=e206/' "$OA/window.env"
r2=$(run "$OA" W2 s03_desk_e207.sh A)
r3=$(run "$OA" W3 s02_window_e207.sh A 2026-11-12 10:00 12:00)
rm -f "$OA/window.env"; r4=$(run "$OA" W4 s02_window_e207.sh B "$TODAY" "$STARTHM" "$ENDHM")
r=$(run "$OA" W0 s02_window_e207.sh A "$TODAY" "$STARTHM" "$ENDHM")
ok "$r1 $(has 'not E207' "$S/W1.txt") $r2 $(has 'not E207' "$S/W2.txt") $r3 $r4 $(has "E207's one arm" "$S/W4.txt") $r" "10 1 10 1 10 10 1 0" "$(grep -m1 STOP "$S/W1.txt" | cut -c1-100); $(grep -m1 STOP "$S/W2.txt" | cut -c1-100); $(grep -m1 STOP "$S/W4.txt" | cut -c1-90)"
step "G: step 2 without RB_GITLOCK"
r=$(RB_OUT=$OA RB_DESKTEST=1 bash "$T/$E/rb/s03_desk_e207.sh" A > "$S/G.txt" 2>&1; echo $?); ok "$r" 10 "$(grep -m1 STOP "$S/G.txt" | cut -c1-100)"
step "N: step 2 inside the lab-git lock (nested)"
r=$(RB_OUT=$OA RB_GITLOCK=$GL RB_DESKTEST=1 RB_GITLOCK_T=3 flock -n "$GL" bash "$T/$E/rb/s03_desk_e207.sh" A > "$S/N.txt" 2>&1; echo $?)
ok "$r $(has 'pull(rc 14; a nested lab-git lock exits 75)' "$S/N.txt")" "16 1" "$(stopline "$S/N.txt" | cut -c1-160)"
step "P1: step 2 on the scratch repository"
r=$(run "$OA" P1 s03_desk_e207.sh A)
ok "$r $(has 'desk check: the window written today for E207' "$S/P1.txt")" "0 1" "$(grep -m1 'desk check:' "$S/P1.txt" | cut -c1-300)"
[ "$r" = 0 ] || tail -n 30 "$S/P1.txt"
step "P2: the registration's list one line short; P3: the kit's list one line short; P4: MM1-v1's folder list one line short"
cp "$T/$E/SHA256SUMS-e207-registration" "$S/reg.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e207-registration"
r=$(run "$OA" P2 s03_desk_e207.sh A); cp "$S/reg.bak" "$T/$E/SHA256SUMS-e207-registration"
cp "$T/$E/SHA256SUMS-e207-kit" "$S/kit.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e207-kit"
r3=$(run "$OA" P3 s03_desk_e207.sh A); cp "$S/kit.bak" "$T/$E/SHA256SUMS-e207-kit"
cp "$T/tools/matmul/mm1/v1/SHA256SUMS" "$S/v1.bak"; sedi -e '$d' "$T/tools/matmul/mm1/v1/SHA256SUMS"
r4=$(run "$OA" P4 s03_desk_e207.sh A); cp "$S/v1.bak" "$T/tools/matmul/mm1/v1/SHA256SUMS"
rn=$(( $(grep -c . "$S/reg.bak") - 1 ))      # fix-e207: the registration's list holds 24 entries since amendment A1 (21 before): read, not typed
ok "$r $(has "SHA256SUMS-e207-registration($rn OK of $rn" "$S/P2.txt") $r3 $(has 'SHA256SUMS-e207-kit(' "$S/P3.txt") $r4 $(has 'SHA256SUMS(76 OK of 76' "$S/P4.txt")" "16 1 16 1 16 1" "$(stopline "$S/P2.txt" | cut -c1-160)"
step "H1: a committed edit of a registration file; H2: a committed shadowing addition (tools/claims-v3/e207/json.py)"
echo "an edit" >> "$T/$E/E207.md"; $G commit -q -am "desk test: an edit of E207.md"
r=$(run "$OA" H1 s03_desk_e207.sh A); $G reset -q --hard "$KIT"
echo "# a shadow" > "$T/$E/json.py"; $G add "$E/json.py"; $G commit -q -m "desk test: a shadow"
r2=$(run "$OA" H2 s03_desk_e207.sh A); /usr/bin/python3 -I -B "$T/$E/rb/check_history_e207.py" tree > "$S/H2b.txt" 2>&1; $G reset -q --hard "$KIT"
ok "$r $(has 'history' "$S/H1.txt") $r2 $(has 'json.py' "$S/H2b.txt")" "16 1 16 1" "$(stopline "$S/H1.txt" | cut -c1-150); $(head -c 150 "$S/H2b.txt")"
step "DA: E207 data committed: step 2 refuses; GS: a gate stop's record committed: step 2 reports it and goes on"
mkdir -p "$T/docs/reports/data/$TODAY-e207-blind-matmul-aifoundry3"; echo "stand-in" > "$T/docs/reports/data/$TODAY-e207-blind-matmul-aifoundry3/README.md"
$G add --sparse -f "docs/reports/data/$TODAY-e207-blind-matmul-aifoundry3/README.md"; $G commit -q -m "desk test: E207 data (stand-in)"
r=$(run "$OA" DA s03_desk_e207.sh A); $G reset -q --hard "$KIT"
mkdir -p "$T/docs/reports/gate-stops/$TODAY-e207-blind-matmul-T1-aifoundry3"; echo "stand-in" > "$T/docs/reports/gate-stops/$TODAY-e207-blind-matmul-T1-aifoundry3/README.md"
$G add --sparse -f "docs/reports/gate-stops/$TODAY-e207-blind-matmul-T1-aifoundry3/README.md"; $G commit -q -m "desk test: an E207 gate stop's record (stand-in)"
rg=$(run "$OA" GS s03_desk_e207.sh A); $G reset -q --hard "$KIT"
ok "$r $(has 'E207-has-data(1 commit(s))' "$S/DA.txt") $rg $(has 'gate-stop commits (reported): 1' "$S/GS.txt")" "16 1 0 1" "$(stopline "$S/DA.txt" | cut -c1-140); $(grep -m1 'gate-stop commits' "$S/GS.txt" | sed 's/.*E207 data commits/E207 data commits/' | cut -c1-120)"
step "O: the look on the stand-in box (k6's s05)"
r3=$(RB_OUT=$OA bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry3 > "$S/O3.txt" 2>&1; echo $?)
ok "$r3 $( [ -s "$OA/box-login-aifoundry3.txt" ] && echo login)" "0 login" "aifoundry3: $(grep -m1 'FREE\|HELD' "$S/O3.txt" | cut -c1-80)"
step "OL: E207's ours_live counts a session_e207.sh by its own script, never by a command string"
mkdir -p "$S/ol"; printf '#!/bin/bash\nsleep 25\n' > "$S/ol/session_e207.sh"
( . "$T/$E/rb/rb_e207.sh" > /dev/null 2>&1; e207_live_text ) > "$S/ol/live.sh"
printf '. "%s"\necho "$(ours_live session_e207.sh) $(ours_live)"\n' "$S/ol/live.sh" > "$S/ol/count.sh"
printf '#!/bin/bash\nsleep 25\n: tools/claims-v3/e207/session_e207.sh\n' > "$S/ol/decoy.sh"
n0=$(bash "$S/ol/count.sh")
setsid bash "$S/ol/decoy.sh" session_e207.sh < /dev/null > /dev/null 2>&1 &
p1=$!
n1=$(sleep 1; bash "$S/ol/count.sh")
setsid bash "$S/ol/session_e207.sh" < /dev/null > /dev/null 2>&1 &
p2=$!
n2=$(sleep 1; bash "$S/ol/count.sh")
kill "$p1" "$p2" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do [ "$(bash "$S/ol/count.sh")" = "0 0" ] && break; sleep 0.5; done
n3=$(bash "$S/ol/count.sh")
ok "$n0|$n1|$n2|$n3" "0 0|0 0|1 1|0 0" "before: $n0; a script whose arguments and text name session_e207.sh: $n1; a session_e207.sh run as a script: $n2; after it ended: $n3"
step "SY: step 5 on the stand-in box"
ra=$(run "$OA" SYA s07_sync_e207.sh A)
ok "$ra $(has 'HARNESS OK on the box' "$S/SYA.txt")" "0 1" "$(grep -m1 'synced to' "$S/SYA.txt" | cut -c1-140)"
step "L1: a login link on a read (step 5's first read); L2: a read that hangs (the read class's bound 3 s for this call)"
touch "$S/ssh-login"; n0=$(grep -c . "$RB_LOCK" 2>/dev/null || echo 0)
r=$(run "$OA" L1 s07_sync_e207.sh A); n1=$(grep -c 'aifoundry3 needs a check' "$RB_LOCK" 2>/dev/null || echo 0)
touch "$S/ssh-hang"
r2=$(RB_READ_S=3 RB_OUT=$OA RB_DESKTEST=1 bash "$T/$E/rb/s07_sync_e207.sh" A > "$S/L2.txt" 2>&1; echo $?); rm -f "$S/ssh-hang"
ok "$r $((n1 - n0)) $r2" "11 1 13" "$(stopline "$S/L1.txt" | cut -c1-120); $(stopline "$S/L2.txt" | cut -c1-100)"
step "T: NO-THIRD-BUILD on aifoundry3"
mkdir -p "$A3/build"; for k in 1 2; do echo "$TODAY 01:0$k:00 PST a3-build-e207 started" >> "$A3/build/e207-build-attempts.txt"; done
r=$(run "$OA" T s08_build_e207.sh A start); rm -f "$A3/build/e207-build-attempts.txt"
ok "$r $(has NO-THIRD-BUILD "$S/T.txt")" "16 1" "$(stopline "$S/T.txt" | cut -c1-140)"
step "BA: step 6 on aifoundry3: the real build"
r=$(run "$OA" BA1 s08_build_e207.sh A start); r2=$(waitjob "$OA" BA2 s08_build_e207.sh A wait)
ok "$r $r2 $(has 'KERNEL OK: ' "$S/BA2.txt")$(cat "$OA/e207-built-A.txt" 2>/dev/null)" "0 0 1rgm" "$(grep -m1 'built today on' "$S/BA2.txt" | cut -c1-160)"
[ "$r2" = 0 ] || tail -n 25 "$S/BA2.txt"
step "NR: step 6n, the never-run search repeated, on stand-in roots: b10 RAN BEFORE (a lab data directory of 1 Nov), n02 TO DATE (a box run folder), b27 AFTER THE FREEZE (a card lane's session T0), b02 DESK-ONLY (kit-e209), b30 never read (ee-*); b01 in an E207 lane's desk test and n01 in E207's own dry pass on the box, both subtracted"
mkdir -p "$A3/build/e999/T5" "$A3/build/e207/T1-A-dry/runs/002-pass1-n01"
rec gemmL3x5x1 int8 int8/full.bin > "$A3/build/e999/T5/proc.out"
rec gemmL1x3x1 int8 int8/full.bin > "$A3/build/e207/T1-A-dry/runs/002-pass1-n01/proc-00.out"
cp "$T/$E/desk/neverrun-e207.json" "$S/reg-neverrun.bak"
r=$(run "$OA" NR1 s06n_neverrun_e207.sh A); r2=$(run "$OA" NR2 s06n_neverrun_e207.sh A --desk-only)
rm -rf "${A3:?}/build/e999" "${A3:?}/build/e207/T1-A-dry"
nrd=$(cat "$OA/e207-neverrun-dir.txt" 2>/dev/null)
ok "$r $(has 'NEVER-RUN 50 of 53 points, 44 of 47 cases; RAN BEFORE: b10; TO DATE: n02; AFTER THE FREEZE (REPORTED, kept): b27; DESK-ONLY (dismissed): b02$' "$S/NR1.txt") $(has 'in E207.s own build/e207 (subtracted)' "$S/NR1.txt") $(has "NOT READ \['ee-1116-mmsweep'\]" "$S/NR1.txt") $(has 'DISMISSED (a desk lane.s folder, never a card run) OUT/' "$S/NR1.txt") $r2 $(has 'NEVER-RUN 51 of 53 points, 45 of 47 cases; RAN BEFORE: b10; AFTER THE FREEZE (REPORTED, kept): b27; DESK-ONLY (dismissed): b02; aifoundry3 NOT SEARCHED$' "$S/NR2.txt") $( [ -s "$OA/e207-neverrun.txt" ] && [ -s "$nrd/reg/desk/neverrun-e207.json" ] && [ -s "$nrd/ranbefore-e207.json" ] && echo report) $(cmp -s "$T/$E/desk/neverrun-e207.json" "$S/reg-neverrun.bak" && echo kept)" \
   "0 1 1 1 1 0 1 report kept" "$(grep -m1 'NEVER-RUN' "$S/NR1.txt" | cut -c1-200); desk-only: $(grep -m1 'NEVER-RUN' "$S/NR2.txt" | cut -c1-170)"
step "R7: STEP 7 needs a fresh never-run report and the rest: (a) no report: 10, no config read; (b) a report 31 minutes old: 10; (c) the rest not run (a session ended 10 minutes ago): 10; (d) both: 0, the reader called once"
O5=$S/out5; mkdir -p "$O5"; cp "$OA/window.env" "$O5/"; touch "$O5/window.env"
c0=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
ra=$(run "$O5" R7a s09_reads_e207.sh A)
cp "$OA/e207-neverrun.txt" "$O5/"; touch -d '-31 min' "$O5/e207-neverrun.txt"
rb=$(run "$O5" R7b s09_reads_e207.sh A)
mkdir -p "$A3/build/e185/T1"
{ echo "$(date -d '-14 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-10 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-10 min' "$A3/build/e185/T1/session.log"
rc_=$(run "$OA" R7c s09_reads_e207.sh A); c1=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
{ echo "$(date -d '-50 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-45 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-45 min' "$A3/build/e185/T1/session.log"
rd=$(run "$OA" R7d s09_reads_e207.sh A); c2=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
ok "$ra $(has 'no never-run report' "$S/R7a.txt") $rb $(has 'minutes old (more than 30)' "$S/R7b.txt") $rc_ $(has 'the rest has not run' "$S/R7c.txt") $((c1 - c0)) $rd $((c2 - c1)) $(has 'config TDP 0 W / 65 C / 600 MHz, et-who clean' "$S/R7d.txt")" \
   "10 1 10 1 10 1 0 0 1 1" "no report: $(stopline "$S/R7a.txt" | cut -c1-90); 31 min: $(stopline "$S/R7b.txt" | cut -c1-90); 10 min after a session: $(stopline "$S/R7c.txt" | cut -c1-90) (reader calls $((c1 - c0))); then: $(grep -m1 'aifoundry3:' "$S/R7d.txt" | cut -c1-90)"
step "D: step 8 on the stand-in box"
ra=$(run "$OA" DA1 s10_dry_e207.sh A start); ra2=$(waitjob "$OA" DA2 s10_dry_e207.sh A wait)
ok "$ra $ra2" "0 0" "$(grep -m1 'E207-DRY' "$S/DA2.txt")"
step "HG: a HUNG marker in a session log of ours on aifoundry3: step 9 refuses"
mkdir -p "$A3/build/e204/T1794800000"
printf '%s session start (T0 1794800000; desk test)\n%s HUNG: a device process did not end after its timeout TERM (desk test)\n%s session end (T0 1794800000)\n' \
  "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" > "$A3/build/e204/T1794800000/session.log"
touch -d '-3 hours' "$A3/build/e204/T1794800000/session.log"
r=$(run "$OA" HG s11_session_e207.sh A); rm -rf "${A3:?}/build/e204"
ok "$r $(has 'REFUSED: a HUNG marker of ours on the box' "$S/HG.txt") $(ls "$A3/build/e207" 2>/dev/null | grep -c '^T[0-9]*-A$')" "10 1 0" "$(grep -m1 'REFUSED' "$S/HG.txt" | cut -c1-140)"
step "SD: the same-day rule: an E207 session that opened the card earlier today"
mkdir -p "$A3/build/e207/T1700000000-A"
printf '%s session start (T0 1700000000; desk test)\n%s the first card command: the start config read through the guard\n%s session end (T0 1700000000)\n' \
  "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-45 min' '+%F %T %Z')" > "$A3/build/e207/T1700000000-A/session.log"
# fix-e207 (verify-e207's finding 5): the same-day rule reads the log's last write by its Pacific date, the rest rule its "session end" line; the
# write is dated inside today (45 minutes ago, or 00:00:01 today when that was yesterday), so the case holds at every hour of the day
if [ "$(TZ=America/Los_Angeles date -d '-45 min' +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then touch -d '-45 min' "$A3/build/e207/T1700000000-A/session.log"
else TZ=America/Los_Angeles touch -d "$(TZ=America/Los_Angeles date +%F) 00:00:01" "$A3/build/e207/T1700000000-A/session.log"; fi
r=$(run "$OA" SD s11_session_e207.sh A); rm -rf "${A3:?}/build/e207/T1700000000-A"
ok "$r $(has 'REFUSED: the same-day rule' "$S/SD.txt")" "10 1" "$(grep -m1 'REFUSED' "$S/SD.txt" | cut -c1-140)"
step "LS: THE LAST START passed (the window's last end still far): step 9 refuses (16) before anything is sent"
O6=$S/out6; mkdir -p "$O6"; cp "$OA/window.env" "$OA/e207-built-A.txt" "$O6/"
sedi -e "s/^RB_LAST_START_EPOCH=.*/RB_LAST_START_EPOCH=$(( $(date +%s) - 60 ))/" "$O6/window.env"; touch "$O6/window.env" "$O6/e207-built-A.txt"
n0=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
r=$(run "$O6" LS s11_session_e207.sh A); n1=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
ok "$r $(has "past the round's last start" "$S/LS.txt") $((n1 - n0))" "16 1 0" "$(stopline "$S/LS.txt" | cut -c1-140); box calls $((n1 - n0))"
step "NS: no never-run report from today in RB_OUT: step 9 refuses (10) before anything is sent"
O7=$S/out7; mkdir -p "$O7"; cp "$OA/window.env" "$OA/e207-built-A.txt" "$O7/"; touch "$O7/window.env" "$O7/e207-built-A.txt"
n0=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
r=$(run "$O7" NS s11_session_e207.sh A); n1=$(grep -c . "$S/calls.log" 2>/dev/null || echo 0)
ok "$r $(has 'no never-run report from today' "$S/NS.txt") $((n1 - n0))" "10 1 0" "$(stopline "$S/NS.txt" | cut -c1-140); box calls $((n1 - n0))"
step "LA: step 9 launches the REAL session_e207.sh, which stops at its box check (the desk's own hostname); step 10 reads the gate"
r=$(run "$OA" LA s11_session_e207.sh A); r2=$(waitjob "$OA" LA2 s20_wait_e207.sh A)
t0=$(cat "$OA/e207-T0-A.txt" 2>/dev/null)
sd=$A3/build/e207/T$t0-A
procs=$(find "$sd" -name 'proc*.out' 2>/dev/null | wc -l | tr -d ' ')
ok "$r $r2 $(has 'refused, no device opened: the box or the build is not the registered one (this host is' "$sd/session.log") $(has '"rc": 16' "$sd/queue.json") $( [ -s "$sd/MANIFEST.sha256" ] && echo manifest) $procs $(has 'GATE-STOPPED e207 arm A' "$S/LA2.txt")" \
   "0 16 1 1 manifest 0 1" "$(grep -m1 'no device opened' "$sd/session.log" | cut -c1-200)"
step "W10: step 10's readings on stand-in logs (a running session, none, HUNG, K1, CRASH, an ended session with a STOP line)"
O3=$S/out3; mkdir -p "$O3"; cp "$OA/window.env" "$OA/box-login-aifoundry3.txt" "$O3/"; touch "$O3/window.env"; echo 7 > "$O3/e207-T0-A.txt"
mkdir -p "$A3/build/q141k"; echo 7 > "$A3/build/q141k/e207A.T0"; W7=$A3/build/e207/T7-A; mkdir -p "$W7"
mkdir -p "$S/wv"; printf '#!/bin/bash\nsleep 30\n' > "$S/wv/session_e207.sh"
wr() { RB_OUT=$O3 RB_DESKTEST=1 RB_WAIT_LOOP_S=4 bash "$T/$E/rb/s20_wait_e207.sh" A > "$S/W10-$1.txt" 2>&1; echo $?; }
echo "$(date '+%F %T %Z') session start (T0 7; desk-test stand-in, no end)" > "$W7/session.log"
setsid bash "$S/wv/session_e207.sh" < /dev/null > /dev/null 2>&1 &
p3=$!
sleep 1
rv=$(wr V)
kill "$p3" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$p3" 2>/dev/null || break; sleep 0.5; done
rg=$(wr G)
printf '%s session start (T0 7; desk test)\n%s HUNG: a device process (the host of 001-tie-t01 (proc-00); its `timeout` pid 9) still runs\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"
rh=$(wr H)
printf '%s session start (T0 7; desk test)\n%s STOP: K1: a launch of run 001-tie-t01 did not finish (the host'"'"'s words): it may leave a hung hart: nothing further started\n%s session end (T0 7)\n' \
  "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo "x  session.log" > "$W7/MANIFEST.sha256"; echo 0 > "$W7/runner.rc"
rk=$(wr K)
printf '%s session start (T0 7; desk test)\n%s CRASH: KeyError: b99\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 1 > "$W7/runner.rc"
rc_=$(wr C)
printf '%s session start (T0 7; desk test)\n%s STOP: board 71.2 W above 70 W on 3 samples in a row: nothing further started\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 0 > "$W7/runner.rc"
re=$(wr E)
rm -rf "${A3:?}/build/e207/T7-A"; echo "$t0" > "$A3/build/q141k/e207A.T0"
ok "$rv $rg $rh $rk $rc_ $re $(has 'RUN-RUNNING' "$S/W10-V.txt")$(has 'RUN-GONE' "$S/W10-G.txt")$(has 'KILL NOTHING' "$S/W10-H.txt")$(has 'K1' "$S/W10-K.txt")$(has 'crashed' "$S/W10-C.txt")$(has 'read its STOP line' "$S/W10-E.txt")" \
   "17 14 16 16 16 0 111111" "running $rv, gone $rg, HUNG $rh, K1 $rk, CRASH $rc_, ended with a STOP line $re"
step "C: step 11 on LA's session, step 12 (the gate stop's record), step 13 refuses it; C2: a byte changed after the manifest"
r=$(run "$OA" C1 s22_collect_e207.sh A); r2=$(run "$OA" C2s s23_data_e207.sh A); r3=$(run "$OA" C3s s24_score_e207.sh A)
gs=$(cat "$OA/e207-data-dir-A.txt" 2>/dev/null)
ok "$r $r2 $(has 'COLLECTED-GATE-STOP docs/reports/gate-stops/' "$S/C2s.txt") $(grep -rl '/home/' "$T/$gs" 2>/dev/null | wc -l | tr -d ' ') $r3" "0 0 1 0 10" \
   "$(grep -m1 'COLLECTED' "$S/C2s.txt" | cut -c1-140); step 13: $(stopline "$S/C3s.txt" | cut -c1-100)"
O2=$S/out2; mkdir -p "$O2"; cp "$OA"/window.env "$OA"/e207-T0-A.txt "$OA"/box-login-aifoundry3.txt "$O2/"; touch "$O2/window.env"
echo "x" >> "$sd/session.log"
r=$(RB_OUT=$O2 RB_DESKTEST=1 bash "$T/$E/rb/s22_collect_e207.sh" A > "$S/C2.txt" 2>&1; echo $?)
ok "$r $(has 'COPY-BACK NOT EXACT' "$S/C2.txt")" "16 1" "$(stopline "$S/C2.txt" | cut -c1-140)"
step "CD: a session that ran (step 8's dry session copied as a session): steps 11, 12 and, after a stand-in data commit, 13 (the FROZEN scorer)"
dd=$(ls -d "$A3"/build/e207/T*-A-dry 2>/dev/null | tail -n 1)
O4=$S/out4; mkdir -p "$O4"; cp "$OA"/window.env "$OA"/box-login-aifoundry3.txt "$OA"/e207-neverrun-dir.txt "$O4/"; touch "$O4/window.env"; echo 8 > "$O4/e207-T0-A.txt"
cp -a "$dd" "$A3/build/e207/T8-A"; rm -f "${A3:?}/build/e207/T8-A/dry.lock"     # a dry session keeps its lock file beside its manifest
r=$(run "$O4" CD1 s22_collect_e207.sh A); rm -rf "${T:?}/docs/reports/data/$TODAY-e207-blind-matmul-aifoundry3"; r2=$(run "$O4" CD2 s23_data_e207.sh A)
dd2=$(cat "$O4/e207-data-dir-A.txt" 2>/dev/null)
$G add --sparse -f "$dd2" > /dev/null 2>&1; $G commit -q -m "desk test: a data commit (stand-in)" > /dev/null 2>&1
r3=$(run "$O4" CD3 s24_score_e207.sh A)
ok "$r $r2 $(has "COLLECTED docs/reports/data/$TODAY-e207-blind-matmul-aifoundry3" "$S/CD2.txt") $( [ -s "$T/$dd2/data-e207.json" ] && echo data) $(grep -c '  neverrun-e207-card\.\(txt\|json\)$' "$T/$dd2/SHA256SUMS" 2>/dev/null) $(grep -c '  ranbefore-e207-card\.json$' "$T/$dd2/SHA256SUMS" 2>/dev/null) $r3 $( [ -s "$O4/scores-e207-A.json" ] && echo scored) $(has 'THE REGISTERED VERDICTS' "$O4/postscore-e207-A.txt") $(has 'labels ranbefore-e207-card.json (step 6n.s proposal): points b10;' "$O4/postscore-e207-A.txt")" \
   "0 0 1 data 2 1 0 scored 1 1" "$(grep -m1 'COLLECTED' "$S/CD2.txt" | cut -c1-140); $(grep -m1 'scored arm A' "$S/CD3.txt" | cut -c1-120); R0 in the scorer's words: $(grep -m1 '^R0 ' "$O4/scores-e207-A.txt" 2>/dev/null | cut -c1-60)"
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
echo "SELFTEST-RB-E207 $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
}
main
