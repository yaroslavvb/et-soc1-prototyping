#!/usr/bin/env bash
# E193 (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum): the desk test of E193's runbook with a FAKE ssh and rsync on a STAND-IN
# BOX, E189's runbook desk test's form (rb/selftest_rb_e189.sh). Its scratch repository is a shared, sparse clone of the lab clone this
# test runs from (so 49a4152e and E193's registration commit are in its history, as on the card day), checked out at the registration
# commit, with the kit's files committed on top as one stand-in kit commit: EVERY FILE UNDER tools/claims-v3/e193 THAT THE REGISTRATION
# COMMIT DID NOT ADD, COMMITTED OR NOT, as the clone holds it (fix-e193, verify-e193's finding 1: the kit lane's form took only the
# uncommitted ones, so on the committed kit its scratch had no kit and it stopped at its setup; this form runs the same whether the kit
# is committed, landed or not yet), and the scratch's upstream a local branch at the registration commit (step 2's pull is then a no-op
# in every condition, never a fast-forward onto the real kit commit); the kit list a stand-in made here by the real list's rule and
# pinned in the scratch copy of step 2's KITPIN line (the one line this test changes in a copy: the real list holds this test's log). The
# stand-in box is aifoundry3's home
# under the scratch (its tree ~/aifoundry); the stand-in ssh serves it with `bash -s` (its host name aifoundry3 from a stand-in
# `hostname` on the box's PATH, E189's way) and refuses any other host or command; the stand-in rsync rewrites aifoundry3: paths onto it; the box's device tools are
# fake_card_e193.py's (the sampler and its config through the box's own copy of E128's guard, et-who), its et-lab-manifest a stand-in,
# its pgrep and ps the real ones less every process outside the stand-in box (a process whose working directory is not under the box's home:
# on a card day the desk's step scripts run on another machine; here they and any other desk test of ours run beside it). THE BOX'S
# BUILD IS REAL: step 6 runs build_e193.sh there, cmake with this desk's /opt/et, the real kernel's bodies check and the real host's
# refusals (inside the no-device sandbox, ET_DEVICES=99, an unreadable kernel). No lab box is reached.
#   A    the dry listing: every step exits 0, no call reaches the stand-ins
#   W1-W5  the window rule: step 2 with no window (10); a window written yesterday (10); one written for E189 (10); step 1 for another
#        day (10); step 9 given sitting B with sitting A's window (10)
#   G    step 2 without RB_GITLOCK (10);  N  step 2 run INSIDE the lab-git lock (nested): its pull cannot take the lock, 16 naming it
#   P1   step 2 on the scratch repository: 0, both lists at their counts and bytes, HISTORY OK, the registration and the kit found by
#        their content;  P2 the registration's list one line short: 16;  P3 the kit's list one line short: 16;  P4 a list with
#        SHA256SUMS in its name, not pinned: reported (0);  H1 a committed edit of a registration file: 16 (the history check);
#        H2 an added tools/claims-v3/json.py: 16 naming it;  H3 an untracked tools/claims-v3/e183/rb/re.py: HISTORY FAIL (not committed)
#   D1   an E193 datum before sitting A (sitting A's own data path committed): 16;  D2 the same before sitting B: 0 (allowed);
#        D3 a sitting-B path before sitting B: 16;  D4 a gate stop's record committed (docs/reports/gate-stops/...) before sitting A: 0,
#        no datum (E193.md 11: no sitting, no data; fix-e193)
#   S    step 5, the sync, into E193's root on the box: 0, HARNESS OK there;  B  step 6 start, then wait: THE REAL BUILD on the box:
#        X04-BUILT (the bodies check, the host's three refusals, the listing SAME x3), RB_OUT/e193-built.txt;  B2 a second start after
#        X04-BUILT today: 10;  B3 NO-THIRD-BUILD: two failed starts recorded today: 16;  SD step 5 with a synced file changed and not
#        committed: 16 (fix-e193);  NB steps 8 and 9 from a window with no build today: 10 each (fix-e193)
#   L1   a login link at a read: 11, "<HH:MM:SS> aifoundry3 needs a check" appended to RB_LOCK (a copy of the round's lock file);
#        L2 a read that hangs: killed at its bound (the read class's bound shortened for this case only): 13;  L3 step 6's wait cut
#        (ssh's 255, nothing printed): 14, "no reading"
#   R    k6's reads (s09) on the stand-in box: 0 (TDP 0 W / 65 C / 600 MHz from the stand-in config, et-who clean)
#   Y    step 8, the dry pass, the session itself with DRY=1 on the box: 0, both listings SAME
#   RS   THE REST RULE THROUGH STEP 9: an E192-form session ended 10 minutes ago on the box: 10, nothing launched
#   BA   step 9 for sitting B with no sitting A on the box: 10 ("B never runs before A");  BC step 9 for sitting B after a sitting A whose
#        main run ended without a registered stop (a crash): 10 (fix-e193);  SG step 9 for sitting A on a day a sitting A's smoke gate
#        failed: 10, "no sitting that day" (E193.md 11; fix-e193)
#   LA   the rest satisfied: step 9 launches THE REAL session_e193.sh (DRY unset) detached; THE WAIT FINDS IT BY ITS REAL SCRIPT NAME:
#        RUN-RUNNING (17) while its holder check is held 25 s by the stand-in; then the session's own count of ops nodes finds none (the
#        sandbox has no /dev/et*): GATE-STOP before any card read (no device opened); the wait reads GATE-STOPPED (16), the manifest
#        written; ours_live counts it while it runs (a second launch is refused, 10)
#   C    step 11 on that session: COPY-BACK EXACT, THE GATE STOP'S RECORD (docs/reports/gate-stops/<day>-...-T<T0>-aifoundry3, never
#        under docs/reports/data: fix-e193), COLLECTED, E183 note 5's desk-path gate CLEAN, HISTORY OK: 0;  C2 again: 10;  C3 one byte of
#        a box file changed after its manifest (a new RB_OUT): COPY-BACK NOT EXACT, 16;  C4 C3's RB_OUT again (its raw copy there): 10;
#        C5 a session log that does not say clearly how it ended (a GATE-STOP line beside a main run): 16, nothing copied (fix-e193)
#   RT   THE RETRY: step 9 launches sitting A again after that gate stop (it opened no device, so the rest rule skips it): 0; the wait
#        reads its GATE-STOPPED (16) (fix-e193: a gate-stopped sitting is tried again, no dead end)
#   WR   THE WAIT ON THE REAL-PATH DESK TEST'S OWN SESSIONS (when its scratch is given): sitting A's (two passes, then the operator's stop):
#        RUN-ENDED, "main run ended at a registered stop" (0); sitting B's (whole): RUN-ENDED (0); its G1 (a smoke gate stop): 16; its X1
#        (the main run's crash): MAIN-CRASHED, 16 (fix-e193)
#   CR   step 11 on the real-path sitting A session; step 13 before its data commit: 10 (fix-e193); its data committed in the scratch
#        repository; then step 13: the registered reducer and the checker on the committed data: 0, x04-e193-A.json and
#        checks-e193-A.json;  CR3 step 13 with a data file changed and not committed: 16;  CR4 with a committed change SHA256SUMS does not
#        hold: 16;  CR5 THE DATA README FORM'S OWN "Re-make it" COMMANDS, read from DATA-README-FORM-e193.md and run on the committed
#        data: the same x04.json as step 13, byte for byte, and the checker's reading (fix-e193, verify-e193's finding 7)
#   Z    no process of this test left on the stand-in box
#   bash tools/claims-v3/e193/rb/selftest_rb_e193.sh <scratch dir> [<the real-path desk test's scratch dir> [<a lock file whose COPY
#        is RB_LOCK>]] > <log>
#   (prints SELFTEST-RB-E193 <n> of <m> PASS or FAIL). On a box with a card (aifoundry2) run it ONLY inside the no-device sandbox, between
#   01:00 and 22:45 Pacific (the stand-in logs of BC and SG are dated 45 minutes back, on today's date).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
RP=${2:-}
LOCKFROM=${3:-}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK RB_WAIT_LOOP_S; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
for c in timeout sha256sum shasum flock cmake rsync; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
for p in /dev/et*; do [ -c "$p" ] && { echo "REFUSED: $p is a character device here: run this test inside the no-device sandbox"; exit 2; }; done
[ "$(TZ=America/Los_Angeles date +%H%M)" -lt 2245 ] || { echo "REFUSED: run before 22:45 Pacific (step 9 needs a window with an hour of sitting A's cap left today)"; exit 2; }
[ "$(TZ=America/Los_Angeles date +%H%M)" -ge 0100 ] || { echo "REFUSED: run after 01:00 Pacific (BC's and SG's stand-in logs are dated 45 minutes back, today)"; exit 2; }
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree box bin boxbin; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; BOXH=$S/box/aifoundry3; TREE=$BOXH/aifoundry; BIN=$S/bin; BB=$S/boxbin; ST=$S/box-state
mkdir -p "$TREE/build" "$BIN" "$BB" "$ST"
E=tools/claims-v3/e193
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
sedi() { local f=${!#} t; t=$(mktemp "$S/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
echo "E193 runbook desk test, $(date '+%F %T %Z'), $(/usr/bin/python3 --version 2>&1), $(cmake --version | head -n 1); scratch outside the repository"
# ---- the scratch repository: a shared sparse clone at the registration, then the kit's files as one stand-in commit
REG=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/E193.md | tail -n 1)
[ -n "$REG" ] || { echo "no registration commit in the lab clone's history"; exit 2; }
git clone -q --shared --no-checkout "$SRC" "$T" || exit 2
G="git -C $T -c user.name=e193-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ || exit 2
$G checkout -q -B main "$REG" || exit 2
$G branch -q -f e193-desktest-registration "$REG" && $G branch -q --set-upstream-to=e193-desktest-registration || exit 2   # step 2's pull: a no-op
( cd "$SRC" && git show "$REG" --name-only --format= -- $E ) > "$S/reg-files.txt"
KITC=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/KIT.md | tail -n 1)
( cd "$SRC" && { git ls-files --cached --others --exclude-standard -- $E | grep -v -x -F -f "$S/reg-files.txt"; git diff --name-only HEAD -- $E; } ) |
  sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
