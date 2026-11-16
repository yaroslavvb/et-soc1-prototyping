#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): the desk test of E202's runbook with a FAKE ssh and rsync on a
# stand-in box, E189's runbook desk test's form (tools/claims-v3/e189/rb/selftest_rb_e189.sh), with THE BOX'S BUILD REAL (E196's: the
# program built by build_e202.sh with this desk's own /opt/et, its .text read, its host read by its behaviour). Its scratch repository is
# a shared, sparse clone of the lab clone this test runs from (so the program commit and E202's registration commit are in its history,
# as on the card day) with the kit's files committed on top as one stand-in kit commit, the kit list a stand-in made here and pinned in
# the scratch copy of step 2's KITPIN line (the one line this test changes in a copy). The stand-in box is aifoundry3's ~/aifoundry under
# the scratch, its build/e202files seeded with the checked inputs of a desk build made today (the real fetch from the mirrors is
# desk/desktest_build_e202.sh's case B1); the stand-in ssh serves it with `bash -s` and refuses any other host; the stand-in rsync rewrites
# aifoundry3: paths onto it; the stand-in box has a stand-in build/ettelem/ettelem (config only: TDP 0 W / 65 C / 600 MHz) for k6's step 7
# and a free et-who. No lab box is reached. Cases:
#   A   the dry listing: every step exits 0, no call reaches the stand-ins;
#   K, W1-W3, G  the window rule and RB_GITLOCK, each refused (10) before any call;  N  step 2 inside the lab-git lock: 16 naming the pull;
#   P1  step 2 on the scratch repository: 0, every list at its count and bytes (12; 75; 23; 39; 17 and the kit's), HISTORY OK, the program
#       and the registration found by their content;  P2-P4, H1  a short registration list, a short kit list (16 each), an unknown list
#       (reported, 0), an edited registration file (16 by the history check);
#   H2  an added tools/claims-v3/e202/json.py (session_e202.sh runs run_e202.py there without -I on the box) and H5 an added
#       workloads/sparseparity/tools/json.py (the collection runs the reducer there without -I): step 2 stops with 16 by the history
#       check, naming each;  H7 an added _strptime.py at the top;  H8 the same names not committed; then clean again;
#   DT  AN E202 DATUM IN ANY REF: a side branch adding docs/reports/data/<day>-e202-x/: step 2 stops with 16;
#   S   steps 5 and 6 on the stand-in box with the REAL build: E202-BUILT (the .text at its pin, 18 of 18 files, the host's behaviour), the
#       harness with the built kernel, the preflight and the self-check read on the box, RB_OUT/e202-built.txt;
#   X   a second start after E202-BUILT today: 10;  T  NO-THIRD-BUILD: two starts recorded today: 16;
#   L1-L3  a login link (11 and the lock line, nothing retried), a hang (13), a cut wait (14, no reading);
#   RD  STEP 7 BEFORE THE REST (E192's data note 1): an E195-form session (its committed log) ended 10 minutes ago: s09 refuses (10), and
#       no config read reaches the box;  RD2 the same session 45 minutes ago: the rest opens, k6's step 7 runs unchanged (its config read
#       through E128's guard and the stand-in ettelem, its holder rule): 0, the time stamped in RB_OUT/e202-step7.txt;
#   D   step 8, the box's dry pass (run_e202.py --dry on the stand-in box): E202-DRY rc=0 bursts=4;
#   RS  THE REST RULE THROUGH STEP 9: the E195-form session ended 10 minutes ago: 10, nothing launched;
#   SD  THE SAME-DAY RULE: an E202 session that opened the card today (a log with its first card command): step 9 refuses (10);
#   LA  rest 45 minutes, no E202 session today: step 9 launches the REAL session_e202.sh and run_e202.py, which refuse before anything
#       here (the host's name is not aifoundry3: "refused, no device opened"), with the manifest; step 10 reads the gate (16);
#   W10 THE WAIT STEP'S PATTERN on the real name: a stand-in session_e202.sh still running is RUN-RUNNING (17); a decoy whose name ends in it
#       (s11_a3_session_e202.sh) is not the session (RUN-GONE, 14);
#   C   step 11 on LA's session: COPY-BACK EXACT, A GATE STOP'S RECORD under docs/reports/gate-stops/ (never docs/reports/data/), COLLECTED,
#       the desk-path gate, HISTORY OK;  C2 one byte of a box file changed after the manifest: COPY-BACK NOT EXACT, 16;
#   SC  step 13 with no committed data directory: 10;
#   Z   no process of this test left running.
# fix-e202 (verify-e202's findings 2, 3 and 6 and note 11): P1 also reads ledger v3 in HEAD and E202's v3 note re-made (V3NOTE CHECK
#   PASS); V3 the note removed while ledger v3 is in HEAD: step 2 stops with 16 naming it; HG a HUNG marker in a session log of ours on
#   the box (2 hours old, past every rest): step 9 refuses (10); WT4 a session that ended with its manifest and no gate line but
#   runner.rc 1 and a CRASH line: step 10 says 16, naming the exit and the crash; WT5 runner.rc not written: 14. Every log the rest
#   rule reads here has its file time set to its last line's (THE ACTIVITY FLOOR reads file times, as on a box).
#   bash tools/claims-v3/e202/rb/selftest_rb_e202.sh <scratch dir> <a box tree built today by build_e202.sh> > <log>
# On a box with a card (aifoundry2) run it ONLY inside W/nodev.sh (no /dev/et*, an empty /run/lock): cases S and LA run the real host's
# checks and the real runner; and only while THE QUIET DESK FLAG is absent. Prints SELFTEST-RB-E202 <n> of <m> PASS or FAIL last.
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
BUILT=${2:?a box tree built today by build_e202.sh (its build/e202files seed the stand-in box)}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK RB_WAIT_LOOP_S; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
for d in /dev/et*; do [ -e "$d" ] || continue; [ -c "$d" ] && { echo "REFUSED: $d is a device here: run this inside W/nodev.sh"; exit 2; }; done
for c in timeout sha256sum flock cmake; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
REAL_TIMEOUT=$(command -v timeout); REAL_RSYNC=$(command -v rsync); REAL_PGREP=$(command -v pgrep)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree box bin out boxbin; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; B=$S/box; BIN=$S/bin; BOXT=$B/aifoundry3/aifoundry
mkdir -p "$BOXT" "$BIN" "$S/boxbin"
E=tools/claims-v3/e202
main() {
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aqE -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
REG=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/E202.md | tail -n 1)
[ -n "$REG" ] || { echo "no registration commit in the lab clone's history"; return 2; }
git clone -q --shared --no-checkout "$SRC" "$T" || return 2
G="git -C $T -c user.name=e202-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /workloads/ /docs/reports/data/2026-11-16-q193-mnistmlp/ /docs/reports/data/2026-11-12-q166-ledger-v2/ \
  /docs/reports/data/2026-11-04-q142m-m10/ /docs/reports/data/2026-09-23-energy-manual/ /docs/reports/data/2026-11-16-e195-x09-dramtoggle-aifoundry3/ \
  /docs/reports/data/2026-11-02-q136w-write-audit/ || return 2
