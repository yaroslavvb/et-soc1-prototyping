#!/usr/bin/env bash
# E206 (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum): the desk test of E206's runbook with a FAKE ssh and rsync on two stand-in
# boxes, E190's rb/selftest_rb_e190_v2.sh form. Its scratch repository is a shared, sparse clone of the lab clone this test runs from (its HEAD
# holds E206's registration as a commit, as on the card day) with the kit's files committed on top as one stand-in kit commit, the kit's list
# a stand-in made here and pinned in the scratch copy of step 2's KITPIN line (the one line this test changes in a copy), and stand-in desk-test
# logs (this test's own log is not final while it runs). The stand-in boxes are aifoundry3's ~/aifoundry and aifoundry1's ~/nekko, two rsync
# targets under the scratch; the stand-in ssh serves them with `bash -s` (and `true`) and refuses any other host or command; the stand-in rsync
# rewrites their paths; the boxes' hostname, uptime (aifoundry1's boot of 26 Oct, before E82's firmware read), et-who, et-lab-manifest and pgrep
# are stand-ins, and each box tree holds a stand-in reader at build/ettelem/ettelem (the doubles' config and sampler) and aifoundry3's E128
# guard (k6's step 7 runs it there); cmake, the compilers and /opt/et are this desk's REAL ones (the build is the real build_e206.sh with THE
# KERNEL GATE; on the stand-in aifoundry1 the ET_DEVICES gate reads this desk's stock device layer). No lab box is reached.
# FIXED BEFORE THE LAND (Q198 lane fix-e206, verify-e206's finding 2): the first version took the kit's files from the lab clone's UNTRACKED
# files only, so once the kit was committed its stand-in list came out empty and the test read 25 of 27 FAIL at HEAD. Now, when the lab
# clone's history holds the kit commit (the commit that added KIT.md), the scratch repository is built at that commit's PARENT (the
# registration in it, as in the kit lane's own state) and the kit's files (the paths that commit added) are taken from HEAD; when it does
# not, the untracked files as before. In the committed form the scratch's main follows a LOCAL branch at that parent (e206-desktest-base),
# so step 2's `git pull --ff-only` finds it up to date, as the untracked form's pull of the lab clone's HEAD does (the lab clone's main,
# holding the real kit commit, would diverge from the stand-in kit commit: fix-e206's own first try read 25 of 27 there, P1 and DA, for
# that reason). Both forms were run before the land (KIT.md section 9). Cases:
#   A   the dry listings, both arms: every step exits 0, no call reaches the stand-ins
#   K   step 2 with no window: 10      W1 a window for the other arm: 10      W2 a window written for another runbook: 10
#   W3  step 1 for another day: 10     G  step 2 without RB_GITLOCK: 10       N  step 2 inside the lab-git lock (nested): 16 naming the pull
#   P1  step 2 on the scratch repository (arm A, then arm B): 0 (both lists at their pins, HISTORY OK, the registration and the kit found by
#       content, the registration's checks and the scorer's two self-tests, the preflight GO, the desk tests' logs)
#   P2  the registration's list one line short: 16      P3 the kit's list one line short: 16
#   H1  a committed edit of a registration file: 16 by the history check      H2 a committed tools/claims-v3/e206/json.py (a shadow): 16
#   DA  arm A's data committed: step 2 of arm A 16 (the arm has run), step 2 of arm B 0 (the other arm's data reported)
#   O   the look on both stand-in boxes (k6's s05, unchanged): FREE, our login recorded for the scrub
#   OL  E206's ours_live: a shell whose command string names session_e206.sh is not a session; a session_e206.sh run as a script is
#   SY  step 5 on both boxes: the rsync, HARNESS OK on each box     L1 a login link on a read: 11, "<HH:MM:SS> aifoundry1 needs a check"
#       appended to RB_LOCK, nothing retried      L2 a read that hangs (the read class's bound 3 s for this call): 13
#   T   NO-THIRD-BUILD: two starts recorded on aifoundry1 today: a third start is refused with 16
#   BB  step 6 on the stand-in aifoundry1 (this desk's stock device layer): RGM-BUILD-FAILED "ET_DEVICES: the host has no ET_DEVICES", the
#       wait 16, no RB_OUT/e206-built-B.txt          BA step 6 on aifoundry3: start, wait (17 while it builds, then 0): the REAL build, KERNEL
#       OK, the record, the harness, the preflight GO and both self-checks read on the box; RB_OUT/e206-built-A.txt
#   R7  STEP 7 ONLY ONCE THE REST HAS OPENED: a session of ours ended 10 minutes ago on aifoundry3: step 7 refuses (10) and the stand-in reader
#       is NEVER called (no config read sent); ended 45 minutes ago: the rest reads open, k6's reads follow (TDP 0 W / 65 C / 600 MHz), 0
#   R7B step 7 on aifoundry1: card 1's forms through E206's guard (ET_DEVICES=1): 0; the reader naming card 0 (519 mV): 16; a holder line of
#       another login on card 0: 17
#   D   step 8 on both stand-in boxes (the doubles there): 0 each
#   HG  THE HUNG MARKER: a session log of ours on aifoundry3 with a HUNG line: step 9 refuses (10), nothing launched
#   SD  THE SAME-DAY RULE: a session of arm A that opened the card earlier today: step 9 refuses (10)
#   LA  step 9 launches the REAL session_e206.sh and run_e206.py on the stand-in aifoundry3, which stop at their box check before any device
#       (the desk's own hostname): "refused, no device opened"; step 10 reads GATE-STOPPED (16) with the manifest written
#   W10 step 10's readings on stand-in logs: a running session_e206.sh with no end 17 (RUN-RUNNING); none running 14 (RUN-GONE); a HUNG line
#       16 (HUNG); a K1 stop 16 (K1-STOPPED); a CRASH line 16 (CRASHED); an ended session (rc 0) with a STOP line 0
#   C   step 11 on LA's session: COPY-BACK EXACT 0; step 12: the gate stop's record under docs/reports/gate-stops/ (COLLECTED-GATE-STOP), the
#       desk-path gate, HISTORY OK: 0; step 13 refuses a gate stop's record: 10      C2 one byte of a box file changed after the manifest:
#       COPY-BACK NOT EXACT 16
#   CD  a session that ran (step 8's dry session copied as a session): step 11 0, step 12 the data directory with data-e206.json (the reducer)
#       and the scrub clean: 0; after a stand-in data commit, step 13 runs the FROZEN scorer on it: 0
#   Z   no process of this test left running
#   bash tools/claims-v3/e206/rb/selftest_rb_e206.sh <scratch dir> > logs/selftest-rb-e206.txt   (prints SELFTEST-RB-E206 <n> of <m> PASS or FAIL)
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
A3=$B/aifoundry3/aifoundry; A1=$B/aifoundry1/nekko
E=tools/claims-v3/e206
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
G="git -C $T -c user.name=e206-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /workloads/ledger/ /docs/reports/data/2026-11-02-e136-large-gemm/ /docs/reports/data/2026-11-01-e119-gemm-speed/ \
  /docs/reports/data/2026-11-02-e126-gemm-arms/ /docs/reports/data/2026-11-02-e146-gemm-stores/ /docs/reports/data/2026-11-12-q166-ledger-v2/ \
  /docs/reports/data/2026-11-01-e107-gemm-placement/ /docs/reports/data/2026-11-01-e95-real-tensors-energy/ /docs/reports/data/2026-09-23-energy-manual/ \
  /docs/reports/data/2026-11-13-e190-large-gemm/ /docs/reports/data/2026-11-01-e105-gemm-layout/ /docs/reports/data/2026-10-26-load-model/ \
  /docs/reports/data/2026-11-12-q166-counter-sparseparity/ || return 2
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
  { $G branch -q -f e206-desktest-base "$BASE" && $G branch -q --set-upstream-to=e206-desktest-base main; } || { echo "the scratch's upstream could not be set"; return 2; }