[ -f "$T/$E/KIT.md" ] && [ -f "$T/$E/harness_e193.py" ] && [ -f "$T/$E/rb/s03_desk_e193.sh" ] || { echo "the kit's files did not reach the scratch tree"; exit 2; }
mkdir -p "$T/$E/logs"
for spec in "desktest-realpath-e193.txt DESKTEST-REALPATH-E193 0 of 0 PASS" "selftest-rb-e193.txt SELFTEST-RB-E193 0 of 0 PASS" \
            "selftest-rest-e193.txt SELFTEST-REST-E193 0 of 0 PASS" "dry-listing-e193.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" \
            "dmcmd-audit-e193.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"     # always a stand-in line: this test never reads its own (or any) log being written
done
( cd "$T" && /usr/bin/python3 -I -B $E/harness_e193.py --make > /dev/null )
rm -f "$T/$E/SHA256SUMS-e193-kit"
( cd "$T" && find $E -type f ! -name 'SHA256SUMS-e193-kit' ! -path "$E/rb/s03_desk_e193.sh" ! -name '*.pyc' | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) |
  grep -v -F -f "$S/reg-files.txt" > "$S/kit-standin.txt"
KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e193-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
sedi -e "s#^KITPIN=$E/SHA256SUMS-e193-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e193-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e193.sh"
grep -q "^KITPIN=$E/SHA256SUMS-e193-kit:$KITN:$KITH:top" "$T/$E/rb/s03_desk_e193.sh" || { echo "the scratch step 2's KITPIN was not set"; exit 2; }
$G add -A $E && $G commit -q -m "E193 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; exit 2; }
echo "scratch repository: a shared sparse clone at the registration ${REG:0:12}, the kit as one stand-in commit $($G rev-parse --short=12 HEAD) (its files from the clone, $([ -n "$KITC" ] && echo "the kit committed there at ${KITC:0:12}" || echo "the kit not committed there")); the kit list's stand-in $KITN files; upstream e193-desktest-registration"
# ---- the stand-ins
REAL_RSYNC=$(command -v rsync); REAL_PGREP=$(command -v pgrep)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; echo "To authenticate, visit: https://login.tailscale.com/a/e193desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
if [ -e "$S/ssh-cut" ]; then rm -f "$S/ssh-cut"; cat > /dev/null; echo "ssh: connection closed (desk-test stand-in)" >&2; exit 255; fi
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'true' and 'bash -s', not '\$cmd'" >&2; exit 97; }
cd "$BOXH" || exit 1
exec /usr/bin/env HOME="$BOXH" PATH="$BB:/usr/bin:/bin" E193_FAKE_STATE="$ST" USER=boxuser LOGNAME=boxuser bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$BOXH/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
FAKE=$T/$E/fake_card_e193.py
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s etwho "$@"\n' "$FAKE" > "$BB/et-who"
printf '#!/bin/sh\necho "et-lab-manifest: a desk-test stand-in (no sysfs read)"\n' > "$BB/et-lab-manifest"
printf '#!/bin/sh\necho aifoundry3\n' > "$BB/hostname"      # the box's name (the session's host-name gate reads it)
cat > "$BB/pgrep" <<EOF
#!/bin/bash
# the stand-in box's pgrep: the real one, less every process whose working directory is outside the stand-in box's home
out=""
for q in \$("$REAL_PGREP" "\$@"); do
  c=\$(readlink "/proc/\$q/cwd" 2>/dev/null) || continue
  case "\$c/" in "$BOXH"/*) out="\$out\$q
" ;; esac
done
[ -n "\$out" ] || exit 1
printf '%s' "\$out"
EOF
cat > "$BB/ps" <<EOF_PS
#!/bin/bash
# the stand-in box's ps for the form k6's hold_read and the session's two rules use (ps -eo uid=,pid=,comm=): the real one's lines, less
# every process outside the stand-in box (its working directory not under the box's home), as the stand-in pgrep
[ "\$*" = "-eo uid=,pid=,comm=" ] || exec /usr/bin/ps "\$@"
/usr/bin/ps -eo uid=,pid=,comm= | while read -r u p c; do d=\$(readlink "/proc/\$p/cwd" 2>/dev/null) || continue; case "\$d/" in "$BOXH"/*) echo "\$u \$p \$c" ;; esac; done
EOF_PS
for n in ssh rsync scp sudo; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$BB/$n"; done
chmod +x "$BIN"/* "$BB"/*
mkdir -p "$TREE/tools/claims-v3/e128" "$TREE/build/ettelem"
cp -p "$T/tools/claims-v3/e128/ettelem_guard.sh" "$TREE/tools/claims-v3/e128/ettelem_guard.sh"
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s ettelem "$@"\n' "$FAKE" > "$TREE/build/ettelem/ettelem"; chmod +x "$TREE/build/ettelem/ettelem"
if [ -n "$LOCKFROM" ]; then cp "$LOCKFROM" "$S/lock.txt" || exit 2; else : > "$S/lock.txt"; fi   # RB_LOCK: a copy, never the round's own file
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$S/gitlock"
R=$T/$E/rb; K6=$T/tools/claims-v3/q141k-runbook/k6
TODAY=$(TZ=America/Los_Angeles date +%F)
cd "$T" || exit 2
win() { mkdir -p "$1"; RB_OUT="$1" bash "$R/s02_window_e193.sh" "$2" "$TODAY" 23:50 23:59 > /dev/null 2>&1; }

step "A. the dry listing"
bash "$R/list_steps_e193.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
tail -n 1 "$S/dry-listing.txt"
ok "$rc.$(grep -c . "$S/calls.log")" "0.0" "A every step 0, no call to the stand-ins"

step "W1-W5, G. the window rule and the lab-git lock"
RB_OUT="$S/out-k" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/w1.txt" 2>&1; w1=$?
win "$S/out-w" A; touch -d '-1 day' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/w2.txt" 2>&1; w2=$?
win "$S/out-w" A; sedi -e 's/^RB_PLAN=e193$/RB_PLAN=e189/' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/w3.txt" 2>&1; w3=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e193.sh" A "$(date -d '+1 day' +%F)" 10:00 12:00 > "$S/w4.txt" 2>&1; w4=$?
win "$S/out-w" A
RB_OUT="$S/out-w" bash "$R/s11_a3_session_e193.sh" B > "$S/w5.txt" 2>&1; w5=$?
RB_OUT="$S/out-w" bash "$R/s03_desk_e193.sh" > "$S/g.txt" 2>&1; g=$?
ok "$w1.$(has 'no window in RB_OUT' "$S/w1.txt").$w2.$(has 'not written today' "$S/w2.txt").$w3.$(has 'written for e189' "$S/w3.txt").$w4.$(has 'is not today' "$S/w4.txt").$w5.$(has "sitting A's, not sitting B's" "$S/w5.txt").$g.$(has 'RB_GITLOCK is not set' "$S/g.txt").$(grep -c . "$S/calls.log")" \
  "10.1.10.1.10.1.10.1.10.1.10.1.0" "W1-W5, G each refused (10) before any call"

step "N. step 2 run inside the lab-git lock (nested): its pull cannot take the lock"
RB_DESKTEST=1 RB_GITLOCK_T=2 /usr/bin/flock -n -E 75 "$S/gitlock" env RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/n.txt" 2>&1; n=$?
stopline "$S/n.txt"
ok "$n.$(has 'pull' "$S/n.txt")" "16.1" "N a nested step 2 stops with 16 naming its pull (never run step 2 inside the lock)"

step "P1. step 2 on the scratch repository"
mkdir -p "$S/out-p"; win "$S/out-p" A
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check|STOP' "$S/p1.txt" | cut -c1-500
ok "$p1.$(has "the lists at their pinned counts and bytes (29; the kit's $KITN)" "$S/p1.txt").$(has 'the paths clean, HISTORY OK' "$S/p1.txt")" \
  "0.1.1" "P1 step 2 passes at every pin, HISTORY OK, the registration and the kit found by their content"

step "P2-P4, H1-H3. a short registration list; a short kit list; an unknown list; an edited registration file; shadows"
sedi -e '$d' "$T/$E/SHA256SUMS-e193-registration"; $G commit -q -am "desk test: the registration's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/p2.txt" 2>&1; p2=$?; $G reset -q --hard HEAD~1
sedi -e '$d' "$T/$E/SHA256SUMS-e193-kit"; $G commit -q -am "desk test: the kit's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/p3.txt" 2>&1; p3=$?; $G reset -q --hard HEAD~1
( cd "$T" && sha256sum $E/E193.md > $E/notes-SHA256SUMS-x ); $G add $E/notes-SHA256SUMS-x; $G commit -q -m "desk test: an unknown list"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/p4.txt" 2>&1; p4=$?; $G reset -q --hard HEAD~1
printf '\n' >> "$T/$E/proposal/src/arms.tsv"; $G commit -q -am "desk test: a registration file edited"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/h1.txt" 2>&1; h1=$?; $G reset -q --hard HEAD~1
printf '# desk test: a stand-in that would shadow json for dmcmd_audit.py\n' > "$T/tools/claims-v3/json.py"; $G add tools/claims-v3/json.py
$G commit -q -m "desk test: json.py beside dmcmd_audit.py"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/h2.txt" 2>&1; h2=$?
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e193.py tree ) > "$S/h2b.txt" 2>&1; $G reset -q --hard HEAD~1
printf '# desk test\n' > "$T/tools/claims-v3/e183/rb/re.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e193.py tree ) > "$S/h3.txt" 2>&1; h3=$?; rm -f "${T:?}/tools/claims-v3/e183/rb/re.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e193.py tree ) > "$S/hc.txt" 2>&1; hc=$?
cut -c1-260 "$S/h2b.txt" "$S/h3.txt"
ok "$p2.$(has 'SHA256SUMS-e193-registration(28 OK of 28; pinned 29' "$S/p2.txt").$p3.$(has "SHA256SUMS-e193-kit($((KITN - 1)) OK of $((KITN - 1)); pinned $KITN" "$S/p3.txt").$p4.$(has 'notes-SHA256SUMS-x' "$S/out-p/runbook.log").$h1.$(has 'history' "$S/h1.txt").$h2.$(has 'a shadowing addition: tools/claims-v3/json.py (as json)' "$S/h2b.txt").$h3.$(has 'a shadowing file not committed: tools/claims-v3/e183/rb/re.py (as re)' "$S/h3.txt").$hc" \
  "16.1.16.1.0.1.16.1.16.1.16.1.0" "P2-P4, H1-H3: each pin refused and named; the unknown list reported; the edit and the shadows refused by the history check; clean again after"

step "D1-D3. no E193 datum in any ref"
mkdir -p "$T/docs/reports/data/2026-11-16-e193-x04-clock-sitting-a-aifoundry3"; echo x > "$T/docs/reports/data/2026-11-16-e193-x04-clock-sitting-a-aifoundry3/x.txt"
$G add --sparse docs/reports/data/2026-11-16-e193-x04-clock-sitting-a-aifoundry3/x.txt; $G commit -q -m "desk test: sitting A's data path"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/d1.txt" 2>&1; d1=$?
mkdir -p "$S/out-pb"; win "$S/out-pb" B
RB_OUT="$S/out-pb" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/d2.txt" 2>&1; d2=$?
mkdir -p "$T/docs/reports/data/2026-11-16-e193-x04-clock-sitting-b-aifoundry3"; echo x > "$T/docs/reports/data/2026-11-16-e193-x04-clock-sitting-b-aifoundry3/x.txt"
$G add --sparse docs/reports/data/2026-11-16-e193-x04-clock-sitting-b-aifoundry3/x.txt; $G commit -q -m "desk test: a sitting B data path"
RB_OUT="$S/out-pb" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/d3.txt" 2>&1; d3=$?
rm -rf "${T:?}/docs/reports/data/2026-11-16-e193-x04-clock-sitting-a-aifoundry3" "${T:?}/docs/reports/data/2026-11-16-e193-x04-clock-sitting-b-aifoundry3"
$G reset -q --hard HEAD~2
stopline "$S/d1.txt"; stopline "$S/d3.txt"
ok "$d1.$(has 'e193-datum(1 paths before sitting A)' "$S/d1.txt").$d2.$d3.$(has "e193-datum(1 paths besides sitting A's before sitting B)" "$S/d3.txt")" "16.1.0.16.1" \
  "D1 an E193 datum before sitting A: 16; D2 sitting A's own before sitting B: 0; D3 a sitting-B path before sitting B: 16"
GS=docs/reports/gate-stops/2026-11-16-e193-x04-clock-sitting-a-T1794700000-aifoundry3
mkdir -p "$T/$GS"; echo x > "$T/$GS/x.txt"; $G add --sparse "$GS/x.txt"; $G commit -q -m "desk test: a gate stop's record"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e193.sh" > "$S/d4.txt" 2>&1; d4=$?
rm -rf "${T:?}/docs/reports/gate-stops"; $G reset -q --hard HEAD~1
stopline "$S/d4.txt"
ok "$d4.$(has 'E193 data paths in any ref: 0 ' "$S/d4.txt")" "0.1" "D4 a gate stop's record committed before sitting A: 0 (no datum: E193.md 11's 'no sitting: no data')"

step "S, B. the sync, then THE REAL BUILD on the stand-in box"
mkdir -p "$S/out-a"; win "$S/out-a" A
RB_OUT="$S/out-a" bash "$R/s07_a3_sync_e193.sh" > "$S/s.txt" 2>&1; s=$?
tail -n 1 "$S/s.txt"
( cd "$TREE/build/claims-v3/aifoundry3/e193" && /usr/bin/python3 -I -B tools/claims-v3/e193/harness_e193.py --box --root . ) > "$S/s2.txt" 2>&1
RB_OUT="$S/out-a" bash "$R/s08_a3_build_e193.sh" start > "$S/b1.txt" 2>&1; b1=$?
b2=17; k=0; while [ "$b2" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-a" bash "$R/s08_a3_build_e193.sh" wait > "$S/b2.txt" 2>&1; b2=$?; k=$((k + 1)); done
grep -E '^ +(COMPILER|ELF|BODIES|HOST|LISTING|SAMPLER|X04)|STOP|built today' "$S/b2.txt" | cut -c1-220
RB_OUT="$S/out-a" bash "$R/s08_a3_build_e193.sh" start > "$S/b3.txt" 2>&1; b3=$?
ok "$s.$(has 'HARNESS OK' "$S/s2.txt").$b1.$b2.$(grep -c '^LISTING SAME' "$S/out-a/e193-built.txt").$(has '^BODIES CHECK PASS' "$S/out-a/e193-built.txt").$(has '^HOST-BEHAVIOUR OK' "$S/out-a/e193-built.txt").$(has '^X04-BUILT rc=0' "$S/out-a/e193-built.txt").$b3.$(has 'was built today' "$S/b3.txt")" \
  "0.1.0.0.3.1.1.1.10.1" "S the sync, HARNESS OK in E193's root on the box; B the real build: BODIES CHECK PASS, HOST-BEHAVIOUR OK, LISTING SAME x3, X04-BUILT; B2 a second start refused (10)"

step "B3. NO-THIRD-BUILD"
AT=$TREE/build/claims-v3/aifoundry3/e193/build/e193-build-attempts.txt
cp -p "$AT" "$S/attempts.keep"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e193 started" >> "$AT"
cp -p "$TREE/build/q141k/jobs/a3-build-e193.out" "$S/jobout.keep"; sed -i 's/^X04-BUILT rc=0/X04-BUILD-FAILED desk test/' "$TREE/build/q141k/jobs/a3-build-e193.out"
RB_OUT="$S/out-a" bash "$R/s08_a3_build_e193.sh" start > "$S/b4.txt" 2>&1; b4=$?
cp -p "$S/attempts.keep" "$AT"; cp -p "$S/jobout.keep" "$TREE/build/q141k/jobs/a3-build-e193.out"
stopline "$S/b4.txt"
ok "$b4.$(has 'NO-THIRD-BUILD' "$S/b4.txt")" "16.1" "B3 a third start the same day refused (16)"

step "SD, NB. the sync with a synced file not committed; steps 8 and 9 with no build today"
printf '# desk test: one line more, not committed\n' >> "$T/$E/check_e193.py"
RB_OUT="$S/out-a" bash "$R/s07_a3_sync_e193.sh" > "$S/sd.txt" 2>&1; sd=$?
$G checkout -q -- "$E/check_e193.py"
mkdir -p "$S/out-nb"; win "$S/out-nb" A
RB_OUT="$S/out-nb" bash "$R/s10_a3_dry_e193.sh" start > "$S/nb1.txt" 2>&1; nb1=$?
RB_OUT="$S/out-nb" bash "$R/s11_a3_session_e193.sh" A > "$S/nb2.txt" 2>&1; nb2=$?
stopline "$S/sd.txt"; stopline "$S/nb1.txt"; stopline "$S/nb2.txt"
ok "$sd.$(has 'the synced paths have uncommitted changes' "$S/sd.txt").$nb1.$(has 'was not built today' "$S/nb1.txt").$nb2.$(has 'was not built today' "$S/nb2.txt")" \
  "16.1.10.1.10.1" "SD a synced file changed and not committed: the sync refused (16), nothing synced; NB no build today: step 8 and step 9 refused (10)"

step "L1-L3. a login link; a hang; a cut wait"
touch "$S/ssh-login"; RB_OUT="$S/out-a" bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/l1.txt" 2>&1; l1=$?
touch "$S/ssh-hang"; RB_READ_S=4 RB_OUT="$S/out-a" bash "$K6/s09_a3_reads_k6.sh" > "$S/l2.txt" 2>&1; l2=$?
touch "$S/ssh-cut"; RB_OUT="$S/out-a" bash "$R/s08_a3_build_e193.sh" wait > "$S/l3.txt" 2>&1; l3=$?
stopline "$S/l1.txt"; stopline "$S/l2.txt"; stopline "$S/l3.txt"
ok "$l1.$(grep -c 'aifoundry3 needs a check' "$S/lock.txt" | awk '{print ($1 > 0) ? 1 : 0}').$l2.$l3.$(has 'no reading' "$S/l3.txt")" "11.1.13.14.1" \
  "L1 a login link: 11 and the lock line; L2 a hang killed at its bound: 13; L3 a cut wait: 14, no reading"

step "R, Y. k6's reads and the dry pass on the stand-in box"
RB_OUT="$S/out-a" bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/look.txt" 2>&1; lk=$?
RB_OUT="$S/out-a" bash "$K6/s09_a3_reads_k6.sh" > "$S/r.txt" 2>&1; r=$?
tail -n 1 "$S/r.txt"
RB_OUT="$S/out-a" bash "$R/s10_a3_dry_e193.sh" start > "$S/y1.txt" 2>&1; y1=$?
RB_OUT="$S/out-a" bash "$R/s10_a3_dry_e193.sh" wait > "$S/y2.txt" 2>&1; y2=$?
grep -E 'E193-DRY|LISTING' "$S/y2.txt" | cut -c1-200
ok "$lk.$r.$y1.$y2.$(grep -c 'LISTING SAME' "$S/y2.txt")" "0.0.0.0.2" "R the look FREE and k6's reads (TDP 0 W / 65 C / 600 MHz, et-who clean); Y the dry pass: the session with DRY=1, both listings SAME"

step "RS, BA. the rest rule through step 9; sitting B before sitting A"
L=$TREE/build/e192/T1794620000/session.log; mkdir -p "$(dirname "$L")"
NOW=$(date +%s); tsm() { date -d @"$((NOW - $1 * 60))" '+%Y-%m-%d %H:%M:%S %Z'; }
{ echo "$(tsm 40) session start (T0 $((NOW - 2400)); E192, the proposal's reference session as committed, kit-e192)"; echo "$(tsm 10) session end (T0 $((NOW - 2400)))"; } > "$L"; touch -d @"$((NOW - 600))" "$L"
RB_OUT="$S/out-a" bash "$R/s11_a3_session_e193.sh" A > "$S/rs.txt" 2>&1; rs=$?
stopline "$S/rs.txt"
mkdir -p "$S/out-b"; win "$S/out-b" B; cp -p "$S/out-a/e193-built.txt" "$S/out-b/e193-built.txt"
RB_OUT="$S/out-b" bash "$R/s10_a3_dry_e193.sh" start > /dev/null 2>&1; RB_OUT="$S/out-b" bash "$R/s10_a3_dry_e193.sh" wait > "$S/ybw.txt" 2>&1
touch -d @"$((NOW - 2700))" "$L"; sedi -e "s/^$(tsm 10 | cut -c1-19)/$(tsm 45 | cut -c1-19)/" "$L"
RB_OUT="$S/out-b" bash "$R/s11_a3_session_e193.sh" B > "$S/ba.txt" 2>&1; ba=$?
stopline "$S/ba.txt"
ok "$rs.$(has 'REFUSED: 10 minutes since E192' "$S/rs.txt").$(has 'LAUNCHED' "$S/rs.txt").$ba.$(has 'B never runs before A' "$S/ba.txt")" "10.1.0.10.1" \
  "RS an E192 session ended 10 minutes ago: step 9 refused (10), nothing launched; BA sitting B with no sitting A: 10"
LC=$TREE/build/e193/T$((NOW - 2900))/session.log; mkdir -p "$(dirname "$LC")"
{ echo "$(tsm 48) session start (T0 $((NOW - 2900)) = x; E193 sitting A, blocks S,D,W,T, cap 60 card-minutes; a desk-test stand-in log)"
  echo "$(tsm 47) main run start: run_x04.py build/e193/T$((NOW - 2900))/x04 --blocks S,D,W,T (9 passes, pass 0 the registered warm-up)"
  echo "$(tsm 46) main run ended without a registered stop: runner rc 1; no stop recorded (the runner's log does not end 'done'): a crash"
  echo "$(tsm 45) session end (T0 $((NOW - 2900)))"; } > "$LC"; touch -d @"$((NOW - 2700))" "$LC"
RB_OUT="$S/out-b" bash "$R/s11_a3_session_e193.sh" B > "$S/bc.txt" 2>&1; bc=$?
rm -rf "${TREE:?}/build/e193/T$((NOW - 2900))"
LG=$TREE/build/e193/T$((NOW - 2950))/session.log; mkdir -p "$(dirname "$LG")"
{ echo "$(tsm 48) session start (T0 $((NOW - 2950)) = x; E193 sitting A, blocks S,D,W,T, cap 60 card-minutes; a desk-test stand-in log)"
  echo "$(tsm 46) GATE-STOP: the smoke gate failed: SMOKE NO-GO: a desk-test stand-in line: no main run"
  echo "$(tsm 45) session end (T0 $((NOW - 2950)))"; } > "$LG"; touch -d @"$((NOW - 2700))" "$LG"
RB_OUT="$S/out-a" bash "$R/s11_a3_session_e193.sh" A > "$S/sg.txt" 2>&1; sg=$?
rm -rf "${TREE:?}/build/e193/T$((NOW - 2950))"
stopline "$S/bc.txt"; stopline "$S/sg.txt"
ok "$bc.$(has "sitting A's main run ended without a registered stop (a crash" "$S/bc.txt").$(has 'LAUNCHED' "$S/bc.txt").$sg.$(has 'ended at its smoke gate today' "$S/sg.txt").$(has 'LAUNCHED' "$S/sg.txt")" \
  "10.1.0.10.1.0" "BC sitting B after a crashed sitting A: 10, nothing launched; SG sitting A again on the day its smoke gate failed: 10 ('no sitting that day'), nothing launched"

step "LA. step 9 launches THE REAL session_e193.sh; the wait finds it by its real script name"
echo 25 > "$ST/etwho-sleep"      # under the session's own 30 s bound on et-who (a longer wait reads as a failed holder check)
RB_OUT="$S/out-a" bash "$R/s11_a3_session_e193.sh" A > "$S/la.txt" 2>&1; la=$?
grep -E '^rest:|LAUNCHED|STOP' "$S/la.txt" | cut -c1-200
RB_WAIT_LOOP_S=5 RB_OUT="$S/out-a" bash "$R/s20_wait_e193.sh" A > "$S/wa1.txt" 2>&1; wa1=$?
RB_OUT="$S/out-a" bash "$R/s11_a3_session_e193.sh" A > "$S/la2.txt" 2>&1; la2=$?
wa2=17; k=0; while [ "$wa2" -eq 17 ] && [ "$k" -lt 6 ]; do RB_OUT="$S/out-a" bash "$R/s20_wait_e193.sh" A > "$S/wa2.txt" 2>&1; wa2=$?; k=$((k + 1)); done
grep -E 'GATE-STOP|RUN-|MANIFEST' "$S/wa2.txt" | cut -c1-220
T0=$(cat "$S/out-a/e193-A-T0.txt" 2>/dev/null)
ok "$la.$(has 'rest: ' "$S/la.txt").$wa1.$(has 'RUN-RUNNING e193-A' "$S/wa1.txt").$la2.$(has 'a card session of ours already runs' "$S/la2.txt").$wa2.$(has 'GATE-STOPPED e193-A' "$S/wa2.txt").$(has 'MANIFEST-WRITTEN' "$S/wa2.txt").$(has 'GATE-STOP: the host shows ops node(s) \[none\], not exactly /dev/et0_ops: .*(no device opened)' "$TREE/build/e193/T$T0/session.log")" \
  "0.1.17.1.10.1.16.1.1.1" "LA launched past the rest; RUN-RUNNING by its real name; a second launch refused while it runs; then GATE-STOPPED at the session's own count of ops nodes (none here), before any card read, the manifest written"

step "C, C2, C3, C4, C5. step 11 on that session"
RB_OUT="$S/out-a" bash "$R/s22_collect_e193.sh" A > "$S/c.txt" 2>&1; c=$?
grep -E 'COPY-BACK|COLLECTED|STOP|collected ' "$S/c.txt" | cut -c1-240      # (the gate's own line names the desk home's entries: not printed)
GSD=docs/reports/gate-stops/$TODAY-e193-x04-clock-sitting-a-T$T0-aifoundry3
gsd=$([ -s "$T/$GSD/SHA256SUMS" ] && [ -s "$T/$GSD/facts-e193-a.json" ] && echo 1 || echo 0)
gsx=$(cd "$T" && find docs/reports/data -path '*e193*' 2>/dev/null | grep -c .)      # paths below the scratch only
RB_OUT="$S/out-a" bash "$R/s22_collect_e193.sh" A > "$S/c2.txt" 2>&1; c2=$?
mkdir -p "$S/out-c3"; cp -p "$S/out-a/window.env" "$S/out-a/e193-A-T0.txt" "$S/out-a/box-login-aifoundry3.txt" "$S/out-c3/"
DSD=$TREE/build/e193/T$T0; cp -p "$DSD/session.log" "$S/sl.keep"; printf 'x' >> "$DSD/session.log"
rm -rf "${T:?}/docs/reports/gate-stops"
RB_OUT="$S/out-c3" bash "$R/s22_collect_e193.sh" A > "$S/c3.txt" 2>&1; c3=$?
cp -p "$S/sl.keep" "$DSD/session.log"
RB_OUT="$S/out-c3" bash "$R/s22_collect_e193.sh" A > "$S/c4.txt" 2>&1; c4=$?
T5=$(( $(date +%s) - 3000 )); D5=$TREE/build/e193/T$T5; mkdir -p "$D5" "$S/out-c5"; win "$S/out-c5" A; cp -p "$S/out-a/box-login-aifoundry3.txt" "$S/out-c5/"
{ echo "$(date -d @"$T5" '+%Y-%m-%d %H:%M:%S %Z') session start (T0 $T5 = x; E193 sitting A, blocks S,D,W,T, cap 60 card-minutes; a desk-test stand-in log)"
  echo "$(date -d @"$((T5 + 60))" '+%Y-%m-%d %H:%M:%S %Z') main run start: run_x04.py build/e193/T$T5/x04 --blocks S,D,W,T (a desk-test stand-in line)"
  echo "$(date -d @"$((T5 + 120))" '+%Y-%m-%d %H:%M:%S %Z') GATE-STOP: a desk-test stand-in line beside a main run: no main run"
  echo "$(date -d @"$((T5 + 180))" '+%Y-%m-%d %H:%M:%S %Z') session end (T0 $T5)"; } > "$D5/session.log"
( cd "$D5" && sha256sum session.log > MANIFEST.sha256 ); echo 3 > "$D5/session.rc"; echo "$T5" > "$S/out-c5/e193-A-T0.txt"
RB_OUT="$S/out-c5" bash "$R/s22_collect_e193.sh" A > "$S/c5.txt" 2>&1; c5=$?
rm -rf "${D5:?}"
stopline "$S/c2.txt"; stopline "$S/c4.txt"; stopline "$S/c5.txt"
ok "$c.$(has 'COPY-BACK EXACT' "$S/c.txt").$(has 'COLLECTED ' "$S/c.txt").$(has "collected the gate stop's record $GSD" "$S/c.txt").$gsd.$gsx.$c2.$(has 'exists already' "$S/c2.txt").$c3.$(has 'COPY-BACK NOT EXACT' "$S/c3.txt").$c4.$(has 'e193-raw/T[0-9]* exists already' "$S/c4.txt").$c5.$(has 'does not say clearly how the session ended' "$S/c5.txt").$([ -e "$S/out-c5/e193-raw/T$T5" ] && echo 1 || echo 0)" \
  "0.1.1.1.1.0.10.1.16.1.10.1.16.1.0" "C COPY-BACK EXACT, COLLECTED into the gate stop's record (docs/reports/gate-stops/, nothing under docs/reports/data), the desk-path gate (E183 note 5) clean, HISTORY OK; C2 again: refused (10); C3 a changed box file: NOT EXACT (16); C4 its raw copy there: refused (10); C5 a gate line beside a main run: refused (16), nothing copied"

step "RT. the retry: sitting A launched again after its gate stop"
RB_OUT="$S/out-a" bash "$R/s11_a3_session_e193.sh" A > "$S/rt.txt" 2>&1; rt=$?
grep -E '^rest:|LAUNCHED|STOP' "$S/rt.txt" | cut -c1-200
rw=17; k=0; while [ "$rw" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-a" bash "$R/s20_wait_e193.sh" A > "$S/rtw.txt" 2>&1; rw=$?; k=$((k + 1)); done
T0R=$(cat "$S/out-a/e193-A-T0.txt" 2>/dev/null)
ok "$rt.$(has 'rest: ' "$S/rt.txt").$([ -n "$T0R" ] && [ "$T0R" != "$T0" ] && echo 1 || echo 0).$rw.$(has 'GATE-STOPPED e193-A' "$S/rtw.txt")" "0.1.1.16.1" \
  "RT a gate-stopped sitting A launched again (a new T0; the rest rule skips a session that opened no device); its wait reads GATE-STOPPED (16)"

RPT=${RP:+$RP/home}/aifoundry       # the real-path test's stand-in box tree (its scratch's home/aifoundry)
if [ -n "$RP" ] && [ -d "$RPT/build/e193" ]; then
  step "WR. the wait on the real-path desk test's own sessions"
  wr_run() {  # wr_run <case's log pattern> <sitting>: copy that session onto the stand-in box, write its T0, run the wait
    local src t
    src=$(grep -l "$1" "$RPT"/build/e193/T[0-9]*/session.log 2>/dev/null | grep -v -- '-dry/' | head -n 1)
    [ -n "$src" ] || { echo "   (no real-path session matching '$1')"; WR=99; return; }
    t=$(basename "$(dirname "$src")"); t=${t#T}
    rm -rf "${TREE:?}/build/e193/T$t"; cp -rp "$(dirname "$src")" "$TREE/build/e193/T$t"
    mkdir -p "$TREE/build/q141k"; echo "$t" > "$TREE/build/q141k/e193-$2.T0"; echo "$t" > "$S/out-wr/e193-$2-T0.txt"
    RB_OUT="$S/out-wr" bash "$R/s20_wait_e193.sh" "$2" > "$S/wr-$t.txt" 2>&1; WR=$?
    grep -E 'RUN-|MANIFEST|GATE-STOPPED|MAIN-STOPPED|MAIN-CRASHED|registered stop|has ended' "$S/wr-$t.txt" | cut -c1-200 | sed 's/^/   /'
    WRT=$t
  }
  mkdir -p "$S/out-wr"; win "$S/out-wr" A
  wr_run 'main run stopped: runner rc 1; stop: stop file' A; wa=$WR; ta=${WRT:-}
  wr_run 'main run end: runner rc 0, every pass' B; wb=$WR
  wr_run 'GATE-STOP: the smoke gate failed: SMOKE NO-GO: spin2 (block S) exited 3' A; wg=$WR
  wr_run 'main run ended without a registered stop: runner rc 1' A; wx=$WR; tx=${WRT:-}
  ok "$wa.$(has 'registered stop' "$S/wr-$ta.txt").$wb.$wg.$wx.$(has 'MAIN-CRASHED e193-A' "$S/wr-$tx.txt").$(has 'WITHOUT a registered stop' "$S/wr-$tx.txt")" "0.1.0.16.16.1.1" \
    "WR the real sessions: A (two passes, the operator's stop) RUN-ENDED with its registered stop (0); B whole (0); a smoke gate stop (16); X1's crash of the main run: MAIN-CRASHED, never a registered stop (16)"
  step "CR. step 11 on the real-path sitting A session, its data committed in the scratch repository, then step 13"
  mkdir -p "$S/out-cr"; win "$S/out-cr" A; cp -p "$S/out-a/box-login-aifoundry3.txt" "$S/out-cr/"
  echo "$ta" > "$S/out-cr/e193-A-T0.txt"
  RB_OUT="$S/out-cr" bash "$R/s22_collect_e193.sh" A > "$S/cr1.txt" 2>&1; cr1=$?
  grep -E 'COPY-BACK|COLLECTED|STOP' "$S/cr1.txt" | cut -c1-220
  DD=docs/reports/data/$TODAY-e193-x04-clock-sitting-a-aifoundry3
  RB_OUT="$S/out-cr" bash "$R/s24_reduce_e193.sh" A > "$S/cr0.txt" 2>&1; cr0=$?
  stopline "$S/cr0.txt"
  printf '# E193 sitting A: a desk test stand-in README (never a lab file)\n' > "$T/$DD/README.md"
  $G add --sparse "$DD" > /dev/null 2>&1; $G commit -q -m "desk test: the real-path sitting A's data committed"
  RB_OUT="$S/out-cr" bash "$R/s24_reduce_e193.sh" A > "$S/cr2.txt" 2>&1; cr2=$?
  grep -E 'CHECKS READ|reduced sitting|STOP|box.s manifest' "$S/cr2.txt" | cut -c1-260
  ok "$cr0.$(has 'is not committed' "$S/cr0.txt").$cr1.$(has 'COLLECTED ' "$S/cr1.txt").$cr2.$([ -s "$S/out-cr/x04-e193-A.json" ] && echo 1 || echo 0).$([ -s "$S/out-cr/checks-e193-A.json" ] && echo 1 || echo 0)" "10.1.0.1.0.1.1" \
    "CR step 13 before the data commit refused (10); the real session collected; after its data commit the registered reducer and the checker ran (x04-e193-A.json, checks-e193-A.json)"
  step "CR3-CR5. step 13 on a changed data directory; the data README form's own re-make commands"
  cp -p "$T/$DD/x04/run.log" "$S/runlog.keep"; printf 'x' >> "$T/$DD/x04/run.log"
  mkdir -p "$S/out-cr3"; win "$S/out-cr3" A
  RB_OUT="$S/out-cr3" bash "$R/s24_reduce_e193.sh" A > "$S/cr3.txt" 2>&1; cr3=$?
  cp -p "$S/runlog.keep" "$T/$DD/x04/run.log"
  awk '/^## Re-make it/ {f = 1; next} f && /^## / {f = 0} f && /^    / {print}' "$T/$E/DATA-README-FORM-e193.md" | sed -n '2,$p' | sed 's/^    //' > "$S/remake.sh"
  echo "   the form's re-make commands ($(grep -c . "$S/remake.sh") lines after its first, which sets D and R):"; sed 's/^/     | /' "$S/remake.sh"
  rm -rf "${S:?}/remake"; mkdir -p "$S/remake"
  ( cd "$T" && D="$DD" R="$S/remake" bash -e "$S/remake.sh" ) > "$S/cr5.txt" 2>&1; cr5=$?
  grep -E 'CHECKS READ|box.s bytes|FAILED|Error' "$S/cr5.txt" | cut -c1-200
  printf 'x' >> "$T/$DD/x04/run.log"; $G add --sparse "$DD/x04/run.log"; $G commit -q -m "desk test: a committed change to a data file, SHA256SUMS left"
  cr4c=$($G log -1 --format=%s | grep -c 'SHA256SUMS left')    # (commit -a skips files outside the sparse cone: added by name)
  mkdir -p "$S/out-cr4"; win "$S/out-cr4" A
  RB_OUT="$S/out-cr4" bash "$R/s24_reduce_e193.sh" A > "$S/cr4.txt" 2>&1; cr4=$?
  [ "$cr4c" -eq 1 ] && $G reset -q --hard HEAD~1
  stopline "$S/cr3.txt"; stopline "$S/cr4.txt"
  ok "$cr3.$(has 'uncommitted changes' "$S/cr3.txt").$cr4.$(has 'does not read every entry OK' "$S/cr4.txt").$cr5.$(has 'CHECKS READ: ' "$S/cr5.txt").$(has "not the box's bytes" "$S/cr5.txt").$(cmp -s "$S/remake/x04.json" "$S/out-cr/x04-e193-A.json" && echo SAME || echo DIFFERENT)" \
    "16.1.16.1.0.1.0.SAME" "CR3 a data file changed, not committed: step 13 refused (16); CR4 a committed change SHA256SUMS does not hold: 16; CR5 the README form's own commands on the committed data: rc 0, the box's bytes, the checker's reading, x04.json the same as step 13's byte for byte"
  [ "${cr4c:-0}" -eq 1 ] || echo "   (CR4's commit was not made: the reset after it would have taken the data commit)"
  rm -rf "${T:?}/$DD"; $G reset -q --hard HEAD~1
else
  echo; echo "== WR, CR: NOT RUN (no real-path desk test scratch given)"
fi

step "Z. nothing of this test left on the stand-in box"
left=$("$REAL_PGREP" -u "$(id -u)" -f 'session_e193\.sh|run_x04\.py|fake_card_e193\.py' | while read -r q; do c=$(readlink "/proc/$q/cwd" 2>/dev/null); case "$c/" in "$BOXH"/*) echo "$q" ;; esac; done | grep -c .)
ok "$left" "0" "Z no session, runner or stand-in of this test left running on the stand-in box"
echo; echo "SELFTEST-RB-E193 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
[ "$fail" -eq 0 ]
