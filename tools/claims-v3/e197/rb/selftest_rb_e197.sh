#!/usr/bin/env bash
# E197 (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum): the desk test of E197's runbook with a FAKE ssh and rsync on a STAND-IN
# BOX, E193's runbook desk test's form (rb/selftest_rb_e193.sh). Its scratch repository is a shared, sparse clone of the lab clone this test
# runs from (so e8a85229 and E197's registration commit are in its history, as on the card day), checked out at the registration commit,
# with EVERY FILE UNDER tools/claims-v3/e197 THAT THE REGISTRATION COMMIT DID NOT ADD, committed or not, as one stand-in kit commit (so it
# runs the same whether the kit is committed, landed or not yet), its upstream a local branch at the registration (step 2's pull a no-op);
# the kit list a stand-in made here by the real list's rule and passed to step 2 as its pin (RB_DESKTEST=1 RB_E197_KITPIN=...: the real
# list holds this test's log). The stand-in box is aifoundry3's home under the scratch (its tree ~/aifoundry); the stand-in ssh serves it
# with `bash -s` and refuses any other host or command; the stand-in rsync rewrites aifoundry3: paths onto it; the box's tools are
# fake_card_e197.py's (et-who, the sampler and its config behind the box's own copy of E128's guard), its et-lab-manifest a stand-in, its
# hostname aifoundry3, its pgrep and ps the real ones less every process outside the stand-in box. THE BOX'S BUILD IS REAL: step 6 runs
# build_e197.sh there (cmake with this desk's /opt/et, make_images.py --check, check_elf.py, the host's table against the registration's,
# the real host's refusals before the device layer, its signal read, the session's dry listings with it). The whole test runs in a
# bubblewrap of its own (inside W/nodev.sh): /dev/et0_ops and /dev/et0_mgmt REGULAR FILES (the host's and the wrapper's node counts read
# names; nothing can be opened), a private /run/lock with the card's lock file, a private PID namespace, the host name aifoundry3. No lab
# box is reached.
#   A    the dry listing: every step exits 0, no call reaches the stand-ins
#   W1-W5, G  the window rule (step 2 with no window; a window written yesterday; one written for E193; step 1 for another day; step 9
#        given sitting 2 with sitting 1's window: each 10) and step 2 without RB_GITLOCK (10);  N  step 2 inside the lab-git lock: 16
#   P1-P4, H1-H3  step 2 at every pin (0); the registration's list short (16); the kit's list short (16); an unknown list reported (0);
#        a committed edit of a registration file (16); an added tools/claims-v3/json.py (16); an untracked e183/rb/re.py (HISTORY FAIL)
#   D1-D4  an E197 datum before sitting 1 (16); sitting 1's own before sitting 2 (0); a sitting-2 path before sitting 2 (16); a gate
#        stop's record before sitting 1 (0: no datum)
#   S, B, B2, B3, SD, NB  the sync (HARNESS OK on the box); THE REAL BUILD (REGFILE-BUILT: make_images and check_elf, the host's table SAME,
#        four refusals, the signal read, LISTING SAME x3); a second start after REGFILE-BUILT (10); NO-THIRD-BUILD (16); a synced file not
#        committed (16); steps 8, 7 and 9 with no build today (10)
#   L1-L3  a login link (11, the lock line in a COPY of the round's lock file); a hang killed at its bound (13); a cut wait (14)
#   Y    step 8, the dry pass: the wrapper's dry path on the box for both of sitting 1's plans: LISTING SAME x2; RB_OUT/e197-1-dry-ok.txt
#   RS   THE REST AT STEP 7, BEFORE ANY CARD COMMAND (E192's data note 1): an E192-form session ended 10 minutes ago: step 7 refused (10),
#        NO config read sent (the stand-in's config calls unchanged), no first card command stamped
#   R, R2  step 7 once rested: the plan "full", the first card command stamped, k6's reads 0 (one config read); again: the stamp kept
#   F1   step 9 with the first card command 11 minutes back: 16 (its cap counts from it); F1b 5 minutes back: 16 (the bound is 120 s)
#   BA, BC, BS  sitting 2 with no sitting 1 on the box; after a crashed sitting 1; after a sitting 1 whose stop named the card: step 7
#        refused (10) each, no config read sent
#   SG   step 9 for sitting 1 on a day its smoke failed: 10
#   LA   step 9 launches THE REAL session_e197.sh detached (DRY unset); THE WAIT FINDS IT BY ITS REAL SCRIPT NAME: RUN-RUNNING (17) while
#        its holder check is held 25 s by the stand-in; a second launch refused while it runs (10); then GATE-STOPPED (16): the stand-in's
#        holder, "no device opened by the session", the manifest written
#   C, C2-C5  step 11 on that session: COPY-BACK EXACT, THE GATE STOP'S RECORD (docs/reports/gate-stops/, nothing under
#        docs/reports/data), COLLECTED, E183 note 5's desk-path gate clean, HISTORY OK (0); again (10); a changed box file in a new RB_OUT
#        (16); that RB_OUT again (10); a log that does not say how it ended (16)
#   RT   THE RETRY in a new RB_OUT: the window, the build's wait, the dry pass, step 7 (the rest rule skips the session that opened no
#        device; a new first card command), step 9: launched; its wait GATE-STOPPED again (16)
#   WR   the wait on the real-path desk test's own sessions (when its scratch is given): P (whole: RUN-ENDED, 0); S1 (a stop by hand:
#        STOPPED, 0); G1 (the kit's smoke check: GATE-STOPPED, 16); X1 (a crash: CRASHED, 16); HG (a hung host: HUNG, 16)
#   CR, CR3-CR5  step 11 on the real-path P session (its data directory); step 13 before its data commit (10); after it, the registered
#        reducer and the checker (regfile-e197-s1.json, checks); a data file changed, not committed (16); THE DATA README FORM'S OWN
#        RE-MAKE COMMANDS on the committed data (the same regfile-e197-s1.json, byte for byte); a committed change SHA256SUMS does not
#        hold (16)
#   CR2  the real-path P2 session collected as sitting 2's data and committed: step 13 for sitting 2, THE POOLED REDUCTION
#        (regfile-e197.json: T1's units 67 + 115 = 182)
#   Z    no process of this test left on the stand-in box
#   bash tools/claims-v3/e197/rb/selftest_rb_e197.sh <scratch dir> [<the real-path desk test's scratch dir> [<a lock file whose COPY is
#        RB_LOCK>]] > <log>        (prints SELFTEST-RB-E197 <n> of <m> PASS or FAIL; run it inside W/nodev.sh, between 01:00 and 22:30
#        Pacific: step 7 needs a window with the full plan's cap and the closing steps left today)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
RP=${2:-}
LOCKFROM=${3:-}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
if [ -z "${E197_RB_INNER:-}" ]; then
  for p in /dev/et*; do [ -c "$p" ] && { echo "REFUSED: $p is a character device here: run this test inside the no-device sandbox"; exit 2; }; done
  [ "$(TZ=America/Los_Angeles date +%H%M)" -lt 2230 ] || { echo "REFUSED: run before 22:30 Pacific (step 7 needs the full plan's cap and 15 minutes before 23:59)"; exit 2; }
  [ "$(TZ=America/Los_Angeles date +%H%M)" -ge 0100 ] || { echo "REFUSED: run after 01:00 Pacific (the stand-in logs are dated 45 minutes back, today)"; exit 2; }
  mkdir -p "$S" && S=$(cd "$S" && pwd)
  [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
  : > "$S/et0_ops"; : > "$S/et0_mgmt"
  exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --bind "$S/et0_ops" /dev/et0_ops --bind "$S/et0_mgmt" /dev/et0_mgmt \
    --unshare-pid --proc /proc --unshare-uts --hostname aifoundry3 --die-with-parent --setenv E197_RB_INNER 1 \
    -- /bin/bash "$SRC/tools/claims-v3/e197/rb/selftest_rb_e197.sh" "$S" "$RP" "$LOCKFROM"
fi
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK RB_WAIT_LOOP_S RB_E197_KITPIN; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
for c in timeout sha256sum shasum flock cmake rsync; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
: > /run/lock/etsoc-shire0.lock
T=$S/tree; BOXH=$S/box/aifoundry3; TREE=$BOXH/aifoundry; BIN=$S/bin; BB=$S/boxbin; ST=$S/box-state
mkdir -p "$TREE/build" "$BIN" "$BB" "$ST"
E=tools/claims-v3/e197
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
sedi() { local f=${!#} t; t=$(mktemp "$S/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
cfgcalls() { grep -c '"mode": "config"' "$ST/calls/sampler.log" 2>/dev/null || echo 0; }
echo "E197 runbook desk test, $(date '+%F %T %Z'), $(/usr/bin/python3 --version 2>&1), $(cmake --version | head -n 1); inside its sandbox: host $(hostname), /dev/et*: $(ls /dev/et* | tr '\n' ' '); scratch outside the repository"
# ---- the scratch repository: a shared sparse clone at the registration, then the kit's files as one stand-in commit
REG=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/E197.md | tail -n 1)
[ -n "$REG" ] || { echo "no registration commit in the lab clone's history"; exit 2; }
git clone -q --shared --no-checkout "$SRC" "$T" || exit 2
G="git -C $T -c user.name=e197-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ '/docs/reports/data/*e197*' '/docs/reports/gate-stops/*e197*' || exit 2   # E197's data stays on disk across resets
$G checkout -q -B main "$REG" || exit 2
$G branch -q -f e197-desktest-registration "$REG" && $G branch -q --set-upstream-to=e197-desktest-registration || exit 2   # step 2's pull: a no-op
( cd "$SRC" && git show "$REG" --name-only --format= -- $E ) > "$S/reg-files.txt"
KITC=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/KIT.md | tail -n 1)
( cd "$SRC" && { git ls-files --cached --others --exclude-standard -- $E | grep -v -x -F -f "$S/reg-files.txt"; git diff --name-only HEAD -- $E; } ) |
  sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
[ -f "$T/$E/session_e197.sh" ] && [ -f "$T/$E/harness_e197.py" ] && [ -f "$T/$E/rb/s03_desk_e197.sh" ] && [ -f "$T/$E/KIT.md" ] || { echo "the kit's files (KIT.md among them: step 2 finds the kit's commit by it) did not reach the scratch tree"; exit 2; }
mkdir -p "$T/$E/logs"
for spec in "desktest-realpath-e197.txt DESKTEST-REALPATH-E197 0 of 0 PASS" "selftest-rb-e197.txt SELFTEST-RB-E197 0 of 0 PASS" \
            "selftest-rest-e197.txt SELFTEST-REST-E197 0 of 0 PASS" "realbytes-e197.txt REALBYTES-E197 0 of 0 PASS" \
            "dry-listing-e197.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e197.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"     # always a stand-in line: this test never reads its own (or any) log being written
done
( cd "$T" && /usr/bin/python3 -I -B $E/harness_e197.py --make > /dev/null )
rm -f "$T/$E/SHA256SUMS-e197-kit"
( cd "$T" && find $E -type f ! -name 'SHA256SUMS-e197-kit' ! -path "$E/rb/s03_desk_e197.sh" ! -name '*.pyc' | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) |
  grep -v -F -f "$S/reg-files.txt" > "$S/kit-standin.txt"
KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e197-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
export RB_E197_KITPIN="$E/SHA256SUMS-e197-kit:$KITN:$KITH:top"
$G add -A $E && $G commit -q -m "E197 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; exit 2; }
echo "scratch repository: a shared sparse clone at the registration ${REG:0:12}, the kit as one stand-in commit $($G rev-parse --short=12 HEAD) (its files from the clone, $([ -n "$KITC" ] && echo "the kit committed there at ${KITC:0:12}" || echo "the kit not committed there")); the stand-in kit list $KITN entries"
# ---- the stand-ins
REAL_RSYNC=$(command -v rsync); REAL_PGREP=$(command -v pgrep)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; echo "To authenticate, visit: https://login.tailscale.com/a/e197desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
if [ -e "$S/ssh-cut" ]; then rm -f "$S/ssh-cut"; cat > /dev/null; echo "ssh: connection closed (desk-test stand-in)" >&2; exit 255; fi
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'true' and 'bash -s', not '\$cmd'" >&2; exit 97; }
cd "$BOXH" || exit 1
exec /usr/bin/env HOME="$BOXH" PATH="$BB:/usr/bin:/bin" E197_STANDIN_DIR="$ST" USER=$(id -un) LOGNAME=$(id -un) bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$BOXH/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
FAKE=$T/$E/fake_card_e197.py
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s etwho "$@"\n' "$FAKE" > "$BB/et-who"
printf '#!/bin/sh\necho "et-lab-manifest: a desk-test stand-in (no sysfs read)"\n' > "$BB/et-lab-manifest"
printf '#!/bin/sh\necho aifoundry3\n' > "$BB/hostname"
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
# the stand-in box's ps for the form k6's hold_read and the session's rules use (ps -eo uid=,pid=,comm=): the real one's lines, less every
# process outside the stand-in box (its working directory not under the box's home)
[ "\$*" = "-eo uid=,pid=,comm=" ] || exec /usr/bin/ps "\$@"
/usr/bin/ps -eo uid=,pid=,comm= | while read -r u p c; do d=\$(readlink "/proc/\$p/cwd" 2>/dev/null) || continue; case "\$d/" in "$BOXH"/*) echo "\$u \$p \$c" ;; esac; done
EOF_PS
for n in ssh rsync scp sudo; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$BB/$n"; done
chmod +x "$BIN"/* "$BB"/*
mkdir -p "$TREE/tools/claims-v3/e128" "$TREE/build/ettelem"
cp -p "$T/tools/claims-v3/e128/ettelem_guard.sh" "$TREE/tools/claims-v3/e128/ettelem_guard.sh"
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s sampler "$@"\n' "$FAKE" > "$TREE/build/ettelem/ettelem"; chmod +x "$TREE/build/ettelem/ettelem"
echo '{}' > "$ST/scenario.json"
if [ -n "$LOCKFROM" ]; then cp "$LOCKFROM" "$S/lock.txt" || exit 2; else : > "$S/lock.txt"; fi   # RB_LOCK: a copy, never the round's own file
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$S/gitlock"
R=$T/$E/rb; K6=$T/tools/claims-v3/q141k-runbook/k6
TODAY=$(TZ=America/Los_Angeles date +%F)
cd "$T" || exit 2
win() { mkdir -p "$1"; RB_OUT="$1" bash "$R/s02_window_e197.sh" "$2" "$TODAY" 23:50 23:59 > /dev/null 2>&1; }
s2() { RB_DESKTEST=1 RB_OUT="$1" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e197.sh"; }

step "A. the dry listing"
bash "$R/list_steps_e197.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
tail -n 1 "$S/dry-listing.txt"
ok "$rc.$(grep -c . "$S/calls.log")" "0.0" "A every step 0, no call to the stand-ins"

step "W1-W5, G. the window rule and the lab-git lock"
s2 "$S/out-k" > "$S/w1.txt" 2>&1; w1=$?
win "$S/out-w" 1; touch -d '-1 day' "$S/out-w/window.env"
s2 "$S/out-w" > "$S/w2.txt" 2>&1; w2=$?
win "$S/out-w" 1; sedi -e 's/^RB_PLAN=e197$/RB_PLAN=e193/' "$S/out-w/window.env"
s2 "$S/out-w" > "$S/w3.txt" 2>&1; w3=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e197.sh" 1 "$(date -d '+1 day' +%F)" 10:00 12:00 > "$S/w4.txt" 2>&1; w4=$?
win "$S/out-w" 1
RB_OUT="$S/out-w" bash "$R/s11_a3_session_e197.sh" 2 > "$S/w5.txt" 2>&1; w5=$?
RB_OUT="$S/out-w" bash "$R/s03_desk_e197.sh" > "$S/g.txt" 2>&1; g=$?
ok "$w1.$(has 'no window in RB_OUT' "$S/w1.txt").$w2.$(has 'not written today' "$S/w2.txt").$w3.$(has 'written for e193' "$S/w3.txt").$w4.$(has 'is not today' "$S/w4.txt").$w5.$(has "sitting 1's, not sitting 2's" "$S/w5.txt").$g.$(has 'RB_GITLOCK is not set' "$S/g.txt").$(grep -c . "$S/calls.log")" \
  "10.1.10.1.10.1.10.1.10.1.10.1.0" "W1-W5, G each refused (10) before any call"

step "N. step 2 run inside the lab-git lock (nested): its pull cannot take the lock"
RB_GITLOCK_T=2 /usr/bin/flock -n -E 75 "$S/gitlock" env RB_DESKTEST=1 RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e197.sh" > "$S/n.txt" 2>&1; n=$?
stopline "$S/n.txt"
ok "$n.$(has 'pull' "$S/n.txt")" "16.1" "N a nested step 2 stops with 16 naming its pull (never run step 2 inside the lock)"

step "P1. step 2 on the scratch repository"
mkdir -p "$S/out-p"; win "$S/out-p" 1
s2 "$S/out-p" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check|STOP' "$S/p1.txt" | cut -c1-500
ok "$p1.$(has "the lists at their pinned counts and bytes (35; the kit's $KITN)" "$S/p1.txt").$(has 'the paths clean, HISTORY OK' "$S/p1.txt")" \
  "0.1.1" "P1 step 2 passes at every pin, HISTORY OK, the registration and the kit found by their content"

step "P2-P4, H1-H3. a short registration list; a short kit list; an unknown list; an edited registration file; shadows"
sedi -e '$d' "$T/$E/SHA256SUMS-e197-registration"; $G commit -q -am "desk test: the registration's list one line short"
s2 "$S/out-p" > "$S/p2.txt" 2>&1; p2=$?; $G reset -q --hard HEAD~1
sedi -e '$d' "$T/$E/SHA256SUMS-e197-kit"; $G commit -q -am "desk test: the kit's list one line short"
s2 "$S/out-p" > "$S/p3.txt" 2>&1; p3=$?; $G reset -q --hard HEAD~1
( cd "$T" && sha256sum $E/E197.md > $E/notes-SHA256SUMS-x ); $G add $E/notes-SHA256SUMS-x; $G commit -q -m "desk test: an unknown list"
s2 "$S/out-p" > "$S/p4.txt" 2>&1; p4=$?; $G reset -q --hard HEAD~1
printf '\n' >> "$T/$E/proposal/src/trains.tsv"; $G commit -q -am "desk test: a registration file edited"
s2 "$S/out-p" > "$S/h1.txt" 2>&1; h1=$?; $G reset -q --hard HEAD~1
printf '# desk test: a stand-in that would shadow json for dmcmd_audit.py\n' > "$T/tools/claims-v3/json.py"; $G add tools/claims-v3/json.py
$G commit -q -m "desk test: json.py beside dmcmd_audit.py"
s2 "$S/out-p" > "$S/h2.txt" 2>&1; h2=$?
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e197.py tree ) > "$S/h2b.txt" 2>&1; $G reset -q --hard HEAD~1
printf '# desk test\n' > "$T/tools/claims-v3/e183/rb/re.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e197.py tree ) > "$S/h3.txt" 2>&1; h3=$?; rm -f "${T:?}/tools/claims-v3/e183/rb/re.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e197.py tree ) > "$S/hc.txt" 2>&1; hc=$?
cut -c1-260 "$S/h2b.txt" "$S/h3.txt"
ok "$p2.$(has 'SHA256SUMS-e197-registration(34 OK of 34; pinned 35' "$S/p2.txt").$p3.$(has "SHA256SUMS-e197-kit($((KITN - 1)) OK of $((KITN - 1)); pinned $KITN" "$S/p3.txt").$p4.$(has 'notes-SHA256SUMS-x' "$S/out-p/runbook.log").$h1.$(has 'history' "$S/h1.txt").$h2.$(has 'json.py' "$S/h2b.txt").$h3.$(has 'HISTORY FAIL' "$S/h3.txt").$hc" \
  "16.1.16.1.0.1.16.1.16.1.16.1.0" "P2-P4, H1-H3: each pin refused and named; the unknown list reported; the edit and the shadows refused by the history check; clean again after"

step "D1-D4. no E197 datum in any ref"
D1P=docs/reports/data/2026-11-16-e197-regfile-sitting-1-aifoundry3
mkdir -p "$T/$D1P"; echo x > "$T/$D1P/x.txt"; $G add --sparse "$D1P/x.txt"; $G commit -q -m "desk test: sitting 1's data path"
s2 "$S/out-p" > "$S/d1.txt" 2>&1; d1=$?
mkdir -p "$S/out-p2"; win "$S/out-p2" 2
s2 "$S/out-p2" > "$S/d2.txt" 2>&1; d2=$?
D2P=docs/reports/data/2026-11-16-e197-regfile-sitting-2-aifoundry3
mkdir -p "$T/$D2P"; echo x > "$T/$D2P/x.txt"; $G add --sparse "$D2P/x.txt"; $G commit -q -m "desk test: a sitting 2 data path"
s2 "$S/out-p2" > "$S/d3.txt" 2>&1; d3=$?
rm -rf "${T:?}/$D1P" "${T:?}/$D2P"; $G reset -q --hard HEAD~2
GS=docs/reports/gate-stops/2026-11-16-e197-regfile-sitting-1-T1794700000-aifoundry3
mkdir -p "$T/$GS"; echo x > "$T/$GS/x.txt"; $G add --sparse "$GS/x.txt"; $G commit -q -m "desk test: a gate stop's record"
s2 "$S/out-p" > "$S/d4.txt" 2>&1; d4=$?
rm -rf "${T:?}/docs/reports/gate-stops"; $G reset -q --hard HEAD~1
stopline "$S/d1.txt"; stopline "$S/d3.txt"
ok "$d1.$(has 'e197-datum(1 paths before sitting 1)' "$S/d1.txt").$d2.$d3.$(has "e197-datum(1 paths besides sitting 1's before sitting 2)" "$S/d3.txt").$d4.$(has 'E197 data paths in any ref: 0 ' "$S/d4.txt")" \
  "16.1.0.16.1.0.1" "D1 a datum before sitting 1: 16; D2 sitting 1's own before sitting 2: 0; D3 a sitting-2 path before sitting 2: 16; D4 a gate stop's record: 0 (no datum)"

step "S, B. the sync, then THE REAL BUILD on the stand-in box"
mkdir -p "$S/out-a"; win "$S/out-a" 1
RB_OUT="$S/out-a" bash "$R/s07_a3_sync_e197.sh" > "$S/s.txt" 2>&1; s=$?
tail -n 1 "$S/s.txt"
( cd "$TREE/build/claims-v3/aifoundry3/e197" && /usr/bin/python3 -I -B tools/claims-v3/e197/harness_e197.py --box --root . ) > "$S/s2.txt" 2>&1
RB_OUT="$S/out-a" bash "$R/s08_a3_build_e197.sh" start > "$S/b1.txt" 2>&1; b1=$?
b2=17; k=0; while [ "$b2" -eq 17 ] && [ "$k" -lt 6 ]; do RB_OUT="$S/out-a" bash "$R/s08_a3_build_e197.sh" wait > "$S/b2.txt" 2>&1; b2=$?; k=$((k + 1)); done
grep -E '^ +(COMPILER|ELF|CHECK|HOST|SIGNAL|LISTING|SAMPLER|REGFILE)|STOP|built today' "$S/b2.txt" | cut -c1-220
RB_OUT="$S/out-a" bash "$R/s08_a3_build_e197.sh" start > "$S/b3.txt" 2>&1; b3=$?
BLT=$S/out-a/e197-built.txt
ok "$s.$(has 'HARNESS OK' "$S/s2.txt").$b1.$b2.$(grep -c '^LISTING SAME' "$BLT").$(grep -c '^CHECK ' "$BLT").$(has '^HOST-TABLE SAME' "$BLT").$(has '^HOST-BEHAVIOUR OK' "$BLT").$(has '^SIGNAL-READ host' "$BLT").$(has '^REGFILE-BUILT rc=0' "$BLT").$b3.$(has 'was built today' "$S/b3.txt")" \
  "0.1.0.0.3.2.1.1.1.1.10.1" "S the sync, HARNESS OK in E197's root on the box; B the real build: make_images and check_elf, HOST-TABLE SAME, HOST-BEHAVIOUR OK, SIGNAL-READ, LISTING SAME x3, REGFILE-BUILT; B2 a second start refused (10)"

step "B3. NO-THIRD-BUILD"
AT=$TREE/build/claims-v3/aifoundry3/e197/build/e197-build-attempts.txt
cp -p "$AT" "$S/attempts.keep"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e197 started" >> "$AT"
cp -p "$TREE/build/q141k/jobs/a3-build-e197.out" "$S/jobout.keep"; sedi -e 's/^REGFILE-BUILT rc=0/REGFILE-BUILD-FAILED desk test/' "$TREE/build/q141k/jobs/a3-build-e197.out"
RB_OUT="$S/out-a" bash "$R/s08_a3_build_e197.sh" start > "$S/b4.txt" 2>&1; b4=$?
cp -p "$S/attempts.keep" "$AT"; cp -p "$S/jobout.keep" "$TREE/build/q141k/jobs/a3-build-e197.out"
stopline "$S/b4.txt"
ok "$b4.$(has 'NO-THIRD-BUILD' "$S/b4.txt")" "16.1" "B3 a third start the same day refused (16)"

step "SD, NB. the sync with a synced file not committed; steps 8, 7 and 9 with no build today"
printf '# desk test: one line more, not committed\n' >> "$T/$E/check_e197.py"
RB_OUT="$S/out-a" bash "$R/s07_a3_sync_e197.sh" > "$S/sd.txt" 2>&1; sd=$?
$G checkout -q -- "$E/check_e197.py"
mkdir -p "$S/out-nb"; win "$S/out-nb" 1
RB_OUT="$S/out-nb" bash "$R/s10_a3_dry_e197.sh" start > "$S/nb1.txt" 2>&1; nb1=$?
RB_OUT="$S/out-nb" bash "$R/s09_a3_reads_e197.sh" 1 > "$S/nb3.txt" 2>&1; nb3=$?
RB_OUT="$S/out-nb" bash "$R/s11_a3_session_e197.sh" 1 > "$S/nb2.txt" 2>&1; nb2=$?
stopline "$S/sd.txt"; stopline "$S/nb1.txt"; stopline "$S/nb3.txt"; stopline "$S/nb2.txt"
ok "$sd.$(has 'the synced paths have uncommitted changes' "$S/sd.txt").$nb1.$(has 'was not built today' "$S/nb1.txt").$nb3.$(has 'was not built today' "$S/nb3.txt").$nb2.$(has 'was not built today' "$S/nb2.txt")" \
  "16.1.10.1.10.1.10.1" "SD a synced file changed and not committed: refused (16); NB no build today: steps 8, 7 and 9 refused (10)"

step "L1-L3. a login link; a hang; a cut wait"
touch "$S/ssh-login"; RB_OUT="$S/out-a" bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/l1.txt" 2>&1; l1=$?
touch "$S/ssh-hang"; RB_READ_S=4 RB_OUT="$S/out-a" bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/l2.txt" 2>&1; l2=$?
touch "$S/ssh-cut"; RB_OUT="$S/out-a" bash "$R/s08_a3_build_e197.sh" wait > "$S/l3.txt" 2>&1; l3=$?
stopline "$S/l1.txt"; stopline "$S/l2.txt"; stopline "$S/l3.txt"
ok "$l1.$(grep -c 'aifoundry3 needs a check' "$S/lock.txt" | awk '{print ($1 > 0) ? 1 : 0}').$l2.$l3.$(has 'no reading' "$S/l3.txt")" "11.1.13.14.1" \
  "L1 a login link: 11 and the lock line (in the COPY); L2 a hang killed at its bound: 13; L3 a cut wait: 14, no reading"

step "Y. step 8, the dry pass on the stand-in box (both of sitting 1's plans)"
RB_OUT="$S/out-a" bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/look.txt" 2>&1; lk=$?
RB_OUT="$S/out-a" bash "$R/s10_a3_dry_e197.sh" start > "$S/y1.txt" 2>&1; y1=$?
y2=17; k=0; while [ "$y2" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-a" bash "$R/s10_a3_dry_e197.sh" wait > "$S/y2.txt" 2>&1; y2=$?; k=$((k + 1)); done
grep -E 'E197-DRY' "$S/y2.txt" | cut -c1-200
ok "$lk.$y1.$y2.$(grep -c '^E197-DRY sitting 1 plan .* rc=0 LISTING SAME' "$S/y2.txt").$([ -s "$S/out-a/e197-1-dry-ok.txt" ] && echo 1 || echo 0)" "0.0.0.2.1" "Y the look FREE; the dry pass: the wrapper's dry path for full and short, LISTING SAME x2; RB_OUT/e197-1-dry-ok.txt"

step "RS, R, R2. step 7: the rest BEFORE any card command; then the reads"
L=$TREE/build/e192/T1794620000/session.log; mkdir -p "$(dirname "$L")"
NOW=$(date +%s); tsm() { date -d @"$((NOW - $1 * 60))" '+%Y-%m-%d %H:%M:%S %Z'; }
{ echo "$(tsm 40) session start (T0 $((NOW - 2400)); E192, the proposal's reference session as committed, kit-e192)"; echo "$(tsm 10) session end (T0 $((NOW - 2400)))"; } > "$L"; touch -d @"$((NOW - 600))" "$L"
c0=$(cfgcalls)
RB_OUT="$S/out-a" bash "$R/s09_a3_reads_e197.sh" 1 > "$S/rs.txt" 2>&1; rs=$?
c1=$(cfgcalls); rsf=$([ -e "$S/out-a/e197-1-first.txt" ] && echo stamped-early || echo ok)
stopline "$S/rs.txt"
touch -d @"$((NOW - 2700))" "$L"; sedi -e "s/^$(tsm 10 | cut -c1-19)/$(tsm 45 | cut -c1-19)/" "$L"
RB_OUT="$S/out-a" bash "$R/s09_a3_reads_e197.sh" 1 > "$S/r.txt" 2>&1; r=$?
c2=$(cfgcalls); F0=$(sed -n 's/^FIRST=//p' "$S/out-a/e197-1-first.txt" 2>/dev/null)
grep -E 'sitting 1:|k6.s reads|STOP' "$S/r.txt" | cut -c1-220
RB_OUT="$S/out-a" bash "$R/s09_a3_reads_e197.sh" 1 > "$S/r2.txt" 2>&1; r2=$?
F1v=$(sed -n 's/^FIRST=//p' "$S/out-a/e197-1-first.txt" 2>/dev/null)
ok "$rs.$(has 'REFUSED: 10 minutes since E192' "$S/rs.txt").$((c1 - c0)).$rsf.$r.$(has 'PLAN=full' "$S/out-a/e197-1-first.txt").$((c2 - c1)).$r2.$([ -n "$F0" ] && [ "$F0" = "$F1v" ] && echo kept || echo moved).$(has 'the first card command stays' "$S/r2.txt")" \
  "10.1.0.ok.0.1.1.0.kept.1" "RS the rest at step 7: refused (10), NO config read sent, nothing stamped; R once rested: plan full, the stamp, one config read, 0; R2 again: the stamp kept"

step "F1. step 9 with the first card command 11 minutes back"
cp -p "$S/out-a/e197-1-first.txt" "$S/first.keep"; sedi -e "s/^FIRST=.*/FIRST=$(( $(date +%s) - 660 ))/" "$S/out-a/e197-1-first.txt"
RB_OUT="$S/out-a" bash "$R/s11_a3_session_e197.sh" 1 > "$S/f1.txt" 2>&1; f1=$?
cp -p "$S/first.keep" "$S/out-a/e197-1-first.txt"
stopline "$S/f1.txt"
ok "$f1.$(has 'more than 120 s' "$S/f1.txt").$(has 'LAUNCHED' "$S/f1.txt")" "16.1.0" "F1 the first card command 11 minutes back: step 9 refused (16), nothing launched"

step "F1b. step 9 with the first card command 5 minutes back (inside the old 600 s bound; the bound is 120 s since fix-e197)"
cp -p "$S/out-a/e197-1-first.txt" "$S/first.keep"; sedi -e "s/^FIRST=.*/FIRST=$(( $(date +%s) - 300 ))/" "$S/out-a/e197-1-first.txt"
RB_OUT="$S/out-a" bash "$R/s11_a3_session_e197.sh" 1 > "$S/f1b.txt" 2>&1; f1b=$?
cp -p "$S/first.keep" "$S/out-a/e197-1-first.txt"
stopline "$S/f1b.txt"
ok "$f1b.$(has 'more than 120 s' "$S/f1b.txt").$(has 'LAUNCHED' "$S/f1b.txt")" "16.1.0" "F1b the first card command 5 minutes back: step 9 refused (16) by the 120 s bound, nothing launched"

step "BA, BC, BS, SG. sitting 2's conditions at step 7; sitting 1 again on a day its smoke failed"
mkdir -p "$S/out-b"; win "$S/out-b" 2; cp -p "$S/out-a/e197-built.txt" "$S/out-b/e197-built.txt"
RB_OUT="$S/out-b" bash "$R/s10_a3_dry_e197.sh" start > /dev/null 2>&1
yb=17; k=0; while [ "$yb" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-b" bash "$R/s10_a3_dry_e197.sh" wait > "$S/ybw.txt" 2>&1; yb=$?; k=$((k + 1)); done
c0=$(cfgcalls)
RB_OUT="$S/out-b" bash "$R/s09_a3_reads_e197.sh" 2 > "$S/ba.txt" 2>&1; ba=$?
mklog() {  # mklog <T0 offset s> <minutes ago it ended> <lines...>: a stand-in E197 sitting-1 log on the box
  local t=$((NOW - $1)) m=$2; shift 2; local d=$TREE/build/e197/T$t; mkdir -p "$d"
  { echo "$(tsm $((m + 40))) session start (T0 $t = x; E197 sitting 1, plan full; a desk-test stand-in log)"
    for ln in "$@"; do echo "$(tsm $((m + 1))) $ln"; done; echo "$(tsm "$m") session end (T0 $t)"; } > "$d/session.log"
  touch -d @"$((NOW - m * 60))" "$d/session.log"; echo "$d"
}
LC=$(mklog 5000 45 "train blocks started: 1 of 4 (A); complete: 0 (none); train processes recorded: 20" "the trains ended without a registered stop: run_session.sh rc 1, no stop recorded (a crash)")
RB_OUT="$S/out-b" bash "$R/s09_a3_reads_e197.sh" 2 > "$S/bc.txt" 2>&1; bc=$?; rm -rf "${LC:?}"
LS=$(mklog 5100 45 "train blocks started: 2 of 4 (A B); complete: 1 (A); train processes recorded: 170" "stop: watch_e197: minion clock 500.0, not 600 MHz, on 3 samples in a row (the kit's stop) (names the card)" "SITTING-RESULT: smoke passed; train blocks complete 1 (A); card stop yes: watch_e197: minion clock 500.0")
RB_OUT="$S/out-b" bash "$R/s09_a3_reads_e197.sh" 2 > "$S/bs.txt" 2>&1; bs=$?; rm -rf "${LS:?}"
c1=$(cfgcalls)
LG=$(mklog 5200 45 "the runner's smoke gate: failed (14 launches, rates 5e+11-5e+11)" "GATE-STOP: no block of trains.tsv began (smoke gate failed (launches 14))")
RB_OUT="$S/out-a" bash "$R/s11_a3_session_e197.sh" 1 > "$S/sg.txt" 2>&1; sg=$?; rm -rf "${LG:?}"
stopline "$S/ba.txt"; stopline "$S/bc.txt"; stopline "$S/bs.txt"; stopline "$S/sg.txt"
ok "$yb.$ba.$(has 'no E197 sitting 1 on this box' "$S/ba.txt").$bc.$(has 'a crash' "$S/bc.txt").$bs.$(has 'sitting 2 needs a dated amendment' "$S/bs.txt").$((c1 - c0)).$sg.$(has 'smoke failed today' "$S/sg.txt").$(has 'LAUNCHED' "$S/sg.txt")" \
  "0.10.1.10.1.10.1.0.10.1.0" "BA no sitting 1, BC a crashed sitting 1, BS a sitting 1 whose stop named the card: step 7 refused (10) each, no config read sent; SG sitting 1 again on a smoke-failed day: 10"

step "LA. step 9 launches THE REAL session_e197.sh; the wait finds it by its real script name"
echo '{"etwho_check_sleep_s": 25, "etwho_check_held": true}' > "$ST/scenario.json"   # under the wrapper's own 30 s bound on et-who
RB_OUT="$S/out-a" bash "$R/s11_a3_session_e197.sh" 1 > "$S/la.txt" 2>&1; la=$?
grep -E '^rest:|LAUNCHED|STOP' "$S/la.txt" | cut -c1-200
RB_WAIT_LOOP_S=5 RB_OUT="$S/out-a" bash "$R/s20_wait_e197.sh" 1 > "$S/wa1.txt" 2>&1; wa1=$?
RB_OUT="$S/out-a" bash "$R/s11_a3_session_e197.sh" 1 > "$S/la2.txt" 2>&1; la2=$?
wa2=17; k=0; while [ "$wa2" -eq 17 ] && [ "$k" -lt 6 ]; do RB_OUT="$S/out-a" bash "$R/s20_wait_e197.sh" 1 > "$S/wa2.txt" 2>&1; wa2=$?; k=$((k + 1)); done
grep -E 'GATE-STOP|RUN-|MANIFEST' "$S/wa2.txt" | cut -c1-220
T0=$(cat "$S/out-a/e197-1-T0.txt" 2>/dev/null)
ok "$la.$(has 'rest: ' "$S/la.txt").$wa1.$(has 'RUN-RUNNING e197-1' "$S/wa1.txt").$la2.$(has 'a card session of ours already runs' "$S/la2.txt").$wa2.$(has 'GATE-STOPPED e197-1' "$S/wa2.txt").$(has 'MANIFEST-WRITTEN' "$S/wa2.txt").$(has 'GATE-STOP: the card is not free: et-who --check exit 1 .*(no device opened by the session)' "$S/wa2.txt")" \
  "0.1.17.1.10.1.16.1.1.1" "LA launched; RUN-RUNNING by its real name; a second launch refused while it runs; then GATE-STOPPED at the holder check (no device opened by the session), the manifest written"

step "C, C2-C5. step 11 on that session"
RB_OUT="$S/out-a" bash "$R/s22_collect_e197.sh" 1 > "$S/c.txt" 2>&1; c=$?
grep -E 'COPY-BACK|COLLECTED|STOP|collected ' "$S/c.txt" | cut -c1-240
GSD=docs/reports/gate-stops/$TODAY-e197-regfile-sitting-1-T$T0-aifoundry3
gsd=$([ -s "$T/$GSD/SHA256SUMS" ] && [ -s "$T/$GSD/facts-e197-1.json" ] && echo 1 || echo 0)
gsx=$(cd "$T" && find docs/reports/data -path '*e197*' 2>/dev/null | grep -c .)
RB_OUT="$S/out-a" bash "$R/s22_collect_e197.sh" 1 > "$S/c2.txt" 2>&1; c2=$?
mkdir -p "$S/out-c3"; cp -p "$S/out-a/window.env" "$S/out-a/e197-1-T0.txt" "$S/out-a/box-login-aifoundry3.txt" "$S/out-c3/"
DSD=$TREE/build/e197/T$T0; cp -p "$DSD/session.log" "$S/sl.keep"; printf 'x' >> "$DSD/session.log"
rm -rf "${T:?}/docs/reports/gate-stops"
RB_OUT="$S/out-c3" bash "$R/s22_collect_e197.sh" 1 > "$S/c3.txt" 2>&1; c3=$?
cp -p "$S/sl.keep" "$DSD/session.log"
RB_OUT="$S/out-c3" bash "$R/s22_collect_e197.sh" 1 > "$S/c4.txt" 2>&1; c4=$?
T5=$(( $(date +%s) - 3000 )); D5=$TREE/build/e197/T$T5; mkdir -p "$D5" "$S/out-c5"; win "$S/out-c5" 1; cp -p "$S/out-a/box-login-aifoundry3.txt" "$S/out-c5/"
{ echo "$(date -d @"$T5" '+%Y-%m-%d %H:%M:%S %Z') session start (T0 $T5 = x; E197 sitting 1, plan full; a desk-test stand-in log)"
  echo "$(date -d @"$((T5 + 60))" '+%Y-%m-%d %H:%M:%S %Z') train blocks started: 2 of 4 (A B); complete: 1 (A); train processes recorded: 170"
  echo "$(date -d @"$((T5 + 120))" '+%Y-%m-%d %H:%M:%S %Z') GATE-STOP: a desk-test stand-in line beside blocks begun"
  echo "$(date -d @"$((T5 + 180))" '+%Y-%m-%d %H:%M:%S %Z') session end (T0 $T5)"; } > "$D5/session.log"
( cd "$D5" && sha256sum session.log > MANIFEST.sha256 ); echo 8 > "$D5/wrapper.rc"; echo "$T5" > "$S/out-c5/e197-1-T0.txt"
RB_OUT="$S/out-c5" bash "$R/s22_collect_e197.sh" 1 > "$S/c5.txt" 2>&1; c5=$?
rm -rf "${D5:?}"
stopline "$S/c2.txt"; stopline "$S/c4.txt"; stopline "$S/c5.txt"
ok "$c.$(has 'COPY-BACK EXACT' "$S/c.txt").$(has 'COLLECTED ' "$S/c.txt").$(has "collected the gate stop's record $GSD" "$S/c.txt").$gsd.$gsx.$c2.$(has 'exists already' "$S/c2.txt").$c3.$(has 'COPY-BACK NOT EXACT' "$S/c3.txt").$c4.$(has 'e197-raw/T[0-9]* exists already' "$S/c4.txt").$c5.$(has 'does not say clearly how the session ended' "$S/c5.txt").$([ -e "$S/out-c5/e197-raw/T$T5" ] && echo copied || echo none)" \
  "0.1.1.1.1.0.10.1.16.1.10.1.16.1.none" "C COPY-BACK EXACT into the gate stop's record (nothing under docs/reports/data), the desk-path gate clean, HISTORY OK; C2 again: 10; C3 a changed box file: NOT EXACT (16); C4 its RB_OUT again: 10; C5 an unclear log: 16"

step "RT. the retry in a new RB_OUT"
mkdir -p "$S/out-rt"; win "$S/out-rt" 1
RB_OUT="$S/out-rt" bash "$K6/s05_look_k6.sh" aifoundry3 > /dev/null 2>&1
rb6=17; k=0; while [ "$rb6" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-rt" bash "$R/s08_a3_build_e197.sh" wait > "$S/rt6.txt" 2>&1; rb6=$?; k=$((k + 1)); done
RB_OUT="$S/out-rt" bash "$R/s10_a3_dry_e197.sh" start > /dev/null 2>&1
ry=17; k=0; while [ "$ry" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-rt" bash "$R/s10_a3_dry_e197.sh" wait > "$S/rty.txt" 2>&1; ry=$?; k=$((k + 1)); done
RB_OUT="$S/out-rt" bash "$R/s09_a3_reads_e197.sh" 1 > "$S/rt7.txt" 2>&1; r7=$?
RB_OUT="$S/out-rt" bash "$R/s11_a3_session_e197.sh" 1 > "$S/rt.txt" 2>&1; rt=$?
grep -E '^rest:|LAUNCHED|STOP|sitting 1:' "$S/rt7.txt" "$S/rt.txt" | cut -c1-200
rw=17; k=0; while [ "$rw" -eq 17 ] && [ "$k" -lt 4 ]; do RB_OUT="$S/out-rt" bash "$R/s20_wait_e197.sh" 1 > "$S/rtw.txt" 2>&1; rw=$?; k=$((k + 1)); done
T0R=$(cat "$S/out-rt/e197-1-T0.txt" 2>/dev/null)
echo '{}' > "$ST/scenario.json"
ok "$rb6.$ry.$r7.$(has 'rest: ' "$S/rt7.txt").$rt.$([ -n "$T0R" ] && [ "$T0R" != "$T0" ] && echo 1 || echo 0).$rw.$(has 'GATE-STOPPED e197-1' "$S/rtw.txt")" "0.0.0.1.0.1.16.1" \
  "RT the retry: the build's wait, the dry pass, step 7 (the rest rule skips the session that opened no device), step 9 launched anew; its wait GATE-STOPPED (16)"

if [ -n "$RP" ] && [ -d "$RP/P" ]; then
  step "WR. the wait on the real-path desk test's own sessions"
  mkdir -p "$S/out-wr"; win "$S/out-wr" 1
  wr_run() {  # wr_run <case>: copy that case's session onto the stand-in box, write its T0, run the wait
    local src t
    src=$(ls -d "$RP/$1"/tree/build/e197/T[0-9]* 2>/dev/null | grep -v -- '-dry$' | head -n 1)
    [ -n "$src" ] || { echo "   (no real-path session for $1)"; WR=99; return; }
    t=$(basename "$src"); t=${t#T}
    rm -rf "${TREE:?}/build/e197/T$t"; cp -rp "$src" "$TREE/build/e197/T$t"
    mkdir -p "$TREE/build/q141k"; echo "$t" > "$TREE/build/q141k/e197-1.T0"; echo "$t" > "$S/out-wr/e197-1-T0.txt"
    RB_OUT="$S/out-wr" bash "$R/s20_wait_e197.sh" 1 > "$S/wr-$1.txt" 2>&1; WR=$?
    grep -E 'RUN-|MANIFEST|GATE-STOPPED|STOPPED|CRASHED|HUNG|has ended' "$S/wr-$1.txt" | cut -c1-200 | sed 's/^/   /'
    WRT=$t
  }
  wr_run P; wp=$WR; tp=${WRT:-}
  wr_run S1; ws=$WR
  wr_run G1; wg=$WR
  wr_run X1; wx=$WR
  wr_run HG; wh=$WR
  ok "$wp.$ws.$(has 'STOPPED e197-1' "$S/wr-S1.txt").$wg.$(has 'GATE-STOPPED e197-1' "$S/wr-G1.txt").$wx.$(has 'CRASHED e197-1' "$S/wr-X1.txt").$wh.$(has 'HUNG e197-1' "$S/wr-HG.txt")" "0.0.1.16.1.16.1.16.1" \
    "WR the real sessions: P whole (0); S1 a stop by hand: STOPPED (0); G1 the kit's smoke check: GATE-STOPPED (16); X1 a crash: CRASHED (16); HG a hung host: HUNG (16)"
  step "CR, CR3-CR5. step 11 on the real-path P session, its data committed in the scratch repository, then step 13"
  mkdir -p "$S/out-cr"; win "$S/out-cr" 1; cp -p "$S/out-a/box-login-aifoundry3.txt" "$S/out-cr/"
  echo "$tp" > "$S/out-cr/e197-1-T0.txt"
  RB_OUT="$S/out-cr" bash "$R/s22_collect_e197.sh" 1 > "$S/cr1.txt" 2>&1; cr1=$?
  grep -E 'COPY-BACK|COLLECTED|STOP' "$S/cr1.txt" | cut -c1-220
  DD=docs/reports/data/$TODAY-e197-regfile-sitting-1-aifoundry3
  RB_OUT="$S/out-cr" bash "$R/s24_reduce_e197.sh" 1 > "$S/cr0.txt" 2>&1; cr0=$?
  stopline "$S/cr0.txt"
  printf '# E197 sitting 1: a desk test stand-in README (never a lab file)\n' > "$T/$DD/README.md"
  $G add --sparse "$DD" > /dev/null 2>&1; $G commit -q -m "desk test: the real-path sitting 1's data committed"
  RB_OUT="$S/out-cr" bash "$R/s24_reduce_e197.sh" 1 > "$S/cr2.txt" 2>&1; cr2=$?
  grep -E 'CHECKS READ|reduced after|STOP|box.s manifest' "$S/cr2.txt" | cut -c1-260
  ok "$cr0.$(has 'is not committed' "$S/cr0.txt").$cr1.$(has 'COLLECTED ' "$S/cr1.txt").$cr2.$([ -s "$S/out-cr/regfile-e197-s1.json" ] && echo 1 || echo 0).$([ -s "$S/out-cr/checks-e197-1.json" ] && echo 1 || echo 0)" "10.1.0.1.0.1.1" \
    "CR step 13 before the data commit refused (10); the real session collected; after its data commit the registered reducer and the checker ran (regfile-e197-s1.json, checks-e197-1.json)"
  cp -p "$T/$DD/run/stderr.txt" "$S/stderr.keep"; printf 'x' >> "$T/$DD/run/stderr.txt"
  mkdir -p "$S/out-cr3"; win "$S/out-cr3" 1
  RB_OUT="$S/out-cr3" bash "$R/s24_reduce_e197.sh" 1 > "$S/cr3.txt" 2>&1; cr3=$?
  cp -p "$S/stderr.keep" "$T/$DD/run/stderr.txt"
  awk '/^## Re-make it/ {f = 1; next} f && /^## / {f = 0} f && /^    / {print}' "$T/$E/DATA-README-FORM-e197.md" | sed -n '2,$p' | sed 's/^    //' > "$S/remake.sh"
  echo "   the form's re-make commands ($(grep -c . "$S/remake.sh") lines after its first, which sets D and R):"; sed 's/^/     | /' "$S/remake.sh"
  rm -rf "${S:?}/remake"; mkdir -p "$S/remake"
  ( cd "$T" && D="$DD" R="$S/remake" bash -e "$S/remake.sh" ) > "$S/cr5.txt" 2>&1; cr5=$?
  grep -E 'CHECKS READ|box.s bytes|Error' "$S/cr5.txt" | cut -c1-200
  printf 'x' >> "$T/$DD/run/stderr.txt"; $G add --sparse "$DD/run/stderr.txt"; $G commit -q -m "desk test: a committed change to a data file, SHA256SUMS left"
  cr4c=$($G log -1 --format=%s | grep -c 'SHA256SUMS left')
  mkdir -p "$S/out-cr4"; win "$S/out-cr4" 1
  RB_OUT="$S/out-cr4" bash "$R/s24_reduce_e197.sh" 1 > "$S/cr4.txt" 2>&1; cr4=$?
  [ "$cr4c" -eq 1 ] && $G reset -q --hard HEAD~1
  stopline "$S/cr3.txt"; stopline "$S/cr4.txt"
  ok "$cr3.$(has 'uncommitted changes' "$S/cr3.txt").$cr4.$(has 'does not read every entry OK' "$S/cr4.txt").$cr5.$(has 'CHECKS READ: ' "$S/cr5.txt").$(has "not the box's bytes" "$S/cr5.txt").$(cmp -s "$S/remake/regfile-e197-s1.json" "$S/out-cr/regfile-e197-s1.json" && echo SAME || echo DIFFERENT)" \
    "16.1.16.1.0.1.0.SAME" "CR3 a data file changed, not committed: 16; CR4 a committed change SHA256SUMS does not hold: 16; CR5 the README form's own commands: the box's bytes, the checker, regfile-e197-s1.json the same as step 13's, byte for byte"
  if [ -d "$RP/P2" ]; then
    step "CR2. the real-path P2 session as sitting 2's data, then step 13 for sitting 2: the pooled reduction"
    src=$(ls -d "$RP/P2"/tree/build/e197/T[0-9]* | grep -v -- '-dry$' | head -n 1); t2=$(basename "$src"); t2=${t2#T}
    rm -rf "${TREE:?}/build/e197/T$t2"; cp -rp "$src" "$TREE/build/e197/T$t2"
    mkdir -p "$S/out-cr2"; win "$S/out-cr2" 2; cp -p "$S/out-a/box-login-aifoundry3.txt" "$S/out-cr2/"; echo "$t2" > "$S/out-cr2/e197-2-T0.txt"
    RB_OUT="$S/out-cr2" bash "$R/s22_collect_e197.sh" 2 > "$S/cr21.txt" 2>&1; cr21=$?
    DD2=docs/reports/data/$TODAY-e197-regfile-sitting-2-aifoundry3
    printf '# E197 sitting 2: a desk test stand-in README (never a lab file)\n' > "$T/$DD2/README.md"
    $G add --sparse "$DD2" > /dev/null 2>&1; $G commit -q -m "desk test: the real-path sitting 2's data committed"
    RB_OUT="$S/out-cr2" bash "$R/s24_reduce_e197.sh" 2 > "$S/cr22.txt" 2>&1; cr22=$?
    grep -E 'CHECKS READ|reduced after|STOP' "$S/cr22.txt" | cut -c1-260
    u=$(/usr/bin/python3 -I -B -c 'import json,sys; t=json.load(open(sys.argv[1]))["trains"]; print(t["T1"]["units"], t["T7"]["units"], t["T14"]["units"])' "$S/out-cr2/regfile-e197.json" 2>/dev/null)
    ok "$cr21.$cr22.$u" "0.0.182 9 9" "CR2 sitting 2 collected and committed; step 13 for sitting 2: the pooled reduction, T1 67 + 115 = 182 units, T7 and T14 9 each"
    rm -rf "${T:?}/$DD2"; $G reset -q --hard HEAD~1
  fi
  rm -rf "${T:?}/$DD"; $G reset -q --hard HEAD~1
else
  echo; echo "== WR, CR, CR2: NOT RUN (no real-path desk test scratch given)"
fi

step "Z. nothing of this test left on the stand-in box"
left=$("$REAL_PGREP" -u "$(id -u)" -f 'session_e197\.sh|run_trains\.py|fake_card_e197\.py' | while read -r q; do c=$(readlink "/proc/$q/cwd" 2>/dev/null); case "$c/" in "$BOXH"/*) echo "$q" ;; esac; done | grep -c .)
ok "$left" "0" "Z no session, runner or stand-in of this test left running on the stand-in box"
echo; echo "SELFTEST-RB-E197 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
[ "$fail" -eq 0 ]
