#!/usr/bin/env bash
# E189 (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): the desk test of E189's runbook with a FAKE ssh and rsync on a stand-in box,
# E188's runbook desk test's form (tools/claims-v3/e188/rb/selftest_rb_e188.sh). Its scratch repository is a shared, sparse clone of the lab
# clone this test runs from (so 46a16bd0 and E189's registration commit are in its history, as on the card day) with the kit's files
# committed on top as one stand-in kit commit, the kit list a stand-in made here and pinned in the scratch copy of step 2's KITPIN line (the
# one line this test changes in a copy: the real list holds this test's log). The stand-in box is aifoundry3's ~/aifoundry under the
# scratch; the stand-in ssh serves it with `bash -s` and refuses any other host; the stand-in rsync rewrites aifoundry3: paths onto it; the
# box's cmake is rb/fake_cmake_e189.sh (the REAL hosts built with g++-13 -O2 against the desk mock, stand-in kernel ELFs whose pins this
# test writes: RB_DESKTEST=1 with E189_KERNEL_PINS and E189_OBJCOPY, desk-test only). No lab box is reached. Cases:
#   A   the dry listing: every step exits 0, no call reaches the stand-ins; the look before the post;
#   K   step 2 with no window: 10, no call;  W1 a window written yesterday: 10;  W2 one written for E188: 10;  W3 step 1 for another day: 10;
#   (the day's budget before the last end is 60 s here, E189_DESK_BUDGET_S with RB_DESKTEST=1: the window is today's last minutes)
#   G   step 2 without RB_GITLOCK: 10;  N   step 2 run INSIDE the lab-git lock (nested): its pull cannot take the lock, 16 naming the pull;
#   P1  step 2 on the scratch repository: 0, every list at its count and bytes, HISTORY OK, the registration found by its content;
#   P2  the registration's list one line short: 16;  P3 the kit's list one line short: 16;  P4 a list with SHA256SUMS in the middle of its
#       name: reported, never a gate (0);  H1 a committed edit of a registration file: 16 by the history check;
#   H2  THE SHADOW CASE (verify-e189's nit): an added tools/ledger/struct.py (forecast --check would import it in place of the standard
#       struct): step 2 stops with 16 by the history check, "a shadowing addition" naming it;  H3 the same tree read the 3.9 way
#       (E189_HISTORY_NAMES=dirs, the names from this interpreter's own standard-library directories, as /usr/bin/python3 3.9.6 on the
#       Intel reads them): HISTORY FAIL naming it;  H4 an added package tools/ledger/ast/__init__.py and an added workloads/ledger/copy.py:
#       HISTORY FAIL naming both;
#   H5  THE REDUCER'S FOLDER (verify-fix189's finding 1): an added workloads/sparseparity/tools/json.py (energy_reduce.py, run at the
#       collection without -I, would import it): step 2 stops with 16 by the history check, which names it, the 3.9 way too;
#   H6  an added tools/claims-v3/re.py (the preflight runs dmcmd_audit.py there without -I) and an added v3.1/subprocess.py (k6's rb_common.sh
#       runs rb_run.py there with -B only; verify-fix189's nit 2): HISTORY FAIL naming both;
#   H7  an added _strptime.py at the lab clone's top (step 1's window script runs on stdin there, '' first on sys.path, and time.strptime
#       imports _strptime; found by fix-fix189): HISTORY FAIL naming it;
#   H8  the same kind of file NOT committed: an untracked workloads/sparseparity/tools/gzip.py and tools/claims-v3/re.py, and a _strptime.py
#       staged as new: HISTORY FAIL naming all three as not committed; then the tree clean again: HISTORY OK;
#   S   step 5 (the sync), then step 6 start and wait (17, then 0): LEDGER-BUILT and SPP-BUILT from the real hosts' behaviour, the harness
#       with the built kernels, the preflight and the self-check read on the box, RB_OUT/e189-built.txt "ledger,spp";
#   X   a second start after both built today: 10;
#   U   THE NEGATIVE CONTROL THROUGH THE RUNBOOK: a fresh day, the ledger host built with its budget refusal at 9.9 s: LEDGER-BUILD-FAILED by
#       the host's behaviour (L4), SPP-BUILT; e189-built.txt "spp";
#   T   NO-THIRD-BUILD: two starts recorded today: a third start is refused with 16;
#   L1  THE TAILSCALE-LAPSE RULE: a login link on a read: 11, "<HH:MM:SS> aifoundry3 needs a check" appended to RB_LOCK, nothing retried;
#   L2  a read that hangs: killed at its bound (the read class's bound shortened for this case only): 13;
#   L3  step 6's wait cut (ssh's 255, nothing printed): 14, "no reading";
#   D   step 8 (the box's dry pass, run_e189.py --dry on the stand-in box): 0;
#   RS  THE REST RULE THROUGH STEP 9: an E185-form session ended 10 minutes ago on the box: 10, nothing launched;
#   LA  an E183-form session ended 45 minutes ago instead: step 9 launches the REAL session_e189.sh and run_e189.py, which stop at a gate
#       before any launch (on the Intel at the card lock: no /run/lock on a Mac; on Linux, run inside a sandbox with an empty /run/lock and
#       no /dev/et*, at the lock, a foreign device process or the start config, the stand-in box having no ettelem: "no device opened" or
#       "the gate, no launch"), and write their manifest; step 10 reads the gate (16), the manifest written; no smoke run started;
#   C   step 11 on that session: COPY-BACK EXACT, the data directory, COLLECTED (0 passes), the desk-path gate, HISTORY OK;  C2 one byte of a
#       box file changed after the manifest: COPY-BACK NOT EXACT, 16;
#   Z   no process of this test left running.
#   bash tools/claims-v3/e189/rb/selftest_rb_e189.sh <scratch dir> > <log>    (prints SELFTEST-RB-E189 <n> of <m> PASS or FAIL)
# PORTED Fri 13 Nov 2026 (fix-e189b) to run on either desk: GNU date as gdate (the Intel's Homebrew name) or as date when it is GNU's
# (Linux); the lab-git lock's nested case N with /usr/bin/lockf where it exists, else /usr/bin/flock (-n outside, the step's own -w and
# -E 75 inside: the same exit 75, so the same 16); every in-place edit through sedi (a copy written back: GNU and BSD sed differ on -i);
# the stand-in box's pgrep leaves out its caller's ancestors (Linux's pgrep counts them, so the box's ours_live read found the desk's own
# step 9 script and refused RS and LA; macOS's pgrep leaves them out by default, and on a card day that script runs on another machine).
# FIXED Fri 13 Nov 2026 (fix-fix189): cases H5-H8 (the history check reads its shadow candidates from the folders themselves, added and
# not committed, in eight folders; KIT.md section 10).
# On a box with a card (aifoundry2) run it ONLY inside a sandbox with no /dev/et* and an empty /run/lock: case LA runs the real runner.
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
for c in timeout sha256sum g++-13; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
GDATE=$(command -v gdate 2> /dev/null) || GDATE=""
if [ -z "$GDATE" ] && date --version 2> /dev/null | grep -q 'GNU coreutils'; then GDATE=$(command -v date); fi
[ -n "$GDATE" ] || { echo "no GNU date on PATH (neither gdate nor a GNU date)"; exit 2; }
if [ -x /usr/bin/lockf ]; then LOCKTOOL=lockf; elif [ -x /usr/bin/flock ]; then LOCKTOOL=flock; else echo "neither /usr/bin/lockf nor /usr/bin/flock"; exit 2; fi
sedi() {  # sedi <sed arguments> <file>: sed in place, the same on GNU and BSD sed (the output written back over the file)
  local f=${!#} t; t=$(mktemp "${TMPDIR:-/tmp}/sedi.XXXXXX") || return 2
  sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"
}
REAL_TIMEOUT=$(command -v timeout); REAL_RSYNC=$(command -v rsync)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree box bin out boxbin; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; B=$S/box; BIN=$S/bin; BOXT=$B/aifoundry3/aifoundry
mkdir -p "$B/aifoundry3/aifoundry" "$BIN" "$S/boxbin"
E=tools/claims-v3/e189
main() {
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
# ---- the scratch repository: a shared sparse clone at the registration, then the kit's files as one stand-in commit
REG=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/E189.md | tail -n 1)
[ -n "$REG" ] || { echo "no registration commit in the lab clone's history"; return 2; }
git clone -q --shared --no-checkout "$SRC" "$T" || return 2
G="git -C $T -c user.name=e189-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /workloads/ /docs/reports/data/2026-11-12-q166-progs/ /docs/reports/data/2026-11-12-q166-ledger-v2/ \
  /docs/reports/data/2026-11-12-q166-counter-sparseparity/ /docs/reports/data/2026-09-23-energy-manual/ /docs/reports/data/2026-10-26-load-model/ || return 2
$G checkout -q -B main "$REG" || return 2
$G branch -q -u origin/main 2>/dev/null || $G branch -q --set-upstream-to=origin/main 2>/dev/null
( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E ) | sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
( cd "$SRC" && git ls-files -- $E ) | while IFS= read -r f; do [ -f "$T/$f" ] || { mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; }; done
mkdir -p "$T/$E/logs"
for spec in "desktest-hosts-e189.txt DESKTEST-HOSTS-E189 0 of 0 PASS" "selftest-run-e189.txt SELFTEST-RUN-E189 0 of 0 PASS" \
            "selftest-rest-e189.txt SELFTEST-REST-E189 0 of 0 PASS" "selftest-rb-e189.txt SELFTEST-RB-E189 0 of 0 PASS" \
            "dry-listing-e189.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e189.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}; [ -f "$T/$E/logs/$f" ] || printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"
done
rm -f "$T/$E/SHA256SUMS-e189-kit"
( cd "$T" && find $E -type f ! -name 'SHA256SUMS-e189-kit' ! -path "$E/rb/s03_desk_e189.sh" ! -path "$E/SHA256SUMS-e189-registration" \
    ! -name '*.pyc' | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/kit-standin.txt"
# the registration's own files stay as committed (the list names them); the kit's stand-in list is every other file
( cd "$T" && git show "$REG" --name-only --format= -- $E ) > "$S/reg-files.txt"
grep -v -F -f "$S/reg-files.txt" "$S/kit-standin.txt" > "$S/kit-standin2.txt"; mv "$S/kit-standin2.txt" "$S/kit-standin.txt"
KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e189-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
sedi -e "s#^KITPIN=$E/SHA256SUMS-e189-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e189-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e189.sh"
grep -q "^KITPIN=$E/SHA256SUMS-e189-kit:$KITN:$KITH:top" "$T/$E/rb/s03_desk_e189.sh" || { echo "the scratch step 2's KITPIN was not set"; return 2; }
( cd "$T" && /usr/bin/python3 -I -B $E/check_e189.py --make > /dev/null )
$G add -A $E && $G commit -q -m "E189 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; return 2; }
# the stand-in kit list was made before harness-e189.json was re-made here: make it again and amend, so step 2 reads them at their pins
( cd "$T" && find $E -type f ! -name 'SHA256SUMS-e189-kit' ! -path "$E/rb/s03_desk_e189.sh" ! -name '*.pyc' | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) | grep -v -F -f "$S/reg-files.txt" > "$S/kit-standin.txt"
KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e189-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
sedi -e "s#^KITPIN=$E/SHA256SUMS-e189-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e189-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e189.sh"
$G add -A $E && $G commit -q --amend --no-edit || return 2
echo "scratch repository: a shared sparse clone at the registration ${REG:0:12}, the kit as one stand-in commit $($G rev-parse --short=12 HEAD); the kit list's stand-in $KITN files"
# ---- the stand-ins
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; echo "To authenticate, visit: https://login.tailscale.com/a/e189desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
if [ -e "$S/ssh-cut" ]; then rm -f "$S/ssh-cut"; cat > /dev/null; echo "ssh: connection closed (desk-test stand-in)" >&2; exit 255; fi
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" FAKE_CMAKE_REPO="$T" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho aifoundry3\n' > "$S/boxbin/hostname"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$GDATE" > "$S/boxbin/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
printf '#!/bin/sh\necho "No process holds an ET-SoC-1 device node or card lock."\n' > "$S/boxbin/et-who"
# the stand-in box's pgrep (ported Fri 13 Nov 2026): the real one less its caller's ancestors. The stand-in box runs on the desk, so the
# desk's own step script that reached it (s11_a3_session_e189.sh, whose name holds "session_e189.sh") is an ancestor of the box's
# ours_live read; on a card day that script runs on another machine. macOS's pgrep leaves its ancestors out by default; Linux's does not.
REAL_PGREP=$(command -v pgrep)
cat > "$S/boxbin/pgrep" <<EOF
#!/bin/bash
anc=" "; p=\$PPID
while [ -n "\$p" ] && [ "\$p" -gt 1 ] 2>/dev/null; do anc="\$anc\$p "; p=\$(awk '{print \$4}' /proc/\$p/stat 2>/dev/null); done
out=""; for q in \$("$REAL_PGREP" "\$@"); do case "\$anc" in *" \$q "*) ;; *) out="\$out\$q
"; esac; done
[ -n "\$out" ] || exit 1
printf '%s' "\$out"
EOF
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$REAL_TIMEOUT" > "$S/boxbin/timeout"
printf '#!/bin/sh\n[ "$1" = "-O" ] && [ "$6" = /dev/stdout ] && exec cat "$5"\nexit 2\n' > "$S/boxbin/objcopy"
cp "$SRC/$E/rb/fake_cmake_e189.sh" "$S/boxbin/cmake"
for n in ssh rsync scp sudo; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$S/boxbin/$n"; done
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
lp=$(printf 'E189 desk-test stand-in kernel: ledger\n' | sha256sum | cut -c1-64); sp=$(printf 'E189 desk-test stand-in kernel: sparse parity\n' | sha256sum | cut -c1-64)
printf '{"kernels": {"ledger": {"elf_sha256": "%s", "text_sha256": "%s"}, "spp": {"elf_sha256": "%s", "text_sha256": "%s"}}}\n' "$lp" "$lp" "$sp" "$sp" > "$S/standin-pins.json"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_DESKTEST=1 E189_KERNEL_PINS="$S/standin-pins.json" E189_OBJCOPY="$S/boxbin/objcopy"
export RB_E189_BASE=46a16bd0 E189_DESK_BUDGET_S=60
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/gitlock"
R=$T/$E/rb; K6=$T/tools/claims-v3/q141k-runbook/k6
TODAY=$(TZ=America/Los_Angeles "$GDATE" +%F)
cd "$T" || return 2

