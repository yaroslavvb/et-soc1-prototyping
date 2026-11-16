#!/usr/bin/env bash
# E194 (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): the desk test of E194's runbook with a
# FAKE ssh and rsync on a stand-in aifoundry2, E191's runbook desk test's form (tools/claims-v3/e191/rb/selftest_rb_e191.sh, unchanged
# beside it): its scratch repository is a shared clone of the lab clone this test runs from, checked out at the commit BEFORE E194's kit
# (the parent of the commit that added tools/claims-v3/e194/KIT.md, or HEAD when none has), with the kit's files committed on top as one
# stand-in kit commit, and its own upstream (a bare copy of itself); it runs in a PRIVATE PID NAMESPACE (rb/selftest_rb_e194_ns.sh).
# The stand-in box is aifoundry2's box tree, ~/claude/et-soc1-prototyping under a stand-in home, a GIT CLONE of the scratch repository (the
# box tree is a git checkout: step 5 reads the kit commit there); the stand-in ssh serves it with `bash -s` and refuses any other host;
# the stand-in rsync rewrites aifoundry2: paths onto it; the box's `hostname` reads "aifoundry2", its `uptime -s` a boot before E69's
# firmware read of record unless a case says otherwise; its cmake is rb/fake_cmake_e194.sh (the REAL hosts built with g++-13 -O2 against
# E189's desk mock), with stand-in kernel ELFs (RB_DESKTEST=1 with E194_KERNEL_PINS, E194_OBJCOPY). THE QUIET DESK FLAG (RB_QUIET) is a
# scratch file raised before the box steps. RB_LOCK is a scratch COPY of the file E194_RB_LOCK_SEED names (the round's lock file), when
# set, else an empty scratch file. No lab box is reached. Cases (verdicts stated first):
#   A   the dry listing: every step exits 0, no call reaches the stand-ins, every printed call names aifoundry2 alone; the runbook's
#       command lines pass desk/drylisting_check_e194.py (ET_DEVICES and V3_DEVICE unset before every device-opening line);
#   K, W1-W3, G  the window rule and RB_GITLOCK: each refused (10) before any call;  N  step 2 inside the lab-git lock: 16 naming its pull;
#   P1  step 2 on the scratch repository: 0, every list at its count and bytes, HISTORY OK, PLANS SAME, NEVER RAN, no E194 data in a ref;
#   P2  E194's registration list one line short: 16;  P3 the kit's list one line short: 16;  P4 a list with SHA256SUMS in its name:
#       reported (0);  H1 a committed edit of a registration file: 16 by the history check;  H2 an added tools/claims-v3/e194/json.py: 16;
#       H3 an edit of E189's hostcheck_e189.py (E194's build runs it): 16;  H4 E194 data in a ref: 16;
#   LK  the look on the box's one card: FREE on the stand-in box, our login written to RB_OUT; LK2 a holder line of another login on card 0:
#       HELD (17); LK3 the box booted after E69's firmware read of record (its `uptime -s`): 16, the identity by continuity not shown;
#   S   step 5 (the tree: the box tree holds the kit commit, its paths clean, HARNESS OK there; nothing copied), then step 6 start and wait
#       (17, then 0): LEDGER-BUILT and SPP-BUILT by behaviour, the ET_DEVICES reading recorded "not a gate", the build records (box
#       aifoundry2), the harness with the built kernels, the preflight and both self-checks read on the box, RB_OUT/e194-built.txt;
#   S0  step 5 on a box tree that lacks the kit commit: 17 (call again); with the word pull it fast-forwards from its upstream and passes;
#   X   a second start after both built today: 10;  U the negative control: a fresh day, the ledger host's budget refusal: LEDGER-BUILD-FAILED
#       by its behaviour (L4);  T NO-THIRD-BUILD: a third start refused with 16;
#   L1  a login link on a read: 11, "<HH:MM:SS> aifoundry2 needs a check" appended to RB_LOCK, nothing retried;  L2 a read that hangs: 13;
#       L3 step 6's wait cut: 14, "no reading";
#   R0  step 7 with a session of ours ended 10 minutes ago in the box tree: THE REST RULE refuses (10) BEFORE any config read (E192's
#       note 1 lesson);  R step 7 after the rest: the stand-in box has no reader: no config line: 16;
#   D   step 8 (the box's dry pass, run_e194.py --dry on the stand-in box): 0, E194-DRY with every pass PASS and the clock ok, dry-check=1,
#       identity-lines=2;
#   RS  THE REST RULE THROUGH STEP 9: E190 arm A's committed session on this card, ended 10 minutes ago: 10, nothing launched;
#   IS  step 9 on a box booted after E69's firmware read of record: k6's guard, IDENTITY-STOP, 16, nothing launched;
#   QP  step 9 with a device-named process of ours on the box (a stand-in ledger_host) that stays: the P2 count refuses (10), nothing
#       launched;
#   LA  a session ended 45 minutes ago instead: step 9 launches the REAL session_e194.sh and run_e194.py, which stop at the box check before
#       any device (the stand-in box tree has no reader: "no device opened") and write their manifest; step 10 reads the gate (16);
#   WT1 step 10 on a stand-in session_e194.sh still running: RUN-RUNNING, 17, never a gate stop;  WT2 that session ended, runner.rc 0: 0;
#       WT3 BOUND: 16;  WT4 (fix-e194, verify-e194's finding 3) the session ended with its manifest and no gate line, runner.rc 1 (a crash
#       after the gate): 16, "the runner exited 1";  WT5 runner.rc not written 10 s after the end: 14;
#   C   step 11 on the LA session: COPY-BACK EXACT, THE BOX-TREE GATE, the data directory, COLLECTED (0 passes), FILES.txt, the scrub, k6's
#       desk-path gate, HISTORY OK, the runner's exit status reported (16, its box check);  C2 one byte of a box file changed after the
#       manifest: COPY-BACK NOT EXACT, 16;
#   SC0 step 13 before the data commit: 10;  SC1 a worktree change: 16;  SC2 a committed byte change: 16;  SC3 committed and clean: 0, "scored:";
#   Z   no process of this test left running.
#   bash tools/claims-v3/e194/rb/selftest_rb_e194_ns.sh <scratch dir> > <log>   (prints SELFTEST-RB-E194 <n> of <m> PASS or FAIL)
# On aifoundry2 run it ONLY inside a sandbox with no /dev/et* and an empty /run/lock: case LA runs the real runner.
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
for c in timeout sha256sum g++-13 flock; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
date --version 2> /dev/null | grep -q 'GNU coreutils' || { echo "no GNU date"; exit 2; }
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox"; exit 3; }
sedi() { local f=${!#} t; t=$(mktemp "${TMPDIR:-/tmp}/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
REAL_TIMEOUT=$(command -v timeout); REAL_RSYNC=$(command -v rsync)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree box bin out boxbin; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; B=$S/box; BIN=$S/bin; BOXT=$B/aifoundry2/claude/et-soc1-prototyping
mkdir -p "$B/aifoundry2/claude" "$BIN" "$S/boxbin" "$S/standin"
E=tools/claims-v3/e194
main() {
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
echo "selftest_rb_e194: $(date '+%F %T %Z'), processes visible: $(ls /proc | grep -c '^[0-9]')"
# ---- the scratch repository: a shared clone at the commit before E194's kit, the kit's files as one stand-in commit, its own upstream
KITC=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/KIT.md | tail -n 1)
if [ -n "$KITC" ]; then BASE=$(git -C "$SRC" rev-parse "$KITC^"); else BASE=$(git -C "$SRC" rev-parse HEAD); fi
git clone -q --shared --no-checkout "$SRC" "$T" || return 2
G="git -C $T -c user.name=e194-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /workloads/ /docs/reports/data/2026-11-12-q166-progs/ /docs/reports/data/2026-11-12-q166-ledger-v2/ \
  /docs/reports/data/2026-11-12-q166-counter-sparseparity/ /docs/reports/data/2026-09-23-energy-manual/ /docs/reports/data/2026-10-26-load-model/ \
  /docs/reports/data/2026-11-13-e190-large-gemm/ /docs/reports/data/2026-11-14-e189-blind-day-aifoundry3/ \
  /docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/ '/docs/reports/data/*-e194-*/' || return 2
$G checkout -q -B main "$BASE" || return 2
( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E; git ls-files -- $E ) | sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
mkdir -p "$T/$E/logs"
for spec in "selftest-run-e194.txt SELFTEST-RUN-E194 0 of 0 PASS" "realpath-e194.txt REALPATH-E194 0 of 0 PASS" \
            "dry-audit-e194.txt DRY-AUDIT-E194 0 of 0 COVERED" "selftest-rest-e194.txt SELFTEST-REST-E194 0 of 0 PASS" \
            "selftest-rb-e194.txt SELFTEST-RB-E194 0 of 0 PASS" "selftest-wait-e194.txt SELFTEST-WAIT-E194 0 of 0 PASS" \
            "selftest-quiet-e194.txt SELFTEST-QUIET-E194 0 of 0 PASS" "parser-e194.txt PARSER-E194 0 of 0 PASS" \
            "identity-e194.txt IDENTITY-E194 0 of 0 PASS" "checks-e194.txt CHECKS-E194 0 of 0 PASS" "realbuild-e194.txt REALBUILD-E194 0 of 0 PASS" \
            "dry-listing-e194.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls beyond aifoundry2" "dmcmd-audit-e194.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}   # a log the clone lacks gets its stand-in line; this test's own log (being written by this run) always does
  if [ "$f" = selftest-rb-e194.txt ] || [ ! -f "$T/$E/logs/$f" ]; then printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"; fi
done
( cd "$T" && git show "$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/E194.md | tail -n 1)" --name-only --format= -- $E ) | sort -u > "$S/reg-files.txt"
mklist() {  # the stand-in kit list: every e194 file but the registration's, the list itself and step 2
  ( cd "$T" && find $E -type f ! -name 'SHA256SUMS-e194-kit' ! -path "$E/rb/s03_desk_e194.sh" ! -name '*.pyc' | LC_ALL=C sort |
    while IFS= read -r f; do sha256sum "$f"; done ) | grep -v -F -f "$S/reg-files.txt" > "$S/kit-standin.txt"
  KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e194-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^KITPIN=$E/SHA256SUMS-e194-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e194-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e194.sh"
}
( cd "$T" && /usr/bin/python3 -I -B $E/check_e194.py --make > /dev/null )
mklist
$G add -A $E && $G commit -q -m "E194 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; return 2; }
grep -q "^KITPIN=$E/SHA256SUMS-e194-kit:$KITN:$KITH:top" "$T/$E/rb/s03_desk_e194.sh" || { echo "the scratch step 2's KITPIN was not set"; return 2; }
git clone -q --bare "$T" "$S/origin.git" && $G remote set-url origin "$S/origin.git" && $G fetch -q origin && $G branch -q -u origin/main main || return 2
echo "scratch repository: a shared sparse clone at ${BASE:0:12} (the commit before E194's kit), the kit as one stand-in commit $($G rev-parse --short=12 HEAD), its own upstream; the kit list's stand-in $KITN files"
# ---- the stand-ins
git clone -q "$T" "$BOXT" || { echo "the stand-in box tree clone failed"; return 2; }
git -C "$BOXT" -c core.hooksPath=/dev/null checkout -q main 2>/dev/null
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry2) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; echo "To authenticate, visit: https://login.tailscale.com/a/e194desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
if [ -e "$S/ssh-cut" ]; then rm -f "$S/ssh-cut"; cat > /dev/null; echo "ssh: connection closed (desk-test stand-in)" >&2; exit 255; fi
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" FAKE_CMAKE_REPO="$T" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry2) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho aifoundry2\n' > "$S/boxbin/hostname"
# aifoundry2 booted Mon 26 Oct 2026 11:54:22, before E69's firmware read of record (27 Oct 13:56:26 PDT): the stand-in box's `uptime -s`
# says so; "$S/boot-late" makes it say this box's real boot after its crash (Fri 13 Nov 2026 16:53:28): cases LK3 and IS
cat > "$S/boxbin/uptime" <<EOF
#!/bin/sh
if [ "\$1" = -s ]; then if [ -e "$S/boot-late" ]; then echo "2026-11-13 16:53:28"; else echo "2026-10-26 11:54:22"; fi; exit 0; fi
exec /usr/bin/uptime "\$@"
EOF
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
cat > "$S/boxbin/et-who" <<EOF
#!/bin/sh
[ -e "$S/etwho-other" ] && { echo "/dev/et0_ops   someoneelse      4242       00:01 other_host"; exit 0; }
echo "No process holds an ET-SoC-1 device node or card lock."
EOF
printf '#!/bin/sh\necho "et-lab-manifest (desk-test stand-in): sysfs and files only"\n' > "$S/boxbin/et-lab-manifest"
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$REAL_TIMEOUT" > "$S/boxbin/timeout"
printf '#!/bin/sh\n[ "$1" = "-O" ] && [ "$6" = /dev/stdout ] && exec cat "$5"\nexit 2\n' > "$S/boxbin/objcopy"
printf '#!/bin/sh\nexec bash "%s" "$@"\n' "$SRC/$E/rb/fake_cmake_e194.sh" > "$S/boxbin/cmake"
for n in ssh rsync scp sudo; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$S/boxbin/$n"; done
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
cp /usr/bin/sleep "$S/standin/ledger_host"
lp=$(printf 'E189 desk-test stand-in kernel: ledger\n' | sha256sum | cut -c1-64); sp=$(printf 'E189 desk-test stand-in kernel: sparse parity\n' | sha256sum | cut -c1-64)
printf '{"kernels": {"ledger": {"elf_sha256": "%s", "text_sha256": "%s"}, "spp": {"elf_sha256": "%s", "text_sha256": "%s"}}}\n' "$lp" "$lp" "$sp" "$sp" > "$S/standin-pins.json"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_DESKTEST=1 E194_KERNEL_PINS="$S/standin-pins.json" E194_OBJCOPY="$S/boxbin/objcopy" \
  E194_DESK_BUDGET_S=60 RB_QUIET="$S/quiet-flag"
: > "$S/calls.log"; : > "$S/gitlock"
# RB_LOCK: a COPY of the round's lock file when E194_RB_LOCK_SEED names it (the task's form: never the file itself), else an empty file;
# L1 counts the lines it adds
if [ -n "${E194_RB_LOCK_SEED:-}" ]; then cp "$E194_RB_LOCK_SEED" "$RB_LOCK" || return 2
  echo "RB_LOCK: a copy of the round's lock file ($(grep -c . "$RB_LOCK") lines), never the file itself"
else : > "$RB_LOCK"; echo "RB_LOCK: an empty scratch file"; fi
R=$T/$E/rb
TODAY=$(TZ=America/Los_Angeles date +%F)
cd "$T" || return 2

step "A. the dry listing, and the runbook's command lines"
bash "$R/list_steps_e194.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
/usr/bin/python3 -I -B "$T/$E/desk/drylisting_check_e194.py" "$S/dry-listing.txt" > "$S/dry-check.txt" 2>&1; dc=$?
tail -n 1 "$S/dry-listing.txt"; tail -n 1 "$S/dry-check.txt"
ok "$rc.$(grep -c . "$S/calls.log").$dc" "0.0.0" "A every step 0, no call to the stand-ins, every printed call to aifoundry2 alone; every device-opening line after an unset of ET_DEVICES and V3_DEVICE"

step "K, W1-W3, G. the window rule and the lab-git lock"
RB_OUT="$S/out-k" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/k.txt" 2>&1; k=$?
mkdir -p "$S/out-w"
RB_OUT="$S/out-w" bash "$R/s02_window_e194.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
touch -t "$(date -d '-1 day' +%Y%m%d%H%M)" "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/w1.txt" 2>&1; w1=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e194.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
sedi -e 's/^RB_PLAN=e194$/RB_PLAN=e191/' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/w2.txt" 2>&1; w2=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e194.sh" "$(date -d '+1 day' +%F)" 10:00 12:00 > "$S/w3.txt" 2>&1; w3=$?
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e194.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
RB_OUT="$S/out-p" bash "$R/s03_desk_e194.sh" > "$S/g.txt" 2>&1; g=$?
ok "$k.$(has 'no window in RB_OUT' "$S/k.txt").$w1.$(has 'not written today' "$S/w1.txt").$w2.$(has 'written for e191' "$S/w2.txt").$w3.$(has 'is not today' "$S/w3.txt").$g.$(has 'RB_GITLOCK is not set' "$S/g.txt")" \
  "10.1.10.1.10.1.10.1.10.1" "K, W1-W3, G each refused (10) before any call"

step "N. step 2 run inside the lab-git lock (nested): its pull cannot take the lock"
RB_GITLOCK_T=2 /usr/bin/flock -n -E 75 "$S/gitlock" env RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/n.txt" 2>&1; n=$?
stopline "$S/n.txt"
ok "$n.$(has 'pull' "$S/n.txt")" "16.1" "N a nested step 2 stops with 16 naming its pull"

step "P1. step 2 on the scratch repository"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check:|STOP' "$S/p1.txt" | cut -c1-600
ok "$p1.$(has 'the lists at their pinned counts and bytes (17; 1; 11; 3; 10; 55; 165; 17, 6; 86)' "$S/p1.txt").$(has "NEVER RAN with E189's and both of E191's data folders left out, no E194 data in any ref" "$S/p1.txt")" "0.1.1" \
  "P1 step 2 passes at every pin, HISTORY OK, PLANS SAME, the never-run check, no E194 data"

step "P2-P4, H1-H4. a short registration list; a short kit list; an unknown list; an edited registration file; shadows; E194 data in a ref"
sedi -e '$d' "$T/$E/SHA256SUMS-e194-registration"; $G commit -q -am "desk test: the registration's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/p2.txt" 2>&1; p2=$?; $G reset -q --hard HEAD~1
sedi -e '$d' "$T/$E/SHA256SUMS-e194-kit"; $G commit -q -am "desk test: the kit's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/p3.txt" 2>&1; p3=$?; $G reset -q --hard HEAD~1
( cd "$T" && sha256sum $E/E194.md > $E/notes-SHA256SUMS-x ); $G add $E/notes-SHA256SUMS-x; $G commit -q -m "desk test: an unknown list"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/p4.txt" 2>&1; p4=$?; $G reset -q --hard HEAD~1
printf '\n' >> "$T/$E/plan_e194.py"; $G commit -q -am "desk test: a registration file edited"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/h1.txt" 2>&1; h1=$?; $G reset -q --hard HEAD~1
printf '# desk test\n' > "$T/$E/json.py"; $G add $E/json.py; $G commit -q -m "desk test: a json.py beside the runner"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/h2.txt" 2>&1; h2=$?
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e194.py tree --base 46a16bd0 ) > "$S/h2b.txt" 2>&1; $G reset -q --hard HEAD~1
printf '\n' >> "$T/tools/claims-v3/e189/hostcheck_e189.py"; $G commit -q -am "desk test: E189's host check edited"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/h3.txt" 2>&1; h3=$?; $G reset -q --hard HEAD~1
$G branch -q e194-data-standin; $G checkout -q e194-data-standin; mkdir -p "$T/docs/reports/data/2026-11-15-e194-x"; echo x > "$T/docs/reports/data/2026-11-15-e194-x/README.md"
$G add --sparse docs/reports/data/2026-11-15-e194-x/README.md; $G commit -q -m "desk test: E194 data in a ref"; $G checkout -q main
rm -rf "${T:?}/docs/reports/data/2026-11-15-e194-x"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e194.sh" > "$S/h4.txt" 2>&1; h4=$?; $G branch -q -D e194-data-standin
ok "$p2.$(has 'SHA256SUMS-e194-registration(16 OK of 16; pinned 17' "$S/p2.txt").$p3.$(has "SHA256SUMS-e194-kit($((KITN - 1)) OK of $((KITN - 1)); pinned $KITN" "$S/p3.txt").$p4.$(has 'notes-SHA256SUMS-x' "$S/out-p/runbook.log").$h1.$(has 'history' "$S/h1.txt").$h2.$(has 'tools/claims-v3/e194/json.py (as json)' "$S/h2b.txt").$h3.$(has 'history' "$S/h3.txt").$h4.$(has 'e194-data(' "$S/h4.txt")" \
  "16.1.16.1.0.1.16.1.16.1.16.1.16.1" "P2-P4, H1-H4: each pin refused and named; the unknown list reported; the edit, the shadow, E189's file and E194 data refused"

export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
bash "$R/s02_window_e194.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1
bash "$R/quiet_e194.sh" raise card-e194-desktest > /dev/null
step "LK, LK2, LK3. the look, the box's one card"
bash "$R/s05_look_e194.sh" > "$S/lk.txt" 2>&1; lk=$?
grep -E 'the card:|FREE|HELD|^    P2' "$S/lk.txt" | cut -c1-260
touch "$S/etwho-other"; bash "$R/s05_look_e194.sh" > "$S/lk2.txt" 2>&1; lk2=$?; rm -f "$S/etwho-other" "$RB_OUT/hold-aifoundry2.since"
grep -E 'the card:' "$S/lk2.txt" | cut -c1-260
touch "$S/boot-late"; bash "$R/s05_look_e194.sh" > "$S/lk3.txt" 2>&1; lk3=$?; rm -f "$S/boot-late"
stopline "$S/lk3.txt"
ok "$lk.$(cat "$RB_OUT/box-login-aifoundry2.txt" 2>/dev/null | grep -c "^$(id -un)$").$lk2.$(has "card 0 holder lines: ours 0, another login's 1" "$S/lk2.txt").$lk3.$(has "booted after E69's firmware read of record" "$S/lk3.txt")" "0.1.17.1.16.1" \
  "LK FREE, our login written; LK2 another login on card 0: HELD (17); LK3 a boot after E69's firmware read of record: 16"

step "S0. step 5 on a box tree that lacks the kit commit: 17; with the word pull it fast-forwards and passes"
git -C "$BOXT" -c core.hooksPath=/dev/null reset -q --hard HEAD~1
bash "$R/s07_tree_e194.sh" > "$S/s0a.txt" 2>&1; s0a=$?
bash "$R/s07_tree_e194.sh" pull > "$S/s0b.txt" 2>&1; s0b=$?
grep -E 'TREE-|HARNESS|STOP|PULL' "$S/s0a.txt" "$S/s0b.txt" | cut -c1-200
ok "$s0a.$(has 'TREE-LACKS-KIT' "$S/s0a.txt").$s0b.$(has 'HARNESS OK there (nothing copied)' "$S/s0b.txt")" "17.1.0.1" "S0 lacking the kit commit: 17; pull --ff-only from its upstream, then HARNESS OK"
step "S. step 5 (the tree) then step 6 start and wait on the stand-in box"
bash "$R/s07_tree_e194.sh" > "$S/s5.txt" 2>&1; s5=$?
bash "$R/s08_build_e194.sh" start > "$S/s6a.txt" 2>&1; s6a=$?
n17=0; for i in $(seq 1 30); do bash "$R/s08_build_e194.sh" wait > "$S/s6b.txt" 2>&1; s6b=$?; [ "$s6b" -eq 17 ] || break; n17=$((n17 + 1)); done
grep -E 'LEDGER|SPP|built today|STOP|HARNESS|ETDEVICES' "$S/s5.txt" "$S/s6b.txt" | cut -c1-220
ok "$s5.$(has 'HARNESS OK there' "$S/s5.txt").$s6a.$s6b.$(cat "$RB_OUT/e194-built.txt" 2>/dev/null).$(has 'BUILD-RECORD ledger ok: builder build_e194.sh, BUILT, .*, box aifoundry2' "$S/s6b.txt").$(grep 'ETDEVICES: no: ' "$S/s6b.txt" | sed 's/^ *//' | sort -u | grep -c .)" \
  "0.1.0.0.ledger,spp.1.2" "S the tree read (nothing copied), built (after $n17 calls of 17): both hosts by behaviour, the ET_DEVICES reading recorded (not a gate), the records and checks on the box"

step "X. a second start after both built today"
bash "$R/s08_build_e194.sh" start > "$S/x.txt" 2>&1; x=$?
ok "$x.$(has 'both programs were built today' "$S/x.txt")" "10.1" "X refused"

AT=$BOXT/build/e194-build-attempts.txt
freshday() { rm -f "${AT:?}"; for z in rc out; do [ -e "$BOXT/build/q141k/jobs/a2-build-e194.$z" ] && touch -t "$(date -d '-2 day' +%Y%m%d%H%M)" "$BOXT/build/q141k/jobs/a2-build-e194.$z"; done; }
step "U. the negative control through the runbook: a fresh day, the ledger host with its budget refusal at 9.9 s"
freshday
printf '#!/bin/sh\nFAKE_CMAKE_MUTANT=l-budget exec bash "%s" "$@"\n' "$SRC/$E/rb/fake_cmake_e194.sh" > "$S/boxbin/cmake"; chmod +x "$S/boxbin/cmake"
bash "$R/s08_build_e194.sh" start > "$S/u1.txt" 2>&1; u1=$?
for i in $(seq 1 30); do bash "$R/s08_build_e194.sh" wait > "$S/u2.txt" 2>&1; u2=$?; [ "$u2" -eq 17 ] || break; done
grep -E 'LEDGER|SPP' "$S/u2.txt" | cut -c1-200
ok "$u1.$u2.$(has 'LEDGER-BUILD-FAILED: the host' "$S/u2.txt").$(has 'L4' "$S/u2.txt").$(cat "$RB_OUT/e194-built.txt")" "0.0.1.1.spp" "U the mutant refused by its behaviour (L4), sparse parity built"
printf '#!/bin/sh\nexec bash "%s" "$@"\n' "$SRC/$E/rb/fake_cmake_e194.sh" > "$S/boxbin/cmake"; chmod +x "$S/boxbin/cmake"

step "T. NO-THIRD-BUILD: two starts recorded today"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a2-build-e194 started" >> "$AT"
bash "$R/s08_build_e194.sh" start > "$S/t.txt" 2>&1; t=$?; stopline "$S/t.txt"
ok "$t.$(has 'NO-THIRD-BUILD' "$S/t.txt")" "16.1" "T a third start the same Pacific day refused with 16"
freshday; bash "$R/s08_build_e194.sh" start > /dev/null 2>&1
for i in $(seq 1 30); do bash "$R/s08_build_e194.sh" wait > "$S/s6c.txt" 2>&1; r=$?; [ "$r" -eq 17 ] || break; done
echo "   (rebuilt both for the later cases: rc $r, $(cat "$RB_OUT/e194-built.txt"))"

step "L1-L3. the kits' form: a login link, a hang, a cut wait"
ln0=$(grep -c . "$RB_LOCK"); touch "$S/ssh-login"
bash "$R/s05_look_e194.sh" > "$S/l1.txt" 2>&1; l1=$?
ln1=$(grep -c . "$RB_LOCK"); tail -n 1 "$RB_LOCK"
touch "$S/ssh-hang"; RB_READ_S=3 bash "$R/s05_look_e194.sh" > "$S/l2.txt" 2>&1; l2=$?
touch "$S/ssh-cut"; bash "$R/s08_build_e194.sh" wait > "$S/l3.txt" 2>&1; l3=$?
ok "$l1.$((ln1 - ln0)).$(tail -n 1 "$RB_LOCK" | grep -cE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry2 needs a check$').$l2.$l3.$(has 'no reading' "$S/l3.txt")" "11.1.1.13.14.1" \
  "L1 a login link: 11 and the lock line, nothing retried; L2 a hang killed at its bound: 13; L3 a cut wait: 14, no reading"

step "R0, R. step 7, the reads: THE REST RULE first (a session of ours ended 10 minutes ago), then after the rest (no reader on the stand-in box)"
mkdir -p "$BOXT/build/e190/T1794614878-A"
cp "$SRC/docs/reports/data/2026-11-13-e190-large-gemm/aifoundry2/session.log" "$BOXT/build/e190/T1794614878-A/session.log"
sedi -e "s/^2026-11-13 16:24:57 PST session end/$(TZ=America/Los_Angeles date -d '-10 min' '+%F %T %Z') session end/" "$BOXT/build/e190/T1794614878-A/session.log"
bash "$R/s09_reads_e194.sh" > "$S/r0.txt" 2>&1; r0=$?; stopline "$S/r0.txt"
mv "$BOXT/build/e190" "$S/e190-aside"
bash "$R/s09_reads_e194.sh" > "$S/r.txt" 2>&1; rr=$?; stopline "$S/r.txt"
ok "$r0.$(has 'the rest has not opened' "$S/r0.txt").$(has 'REFUSED: 10 minutes since E190' "$S/r0.txt").$(grep -c '^CONFIG' "$S/r0.txt").$rr.$(has 'no config read came back' "$S/r.txt")" "10.1.1.0.16.1" \
  "R0 the rest not open: refused (10) before any config read (E192's note 1 lesson); R after the rest: no config line from the stand-in box: 16"

step "D. step 8, the box's dry pass (run_e194.py --dry on the stand-in box)"
bash "$R/s10_dry_e194.sh" start > "$S/d1.txt" 2>&1; d1=$?
for i in $(seq 1 30); do bash "$R/s10_dry_e194.sh" wait > "$S/d2.txt" 2>&1; d2=$?; [ "$d2" -eq 17 ] || break; done
grep -E 'E194-DRY|smoke gate|device-command check' "$S/d2.txt" | cut -c1-220
ok "$d1.$d2.$(has 'E194-DRY rc=0 passes=6 of 6 (each PASS with the clock ok) dry-check=1 identity-lines=2' "$S/d2.txt")" "0.0.1" \
  "D the dry pass ran six passes, each PASS with the clock ok, its dry check and identity lines, rc 0"

step "RS. the rest rule through step 9: E190 arm A's committed session on this card ended 10 minutes ago"
mv "$S/e190-aside" "$BOXT/build/e190"
bash "$R/s11_session_e194.sh" FULL > "$S/rs.txt" 2>&1; rs=$?; stopline "$S/rs.txt"
ok "$rs.$(has 'REFUSED: 10 minutes since E190' "$S/rs.txt").$(ls "$BOXT/build/e194" 2>/dev/null | grep -c '^T[0-9]*$')" "10.1.0" "RS refused (10) naming E190, nothing launched"
rm -rf "${BOXT:?}/build/e190"
mkdir -p "$BOXT/build/e184"
printf '%s session start (T0 1 = 00:00:00 PST; arm B)\n%s session end (T0 1)\n' "$(TZ=America/Los_Angeles date -d '-100 min' '+%F %T %Z')" "$(TZ=America/Los_Angeles date -d '-45 min' '+%F %T %Z')" > "$BOXT/build/e184/session-B-t1.log"
step "IS. step 9 on a box booted after E69's firmware read of record: k6's guard"
touch "$S/boot-late"; bash "$R/s11_session_e194.sh" FULL > "$S/is.txt" 2>&1; is=$?; rm -f "$S/boot-late"; stopline "$S/is.txt"
ok "$is.$(has 'IDENTITY-STOP: aifoundry2 booted' "$S/is.txt").$(ls "$BOXT/build/e194" 2>/dev/null | grep -c '^T[0-9]*$')" "16.1.0" "IS IDENTITY-STOP (16), nothing launched"
step "QP. step 9 with a device-named process of ours on the box that stays: THE P2 COUNT"
"$S/standin/ledger_host" 60 & qp=$!
bash "$R/s11_session_e194.sh" FULL > "$S/qp.txt" 2>&1; qpr=$?; kill "$qp" 2>/dev/null; wait "$qp" 2>/dev/null; stopline "$S/qp.txt"
ok "$qpr.$(has 'the P2 count is not 0 after 5 reads' "$S/qp.txt").$(ls "$BOXT/build/e194" 2>/dev/null | grep -c '^T[0-9]*$')" "10.1.0" "QP the P2 count read 1 five times: refused (10), nothing launched"
step "LA. step 9 launches the REAL session (its box check stops it before any device: no reader in the stand-in box tree); step 10 reads the gate"
bash "$R/s11_session_e194.sh" FULL > "$S/la.txt" 2>&1; la=$?
grep -E 'LAUNCHED|rest:|quiet desk' "$S/la.txt" | cut -c1-200
sleep 3
for i in 1 2 3 4; do RB_WAIT_LOOP_S=20 bash "$R/s20_wait_e194.sh" > "$S/w.txt" 2>&1; w=$?; [ "$w" -eq 17 ] || break; done
grep -E 'box check|GATE|MANIFEST' "$S/w.txt" | cut -c1-220
ok "$la.$(has 'rest: 45 minutes since E184' "$S/la.txt").$(has 'quiet desk: P2 0 ' "$S/la.txt").$w.$(has 'MANIFEST-WRITTEN' "$S/w.txt").$(has 'the box check: no reader build/ettelem-hpl/ettelem' "$S/w.txt").$(grep -c ' smoke [a-z0-9-]*: rc' "$S/w.txt")" "0.1.1.16.1.1.0" \
  "LA launched after 45 minutes' rest and a P2 count of 0; the real session stopped at its box check before any device, with its manifest; step 10 reads the gate (16)"

step "WT1-WT3. step 10 on a stand-in session_e194.sh: running, ended, BOUND"
t0=$(cat "$RB_OUT/e194-T0.txt"); SD=$BOXT/build/e194/T$t0; mv "$SD" "$S/la-session"; mkdir -p "$SD" "$S/standin/tools/claims-v3/e194"
printf '#!/bin/bash\nsleep 40\n' > "$S/standin/tools/claims-v3/e194/session_e194.sh"
{ printf '%s session start (T0 %s = 00:00:00 PST; plan FULL; programs ledger+spp; aifoundry2 card 0, ET_DEVICES unset; its files in build/e194/T%s)\n' "$(date '+%F %T %Z')" "$t0" "$t0"
  printf '%s the box check: aifoundry2, ET_DEVICES and V3_DEVICE unset, the reader at its pin, today'"'"'s builds on aifoundry2 by build_e194.sh\n' "$(date '+%F %T %Z')"
  printf '%s config start: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 519 (read, nothing set); identity (a): /dev/et0_mgmt, device ID 0, minion_mv between 450 and 600\n' "$(date '+%F %T %Z')"
  printf '%s identity (b): et-who with the sampler running: ours on card 0 2 (on /dev/et0_mgmt 1), ours off card 0 0, another login'"'"'s 0; the sampler holds /dev/et0_mgmt only\n' "$(date '+%F %T %Z')"
  printf '%s pass 1: copy-zeros p1 done: host rc 1, status FAIL, reading SHORT (7 of 8 launches, the host'"'"'s own budget: scored on its launches), the clock off (12 samples), SET ASIDE: the clock: 2 of 12 live samples read [700] MHz, not 800\n' "$(date '+%F %T %Z')"; } > "$SD/session.log"
bash "$S/standin/tools/claims-v3/e194/session_e194.sh" &
sp=$!
RB_WAIT_LOOP_S=3 bash "$R/s20_wait_e194.sh" > "$S/wt1.txt" 2>&1; wt1=$?
printf '%s session end (T0 %s)\n' "$(date '+%F %T %Z')" "$t0" >> "$SD/session.log"; echo "x  session.log" > "$SD/MANIFEST.sha256"
kill "$sp" 2>/dev/null; wait "$sp" 2>/dev/null
echo 1 > "$SD/runner.rc"                                       # fix-e194 (finding 3): WT4, a crash after the gate (no gate line)
RB_WAIT_LOOP_S=3 bash "$R/s20_wait_e194.sh" > "$S/wt4.txt" 2>&1; wt4=$?
rm -f "$SD/runner.rc"                                          # WT5: runner.rc not written
RB_WAIT_LOOP_S=3 bash "$R/s20_wait_e194.sh" > "$S/wt5.txt" 2>&1; wt5=$?
echo 0 > "$SD/runner.rc"
RB_WAIT_LOOP_S=3 bash "$R/s20_wait_e194.sh" > "$S/wt2.txt" 2>&1; wt2=$?
printf '%s BOUND: the host process (pid 1) outlived the runner'"'"'s 30 s bound: `timeout 10` did not end it; nothing is killed; the queue stops\n' "$(date '+%F %T %Z')" >> "$SD/session.log"
RB_WAIT_LOOP_S=3 bash "$R/s20_wait_e194.sh" > "$S/wt3.txt" 2>&1; wt3=$?
rm -rf "${SD:?}"; mv "$S/la-session" "$SD"
ok "$wt1.$(has 'RUN-RUNNING' "$S/wt1.txt").$(has 'GATE-STOPPED' "$S/wt1.txt").$(has 'reading SHORT (7 of 8' "$S/wt1.txt").$wt2.$(has 'the runner exited 0' "$S/wt2.txt").$wt3.$(has 'BOUND-SEEN' "$S/wt3.txt")" "17.1.0.1.0.1.16.1" \
  "WT1 running by its own script (17, no gate stop: its clock set-aside line too); WT2 ended with its manifest, runner.rc 0 (0); WT3 BOUND (16)"
ok "$wt4.$(has 'RUNNER-RC 1' "$S/wt4.txt").$(has 'the runner exited 1 after the session' "$S/wt4.txt").$(has 'GATE-STOPPED' "$S/wt4.txt").$wt5.$(has 'runner.rc is not written' "$S/wt5.txt")" "16.1.1.0.14.1" \
  "WT4 a session that ended with its manifest and no gate line but runner.rc 1: 16, the runner's exit named (fix-e194); WT5 runner.rc not written: 14"

step "C, C2. step 11 on the LA session; then one byte changed after the manifest"
bash "$R/s22_collect_e194.sh" > "$S/c.txt" 2>&1; c=$?
grep -E 'COPY-BACK|BOX-TREE|COLLECTED|HISTORY|STOP' "$S/c.txt" | cut -c1-220
D0=docs/reports/data/$TODAY-e194-blind-day-aifoundry2
ok "$c.$(has 'COPY-BACK EXACT' "$S/c.txt").$(has 'BOX-TREE GATE: every path' "$S/c.txt").$(has 'COLLECTED' "$S/c.txt").$([ -f "$T/$D0/SHA256SUMS" ] && [ -f "$T/$D0/FILES.txt" ] && echo 1 || echo 0).$(grep -rlE "/home/|(^|[^A-Za-z0-9_.-])$(id -un)([^A-Za-z0-9_-]|$)" "$T/$D0" 2>/dev/null | grep -c .).$(has 'the runner exited 16' "$S/c.txt")" \
  "0.1.1.1.1.0.1" "C collected exactly, the box-tree gate passed, SHA256SUMS and FILES.txt written, no home path and no box login in it; the runner's exit status reported (16, its box check)"

step "SC0-SC3. step 13's real path: before the data commit, a worktree change, a committed byte change, committed and clean"
RB_OUT="$S/out-b" bash "$R/s24_score_e194.sh" > "$S/sc0.txt" 2>&1; sc0=$?
$G add --sparse "$D0" > /dev/null 2>&1 && $G commit -q -m "desk test: the collected data directory" > /dev/null 2>&1 || echo "data commit failed"
DC=$($G rev-parse HEAD)
printf 'x' >> "$T/$D0/session/session.log"
bash "$R/s24_score_e194.sh" > "$S/sc1.txt" 2>&1; sc1=$?
$G add --sparse "$D0" > /dev/null 2>&1 && $G commit -q -m "desk test: a committed byte change" > /dev/null 2>&1 || echo "byte-change commit failed"
bash "$R/s24_score_e194.sh" > "$S/sc2.txt" 2>&1; sc2=$?
$G reset -q --hard "$DC"
bash "$R/s24_score_e194.sh" > "$S/sc3.txt" 2>&1; sc3=$?
grep -E 'scored:|STOP' "$S/sc3.txt" | cut -c1-200
ok "$sc0.$sc1.$sc2.$(has 'does not read every entry OK' "$S/sc2.txt").$sc3.$(has 'scored:' "$S/sc3.txt").$([ -s "$S/out-b/scores-e194.json" ] && echo 1 || echo 0)" \
  "10.16.16.1.0.1.1" "SC0 not committed 10; SC1 a worktree change 16; SC2 a committed byte change 16; SC3 committed and clean: scored, scores-e194.json"
$G reset -q --hard "$DC~1"
rm -rf "${T:?}/$D0" "${RB_OUT:?}/e194-raw"
t0=$(cat "$RB_OUT/e194-T0.txt"); printf 'x' >> "$BOXT/build/e194/T$t0/session.log"
bash "$R/s22_collect_e194.sh" > "$S/c2.txt" 2>&1; c2=$?
ok "$c2.$(has 'COPY-BACK NOT EXACT' "$S/c2.txt").$([ -e "$T/$D0" ] && echo 1 || echo 0)" "16.1.0" "C2 a changed byte: not exact, 16, nothing written"
rm -rf "${RB_OUT:?}/e194-raw"
bash "$R/quiet_e194.sh" lower card-e194-desktest > /dev/null

step "Z. no process of this test left running"
sleep 1
z=$(pgrep -f "$S/" 2>/dev/null | grep -c .)
ok "$z" "0" "Z nothing left"
echo
echo "SELFTEST-RB-E194 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<lab clone>#g"
exit "${PIPESTATUS[0]}"