else
  $G branch -q --set-upstream-to=origin/main 2>/dev/null
fi
$G log --diff-filter=A --format=%H -- $E/E206.md | grep -q . || { echo "the registration is not in the scratch repository's history"; return 2; }
if [ -n "$KITC" ]; then      # the paths the kit commit added, at HEAD's bytes (the history check keeps them as first committed)
  git -C "$SRC" diff-tree --no-commit-id --name-only -r --diff-filter=A "$KITC" -- $E | while IFS= read -r f; do
    mkdir -p "$T/$(dirname "$f")"; git -C "$SRC" show "HEAD:$f" > "$T/$f" || exit 2; done || { echo "the kit's files could not be taken from HEAD"; return 2; }
else
  ( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E ) | sort -u | while IFS= read -r f; do
    [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
fi
mkdir -p "$T/$E/logs"
for spec in "selftest-run-e206.txt SELFTEST-RUN-E206 0 of 0 PASS" "realpath-e206.txt REALPATH-E206 0 of 0 PASS" "realbytes-e206.txt REALBYTES-E206 0 of 0 PASS" \
            "desktest-build-e206.txt DESKTEST-BUILD-E206 0 of 0 PASS" "selftest-rb-e206.txt SELFTEST-RB-E206 0 of 0 PASS" \
            "dry-listing-e206-A.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dry-listing-e206-B.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" \
            "dmcmd-audit-e206.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"
done
( cd "$T" && /usr/bin/python3 -I -B $E/check_e206.py --make > /dev/null )
mklist() {  # the kit's stand-in list: every file this stand-in commit adds under E206's folder, but the list itself and step 2
  ( cd "$T" && git ls-files --others --exclude-standard -- $E | grep -v -x -e "$E/SHA256SUMS-e206-kit" -e "$E/rb/s03_desk_e206.sh" |
      LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/kit-standin.txt"
  KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e206-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^KITPIN=$E/SHA256SUMS-e206-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e206-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e206.sh"
  grep -q "^KITPIN=$E/SHA256SUMS-e206-kit:$KITN:$KITH:top" "$T/$E/rb/s03_desk_e206.sh"
}
mklist || { echo "the scratch step 2's KITPIN was not set"; return 2; }
$G add -A $E && $G commit -q -m "E206 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; return 2; }
KIT=$($G rev-parse HEAD)
echo "scratch repository: a shared sparse clone of the lab clone ($FORM; the registration in it), the kit as one stand-in commit ${KIT:0:12}; the kit's stand-in list $KITN files"
[ "$KITN" -gt 0 ] || { echo "the kit's stand-in list is empty"; return 2; }
# ---- the stand-ins
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry1|aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; cat > /dev/null; echo "To authenticate, visit: https://login.tailscale.com/a/e206desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'bash -s' and 'true' are served (got: \$cmd)" >&2; exit 97; }
cd "$B/\$host" || exit 1
exec env HOME="$B/\$host" STANDIN_HOST="\$host" STANDIN_S="$S" PATH="$BB:\$PATH" bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry1|aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho "scp refused by the desk test" >&2\nexit 97\n' > "$BIN/scp"
printf '#!/bin/sh\necho "${STANDIN_HOST:-desk}"\n' > "$BB/hostname"
cat > "$BB/uptime" <<'EOF'
#!/bin/sh
if [ "${1:-}" = -s ] && [ "${STANDIN_HOST:-}" = aifoundry1 ]; then echo "2026-10-26 15:02:04"; exit 0; fi
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
for spec in "$A3:A" "$A1:B"; do       # each box's own tools: a stand-in reader (counting its calls), and on aifoundry3 the E128 guard
  bt=${spec%%:*}; arm=${spec#*:}
  mkdir -p "$bt/build/ettelem" "$bt/tools/claims-v3/e128"
  cat > "$bt/build/ettelem/ettelem" <<EOF
#!/bin/sh
echo "\$(date +%s) \$*" >> "$S/reader-calls-$arm.txt"
mode=ok; [ -s "$S/reader-mode-$arm" ] && mode=\$(cat "$S/reader-mode-$arm")
exec env E206_FAKE_ARM=$arm E206_FAKE_CONFIG=\$mode /usr/bin/python3 -B "$T/$E/fake_card_e206.py" "\$@"
EOF
  chmod +x "$bt/build/ettelem/ettelem"
done
cp -p "$SRC/tools/claims-v3/e128/ettelem_guard.sh" "$A3/tools/claims-v3/e128/ettelem_guard.sh"
export PATH="$BIN:$PATH" RB_LOCK="$S/rb-lock.txt"
GL=$S/lab-git.lock; : > "$GL"
TODAY=$(TZ=America/Los_Angeles date +%F)
STARTHM=23:58; ENDHM=23:59           # the window is today's last minutes: the steps' budgets are E206_DESK_BUDGET_S (60 s) here
OA=$S/outA; OB=$S/outB; mkdir -p "$OA" "$OB"
run() {  # run <arm's RB_OUT> <log> <script> [args]: a step of the scratch repository's runbook
  local o=$1 lg=$2; shift 2
  RB_OUT=$o RB_GITLOCK=$GL RB_DESKTEST=1 E206_DESK_BUDGET_S=60 bash "$T/$E/rb/$1" "${@:2}" > "$S/$lg.txt" 2>&1
  echo $?
}
waitjob() {  # waitjob <RB_OUT> <tag> <script> <args...>: call a wait step until it says something other than 17 (at most 40 calls)
  local o=$1 tag=$2 r k; shift 2
  for k in $(seq 1 40); do r=$(run "$o" "$tag-$k" "$@"); [ "$r" = 17 ] || { cp "$S/$tag-$k.txt" "$S/$tag.txt"; echo "$r"; return; }; done; echo 17
}
step "A: the dry listings, both arms"
mkdir -p "$S/listing-A" "$S/listing-B"
( cd "$T" && bash $E/rb/list_steps_e206.sh "$S/listing-A" A > "$S/A-A.txt" 2>&1; bash $E/rb/list_steps_e206.sh "$S/listing-B" B > "$S/A-B.txt" 2>&1 )
ok "$(grep -c 'dry listing: 14 steps listed, 0 exited non-zero, 0 box calls' "$S/A-A.txt") $(grep -c 'dry listing: 14 steps listed, 0 exited non-zero, 0 box calls' "$S/A-B.txt")" "1 1" \
   "arm A: $(tail -n 1 "$S/A-A.txt"); arm B: $(tail -n 1 "$S/A-B.txt")"
step "K: step 2 with no window"
r=$(run "$OA" K s03_desk_e206.sh A); ok "$r $( [ -s "$S/calls.log" ] && echo calls || echo nocalls)" "10 nocalls" "$(grep -m1 STOP "$S/K.txt" | cut -c1-120)"
step "W1: a window written for the other arm; W2: a window written for another runbook; W3: step 1 for another day"
r=$(run "$OA" W1a s02_window_e206.sh B "$TODAY" "$STARTHM" "$ENDHM"); r1=$(run "$OA" W1 s03_desk_e206.sh A)
rm -f "$OA/window.env"; r=$(run "$OA" W2a s02_window_e206.sh A "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_PLAN=e206/RB_PLAN=e202/' "$OA/window.env"
r2=$(run "$OA" W2 s03_desk_e206.sh A)
r3=$(run "$OA" W3 s02_window_e206.sh A 2026-11-12 10:00 12:00)
rm -f "$OA/window.env"; r=$(run "$OA" W0 s02_window_e206.sh A "$TODAY" "$STARTHM" "$ENDHM"); r=$(run "$OB" W0B s02_window_e206.sh B "$TODAY" "$STARTHM" "$ENDHM")
ok "$r1 $(has 'not arm A' "$S/W1.txt") $r2 $(has 'not E206' "$S/W2.txt") $r3" "10 1 10 1 10" "$(grep -m1 STOP "$S/W1.txt" | cut -c1-100); $(grep -m1 STOP "$S/W2.txt" | cut -c1-100)"
step "G: step 2 without RB_GITLOCK"
r=$(RB_OUT=$OA RB_DESKTEST=1 bash "$T/$E/rb/s03_desk_e206.sh" A > "$S/G.txt" 2>&1; echo $?); ok "$r" 10 "$(grep -m1 STOP "$S/G.txt" | cut -c1-100)"
step "N: step 2 inside the lab-git lock (nested)"
r=$(RB_OUT=$OA RB_GITLOCK=$GL RB_DESKTEST=1 RB_GITLOCK_T=3 flock -n "$GL" bash "$T/$E/rb/s03_desk_e206.sh" A > "$S/N.txt" 2>&1; echo $?)
ok "$r $(has 'pull(rc 14; a nested lab-git lock exits 75)' "$S/N.txt")" "16 1" "$(stopline "$S/N.txt" | cut -c1-160)"
step "P1: step 2 on the scratch repository (arm A, then arm B)"
r=$(run "$OA" P1 s03_desk_e206.sh A); rb=$(run "$OB" P1B s03_desk_e206.sh B)
ok "$r $rb $(has 'desk check (arm A): the window written today for E206 arm A' "$S/P1.txt")" "0 0 1" "$(grep -m1 'desk check (arm A):' "$S/P1.txt" | cut -c1-300)"
[ "$r" = 0 ] || tail -n 30 "$S/P1.txt"
step "P2: the registration's list one line short; P3: the kit's list one line short"
cp "$T/$E/SHA256SUMS-e206-registration" "$S/reg.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e206-registration"
r=$(run "$OA" P2 s03_desk_e206.sh A); cp "$S/reg.bak" "$T/$E/SHA256SUMS-e206-registration"
cp "$T/$E/SHA256SUMS-e206-kit" "$S/kit.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e206-kit"
r3=$(run "$OA" P3 s03_desk_e206.sh A); cp "$S/kit.bak" "$T/$E/SHA256SUMS-e206-kit"
ok "$r $(has 'SHA256SUMS-e206-registration(24 OK of 24' "$S/P2.txt") $r3 $(has 'SHA256SUMS-e206-kit(' "$S/P3.txt")" "16 1 16 1" "$(stopline "$S/P2.txt" | cut -c1-160)"
step "H1: a committed edit of a registration file; H2: a committed shadowing addition (tools/claims-v3/e206/json.py)"
echo "an edit" >> "$T/$E/E206.md"; $G commit -q -am "desk test: an edit of E206.md"
r=$(run "$OA" H1 s03_desk_e206.sh A); $G reset -q --hard "$KIT"
echo "# a shadow" > "$T/$E/json.py"; $G add "$E/json.py"; $G commit -q -m "desk test: a shadow"
r2=$(run "$OA" H2 s03_desk_e206.sh A); /usr/bin/python3 -I -B "$T/$E/rb/check_history_e206.py" tree > "$S/H2b.txt" 2>&1; $G reset -q --hard "$KIT"
ok "$r $(has 'history' "$S/H1.txt") $r2 $(has 'json.py' "$S/H2b.txt")" "16 1 16 1" "$(stopline "$S/H1.txt" | cut -c1-150); $(head -c 150 "$S/H2b.txt")"
step "DA: arm A's data committed: step 2 of arm A refuses, step 2 of arm B reports it"
mkdir -p "$T/docs/reports/data/$TODAY-e206-matmul-sweep-aifoundry3"; echo "stand-in" > "$T/docs/reports/data/$TODAY-e206-matmul-sweep-aifoundry3/README.md"
$G add --sparse -f "docs/reports/data/$TODAY-e206-matmul-sweep-aifoundry3/README.md"; $G commit -q -m "desk test: arm A's data (stand-in)"
r=$(run "$OA" DA s03_desk_e206.sh A); rb=$(run "$OB" DAB s03_desk_e206.sh B); $G reset -q --hard "$KIT"
ok "$r $(has 'arm-A-has-data(1 commit(s))' "$S/DA.txt") $rb" "16 1 0" "$(stopline "$S/DA.txt" | cut -c1-140); arm B: $(grep -m1 'any E206 data' "$S/DAB.txt" | sed 's/.*any E206 data/any E206 data/' | cut -c1-80)"
step "O: the look on both stand-in boxes (k6's s05)"
r3=$(RB_OUT=$OA bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry3 > "$S/O3.txt" 2>&1; echo $?)
r1=$(RB_OUT=$OB bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry1 > "$S/O1.txt" 2>&1; echo $?)
ok "$r3 $r1 $( [ -s "$OA/box-login-aifoundry3.txt" ] && [ -s "$OB/box-login-aifoundry1.txt" ] && echo logins)" "0 0 logins" "aifoundry3: $(grep -m1 'FREE\|HELD' "$S/O3.txt" | cut -c1-80); aifoundry1: $(grep -m1 'FREE\|HELD\|STOP' "$S/O1.txt" | cut -c1-80)"
step "OL: E206's ours_live counts a session_e206.sh by its own script, never by a command string"
mkdir -p "$S/ol"; printf '#!/bin/bash\nsleep 25\n' > "$S/ol/session_e206.sh"
( . "$T/$E/rb/rb_e206.sh" > /dev/null 2>&1; e206_live_text ) > "$S/ol/live.sh"
printf '. "%s"\necho "$(ours_live session_e206.sh) $(ours_live)"\n' "$S/ol/live.sh" > "$S/ol/count.sh"
printf '#!/bin/bash\nsleep 25\n: tools/claims-v3/e206/session_e206.sh\n' > "$S/ol/decoy.sh"
n0=$(bash "$S/ol/count.sh")
setsid bash "$S/ol/decoy.sh" session_e206.sh < /dev/null > /dev/null 2>&1 &
p1=$!
n1=$(sleep 1; bash "$S/ol/count.sh")
setsid bash "$S/ol/session_e206.sh" < /dev/null > /dev/null 2>&1 &
p2=$!
n2=$(sleep 1; bash "$S/ol/count.sh")
kill "$p1" "$p2" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do [ "$(bash "$S/ol/count.sh")" = "0 0" ] && break; sleep 0.5; done
n3=$(bash "$S/ol/count.sh")
ok "$n0|$n1|$n2|$n3" "0 0|0 0|1 1|0 0" "before: $n0; a script whose arguments and text name session_e206.sh: $n1; a session_e206.sh run as a script: $n2; after it ended: $n3"
step "SY: step 5 on both boxes"
ra=$(run "$OA" SYA s07_sync_e206.sh A); rb=$(run "$OB" SYB s07_sync_e206.sh B)
ok "$ra $rb $(has 'HARNESS OK on the box' "$S/SYA.txt")$(has 'HARNESS OK on the box' "$S/SYB.txt")" "0 0 11" "$(grep -m1 'synced to' "$S/SYA.txt" | cut -c1-140)"
step "L1: a login link on a read (step 5, arm B's first read); L2: a read that hangs (the read class's bound 3 s for this call)"
touch "$S/ssh-login"; n0=$(grep -c . "$RB_LOCK" 2>/dev/null || echo 0)
r=$(run "$OB" L1 s07_sync_e206.sh B); n1=$(grep -c 'aifoundry1 needs a check' "$RB_LOCK" 2>/dev/null || echo 0)
touch "$S/ssh-hang"
r2=$(RB_READ_S=3 RB_OUT=$OB RB_DESKTEST=1 bash "$T/$E/rb/s07_sync_e206.sh" B > "$S/L2.txt" 2>&1; echo $?); rm -f "$S/ssh-hang"
ok "$r $((n1 - n0)) $r2" "11 1 13" "$(stopline "$S/L1.txt" | cut -c1-120); $(stopline "$S/L2.txt" | cut -c1-100)"
step "T: NO-THIRD-BUILD on aifoundry1"
mkdir -p "$A1/build"; for k in 1 2; do echo "$TODAY 01:0$k:00 PST a1-build-e206 started" >> "$A1/build/e206-build-attempts.txt"; done
r=$(run "$OB" T s08_build_e206.sh B start); rm -f "$A1/build/e206-build-attempts.txt"
ok "$r $(has NO-THIRD-BUILD "$S/T.txt")" "16 1" "$(stopline "$S/T.txt" | cut -c1-140)"
step "BB: step 6 on the stand-in aifoundry1 (this desk's stock device layer): the ET_DEVICES gate"
r=$(run "$OB" BB1 s08_build_e206.sh B start); r2=$(waitjob "$OB" BB2 s08_build_e206.sh B wait)
ok "$r $r2 $(has 'RGM-BUILD-FAILED: ET_DEVICES: the host has no ET_DEVICES' "$S/BB2.txt") $(grep -c '^    HOSTCHECK .*: ok' "$S/BB2.txt") $( [ -e "$OB/e206-built-B.txt" ] && echo built || echo none)" \
   "0 16 1 4 none" "$(grep -m1 'RGM-BUILD-FAILED: ET' "$S/BB2.txt" | cut -c1-140)"
step "BA: step 6 on aifoundry3: the real build"
r=$(run "$OA" BA1 s08_build_e206.sh A start); r2=$(waitjob "$OA" BA2 s08_build_e206.sh A wait)
ok "$r $r2 $(has 'KERNEL OK: ' "$S/BA2.txt")$(cat "$OA/e206-built-A.txt" 2>/dev/null)" "0 0 1rgm" "$(grep -m1 'built today on' "$S/BA2.txt" | cut -c1-160)"
[ "$r2" = 0 ] || tail -n 25 "$S/BA2.txt"
step "R7: step 7 only once the rest has opened (aifoundry3)"
mkdir -p "$A3/build/e185/T1"
{ echo "$(date -d '-14 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-10 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-10 min' "$A3/build/e185/T1/session.log"
c0=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
r=$(run "$OA" R7a s09_reads_e206.sh A); c1=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
{ echo "$(date -d '-50 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-45 min' '+%F %T %Z') session end (T0 1)"; } > "$A3/build/e185/T1/session.log"
touch -d '-45 min' "$A3/build/e185/T1/session.log"
r2=$(run "$OA" R7b s09_reads_e206.sh A); c2=$(grep -c . "$S/reader-calls-A.txt" 2>/dev/null || echo 0)
ok "$r $((c1 - c0)) $r2 $((c2 - c1)) $(has 'config TDP 0 W / 65 C / 600 MHz, et-who clean' "$S/R7b.txt")" "10 0 0 1 1" \
   "10 minutes after a session: $(grep -m1 'STOP' "$S/R7a.txt" | cut -c1-110) (reader calls $((c1 - c0))); 45 minutes after: $(grep -m1 'aifoundry3:' "$S/R7b.txt" | cut -c1-90)"
step "R7B: step 7 on aifoundry1: card 1's forms; the reader naming card 0; another login's holder on card 0"
r=$(run "$OB" R7Ba s09_reads_e206.sh B)
echo card0 > "$S/reader-mode-B"; r2=$(run "$OB" R7Bb s09_reads_e206.sh B); rm -f "$S/reader-mode-B"
echo "/dev/et0_ops   someoneelse      4444       00:01 other_host" > "$S/etwho-lines-aifoundry1"; r3=$(run "$OB" R7Bc s09_reads_e206.sh B); rm -f "$S/etwho-lines-aifoundry1"
ok "$r $r2 $r3" "0 16 17" "card 1: $(grep -m1 'aifoundry1 card 1:' "$S/R7Ba.txt" | cut -c1-120); card 0: $(stopline "$S/R7Bb.txt" | cut -c1-100); card 0 held: $(stopline "$S/R7Bc.txt" | cut -c1-90)"
step "D: step 8 on both stand-in boxes"
ra=$(run "$OA" DA1 s10_dry_e206.sh A start); ra2=$(waitjob "$OA" DA2 s10_dry_e206.sh A wait)
rb=$(run "$OB" DB1 s10_dry_e206.sh B start); rb2=$(waitjob "$OB" DB2 s10_dry_e206.sh B wait)
ok "$ra $ra2 $rb $rb2" "0 0 0 0" "$(grep -m1 'E206-DRY' "$S/DA2.txt"); $(grep -m1 'E206-DRY' "$S/DB2.txt")"
step "HG: a HUNG marker in a session log of ours on aifoundry3: step 9 refuses"
mkdir -p "$A3/build/e204/T1794800000"
printf '%s session start (T0 1794800000; desk test)\n%s HUNG: a device process did not end after its timeout TERM (desk test)\n%s session end (T0 1794800000)\n' \
  "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" "$(date -d '-3 hours' '+%F %T %Z')" > "$A3/build/e204/T1794800000/session.log"
touch -d '-3 hours' "$A3/build/e204/T1794800000/session.log"
r=$(run "$OA" HG s11_session_e206.sh A); rm -rf "${A3:?}/build/e204"
ok "$r $(has 'REFUSED: a HUNG marker of ours on the box' "$S/HG.txt") $(ls "$A3/build/e206" 2>/dev/null | grep -c '^T[0-9]*-A$')" "10 1 0" "$(grep -m1 'REFUSED' "$S/HG.txt" | cut -c1-140)"
step "SD: the same-day rule: a session of arm A that opened the card earlier today"
mkdir -p "$A3/build/e206/T1700000000-A"
printf '%s session start (T0 1700000000; desk test)\n%s the first card command: the start config read through the guard\n%s session end (T0 1700000000)\n' \
  "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-50 min' '+%F %T %Z')" "$(date -d '-45 min' '+%F %T %Z')" > "$A3/build/e206/T1700000000-A/session.log"
touch -d '-45 min' "$A3/build/e206/T1700000000-A/session.log"
r=$(run "$OA" SD s11_session_e206.sh A); rm -rf "${A3:?}/build/e206/T1700000000-A"
ok "$r $(has 'REFUSED: the same-day rule' "$S/SD.txt")" "10 1" "$(grep -m1 'REFUSED' "$S/SD.txt" | cut -c1-140)"
step "LA: step 9 launches the REAL session_e206.sh, which stops at its box check (the desk's own hostname); step 10 reads the gate"
r=$(run "$OA" LA s11_session_e206.sh A); r2=$(waitjob "$OA" LA2 s20_wait_e206.sh A)
t0=$(cat "$OA/e206-T0-A.txt" 2>/dev/null)
sd=$A3/build/e206/T$t0-A
procs=$(find "$sd" -name 'proc*.out' 2>/dev/null | wc -l | tr -d ' ')
ok "$r $r2 $(has 'refused, no device opened: the box or the build is not the registered one (this host is' "$sd/session.log") $(has '"rc": 16' "$sd/queue.json") $( [ -s "$sd/MANIFEST.sha256" ] && echo manifest) $procs $(has 'GATE-STOPPED e206 arm A' "$S/LA2.txt")" \
   "0 16 1 1 manifest 0 1" "$(grep -m1 'no device opened' "$sd/session.log" | cut -c1-200)"
step "W10: step 10's readings on stand-in logs (a running session, none, HUNG, K1, CRASH, an ended session with a STOP line)"
O3=$S/out3; mkdir -p "$O3"; cp "$OA/window.env" "$OA/box-login-aifoundry3.txt" "$O3/"; touch "$O3/window.env"; echo 7 > "$O3/e206-T0-A.txt"
mkdir -p "$A3/build/q141k"; echo 7 > "$A3/build/q141k/e206A.T0"; W7=$A3/build/e206/T7-A; mkdir -p "$W7"
mkdir -p "$S/wv"; printf '#!/bin/bash\nsleep 30\n' > "$S/wv/session_e206.sh"
wr() { RB_OUT=$O3 RB_DESKTEST=1 RB_WAIT_LOOP_S=4 bash "$T/$E/rb/s20_wait_e206.sh" A > "$S/W10-$1.txt" 2>&1; echo $?; }
echo "$(date '+%F %T %Z') session start (T0 7; desk-test stand-in, no end)" > "$W7/session.log"
setsid bash "$S/wv/session_e206.sh" < /dev/null > /dev/null 2>&1 &
p3=$!
sleep 1
rv=$(wr V)
kill "$p3" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$p3" 2>/dev/null || break; sleep 0.5; done
rg=$(wr G)
printf '%s session start (T0 7; desk test)\n%s HUNG: a device process (the host of 001-tie-p001 (proc-00); its `timeout` pid 9) still runs\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"
rh=$(wr H)
printf '%s session start (T0 7; desk test)\n%s STOP: K1: a launch of run 001-tie-p001 did not finish (the host'"'"'s words): it may leave a hung hart: nothing further started\n%s session end (T0 7)\n' \
  "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo "x  session.log" > "$W7/MANIFEST.sha256"; echo 0 > "$W7/runner.rc"
rk=$(wr K)
printf '%s session start (T0 7; desk test)\n%s CRASH: KeyError: p999\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 1 > "$W7/runner.rc"
rc_=$(wr C)
printf '%s session start (T0 7; desk test)\n%s STOP: board 71.2 W above 70 W on 3 samples in a row: nothing further started\n%s session end (T0 7)\n' "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" "$(date '+%F %T %Z')" > "$W7/session.log"; echo 0 > "$W7/runner.rc"
re=$(wr E)
rm -rf "${A3:?}/build/e206/T7-A"; echo "$t0" > "$A3/build/q141k/e206A.T0"
ok "$rv $rg $rh $rk $rc_ $re $(has 'RUN-RUNNING' "$S/W10-V.txt")$(has 'RUN-GONE' "$S/W10-G.txt")$(has 'KILL NOTHING' "$S/W10-H.txt")$(has 'K1' "$S/W10-K.txt")$(has 'crashed' "$S/W10-C.txt")$(has 'read its STOP line' "$S/W10-E.txt")" \
   "17 14 16 16 16 0 111111" "running $rv, gone $rg, HUNG $rh, K1 $rk, CRASH $rc_, ended with a STOP line $re"
step "C: step 11 on LA's session, step 12 (the gate stop's record), step 13 refuses it; C2: a byte changed after the manifest"
r=$(run "$OA" C1 s22_collect_e206.sh A); r2=$(run "$OA" C2s s23_data_e206.sh A); r3=$(run "$OA" C3s s24_score_e206.sh A)
gs=$(cat "$OA/e206-data-dir-A.txt" 2>/dev/null)
ok "$r $r2 $(has 'COLLECTED-GATE-STOP docs/reports/gate-stops/' "$S/C2s.txt") $(grep -rl '/home/' "$T/$gs" 2>/dev/null | wc -l | tr -d ' ') $r3" "0 0 1 0 10" \
   "$(grep -m1 'COLLECTED' "$S/C2s.txt" | cut -c1-140); step 13: $(stopline "$S/C3s.txt" | cut -c1-100)"
O2=$S/out2; mkdir -p "$O2"; cp "$OA"/window.env "$OA"/e206-T0-A.txt "$OA"/box-login-aifoundry3.txt "$O2/"; touch "$O2/window.env"
echo "x" >> "$sd/session.log"
r=$(RB_OUT=$O2 RB_DESKTEST=1 bash "$T/$E/rb/s22_collect_e206.sh" A > "$S/C2.txt" 2>&1; echo $?)
ok "$r $(has 'COPY-BACK NOT EXACT' "$S/C2.txt")" "16 1" "$(stopline "$S/C2.txt" | cut -c1-140)"
step "CD: a session that ran (step 8's dry session copied as a session): steps 11, 12 and, after a stand-in data commit, 13"
dd=$(ls -d "$A3"/build/e206/T*-A-dry 2>/dev/null | tail -n 1)
O4=$S/out4; mkdir -p "$O4"; cp "$OA"/window.env "$OA"/box-login-aifoundry3.txt "$O4/"; touch "$O4/window.env"; echo 8 > "$O4/e206-T0-A.txt"
cp -a "$dd" "$A3/build/e206/T8-A"; rm -f "${A3:?}/build/e206/T8-A/dry.lock"     # a dry session keeps its lock file beside its manifest
r=$(run "$O4" CD1 s22_collect_e206.sh A); rm -rf "${T:?}/docs/reports/data/$TODAY-e206-matmul-sweep-aifoundry3"; r2=$(run "$O4" CD2 s23_data_e206.sh A)
dd2=$(cat "$O4/e206-data-dir-A.txt" 2>/dev/null)
$G add --sparse -f "$dd2" > /dev/null 2>&1; $G commit -q -m "desk test: a data commit (stand-in)" > /dev/null 2>&1
r3=$(run "$O4" CD3 s24_score_e206.sh A)
ok "$r $r2 $(has "COLLECTED docs/reports/data/$TODAY-e206-matmul-sweep-aifoundry3" "$S/CD2.txt") $( [ -s "$T/$dd2/data-e206.json" ] && echo data) $r3 $( [ -s "$O4/scores-e206-A.json" ] && echo scored)" \
   "0 0 1 data 0 scored" "$(grep -m1 'COLLECTED' "$S/CD2.txt" | cut -c1-140); $(grep -m1 'scored arm A' "$S/CD3.txt" | cut -c1-120)"
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
echo "SELFTEST-RB-E206 $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
}
main