step "A. the dry listing"
bash "$R/list_steps_e189.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
lp2=$(awk '/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s ONE post, made AFTER the look/ {p=NR} END {print (l > 0 && p > l) ? 1 : 0}' "$S/dry-listing.txt")
tail -n 1 "$S/dry-listing.txt"
ok "$rc.$(grep -c . "$S/calls.log").$lp2" "0.0.1" "A every step 0, no call to the stand-ins, the look before the post"

step "K, W1-W3, G. the window rule and the lab-git lock"
RB_OUT="$S/out-k" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/k.txt" 2>&1; k=$?
mkdir -p "$S/out-w"
RB_OUT="$S/out-w" bash "$R/s02_window_e189.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
touch -t "$("$GDATE" -d '-1 day' +%Y%m%d%H%M)" "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/w1.txt" 2>&1; w1=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e189.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
sedi -e 's/^RB_PLAN=e189$/RB_PLAN=e188/' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/w2.txt" 2>&1; w2=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e189.sh" "$("$GDATE" -d '+1 day' +%F)" 10:00 12:00 > "$S/w3.txt" 2>&1; w3=$?
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e189.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
RB_OUT="$S/out-p" bash "$R/s03_desk_e189.sh" > "$S/g.txt" 2>&1; g=$?
ok "$k.$(has 'no window in RB_OUT' "$S/k.txt").$w1.$(has 'not written today' "$S/w1.txt").$w2.$(has 'written for e188' "$S/w2.txt").$w3.$(has 'is not today' "$S/w3.txt").$g.$(has 'RB_GITLOCK is not set' "$S/g.txt")" \
  "10.1.10.1.10.1.10.1.10.1" "K, W1-W3, G each refused (10) before any call"

