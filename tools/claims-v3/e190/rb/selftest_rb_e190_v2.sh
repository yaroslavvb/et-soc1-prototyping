#!/usr/bin/env bash
# E190 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum): the desk test of E190's runbook v2 with a FAKE
# ssh and rsync on two stand-in boxes, rb/selftest_rb_e190.sh's form (the kit, unchanged beside it). Its scratch repository is a shared,
# sparse clone of the lab clone this test runs from (so the registration 508d48d9 and the kit 241726bd are in its history, as on the card
# day) with note 1's files committed on top as one stand-in note commit, note 1's list a stand-in made here and pinned in the scratch copy of
# step 2 v2's NOTEPIN line (the one line this test changes in a copy). The stand-in boxes are aifoundry2's ~/claude/et-soc1-prototyping (a
# git clone of the scratch repository, at the registration: arm A's tree is a git checkout) and aifoundry1's ~/nekko (an rsync target),
# under the scratch; the stand-in ssh serves them with `bash -s` (and `true`) and refuses any other host or command; the stand-in rsync
# rewrites aifoundry1: and aifoundry2: paths onto them; the boxes' hostname, et-who and pgrep are stand-ins; cmake, the compilers and
# /opt/et are this desk's REAL ones (the build is the real build_e190_v2.sh: the kernel must come out at the registration's pin, and on the
# stand-in aifoundry1 the ET_DEVICES gate reads this desk's stock device layer). No lab box is reached. Cases:
#   A   the dry listing v2: every step exits 0, no call reaches the stand-ins (23 steps)
#   K   step 2 v2 with no window: 10;  W1 a window written for E189: 10;  W3 step 1 for another day: 10;  G step 2 v2 without RB_GITLOCK: 10
#   N   step 2 v2 run INSIDE the lab-git lock (nested): its pull cannot take the lock: 16 naming the pull
#   P1  step 2 v2 on the scratch repository: 0 (the three lists at their counts and bytes, HISTORY OK, the kit and note 1 found by content)
#   P2  the registration's list one line short: 16;  P3 the kit's list one line short: 16;  P4 note 1's list one line short: 16
#   H1  a committed edit of a registration file: 16 by the history check;  H2 a committed tools/claims-v3/e190/json.py (a shadow): 16
#   O   the look on both stand-in boxes (k6's s05, unchanged): FREE, our login recorded for the scrub
#   OL  E190's ours_live (rb_e190.sh, unchanged): a shell whose command string names session_e190_v2.sh is not a session of ours; a
#       session_e190_v2.sh run as a script is, counted by its own name, and NOT by the v1 name session_e190.sh (E183's s20 lesson)
#   SA  step 5 v2, arm A: the stand-in tree lacks note 1's commit: 17; with `pull`: fast-forwarded, HARNESS OK (v2): 0
#   SB  step 5 v2, arm B: the rsync onto the stand-in nekko, HARNESS OK (v2) on the box: 0
#   L1  THE TAILSCALE-LAPSE RULE: a login link on a read: 11, "<HH:MM:SS> aifoundry1 needs a check" appended to RB_LOCK, nothing retried
#   L2  a read that hangs: killed at its bound (the read class's bound shortened for this case only): 13
#   T   NO-THIRD-BUILD, v1 and v2 counted together: two v1 build starts recorded on aifoundry1 today: a v2 start is refused with 16
#   U   THE NEGATIVE CONTROL THROUGH THE RUNBOOK: arm B's rgm136 source changed on the box: RGM-BUILD-FAILED (the sources are not the
#       harness v2's), the wait 16; the source restored
#   BB  THE ET_DEVICES GATE THROUGH THE RUNBOOK (the verifier's finding 1): arm B's second start on the stand-in aifoundry1, this desk's
#       stock device layer: RGM-BUILD-FAILED "ET_DEVICES: the host has no ET_DEVICES", the wait 16, no RB_OUT/e190-built-v2-B.txt
#   X   a third start that day: NO-THIRD-BUILD, 16
#   BA  step 6 v2, arm A: start, wait (17 while it builds, then 0): the REAL build v2, the kernel at the pin aace138c..., the host's four
#       refusals, the ET_DEVICES reading (not a gate on aifoundry2), the record v2, the harness v2, the preflight v2 GO and both self-checks
#       read on the box; RB_OUT/e190-built-v2-A.txt;  L3 a cut wait (ssh's 255): 14
#   D   step 8 v2 on both stand-in boxes (run_e190_v2.py --dry with the v2 doubles there): 0 each
#   RS  THE REST RULE THROUGH STEP 9 v2: a session of ours ended 10 minutes ago on aifoundry2: 10, nothing launched
#   LA  the same ended 45 minutes ago: step 9 v2 launches the REAL session_e190_v2.sh and run_e190_v2.py, which stop at their box check
#       before any device (the stand-in tree has no telemetry reader; in a sandbox there is no /dev/et* and no card lock either): "no
#       device opened"; step 10 v2 reads the gate (16) with the manifest written; no smoke process started
#   WV  step 10 v2 while a session_e190_v2.sh of ours runs and its log has no end: 17 (RUN-RUNNING), never a false RUN-GONE;
#   WG  the same log with no session process: 14 (RUN-GONE)
#   C   step 11 v2 on LA's session: COPY-BACK EXACT: 0; step 12 (the kit's): the data directory (arm A), COLLECTED, the desk-path gate,
#       HISTORY OK: 0;  C2 one byte of a box file changed after the manifest: COPY-BACK NOT EXACT: 16
#   Z   no process of this test left running
#   bash tools/claims-v3/e190/rb/selftest_rb_e190_v2.sh <scratch dir> > <log>    (prints SELFTEST-RB-E190-V2 <n> of <m> PASS or FAIL)
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
A2=$B/aifoundry2/claude/et-soc1-prototyping; A1=$B/aifoundry1/nekko
E=tools/claims-v3/e190
REG=508d48d9a889ee91a9ff41140a906d103594978a
mkdir -p "$B/aifoundry2/claude" "$A1" "$BIN" "$BB"
sedi() { local f=${!#} t; t=$(mktemp "$S/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
main() {
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
# ---- the scratch repository: a shared sparse clone of the lab clone's HEAD, note 1's files as one stand-in commit
git clone -q --shared --no-checkout "$SRC" "$T" || return 2
G="git -C $T -c user.name=e190-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /docs/reports/data/2026-11-01-e105-gemm-layout/ /docs/reports/data/2026-11-01-e107-gemm-placement/ \
  /docs/reports/data/2026-11-01-e119-gemm-speed/ /docs/reports/data/2026-11-01-e95-real-tensors-energy/ /docs/reports/data/2026-11-02-e126-gemm-arms/ \
  /docs/reports/data/2026-11-02-e136-large-gemm/ /docs/reports/data/2026-11-02-e146-gemm-stores/ /docs/reports/data/2026-11-12-q166-ledger-v2/ \
  /docs/reports/data/2026-10-26-load-model/ || return 2
$G checkout -q -B main "$(git -C "$SRC" rev-parse HEAD)" || return 2
$G branch -q --set-upstream-to=origin/main 2>/dev/null
$G merge-base --is-ancestor "$REG" HEAD || { echo "the registration is not in the lab clone's history"; return 2; }
$G log --diff-filter=A --format=%H -- $E/KIT.md | grep -q . || { echo "the kit commit is not in the lab clone's history"; return 2; }
( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E ) | sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
mkdir -p "$T/$E/logs"
for spec in "selftest-run-e190-v2.txt SELFTEST-RUN-E190-V2 0 of 0 PASS" "realpath-e190-v2.txt REALPATH-E190-V2 0 of 0 PASS" \
            "desktest-build-e190-v2.txt DESKTEST-BUILD-E190-V2 0 of 0 PASS" "selftest-rb-e190-v2.txt SELFTEST-RB-E190-V2 0 of 0 PASS" \
            "dry-listing-e190-v2.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e190-v2.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"     # stand-ins always: this test's own log is not final while it runs
done
( cd "$T" && /usr/bin/python3 -I -B $E/check_e190_v2.py --make > /dev/null )
mklist() {  # note 1's stand-in list: every file this stand-in commit adds under E190's folder, but the list itself and step 2 v2
  ( cd "$T" && git ls-files --others --exclude-standard -- $E | grep -v -x -e "$E/SHA256SUMS-e190-kit-note1" -e "$E/rb/s03_desk_e190_v2.sh" |
      LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/note1-standin.txt"
  NOTEN=$(grep -c . "$S/note1-standin.txt"); cp "$S/note1-standin.txt" "$T/$E/SHA256SUMS-e190-kit-note1"; NOTEH=$(sha256sum "$S/note1-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^NOTEPIN=$E/SHA256SUMS-e190-kit-note1:[^ ]*#NOTEPIN=$E/SHA256SUMS-e190-kit-note1:$NOTEN:$NOTEH:top#" "$T/$E/rb/s03_desk_e190_v2.sh"
  grep -q "^NOTEPIN=$E/SHA256SUMS-e190-kit-note1:$NOTEN:$NOTEH:top" "$T/$E/rb/s03_desk_e190_v2.sh"
}
mklist || { echo "the scratch step 2 v2's NOTEPIN was not set"; return 2; }
$G add -A $E && $G commit -q -m "E190 runbook desk test v2: note 1's files (stand-in note commit)" || { echo "the scratch note commit failed"; return 2; }
NOTE=$($G rev-parse HEAD)
echo "scratch repository: a shared sparse clone of the lab clone's HEAD, note 1 as one stand-in commit ${NOTE:0:12}; note 1's stand-in list $NOTEN files"
# ---- the stand-in boxes: aifoundry2's tree a git clone at the registration (so it lacks note 1's commit), aifoundry1's an empty nekko
git clone -q --shared --no-checkout "$T" "$A2" || return 2
G2="git -C $A2 -c user.name=e190-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null"
$G2 sparse-checkout set --no-cone /tools/claims-v3/e190/ /tools/claims-v3/e136/ /tools/claims-v3/kinds/ /tools/claims-v3/e128/ \
  /tools/claims-v3/dmcmd_audit.py /tools/claims-v3/dmcmd_table.json || return 2
$G2 checkout -q -B main "$REG" && $G2 branch -q --set-upstream-to=origin/main || return 2
# ---- the stand-ins
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry1|aifoundry2) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; cat > /dev/null; echo "To authenticate, visit: https://login.tailscale.com/a/e190desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
if [ -e "$S/ssh-cut" ]; then rm -f "$S/ssh-cut"; cat > /dev/null; echo "ssh: connection closed (desk-test stand-in)" >&2; exit 255; fi
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'bash -s' and 'true' are served (got: \$cmd)" >&2; exit 97; }
cd "$B/\$host" || exit 1
exec env HOME="$B/\$host" STANDIN_HOST="\$host" PATH="$BB:\$PATH" bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry1|aifoundry2) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho "scp refused by the desk test" >&2\nexit 97\n' > "$BIN/scp"
printf '#!/bin/sh\necho "${STANDIN_HOST:-desk}"\n' > "$BB/hostname"
printf '#!/bin/sh\necho "No process holds an ET-SoC-1 device node or card lock."\n' > "$BB/et-who"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$BB/python3"
REAL_PGREP=$(command -v pgrep)
cat > "$BB/pgrep" <<EOF
#!/bin/bash
# the real pgrep less its caller's ancestors (the stand-in boxes run on the desk; on a card day the desk's step scripts run elsewhere)
anc=" "; p=\$\$
while [ -n "\$p" ] && [ "\$p" -gt 1 ]; do anc="\$anc\$p "; p=\$(ps -o ppid= -p "\$p" 2>/dev/null | tr -d ' '); done
"$REAL_PGREP" "\$@" | while IFS= read -r x; do case "\$anc" in *" \${x%% *} "*) ;; *) echo "\$x" ;; esac; done
EOF
chmod +x "$BIN"/* "$BB"/*
export PATH="$BIN:$PATH" RB_LOCK="$S/rb-lock.txt"
GL=$S/lab-git.lock; : > "$GL"
TODAY=$(TZ=America/Los_Angeles date +%F)
STARTHM=23:58; ENDHM=23:59           # the window is today's last minutes: the steps' budgets are E190_DESK_BUDGET_S (60 s) here
O=$S/out; mkdir -p "$O"
run() {  # run <log> <script> [args]: a step of the scratch repository's runbook with RB_OUT=$O
  local lg=$1; shift
  RB_OUT=$O RB_GITLOCK=$GL RB_DESKTEST=1 E190_DESK_BUDGET_S=60 bash "$T/$E/rb/$1" "${@:2}" > "$S/$lg.txt" 2>&1
  echo $?
}
step "A: the dry listing v2"
mkdir -p "$S/listing"
( cd "$T" && bash $E/rb/list_steps_e190_v2.sh "$S/listing" > "$S/A.txt" 2>&1 ); r=$?
ok "$r $(grep -c 'dry listing: 23 steps listed, 0 exited non-zero, 0 box calls' "$S/A.txt")" "0 1" "the dry listing: $(tail -n 1 "$S/A.txt")"
step "K: step 2 v2 with no window"
r=$(run K s03_desk_e190_v2.sh); ok "$r $( [ -s "$S/calls.log" ] && echo calls || echo nocalls)" "10 nocalls" "$(grep -m1 STOP "$S/K.txt" | cut -c1-120)"
step "W1: a window written for E189"
r=$(run W1a s02_window_e190.sh "$TODAY" "$STARTHM" "$ENDHM"); sedi -e 's/^RB_PLAN=e190/RB_PLAN=e189/' "$O/window.env"
r=$(run W1 s03_desk_e190_v2.sh); ok "$r" 10 "$(grep -m1 STOP "$S/W1.txt" | cut -c1-120)"
step "W3: step 1 for another day"
r=$(run W3 s02_window_e190.sh 2026-11-12 10:00 12:00); ok "$r" 10 "$(grep -m1 STOP "$S/W3.txt" | cut -c1-100)"
r=$(run W0 s02_window_e190.sh "$TODAY" "$STARTHM" "$ENDHM")
step "G: step 2 v2 without RB_GITLOCK"
r=$(RB_OUT=$O RB_DESKTEST=1 bash "$T/$E/rb/s03_desk_e190_v2.sh" > "$S/G.txt" 2>&1; echo $?); ok "$r" 10 "$(grep -m1 STOP "$S/G.txt" | cut -c1-100)"
step "N: step 2 v2 inside the lab-git lock (nested)"
r=$(RB_OUT=$O RB_GITLOCK=$GL RB_DESKTEST=1 RB_GITLOCK_T=3 flock -n "$GL" bash "$T/$E/rb/s03_desk_e190_v2.sh" > "$S/N.txt" 2>&1; echo $?)
ok "$r $(has 'pull(rc 14; a nested lab-git lock exits 75)' "$S/N.txt") $(grep -c 'child_rc=75' "$O/runbook.log")" "16 1 1" "$(stopline "$S/N.txt" | cut -c1-160)"
step "P1: step 2 v2 on the scratch repository"
r=$(run P1 s03_desk_e190_v2.sh); ok "$r $(has 'desk check v2: the window written today for E190' "$S/P1.txt")" "0 1" "$(grep -m1 'desk check v2:' "$S/P1.txt" | cut -c1-260)"
[ "$r" = 0 ] || tail -n 30 "$S/P1.txt"
step "P2: the registration's list one line short"
cp "$T/$E/SHA256SUMS-e190-registration" "$S/reg.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e190-registration"
r=$(run P2 s03_desk_e190_v2.sh); cp "$S/reg.bak" "$T/$E/SHA256SUMS-e190-registration"
ok "$r $(has 'SHA256SUMS-e190-registration(15 OK of 15' "$S/P2.txt")" "16 1" "$(stopline "$S/P2.txt" | cut -c1-200)"
step "P3: the kit's list one line short"
cp "$T/$E/SHA256SUMS-e190-kit" "$S/kit.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e190-kit"
r=$(run P3 s03_desk_e190_v2.sh); cp "$S/kit.bak" "$T/$E/SHA256SUMS-e190-kit"
ok "$r $(has 'SHA256SUMS-e190-kit(55 OK of 55' "$S/P3.txt")" "16 1" "$(stopline "$S/P3.txt" | cut -c1-200)"
step "P4: note 1's list one line short"
cp "$T/$E/SHA256SUMS-e190-kit-note1" "$S/note.bak"; sedi -e '$d' "$T/$E/SHA256SUMS-e190-kit-note1"
r=$(run P4 s03_desk_e190_v2.sh); cp "$S/note.bak" "$T/$E/SHA256SUMS-e190-kit-note1"
ok "$r $(has 'SHA256SUMS-e190-kit-note1(' "$S/P4.txt")" "16 1" "$(stopline "$S/P4.txt" | cut -c1-200)"
step "H1: a committed edit of a registration file"
echo "an edit" >> "$T/$E/E190.md"; $G commit -q -am "desk test: an edit of E190.md"
r=$(run H1 s03_desk_e190_v2.sh); $G reset -q --hard "$NOTE"
ok "$r $(has 'history' "$S/H1.txt")" "16 1" "$(stopline "$S/H1.txt" | cut -c1-200)"
step "H2: a committed shadowing addition (tools/claims-v3/e190/json.py)"
echo "# a shadow" > "$T/$E/json.py"; $G add "$E/json.py"; $G commit -q -m "desk test: a shadow"
r=$(run H2 s03_desk_e190_v2.sh); /usr/bin/python3 -I -B "$T/$E/rb/check_history_e190.py" tree > "$S/H2b.txt" 2>&1; $G reset -q --hard "$NOTE"
ok "$r $(has 'json.py' "$S/H2b.txt")" "16 1" "$(head -c 200 "$S/H2b.txt")"
step "O: the look on both stand-in boxes (k6's s05)"
r2=$(RB_OUT=$O bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry2 > "$S/O2.txt" 2>&1; echo $?)
r1=$(RB_OUT=$O bash "$T/tools/claims-v3/q141k-runbook/k6/s05_look_k6.sh" aifoundry1 > "$S/O1.txt" 2>&1; echo $?)
ok "$r2 $r1 $( [ -s "$O/box-login-aifoundry2.txt" ] && [ -s "$O/box-login-aifoundry1.txt" ] && echo logins)" "0 0 logins" "aifoundry2: $(grep -m1 'FREE\|HELD' "$S/O2.txt" | cut -c1-80); aifoundry1: $(grep -m1 'FREE\|HELD\|STOP' "$S/O1.txt" | cut -c1-80)"
step "OL: E190's ours_live: a v2 session counted by its own script's name, never by a command string, and not by the v1 name"
mkdir -p "$S/ol"; printf '#!/bin/bash\nsleep 25\n' > "$S/ol/session_e190_v2.sh"
( . "$T/$E/rb/rb_e190_v2.sh" > /dev/null 2>&1; e190_live_text ) > "$S/ol/live.sh"
printf '. "%s"\necho "$(ours_live session_e190_v2.sh) $(ours_live session_e190.sh) $(ours_live)"\n' "$S/ol/live.sh" > "$S/ol/count.sh"
n0=$(bash "$S/ol/count.sh")
setsid bash -c "sleep 25; : tools/claims-v3/e190/session_e190_v2.sh" < /dev/null > /dev/null 2>&1 &
p1=$!
n1=$(sleep 1; bash "$S/ol/count.sh")
setsid bash "$S/ol/session_e190_v2.sh" < /dev/null > /dev/null 2>&1 &
p2=$!
n2=$(sleep 1; bash "$S/ol/count.sh")
kill "$p1" "$p2" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do [ "$(bash "$S/ol/count.sh")" = "0 0 0" ] && break; sleep 0.5; done
n3=$(bash "$S/ol/count.sh")
ok "$n0|$n1|$n2|$n3" "0 0 0|0 0 0|1 0 1|0 0 0" "before: $n0; a shell whose command string names session_e190_v2.sh: $n1; a session_e190_v2.sh run as a script (v2 name, v1 name, any): $n2; after it ended: $n3"
step "SA: step 5 v2, arm A (the git tree)"
r=$(run SA1 s07_sync_e190_v2.sh A); r2=$(run SA2 s07_sync_e190_v2.sh A pull)
ok "$r $r2 $(has 'TREE-HAS-NOTE1' "$S/SA2.txt")$(has 'holds note 1.s commit; HARNESS OK (v2) there' "$S/SA2.txt")" "17 0 11" "$(grep -m1 'TREE-LACKS' "$S/SA1.txt" | cut -c1-110); $(grep -m1 'aifoundry2.s tree' "$S/SA2.txt" | cut -c1-120)"
step "L1: a login link on a read (step 5 v2, arm B's first read)"
touch "$S/ssh-login"; n0=$(grep -c . "$RB_LOCK" 2>/dev/null || echo 0)
r=$(run L1 s07_sync_e190_v2.sh B); n1=$(grep -c 'aifoundry1 needs a check' "$RB_LOCK" 2>/dev/null || echo 0)
ok "$r $((n1 - n0))" "11 1" "$(stopline "$S/L1.txt" | cut -c1-160)"
step "L2: a read that hangs (the read class's bound 3 s for this call)"
touch "$S/ssh-hang"
r=$(RB_READ_S=3 RB_OUT=$O RB_DESKTEST=1 bash "$T/$E/rb/s07_sync_e190_v2.sh" B > "$S/L2.txt" 2>&1; echo $?); rm -f "$S/ssh-hang"
ok "$r" 13 "$(stopline "$S/L2.txt" | cut -c1-140)"
step "SB: step 5 v2, arm B (the rsync)"
r=$(run SB s07_sync_e190_v2.sh B); ok "$r $(has 'HARNESS OK (v2) on the box' "$S/SB.txt")" "0 1" "$(grep -m1 'synced to' "$S/SB.txt" | cut -c1-160)"
step "T: NO-THIRD-BUILD on aifoundry1, v1 and v2 starts counted together"
mkdir -p "$A1/build"; for k in 1 2; do echo "$TODAY 01:0$k:00 PST a1-build-e190 started" >> "$A1/build/e190-build-attempts.txt"; done
r=$(run T s08_build_e190_v2.sh B start); rm -f "$A1/build/e190-build-attempts.txt"
ok "$r $(has NO-THIRD-BUILD "$S/T.txt")" "16 1" "$(stopline "$S/T.txt" | cut -c1-140)"
waitjob() {  # waitjob <tag> <script> <args...>: call a wait step until it says something other than 17 (at most 40 calls)
  local tag=$1 r k; shift
  for k in $(seq 1 40); do r=$(run "$tag-$k" "$@"); [ "$r" = 17 ] || { cp "$S/$tag-$k.txt" "$S/$tag.txt"; echo "$r"; return; }; done; echo 17
}
step "U: the negative control: arm B's source changed on the box"
echo "/* changed */" >> "$A1/tools/claims-v3/e136/rgm136/kernel/sparsity.c"
r=$(run U1 s08_build_e190_v2.sh B start); r2=$(waitjob U2 s08_build_e190_v2.sh B wait)
"$REAL_RSYNC" -a "$T/tools/claims-v3/e136/rgm136/kernel/sparsity.c" "$A1/tools/claims-v3/e136/rgm136/kernel/sparsity.c"
ok "$r $r2 $(has "RGM-BUILD-FAILED: rgm136's sources are not harness-e190-v2.json's" "$S/U2.txt")" "0 16 1" "$(grep -m1 'RGM-BUILD-FAILED' "$S/U2.txt" | cut -c1-140)"
step "BB: the ET_DEVICES gate: arm B's second start on the stand-in aifoundry1 (this desk's stock device layer)"
r=$(run BB1 s08_build_e190_v2.sh B start); r2=$(waitjob BB2 s08_build_e190_v2.sh B wait)
ok "$r $r2 $(has 'RGM-BUILD-FAILED: ET_DEVICES: the host has no ET_DEVICES' "$S/BB2.txt") $(grep -c '^    HOSTCHECK .*: ok' "$S/BB2.txt") $( [ -e "$O/e190-built-v2-B.txt" ] && echo built || echo none)" \
   "0 16 1 4 none" "$(grep -m1 'ETDEVICES\|RGM-BUILD-FAILED: ET' "$S/BB2.txt" | cut -c1-160)"
step "X: a third start that day"
r=$(run X s08_build_e190_v2.sh B start); ok "$r $(has NO-THIRD-BUILD "$S/X.txt")" "16 1" "$(stopline "$S/X.txt" | cut -c1-120)"
step "BA: step 6 v2, arm A: the real build v2"
r=$(run BA1 s08_build_e190_v2.sh A start); r2=$(waitjob BA2 s08_build_e190_v2.sh A wait)
ok "$r $r2 $(has 'KERNEL aace138caf8071cc' "$S/BA2.txt")$(has 'ETDEVICES host' "$S/BA2.txt")$(cat "$O/e190-built-v2-A.txt" 2>/dev/null)" "0 0 11rgm-v2" "$(grep -m1 'built today on' "$S/BA2.txt" | cut -c1-160)"
[ "$r2" = 0 ] || tail -n 25 "$S/BA2.txt"
step "L3: a cut wait (ssh's 255)"
touch "$S/ssh-cut"; r=$(run L3 s08_build_e190_v2.sh A wait); rm -f "$S/ssh-cut"
ok "$r" 14 "$(stopline "$S/L3.txt" | cut -c1-140)"
step "D: step 8 v2 on both stand-in boxes"
ra=$(run DA1 s10_dry_e190_v2.sh A start); ra2=$(waitjob DA2 s10_dry_e190_v2.sh A wait)
rb=$(run DB1 s10_dry_e190_v2.sh B start); rb2=$(waitjob DB2 s10_dry_e190_v2.sh B wait)
ok "$ra $ra2 $rb $rb2" "0 0 0 0" "$(grep -m1 'E190-DRY-V2' "$S/DA2.txt"); $(grep -m1 'E190-DRY-V2' "$S/DB2.txt")"
step "RS: the rest rule through step 9 v2 (a session of ours ended 10 minutes ago on aifoundry2)"
mkdir -p "$A2/build/e185/T1"
{ echo "$(date -d '-14 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-10 min' '+%F %T %Z') session end (T0 1)"; } > "$A2/build/e185/T1/session.log"
r=$(run RS s11_session_e190_v2.sh A); ok "$r $(has 'REFUSED: 10 minutes since E185' "$S/RS.txt")" "10 1" "$(grep -m1 'REFUSED' "$S/RS.txt" | cut -c1-140)"
step "LA: ended 45 minutes ago: step 9 v2 launches the REAL session v2, which stops at its box check"
{ echo "$(date -d '-50 min' '+%F %T %Z') session start (T0 1; desk-test stand-in)"; echo "$(date -d '-45 min' '+%F %T %Z') session end (T0 1)"; } > "$A2/build/e185/T1/session.log"
r=$(run LA s11_session_e190_v2.sh A); r2=$(waitjob LA2 s20_wait_e190_v2.sh A)
t0=$(cat "$O/e190-T0-A.txt" 2>/dev/null)
sd=$A2/build/e190/T$t0-A
procs=$(find "$sd" -name 'proc*.out' 2>/dev/null | wc -l | tr -d ' ')
ok "$r $r2 $(has 'no device opened' "$sd/session.log") $(has 'run_e190_v2.py' "$sd/queue.json") $( [ -s "$sd/MANIFEST.sha256" ] && echo manifest) $procs" "0 16 1 1 manifest 0" \
   "$(grep -m1 'no device opened' "$sd/session.log" | cut -c1-200)"
step "WV / WG: step 10 v2 counts a running session_e190_v2.sh by its name (never a false RUN-GONE); with none running: RUN-GONE"
O3=$S/out3; mkdir -p "$O3"; cp "$O/window.env" "$O/box-login-aifoundry2.txt" "$O3/"; touch "$O3/window.env"; echo 7 > "$O3/e190-T0-A.txt"
echo 7 > "$A2/build/q141k/e190A.T0"; mkdir -p "$A2/build/e190/T7-A"
echo "$(date '+%F %T %Z') session start (T0 7; desk-test stand-in, no end)" > "$A2/build/e190/T7-A/session.log"
mkdir -p "$S/wv"; printf '#!/bin/bash\nsleep 30\n' > "$S/wv/session_e190_v2.sh"
setsid bash "$S/wv/session_e190_v2.sh" < /dev/null > /dev/null 2>&1 &
p3=$!
sleep 1
rv=$(RB_OUT=$O3 RB_DESKTEST=1 RB_WAIT_LOOP_S=4 bash "$T/$E/rb/s20_wait_e190_v2.sh" A > "$S/WV.txt" 2>&1; echo $?)
kill "$p3" 2>/dev/null
for k in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$p3" 2>/dev/null || break; sleep 0.5; done
rg=$(RB_OUT=$O3 RB_DESKTEST=1 RB_WAIT_LOOP_S=4 bash "$T/$E/rb/s20_wait_e190_v2.sh" A > "$S/WG.txt" 2>&1; echo $?)
echo "$t0" > "$A2/build/q141k/e190A.T0"
ok "$rv $(has 'RUN-RUNNING e190 arm A' "$S/WV.txt") $(has 'RUN-GONE' "$S/WV.txt") $rg $(has 'RUN-GONE e190 arm A' "$S/WG.txt")" "17 1 0 14 1" \
   "with a session_e190_v2.sh running: $(grep -m1 'RUN-' "$S/WV.txt" | cut -c1-80); with none: $(grep -m1 'RUN-' "$S/WG.txt" | cut -c1-80)"
step "C: step 11 v2 (arm A) and step 12"
r=$(run C1 s22_collect_e190_v2.sh A); r2=$(run C2s s23_data_e190.sh)
ok "$r $r2 $(has 'COLLECTED docs/reports/data/' "$S/C2s.txt") $(has '/home/' "$T/docs/reports/data/$TODAY-e190-large-gemm/aifoundry2/session.log")" "0 0 1 0" \
   "$(grep -m1 'COLLECTED' "$S/C2s.txt" | cut -c1-160)"
step "C2: one byte of a box file changed after the manifest"
O2=$S/out2; mkdir -p "$O2"; cp "$O"/window.env "$O"/e190-T0-A.txt "$O"/box-login-aifoundry2.txt "$O2/"; touch "$O2/window.env"
echo "x" >> "$sd/session.log"
r=$(RB_OUT=$O2 RB_DESKTEST=1 bash "$T/$E/rb/s22_collect_e190_v2.sh" A > "$S/C2.txt" 2>&1; echo $?)
ok "$r $(has 'COPY-BACK NOT EXACT' "$S/C2.txt")" "16 1" "$(stopline "$S/C2.txt" | cut -c1-140)"
step "Z: nothing of this test left running"
left=0
for p in /proc/[0-9]*; do
  c=$(readlink "$p/cwd" 2>/dev/null) || continue
  case "$c" in "$S"|"$S"/*) [ "${p#/proc/}" = "$$" ] || left=$((left + 1)) ;; esac
done
ok "$left" 0 "processes whose working directory is under the scratch directory (the stand-in boxes' jobs, sessions, builds)"
echo
echo "box calls the stand-ins served: $(grep -c . "$S/calls.log" 2>/dev/null || echo 0) (all to the stand-in boxes; no lab box was reached)"
echo "SELFTEST-RB-E190-V2 $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
}
main