$G checkout -q -B main "$REG" || return 2
$G branch -q --set-upstream-to=origin/main 2>/dev/null
( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E ) | sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
mkdir -p "$T/$E/logs"
for spec in "desktest-build-e202.txt DESKTEST-BUILD-E202 0 of 0 PASS" "selftest-run-e202.txt SELFTEST-RUN-E202 0 of 0 PASS" \
            "desktest-realpath-e202.txt DESKTEST-REALPATH-E202 0 of 0 PASS" "realbytes-e202.txt REALBYTES-E202 0 of 0 PASS" \
            "selftest-rb-e202.txt SELFTEST-RB-E202 0 of 0 PASS" "selftest-rest-e202.txt SELFTEST-REST-E202 0 of 0 PASS" \
            "dry-listing-e202.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e202.txt dmcmd_audit: GO (stand-in)" \
            "checks-e202.txt CHECKS-E202 0 of 0 PASS"; do
  f=${spec%% *}; [ -f "$T/$E/logs/$f" ] || printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"
done
( cd "$T" && git show "$REG" --name-only --format= -- $E ) > "$S/reg-files.txt"
mkkit() {
  rm -f "$T/$E/SHA256SUMS-e202-kit"
  ( cd "$T" && find $E -type f ! -name 'SHA256SUMS-e202-kit' ! -path "$E/rb/s03_desk_e202.sh" ! -name '*.pyc' | LC_ALL=C sort |
      while IFS= read -r f; do sha256sum "$f"; done ) | grep -v -F -f "$S/reg-files.txt" > "$S/kit-standin.txt"
  KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e202-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
  sed -i -e "s#^KITPIN=$E/SHA256SUMS-e202-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e202-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e202.sh"
}
( cd "$T" && /usr/bin/python3 -I -B $E/check_e202.py --make > /dev/null )
mkkit
$G add -A $E && $G commit -q -m "E202 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; return 2; }
grep -q "^KITPIN=$E/SHA256SUMS-e202-kit:$KITN:$KITH:top" "$T/$E/rb/s03_desk_e202.sh" || { echo "the scratch step 2's KITPIN was not set"; return 2; }
echo "scratch repository: a shared sparse clone at the registration ${REG:0:12}, the kit as one stand-in commit $($G rev-parse --short=12 HEAD); the kit list's stand-in $KITN files"
# ---- the stand-ins
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; echo "To authenticate, visit: https://login.tailscale.com/a/e202desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
if [ -e "$S/ssh-cut" ]; then rm -f "$S/ssh-cut"; cat > /dev/null; echo "ssh: connection closed (desk-test stand-in)" >&2; exit 255; fi
cat > "$S/remote-\$\$.sh"
env -u RB_DESKTEST -u E202_DESK_BUDGET_S HOME="$B/\$host" PATH="$S/boxbin:\$PATH" bash "$S/remote-\$\$.sh" < /dev/null
r=\$?; rm -f "$S/remote-\$\$.sh"; exit \$r
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho aifoundry3\n' > "$S/boxbin/hostname"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
printf '#!/bin/sh\necho "No process holds an ET-SoC-1 device node or card lock."\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\necho "et-lab-manifest (desk-test stand-in): no device read"\n' > "$S/boxbin/et-lab-manifest"
# the stand-in box's pgrep: the real one, less its caller's ancestors (E189's port: on a card day the desk's step scripts run on another
# machine), and only the processes OF THE STAND-IN BOX (their working directory under this test's scratch): the box shares this desk
# with other lanes' processes, whose session_eNNN.sh names its guard would otherwise count (a real box sees only its own)
cat > "$S/boxbin/pgrep" <<EOF
#!/bin/bash
anc=" "; p=\$PPID
while [ -n "\$p" ] && [ "\$p" -gt 1 ] 2>/dev/null; do anc="\$anc\$p "; p=\$(awk '{print \$4}' /proc/\$p/stat 2>/dev/null); done
out=""; for q in \$("$REAL_PGREP" "\$@"); do
  case "\$anc" in *" \$q "*) continue ;; esac
  case "\$(readlink /proc/\$q/cwd 2>/dev/null)" in "$S"|"$S"/*) out="\$out\$q
" ;; esac
done
[ -n "\$out" ] || exit 1
printf '%s' "\$out"
EOF
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
for n in ssh rsync scp sudo curl; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$S/boxbin/$n"; done
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
mkdir -p "$BOXT/build/ettelem" "$BOXT/build"
printf '#!/bin/sh\n[ "$1" = config ] && { echo "{\\"tdp_w\\":0,\\"temp_threshold_c\\":65,\\"power_state\\":0,\\"minion_mhz\\":600,\\"minion_mv\\":523,\\"standin\\":true}"; exit 0; }\nexit 97\n' > "$BOXT/build/ettelem/ettelem"
chmod +x "$BOXT/build/ettelem/ettelem"
cp -a "$BUILT/build/e202files" "$BOXT/build/e202files"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_DESKTEST=1 E202_DESK_BUDGET_S=60
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/gitlock"
R=$T/$E/rb; K6=$T/tools/claims-v3/q141k-runbook/k6
TODAY=$(TZ=America/Los_Angeles date +%F)
cd "$T" || return 2

step "A. the dry listing"
bash "$R/list_steps_e202.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
tail -n 1 "$S/dry-listing.txt"
ok "$rc.$(grep -c . "$S/calls.log")" "0.0" "A every step 0, no call to the stand-ins"

step "K, W1-W3, G. the window rule and the lab-git lock"
RB_OUT="$S/out-k" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/k.txt" 2>&1; k=$?
mkdir -p "$S/out-w"
RB_OUT="$S/out-w" bash "$R/s02_window_e202.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
touch -d '-1 day' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/w1.txt" 2>&1; w1=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e202.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
sed -i 's/^RB_PLAN=e202$/RB_PLAN=e196/' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/w2.txt" 2>&1; w2=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e202.sh" "$(date -d '+1 day' +%F)" 10:00 12:00 > "$S/w3.txt" 2>&1; w3=$?
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e202.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1
RB_OUT="$S/out-p" bash "$R/s03_desk_e202.sh" > "$S/g.txt" 2>&1; g=$?
ok "$k.$(has 'no window in RB_OUT' "$S/k.txt").$w1.$(has 'not written today' "$S/w1.txt").$w2.$(has 'written for e196' "$S/w2.txt").$w3.$(has 'is not today' "$S/w3.txt").$g.$(has 'RB_GITLOCK is not set' "$S/g.txt").$(grep -c . "$S/calls.log")" \
  "10.1.10.1.10.1.10.1.10.1.0" "K, W1-W3, G each refused (10) before any call"

step "N. step 2 run inside the lab-git lock (nested): its pull cannot take the lock"
RB_GITLOCK_T=2 /usr/bin/flock -n -E 75 "$S/gitlock" env RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/n.txt" 2>&1; n=$?
stopline "$S/n.txt"
ok "$n.$(has 'pull' "$S/n.txt")" "16.1" "N a nested step 2 stops with 16 naming its pull"

step "P1. step 2 on the scratch repository"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check:|STOP' "$S/p1.txt" | cut -c1-600
ok "$p1.$(has 'the lists at their pinned counts and bytes \(12; 75; 23; 39; 17\)' "$S/p1.txt").$(has 'HISTORY OK' "$S/p1.txt").$(has 'ledger v3 in HEAD yes, E202.s v3 note in HEAD yes \(V3NOTE CHECK PASS\)' "$S/p1.txt")" "0.1.1.1" "P1 step 2 passes at every pin, HISTORY OK, the program and the registration found by their content, ledger v3 in HEAD and E202's v3 note re-made"

step "V3. E202's v3 note removed while ledger v3 is in HEAD (fix-e202, finding 3)"
$G rm -q $E/E202-ledger-v3-note.md; $G commit -q -m "desk test: the v3 note removed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/v3.txt" 2>&1; v3=$?; $G reset -q --hard HEAD~1
stopline "$S/v3.txt"
ok "$v3.$(has 'ledger-v3-note\(ledger v3 in HEAD; the note in HEAD: no\)' "$S/v3.txt")" "16.1" "V3 step 2 refuses (16) naming the missing v3 note"

step "P2-P4, H1. a short registration list; a short kit list; an unknown list; an edited registration file"
sed -i '$d' "$T/$E/SHA256SUMS-e202-registration"; $G commit -q -am "desk test: the registration's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/p2.txt" 2>&1; p2=$?; $G reset -q --hard HEAD~1
sed -i '$d' "$T/$E/SHA256SUMS-e202-kit"; $G commit -q -am "desk test: the kit's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/p3.txt" 2>&1; p3=$?; $G reset -q --hard HEAD~1
( cd "$T" && sha256sum $E/E202.md > $E/notes-SHA256SUMS-x ); $G add $E/notes-SHA256SUMS-x; $G commit -q -m "desk test: an unknown list"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/p4.txt" 2>&1; p4=$?; $G reset -q --hard HEAD~1
printf '\n' >> "$T/$E/plan_e202.py"; $G commit -q -am "desk test: a registration file edited"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/h1.txt" 2>&1; h1=$?; $G reset -q --hard HEAD~1
ok "$p2.$(has 'SHA256SUMS-e202-registration\(11 OK of 11; pinned 12' "$S/p2.txt").$p3.$(has "SHA256SUMS-e202-kit\($((KITN - 1)) OK of $((KITN - 1)); pinned $KITN" "$S/p3.txt").$p4.$(has 'notes-SHA256SUMS-x' "$S/out-p/runbook.log").$h1.$(has 'history' "$S/h1.txt")" \
  "16.1.16.1.0.1.16.1" "P2-P4, H1: each pin refused and named; the unknown list reported; the edit refused by the history check"

step "H2, H5, H7, H8. the shadow cases"
printf '# desk test: would shadow json for run_e202.py (run there without -I on the box)\n' > "$T/$E/json.py"
$G add $E/json.py; $G commit -q -m "desk test: json.py beside run_e202.py"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/h2.txt" 2>&1; h2=$?
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e202.py tree ) > "$S/h2b.txt" 2>&1; h2b=$?
$G reset -q --hard HEAD~1
printf '# desk test: would shadow json for the reducer\n' > "$T/workloads/sparseparity/tools/json.py"
$G add workloads/sparseparity/tools/json.py; $G commit -q -m "desk test: json.py beside the reducer"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e202.py tree ) > "$S/h5.txt" 2>&1; h5=$?
$G reset -q --hard HEAD~1
printf '# desk test\n' > "$T/_strptime.py"; $G add --sparse _strptime.py; $G commit -q -m "desk test: _strptime at the top"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e202.py tree ) > "$S/h7.txt" 2>&1; h7=$?
rm -f "${T:?}/_strptime.py"; $G reset -q --hard HEAD~1
printf '# desk test\n' > "$T/workloads/sparseparity/tools/gzip.py"; printf '# desk test\n' > "$T/$E/re.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e202.py tree ) > "$S/h8.txt" 2>&1; h8=$?
rm -f "${T:?}/workloads/sparseparity/tools/gzip.py" "${T:?}/$E/re.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e202.py tree ) > "$S/h8c.txt" 2>&1; h8c=$?
cut -c1-260 "$S/h2b.txt" "$S/h5.txt" "$S/h7.txt" "$S/h8.txt" "$S/h8c.txt"
ok "$h2.$(has 'history' "$S/h2.txt").$h2b.$(has 'tools/claims-v3/e202/json.py \(as json\)' "$S/h2b.txt").$h5.$(has 'workloads/sparseparity/tools/json.py \(as json\)' "$S/h5.txt").$h7.$(has '_strptime.py \(as _strptime\)' "$S/h7.txt").$h8.$(has 'not committed' "$S/h8.txt").$h8c" \
  "16.1.16.1.16.1.16.1.16.1.0" "H2 H5 H7 H8 each shadow refused by the history check, named; the tree clean again after"

step "DT. an E202 datum in another ref"
$G checkout -q -b desk-datum
mkdir -p "$T/docs/reports/data/$TODAY-e202-x"; printf 'desk test\n' > "$T/docs/reports/data/$TODAY-e202-x/README.md"
$G add --sparse "docs/reports/data/$TODAY-e202-x/README.md"; $G commit -q -m "desk test: an E202 datum on a side branch"
$G checkout -q main; rm -rf "${T:?}/docs/reports/data/$TODAY-e202-x"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e202.sh" > "$S/dt.txt" 2>&1; dt=$?
$G branch -q -D desk-datum
stopline "$S/dt.txt"
ok "$dt.$(has 'e202-datum-exists' "$S/dt.txt")" "16.1" "DT an E202 data path in any ref: step 2 refuses (16)"

export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
bash "$R/s02_window_e202.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1
bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/look.txt" 2>&1
step "S. steps 5 and 6 on the stand-in box, the REAL build"
bash "$R/s07_a3_sync_e202.sh" > "$S/s5.txt" 2>&1; s5=$?
bash "$R/s08_a3_build_e202.sh" start > "$S/s6a.txt" 2>&1; s6a=$?
n17=0; for i in $(seq 1 40); do bash "$R/s08_a3_build_e202.sh" wait > "$S/s6b.txt" 2>&1; s6b=$?; [ "$s6b" -eq 17 ] || break; n17=$((n17 + 1)); done
grep -E 'E202|HOST-BEHAVIOUR|built today|STOP' "$S/s6b.txt" | cut -c1-200
ok "$s5.$s6a.$s6b.$(cat "$RB_OUT/e202-built.txt" 2>/dev/null).$(has 'HARNESS OK: 33' "$S/s6b.txt").$(has 'HOST-BEHAVIOUR OK: 20 of 20' "$S/s6b.txt").$(has 'E202-FILES OK: 18 of 18' "$S/s6b.txt")" "0.0.0.E202-BUILT.1.1.1" \
  "S synced; built for real (after $n17 calls of 17): the .text at its pin, the files, the host's behaviour; the checks on the box"

step "X, T. a second start after E202-BUILT today; NO-THIRD-BUILD"
bash "$R/s08_a3_build_e202.sh" start > "$S/x.txt" 2>&1; x=$?
AT=$BOXT/build/e202-build-attempts.txt
for z in rc out; do [ -e "$BOXT/build/q141k/jobs/a3-build-e202.$z" ] && touch -d '-2 day' "$BOXT/build/q141k/jobs/a3-build-e202.$z"; done
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e202 started" >> "$AT"
bash "$R/s08_a3_build_e202.sh" start > "$S/t.txt" 2>&1; t=$?
for z in rc out; do [ -e "$BOXT/build/q141k/jobs/a3-build-e202.$z" ] && touch "$BOXT/build/q141k/jobs/a3-build-e202.$z"; done
ok "$x.$(has 'was built today' "$S/x.txt").$t.$(has 'NO-THIRD-BUILD' "$S/t.txt")" "10.1.16.1" "X refused (10); T a third start the same day refused (16)"

step "L1-L3. the kits' form: a login link, a hang, a cut wait"
ln0=$(grep -c . "$RB_LOCK"); touch "$S/ssh-login"
bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/l1.txt" 2>&1; l1=$?
ln1=$(grep -c . "$RB_LOCK")
touch "$S/ssh-hang"; RB_READ_S=3 bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/l2.txt" 2>&1; l2=$?
touch "$S/ssh-cut"; bash "$R/s08_a3_build_e202.sh" wait > "$S/l3.txt" 2>&1; l3=$?
ok "$l1.$((ln1 - ln0)).$(tail -n 1 "$RB_LOCK" | grep -cE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry3 needs a check$').$l2.$l3.$(has 'no reading' "$S/l3.txt")" "11.1.1.13.14.1" \
  "L1 a login link: 11 and the lock line; L2 a hang killed at its bound: 13; L3 a cut wait: 14, no reading"

step "RD, RD2. step 7 before the rest has opened; then after it"
mkdir -p "$BOXT/build/e195/T1794822000"
SL=$BOXT/build/e195/T1794822000/session.log
cp "$T/docs/reports/data/2026-11-16-e195-x09-dramtoggle-aifoundry3/session/session.log" "$SL"
setend() { local cur new; cur=$(grep -a ' session end' "$SL" | tail -n 1 | cut -c1-23); new=$(TZ=America/Los_Angeles date -d "$1" '+%F %T %Z'); sed -i "s/^$cur session end/$new session end/" "$SL"; touch -d "$1" "$SL"; }
setend '-10 min'
c0=$(grep -c 'ssh ' "$S/calls.log")
bash "$R/s09_a3_reads_e202.sh" > "$S/rd.txt" 2>&1; rd=$?
c1=$(grep -c 'ssh ' "$S/calls.log")
stopline "$S/rd.txt"
setend '-45 min'
bash "$R/s09_a3_reads_e202.sh" > "$S/rd2.txt" 2>&1; rd2=$?
grep -E 'rest:|config|FREE|STOP' "$S/rd2.txt" | cut -c1-200
ok "$rd.$(has 'the rest has not run: REFUSED: 1?[0-9] minutes since E195' "$S/rd.txt").$((c1 - c0)).$rd2.$(has 'rest: 4[5-6] minutes since E195' "$S/rd2.txt").$(has 'config TDP 0 W / 65 C / 600 MHz, et-who clean' "$S/rd2.txt").$([ -s "$RB_OUT/e202-step7.txt" ] && echo 1 || echo 0)" \
  "10.1.2.0.1.1.1" "RD step 7 refused before the rest (two calls: the probe and the rest read; no config read); RD2 the rest open, k6's step 7 ran, the time stamped"

step "D. step 8, the box's dry pass"
bash "$R/s10_a3_dry_e202.sh" start > "$S/d1.txt" 2>&1; d1=$?
for i in $(seq 1 30); do bash "$R/s10_a3_dry_e202.sh" wait > "$S/d2.txt" 2>&1; d2=$?; [ "$d2" -eq 17 ] || break; done
grep -E 'E202-DRY|smoke gate' "$S/d2.txt" | cut -c1-200
ok "$d1.$d2.$(has 'E202-DRY rc=0 bursts=4' "$S/d2.txt")" "0.0.1" "D the dry pass: the smoke gate, four bursts, rc 0"

step "RS. the rest rule through step 9: the E195-form session 10 minutes ago"
setend '-10 min'
bash "$R/s11_a3_session_e202.sh" > "$S/rs.txt" 2>&1; rs=$?; stopline "$S/rs.txt"
ok "$rs.$(has 'REFUSED: 1?[0-9] minutes since E195' "$S/rs.txt").$(ls "$BOXT/build/e202" 2>/dev/null | grep -c '^T[0-9]*$')" "10.1.0" "RS refused (10) naming E195, nothing launched"
setend '-45 min'

step "SD. the same-day rule: an E202 session opened the card today"
mkdir -p "$BOXT/build/e202/T1794820001"
printf '%s session start (T0 1794820001; plan FULL)\n%s first card command: config start, stamped as it starts at 00:00:00.000 (the cap counts from it)\n%s session end (T0 1794820001)\n' \
  "$(TZ=America/Los_Angeles date -d '-50 min' '+%F %T %Z')" "$(TZ=America/Los_Angeles date -d '-50 min' '+%F %T %Z')" "$(TZ=America/Los_Angeles date -d '-49 min' '+%F %T %Z')" > "$BOXT/build/e202/T1794820001/session.log"
bash "$R/s11_a3_session_e202.sh" > "$S/sd.txt" 2>&1; sd=$?; stopline "$S/sd.txt"
rm -rf "${BOXT:?}/build/e202/T1794820001"
ok "$sd.$(has 'opened the card today' "$S/sd.txt")" "10.1" "SD step 9 refuses a second session the same day (10)"

step "HG. a HUNG marker in a session log of ours on the box (fix-e202, note 11): step 9 refuses"
mkdir -p "$BOXT/build/e197/T1794800000"; HL=$BOXT/build/e197/T1794800000/session.log
printf '%s session start (T0 1794800000; E197, desk test)\n%s HUNG: a device process did not end after its timeout TERM (desk test)\n%s session end (T0 1794800000)\n' \
  "$(TZ=America/Los_Angeles date -d '-125 min' '+%F %T %Z')" "$(TZ=America/Los_Angeles date -d '-124 min' '+%F %T %Z')" "$(TZ=America/Los_Angeles date -d '-120 min' '+%F %T %Z')" > "$HL"
touch -d '-120 min' "$HL"
bash "$R/s11_a3_session_e202.sh" > "$S/hg.txt" 2>&1; hg=$?; stopline "$S/hg.txt"
rm -rf "${BOXT:?}/build/e197"
ok "$hg.$(has 'REFUSED: a HUNG marker of ours on the box' "$S/hg.txt").$(ls "$BOXT/build/e202" 2>/dev/null | grep -c '^T[0-9]*$')" "10.1.0" "HG step 9 refuses (10) on a HUNG marker, nothing launched"

step "LA. step 9 launches the REAL session (refused before anything here: the host's name); step 10 reads the gate"
bash "$R/s11_a3_session_e202.sh" > "$S/la.txt" 2>&1; la=$?
grep -E 'LAUNCHED|rest:|same-day:' "$S/la.txt" | cut -c1-200
cp "$RB_OUT/e202-T0.txt" "$S/la-t0.txt" 2>/dev/null
sleep 4
for i in 1 2 3 4; do bash "$R/s20_wait_e202.sh" > "$S/w.txt" 2>&1; w=$?; [ "$w" -eq 17 ] || break; done
grep -E 'refused|RUN-|MANIFEST|GATE' "$S/w.txt" | cut -c1-200
ok "$la.$(has 'rest: 4[5-6] minutes since E195' "$S/la.txt").$w.$(has 'MANIFEST-WRITTEN' "$S/w.txt").$(has 'refused, no device opened: the host' "$S/w.txt").$(has 'RUNNER-RC 2' "$S/w.txt")" "0.1.16.1.1.1" \
  "LA launched after 45 minutes' rest; the real runner refused before anything (rc 2) with its manifest; step 10 reads the gate (16)"

step "W10. the wait step's pattern on the real name, and a decoy"
WT0=1794821111; mkdir -p "$BOXT/build/e202/T$WT0" "$S/wstand/tools/claims-v3/e202"
printf '%s session start (T0 %s; plan FULL)\n' "$(TZ=America/Los_Angeles date '+%F %T %Z')" "$WT0" > "$BOXT/build/e202/T$WT0/session.log"
echo "$WT0" > "$BOXT/build/q141k/e202.T0"; echo "$WT0" > "$RB_OUT/e202-T0.txt"
printf '#!/bin/bash\nsleep 25\n' > "$S/wstand/tools/claims-v3/e202/session_e202.sh"
( cd "$S/wstand" && exec bash tools/claims-v3/e202/session_e202.sh ) > /dev/null 2>&1 &
wp=$!
RB_WAIT_LOOP_S=4 bash "$R/s20_wait_e202.sh" > "$S/w10a.txt" 2>&1; w10a=$?
kill "$wp" 2>/dev/null; wait "$wp" 2>/dev/null
cp /usr/bin/sleep "$S/s11_a3_session_e202.sh"
"$S/s11_a3_session_e202.sh" 25 & dp=$!
RB_WAIT_LOOP_S=4 bash "$R/s20_wait_e202.sh" > "$S/w10b.txt" 2>&1; w10b=$?
kill "$dp" 2>/dev/null; wait "$dp" 2>/dev/null
rm -rf "${BOXT:?}/build/e202/T$WT0"
ok "$w10a.$(has 'RUN-RUNNING' "$S/w10a.txt").$w10b.$(has 'RUN-GONE' "$S/w10b.txt")" "17.1.14.1" "W10 the real name read as the session (17); a decoy ending in it is not (RUN-GONE, 14)"

step "WT4, WT5. the runner's exit status after the session's end (fix-e202, finding 2)"
WT1=1794822222; WD=$BOXT/build/e202/T$WT1; mkdir -p "$WD"
{ echo "$(TZ=America/Los_Angeles date '+%F %T %Z') session start (T0 $WT1; plan FULL)"
  echo "$(TZ=America/Los_Angeles date '+%F %T %Z') CRASH: NotADirectoryError: [Errno 20] Not a directory (desk test) (the runner's own fault: nothing further starts, the closing follows, the runner exits 1)"
  echo "$(TZ=America/Los_Angeles date '+%F %T %Z') session end (T0 $WT1)"; } > "$WD/session.log"
echo "x  session.log" > "$WD/MANIFEST.sha256"; echo 1 > "$WD/runner.rc"
echo "$WT1" > "$BOXT/build/q141k/e202.T0"; echo "$WT1" > "$RB_OUT/e202-T0.txt"
bash "$R/s20_wait_e202.sh" > "$S/wt4.txt" 2>&1; wt4=$?; stopline "$S/wt4.txt"
rm -f "$WD/runner.rc"
bash "$R/s20_wait_e202.sh" > "$S/wt5.txt" 2>&1; wt5=$?; stopline "$S/wt5.txt"
rm -rf "${BOXT:?}/build/e202/T$WT1"
ok "$wt4.$(has 'the runner exited 1 after the session.s end and stopped at no gate \(CRASHED e202: CRASH: NotADirectoryError' "$S/wt4.txt").$wt5.$(has 'runner.rc is not written' "$S/wt5.txt")" "16.1.14.1" \
  "WT4 runner.rc 1 with no gate line: 16, the exit and the crash named; WT5 runner.rc not written: 14"
cp "$S/la-t0.txt" "$RB_OUT/e202-T0.txt"; cp "$S/la-t0.txt" "$BOXT/build/q141k/e202.T0"

step "C, C2. step 11 on LA's session: a gate stop's record; then one byte changed after the manifest"
bash "$R/s22_collect_e202.sh" > "$S/c.txt" 2>&1; c=$?
grep -E 'COPY-BACK|COLLECTED|HISTORY|STOP' "$S/c.txt" | cut -c1-200
t0=$(cat "$RB_OUT/e202-T0.txt")
D0=docs/reports/gate-stops/$TODAY-e202-mnist-int8-T$t0-aifoundry3
ok "$c.$(has 'COPY-BACK EXACT' "$S/c.txt").$(has 'a gate stop record' "$S/c.txt").$([ -f "$T/$D0/SHA256SUMS" ] && echo 1 || echo 0).$([ -e "$T/docs/reports/data/$TODAY-e202-mnist-int8-aifoundry3" ] && echo 1 || echo 0).$(grep -rl '/home/' "$T/$D0" 2>/dev/null | grep -c .)" \
  "0.1.1.1.0.0" "C collected exactly as a gate stop's record under docs/reports/gate-stops/, never data; no home path in it"
rm -rf "${T:?}/$D0" "${RB_OUT:?}/e202-raw"
printf 'x' >> "$BOXT/build/e202/T$t0/session.log"
bash "$R/s22_collect_e202.sh" > "$S/c2.txt" 2>&1; c2=$?
ok "$c2.$(has 'COPY-BACK NOT EXACT' "$S/c2.txt").$([ -e "$T/$D0" ] && echo 1 || echo 0)" "16.1.0" "C2 a changed byte: not exact, 16, nothing written"
rm -rf "${RB_OUT:?}/e202-raw"

step "SC. step 13 with no committed data directory"
bash "$R/s24_score_e202.sh" > "$S/sc.txt" 2>&1; sc=$?
ok "$sc.$(has 'is not committed' "$S/sc.txt")" "10.1" "SC the scorer refuses before the data commit (10)"

step "Z. no process of this test left running"
z=$(pgrep -f "$S/" 2>/dev/null | grep -c .)
ok "$z" "0" "Z nothing left"
echo
echo "SELFTEST-RB-E202 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<lab clone>#g; s#$HOME#~#g"
exit "${PIPESTATUS[0]}"