step "N. step 2 run inside the lab-git lock (nested): its pull cannot take the lock"
if [ "$LOCKTOOL" = lockf ]; then
  RB_GITLOCK_T=2 /usr/bin/lockf -k -t 0 "$S/gitlock" env RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/n.txt" 2>&1; n=$?
else
  RB_GITLOCK_T=2 /usr/bin/flock -n -E 75 "$S/gitlock" env RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/n.txt" 2>&1; n=$?
fi
echo "   (the outer lock taken with $LOCKTOOL; the step's own pull waits 2 s for it with $LOCKTOOL, then exits 75)"
stopline "$S/n.txt"
ok "$n.$(has 'pull' "$S/n.txt")" "16.1" "N a nested step 2 stops with 16 naming its pull (never run step 2 inside the lock; outer lock by $LOCKTOOL)"

step "P1. step 2 on the scratch repository"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check:|STOP' "$S/p1.txt" | cut -c1-400
ok "$p1.$(has 'the lists at their pinned counts and bytes (10; 165; 17, 6; 86)' "$S/p1.txt")" "0.1" "P1 step 2 passes at every pin, HISTORY OK, the registration found by its content"

step "P2-P4, H1. a short registration list; a short kit list; an unknown list; an edited registration file"
sedi -e '$d' "$T/$E/SHA256SUMS-e189-registration"; $G commit -q -am "desk test: the registration's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/p2.txt" 2>&1; p2=$?; $G reset -q --hard HEAD~1
sedi -e '$d' "$T/$E/SHA256SUMS-e189-kit"; $G commit -q -am "desk test: the kit's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/p3.txt" 2>&1; p3=$?; $G reset -q --hard HEAD~1
( cd "$T" && sha256sum $E/E189.md > $E/notes-SHA256SUMS-x ); $G add $E/notes-SHA256SUMS-x; $G commit -q -m "desk test: an unknown list"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/p4.txt" 2>&1; p4=$?; $G reset -q --hard HEAD~1
printf '\n' >> "$T/$E/plan_e189.py"; $G commit -q -am "desk test: a registration file edited"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/h1.txt" 2>&1; h1=$?; $G reset -q --hard HEAD~1
ok "$p2.$(has 'SHA256SUMS-e189-registration(9 OK of 9; pinned 10' "$S/p2.txt").$p3.$(has "SHA256SUMS-e189-kit($((KITN - 1)) OK of $((KITN - 1)); pinned $KITN" "$S/p3.txt").$p4.$(has 'notes-SHA256SUMS-x' "$S/out-p/runbook.log").$h1.$(has 'history' "$S/h1.txt")" \
  "16.1.16.1.0.1.16.1" "P2-P4, H1: each pin refused and named; the unknown list reported; the edit refused by the history check"

step "H2-H4. the shadow cases: an added tools/ledger/struct.py; the 3.9 way; an added package and copy.py"
printf 'from _struct import *  # desk test: a stand-in that would shadow the standard struct\n' > "$T/tools/ledger/struct.py"
$G add tools/ledger/struct.py; $G commit -q -m "desk test: a module that shadows the standard struct"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/h2.txt" 2>&1; h2=$?
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e189.py tree --base 46a16bd0 ) > "$S/h2b.txt" 2>&1; h2b=$?
( cd "$T" && E189_HISTORY_NAMES=dirs /usr/bin/python3 -I -B $E/rb/check_history_e189.py tree --base 46a16bd0 ) > "$S/h3.txt" 2>&1; h3=$?
cut -c1-300 "$S/h2b.txt" "$S/h3.txt"
$G reset -q --hard HEAD~1
mkdir -p "$T/tools/ledger/ast"; printf '# desk test\n' > "$T/tools/ledger/ast/__init__.py"; printf '# desk test\n' > "$T/workloads/ledger/copy.py"
$G add tools/ledger/ast/__init__.py workloads/ledger/copy.py; $G commit -q -m "desk test: a package named ast and a module named copy"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e189.py tree --base 46a16bd0 ) > "$S/h4.txt" 2>&1; h4=$?
cut -c1-300 "$S/h4.txt"
$G reset -q --hard HEAD~1
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e189.py tree --base 46a16bd0 ) > "$S/hc.txt" 2>&1; hc=$?
ok "$h2.$(has 'history' "$S/h2.txt").$h2b.$(has 'a shadowing addition: tools/ledger/struct.py (as struct)' "$S/h2b.txt").$h3.$(has 'a shadowing addition: tools/ledger/struct.py (as struct)' "$S/h3.txt").$(has 'standard-library directories' "$S/h3.txt").$h4.$(has 'tools/ledger/ast/__init__.py (as ast)' "$S/h4.txt").$(has 'workloads/ledger/copy.py (as copy)' "$S/h4.txt").$hc" \
  "16.1.16.1.16.1.0.16.1.1.0" "H2-H4 each shadowing addition refused (step 2: 16 by the history check; the 3.9 way too); the tree clean again after"

step "H5-H8. the folders the first fix missed: the reducer's, tools/claims-v3/ and v3.1/, the lab clone's top; files not committed"
printf '# desk test: a stand-in that would shadow the standard json for the reducer\n' > "$T/workloads/sparseparity/tools/json.py"
$G add workloads/sparseparity/tools/json.py; $G commit -q -m "desk test: a module in the reducer's folder that shadows json"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e189.sh" > "$S/h5.txt" 2>&1; h5=$?
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e189.py tree --base 46a16bd0 ) > "$S/h5b.txt" 2>&1; h5b=$?
( cd "$T" && E189_HISTORY_NAMES=dirs /usr/bin/python3 -I -B $E/rb/check_history_e189.py tree --base 46a16bd0 ) > "$S/h5c.txt" 2>&1; h5c=$?
stopline "$S/h5.txt"; cut -c1-300 "$S/h5b.txt" "$S/h5c.txt"
$G reset -q --hard HEAD~1
ok "$h5.$(has 'history' "$S/h5.txt").$h5b.$(has 'a shadowing addition: workloads/sparseparity/tools/json.py (as json)' "$S/h5b.txt").$h5c.$(has 'a shadowing addition: workloads/sparseparity/tools/json.py (as json)' "$S/h5c.txt")" \
  "16.1.16.1.16.1" "H5 an added json.py in the reducer's folder: step 2 stops with 16 by the history check, which names it (the 3.9 way too)"
printf '# desk test\n' > "$T/tools/claims-v3/re.py"; printf '# desk test\n' > "$T/tools/claims-v3/q141k-runbook/v3.1/subprocess.py"
$G add tools/claims-v3/re.py tools/claims-v3/q141k-runbook/v3.1/subprocess.py; $G commit -q -m "desk test: re beside dmcmd_audit.py, subprocess beside rb_run.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e189.py tree --base 46a16bd0 ) > "$S/h6.txt" 2>&1; h6=$?
cut -c1-300 "$S/h6.txt"
$G reset -q --hard HEAD~1
ok "$h6.$(has 'tools/claims-v3/re.py (as re)' "$S/h6.txt").$(has 'tools/claims-v3/q141k-runbook/v3.1/subprocess.py (as subprocess)' "$S/h6.txt")" \
  "16.1.1" "H6 an added re.py in tools/claims-v3/ and subprocess.py in v3.1/: HISTORY FAIL naming both"
printf '# desk test\n' > "$T/_strptime.py"
$G add --sparse _strptime.py; $G commit -q -m "desk test: _strptime at the top, where step 1's window script runs on stdin"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e189.py tree --base 46a16bd0 ) > "$S/h7.txt" 2>&1; h7=$?
cut -c1-300 "$S/h7.txt"
rm -f "${T:?}/_strptime.py"; $G reset -q --hard HEAD~1     # the file first: it lies outside the sparse checkout's folders
ok "$h7.$(has 'a shadowing addition: _strptime.py (as _strptime)' "$S/h7.txt")" "16.1" "H7 an added _strptime.py at the lab clone's top: HISTORY FAIL naming it"
printf '# desk test\n' > "$T/workloads/sparseparity/tools/gzip.py"; printf '# desk test\n' > "$T/tools/claims-v3/re.py"; printf '# desk test\n' > "$T/_strptime.py"
$G add --sparse _strptime.py
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e189.py tree --base 46a16bd0 ) > "$S/h8.txt" 2>&1; h8=$?
cut -c1-400 "$S/h8.txt"
rm -f "${T:?}/_strptime.py" "${T:?}/workloads/sparseparity/tools/gzip.py" "${T:?}/tools/claims-v3/re.py"; $G reset -q --hard HEAD
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e189.py tree --base 46a16bd0 ) > "$S/h8c.txt" 2>&1; h8c=$?
cut -c1-120 "$S/h8c.txt"
ok "$h8.$(has 'a shadowing file not committed' "$S/h8.txt").$(has 'workloads/sparseparity/tools/gzip.py (as gzip)' "$S/h8.txt").$(has 'tools/claims-v3/re.py (as re)' "$S/h8.txt").$(has '_strptime.py (as _strptime)' "$S/h8.txt").$h8c.$(has '^HISTORY OK: ' "$S/h8c.txt")" \
  "16.1.1.1.1.0.1" "H8 the same names not committed (two untracked, one staged as new): HISTORY FAIL naming all three; the tree clean again after"

export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
wd=$TODAY; ls_=23:58; le_=23:59
bash "$R/s02_window_e189.sh" "$wd" "$ls_" "$le_" > /dev/null 2>&1
step "S. step 5 (the sync), then step 6 start and wait on the stand-in box"
bash "$R/s07_a3_sync_e189.sh" > "$S/s5.txt" 2>&1; s5=$?
bash "$R/s08_a3_build_e189.sh" start > "$S/s6a.txt" 2>&1; s6a=$?
n17=0; for i in $(seq 1 20); do bash "$R/s08_a3_build_e189.sh" wait > "$S/s6b.txt" 2>&1; s6b=$?; [ "$s6b" -eq 17 ] || break; n17=$((n17 + 1)); done
grep -E 'LEDGER|SPP|built today|STOP' "$S/s6b.txt" | cut -c1-200
ok "$s5.$s6a.$s6b.$(cat "$RB_OUT/e189-built.txt" 2>/dev/null).$(has 'HARNESS OK' "$S/s6b.txt")" "0.0.0.ledger,spp.1" "S synced, built (after $n17 calls of 17), both hosts read OK by behaviour, the checks on the box"

step "X. a second start after both built today"
bash "$R/s08_a3_build_e189.sh" start > "$S/x.txt" 2>&1; x=$?
ok "$x.$(has 'both programs were built today' "$S/x.txt")" "10.1" "X refused"

step "U. the negative control through the runbook: a fresh day, the ledger host with its budget refusal at 9.9 s"
AT=$BOXT/build/e189-build-attempts.txt
rm -f "${AT:?}"; for z in rc out; do [ -e "$BOXT/build/q141k/jobs/a3-build-e189.$z" ] && touch -t "$("$GDATE" -d '-2 day' +%Y%m%d%H%M)" "$BOXT/build/q141k/jobs/a3-build-e189.$z"; done
printf '#!/bin/sh\nFAKE_CMAKE_MUTANT=l-budget exec bash "%s" "$@"\n' "$SRC/$E/rb/fake_cmake_e189.sh" > "$S/boxbin/cmake"; chmod +x "$S/boxbin/cmake"
bash "$R/s08_a3_build_e189.sh" start > "$S/u1.txt" 2>&1; u1=$?
for i in $(seq 1 20); do bash "$R/s08_a3_build_e189.sh" wait > "$S/u2.txt" 2>&1; u2=$?; [ "$u2" -eq 17 ] || break; done
grep -E 'LEDGER|SPP' "$S/u2.txt" | cut -c1-200
ok "$u1.$u2.$(has 'LEDGER-BUILD-FAILED: the host' "$S/u2.txt").$(has 'L4' "$S/u2.txt").$(cat "$RB_OUT/e189-built.txt")" "0.0.1.1.spp" "U the mutant refused by its behaviour (L4), sparse parity built, e189-built.txt 'spp'"
cp "$SRC/$E/rb/fake_cmake_e189.sh" "$S/boxbin/cmake"; chmod +x "$S/boxbin/cmake"

step "T. NO-THIRD-BUILD: two starts recorded today"
echo "$(TZ=America/Los_Angeles "$GDATE" '+%F %T %Z') a3-build-e189 started" >> "$AT"
bash "$R/s08_a3_build_e189.sh" start > "$S/t.txt" 2>&1; t=$?; stopline "$S/t.txt"
ok "$t.$(has 'NO-THIRD-BUILD' "$S/t.txt")" "16.1" "T a third start the same Pacific day refused with 16"
rm -f "${AT:?}"; bash "$R/s08_a3_build_e189.sh" start > /dev/null 2>&1
for i in $(seq 1 20); do bash "$R/s08_a3_build_e189.sh" wait > "$S/s6c.txt" 2>&1; r=$?; [ "$r" -eq 17 ] || break; done
echo "   (rebuilt both for the later cases: rc $r, $(cat "$RB_OUT/e189-built.txt"))"

step "L1-L3. the kits' form: a login link, a hang, a cut wait"
ln0=$(grep -c . "$RB_LOCK"); touch "$S/ssh-login"
bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/l1.txt" 2>&1; l1=$?
ln1=$(grep -c . "$RB_LOCK"); tail -n 1 "$RB_LOCK"
touch "$S/ssh-hang"; RB_READ_S=3 bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/l2.txt" 2>&1; l2=$?
touch "$S/ssh-cut"; bash "$R/s08_a3_build_e189.sh" wait > "$S/l3.txt" 2>&1; l3=$?
ok "$l1.$((ln1 - ln0)).$(tail -n 1 "$RB_LOCK" | grep -cE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry3 needs a check$').$l2.$l3.$(has 'no reading' "$S/l3.txt")" "11.1.1.13.14.1" \
  "L1 a login link: 11 and the lock line, nothing retried; L2 a hang killed at its bound: 13; L3 a cut wait: 14, no reading"

step "D. step 8, the box's dry pass (run_e189.py --dry on the stand-in box)"
bash "$R/s10_a3_dry_e189.sh" start > "$S/d1.txt" 2>&1; d1=$?
for i in $(seq 1 20); do bash "$R/s10_a3_dry_e189.sh" wait > "$S/d2.txt" 2>&1; d2=$?; [ "$d2" -eq 17 ] || break; done
grep -E 'E189-DRY|smoke gate' "$S/d2.txt" | cut -c1-200
ok "$d1.$d2.$(has 'E189-DRY rc=0 passes=6' "$S/d2.txt")" "0.0.1" "D the dry pass ran six passes and ended rc 0"

step "RS. the rest rule through step 9: an E185-form session ended 10 minutes ago on the box"
mkdir -p "$BOXT/build/e185/T1794486764"
cp "$SRC/docs/reports/data/2026-11-12-e185-m11-session3-aifoundry3/logs/session.log" "$BOXT/build/e185/T1794486764/session.log"
sedi -e "s/^2026-11-12 06:15:21 PST session end/$(TZ=America/Los_Angeles "$GDATE" -d '-10 min' '+%F %T %Z') session end/" "$BOXT/build/e185/T1794486764/session.log"
bash "$R/s11_a3_session_e189.sh" FULL > "$S/rs.txt" 2>&1; rs=$?; stopline "$S/rs.txt"
ok "$rs.$(has 'REFUSED: 10 minutes since E185' "$S/rs.txt").$(ls "$BOXT/build/e189" 2>/dev/null | grep -c '^T[0-9]*$')" "10.1.0" "RS refused (10) naming E185, nothing launched"
rm -rf "${BOXT:?}/build/e185"
mkdir -p "$BOXT/build/e183"
printf '%s session start (T0 1 = 00:00:00 PST), kit note 4; plan FULL\n%s session end (T0 1)\n' "$(TZ=America/Los_Angeles "$GDATE" -d '-100 min' '+%F %T %Z')" "$(TZ=America/Los_Angeles "$GDATE" -d '-45 min' '+%F %T %Z')" > "$BOXT/build/e183/session-t1.log"
step "LA. step 9 launches the REAL session (it stops at a gate before any launch: on a Mac at the card lock, in a Linux sandbox at its start config; no device); step 10 reads the gate"
bash "$R/s11_a3_session_e189.sh" FULL > "$S/la.txt" 2>&1; la=$?
grep -E 'LAUNCHED|rest:' "$S/la.txt" | cut -c1-200
sleep 3
for i in 1 2 3 4; do bash "$R/s20_wait_e189.sh" > "$S/w.txt" 2>&1; w=$?; [ "$w" -eq 17 ] || break; done
ok "$la.$(has 'rest: 45 minutes since E183' "$S/la.txt").$w.$(has 'MANIFEST-WRITTEN' "$S/w.txt").$(has "lock cannot be opened\|lock is held\|no device opened\|the gate, no launch" "$S/w.txt").$(grep -c ' smoke [a-z0-9-]*: rc' "$S/w.txt")" "0.1.16.1.1.0" "LA launched after 45 minutes' rest; the session stopped at a gate before any launch, with its manifest, no smoke run; step 10 reads the gate (16)"

step "C, C2. step 11 on that session; then one byte changed after the manifest"
bash "$R/s22_collect_e189.sh" > "$S/c.txt" 2>&1; c=$?
grep -E 'COPY-BACK|COLLECTED|HISTORY|STOP' "$S/c.txt" | cut -c1-200
D0=docs/reports/data/$wd-e189-blind-day-aifoundry3
ok "$c.$(has 'COPY-BACK EXACT' "$S/c.txt").$(has 'COLLECTED' "$S/c.txt").$([ -f "$T/$D0/SHA256SUMS" ] && echo 1 || echo 0).$(grep -rl '/Users/\|/home/' "$T/$D0" 2>/dev/null | grep -c .)" "0.1.1.1.0" "C collected exactly, the data directory written, no desk or box home path in it"
rm -rf "${T:?}/$D0" "${RB_OUT:?}/e189-raw"
t0=$(cat "$RB_OUT/e189-T0.txt"); printf 'x' >> "$BOXT/build/e189/T$t0/session.log"
bash "$R/s22_collect_e189.sh" > "$S/c2.txt" 2>&1; c2=$?
ok "$c2.$(has 'COPY-BACK NOT EXACT' "$S/c2.txt").$([ -e "$T/$D0" ] && echo 1 || echo 0)" "16.1.0" "C2 a changed byte: not exact, 16, nothing written"
rm -rf "${RB_OUT:?}/e189-raw"

step "Z. no process of this test left running"
z=$(pgrep -f "$S/" 2>/dev/null | grep -c .)
ok "$z" "0" "Z nothing left"
echo
echo "SELFTEST-RB-E189 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<lab clone>#g"
exit "${PIPESTATUS[0]}"
