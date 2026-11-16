#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE RUNBOOK DESK TEST of E199's runbook from aifoundry2, with a FAKE ssh
# and rsync on a stand-in aifoundry1. E192's runbook desk test (rb/selftest_rb_e192.sh, a6fe5c20, unchanged beside it) made aifoundry1
# card 1's. Its scratch repository is a shared, sparse clone of the lab clone this test runs from, at E199's registration commit (found by
# its content), with the kit's files committed on top as one stand-in kit commit, the kit list a stand-in made here and pinned in the scratch
# copy of step 2's KITPIN line (the one line this test changes in a copy: the real list holds this test's log). The stand-in box is
# aifoundry1's ~/nekko under the scratch; the stand-in ssh serves only `bash -s` (and the probe's `true`) and refuses any other host or
# command; the stand-in rsync rewrites aifoundry1: paths onto it. The box's build is REAL: cmake with this desk's /opt/et, check_elf.py,
# E192's loop_order_e192.py, the built host's --list (no device), with the desk-only E199_SELECTION_REPORT_ONLY (aifoundry2's /opt/et has no
# ET_DEVICES; the stand-in ssh passes the desk test's variables to the box's scripts, the real one passes none). The box's reader, heater
# and (for the launched session) host are desk/standin_e199.py; et-who is the stand-in's (every open stand-in node, like et-holders);
# `uptime -s` answers aifoundry1's boot (2026-10-26 15:02:04) unless a case sets another; card 1's and card 0's lock files are files in the
# sandbox's /run/lock. No lab box is reached. Cases:
#   A   the dry listing: every step exits 0, no call reaches the stand-ins;
#   K   step 2 with no window: 10;  W1 a window written yesterday: 10;  W2 one written for E189: 10;  W3 step 1 for another day: 10;
#   G   step 2 without RB_GITLOCK: 10;  N step 2 run INSIDE the lab-git lock (nested): 16 naming its pull;
#   P1  step 2 on the scratch repository: 0 (the four lists at their pins, HISTORY OK, the two freeze lines (E199.md's line 2, the sealed
#       card-1 forecast, printed), no later note: none, no datum, GO);
#   SN1 THE SEALED CARD-1 NOTE committed at tools/claims-v3/sealed-card1/e199-freeze-lines.md: step 2 passes and prints its sha256;
#   SN2 the note untracked: 16;  SN3 the note edited after its add: 16 (the history check: additions only);
#   P2  E199's registration list one line short: 16;  P3 the kit's list one line short: 16;  H1 E192's run_block.py edited: 16;
#   H2  an added tools/claims-v3/e192/proposal/src/json.py (run_block.py runs there without -I on the box): 16 naming it;
#   H3  an untracked tools/claims-v3/e89/random.py: 16;  D1 an E199 data folder on a side branch: 16;
#   S   step 5: E199's files into E199's root (build/claims-v3/aifoundry1-c1/e199) at their pins; another run's files untouched;
#   B   step 6: a real build, the bounded wait, then 0 (INTBITS-BUILT, the box's tools and pins OK);  X a second start: 10;  T NO-THIRD-BUILD;
#   L1  THE LOGIN CHECK at the look: 11, one line appended to RB_LOCK;  L2 a hang: 13;  L3 a cut wait: 14;
#   LK  the look: FREE on both cards;  RG THE REBOOT GATE: a box booted after E82's firmware read: the look 16, step 9's guard 16;
#   R7a step 7 before the rest opens: REFUSED (10) and NO config read sent;  R7b after it: card 1's read OK through E199's guard;
#   DR  step 8 (session_e199.sh --dry on the stand-in box): 0, E199-DRY OK;
#   RS  THE REST RULE THROUGH STEP 9: an E191-form session ended 10 minutes ago: 10, nothing launched;
#   LA  an E183-form session 45 minutes ago instead: step 9 launches the REAL session_e199.sh (--plain-sampler) on the stand-in box: the
#       identity gates, the gate, E192's run_session.sh with ET_DEVICES=1 and card 1's lock;
#   W1r step 10 while it runs: 17;  a stop by hand once pass 0 is done;  W2r step 10 again: 0, RUN-ENDED, MANIFEST-WRITTEN, 1 pass complete;
#   WN  a decoy session_e1990.sh that outlives the wait's bound (40 s here) and a session log with no end: 14 (RUN-GONE) within one loop
#       (under 17 s): the patterns match the real name only (a pattern that matched the decoy would read 17 after 40 s; fix-e199, F9);
#   C   step 11: COPY EXACT, k6's desk-path gate, the data directory, SCRUB-CHECK OK, the login scrub, NO-DATUM OK: 0;
#   R   the data directory committed in the scratch repository: step 13 (E151's filter, E192's reducer, E192's checker, the transport
#       scorer, the unfiltered reduction): 0;
#   C2  one byte of a box file changed after the session's manifest: COPY NOT EXACT, 16;
#   Z   no process of this test left running.
# NOT RUN (exit 5), never a FAIL (fix-e199, verify-e199 F6 and F7): a start from 23:20 Pacific (the desk window is today's last minutes,
# 23:58-23:59, and a run takes about 5-10 minutes); THE QUIET DESK FLAG named by E199_QUIET_FLAG existing at the start or before any case.
#   bash tools/claims-v3/e199/rb/selftest_rb_e199.sh <scratch dir> [<a lock file of checks to copy as RB_LOCK>] > <log>
# On aifoundry2 run it ONLY inside W/slot.sh and W/nodev.sh: it re-executes itself in bubblewrap (a private /dev holding aifoundry1's four
# node names as binds of /dev/null, a private /run/lock, a private PID namespace and /proc, the host name aifoundry1).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
LOCKFROM=${2:-}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
[ -z "$LOCKFROM" ] || [ -f "$LOCKFROM" ] || { echo "no lock file $LOCKFROM to copy"; exit 2; }
hm=$(TZ=America/Los_Angeles date +%H%M)
if [ "$((10#$hm))" -ge 2320 ]; then echo "SELFTEST-RB-E199 NOT RUN: $(TZ=America/Los_Angeles date '+%H:%M %Z') is past 23:20 (the desk window is today's last minutes): run it after midnight"; exit 5; fi
quiet_or_exit() { if [ -n "${E199_QUIET_FLAG:-}" ] && [ -e "$E199_QUIET_FLAG" ]; then echo "SELFTEST-RB-E199 NOT RUN: the quiet-desk flag exists ($1)"; exit 5; fi; }
quiet_or_exit "at the start"
if [ -z "${E199_RB_INNER:-}" ]; then
  for d in /dev/et*; do [ -e "$d" ] || continue; if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node: run inside W/nodev.sh"; exit 2; fi; done
  mkdir -p "$S" && S=$(cd "$S" && pwd -P); [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
  exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock \
    --dev-bind /dev/null /dev/et0_ops --dev-bind /dev/null /dev/et0_mgmt --dev-bind /dev/null /dev/et1_ops --dev-bind /dev/null /dev/et1_mgmt \
    --unshare-pid --proc /proc --unshare-uts --hostname aifoundry1 --die-with-parent --setenv E199_RB_INNER 1 \
    -- /bin/bash "$SRC/tools/claims-v3/e199/rb/selftest_rb_e199.sh" "$S" "$LOCKFROM"
fi
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK; do [ -z "${!v:-}" ] || { echo "$v is set"; exit 2; }; done
sedi() { local f=${!#} t; t=$(mktemp "$S/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
REAL_RSYNC=$(command -v rsync); REAL_PGREP=$(command -v pgrep)
T=$S/tree; B=$S/box; BIN=$S/bin; BB=$S/boxbin; BOXT=$B/aifoundry1/nekko
mkdir -p "$BOXT/build/claims-v3/aifoundry1-c1" "$BIN" "$BB" "$S/sd"
E=tools/claims-v3/e199
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { quiet_or_exit "before $*"; echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
echo "E199 runbook desk test (kit-e199), $(date '+%F %T %Z'); bash ${BASH_VERSION}; $(rsync --version | head -n 1 | cut -c1-40); Python $(/usr/bin/python3 -V 2>&1); host name $(hostname)"
# ---- the scratch repository: a shared sparse clone at the registration, then the kit's files as one stand-in commit
REG=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/E199.md | tail -n 1)
[ -n "$REG" ] || { echo "no registration commit in the lab clone's history"; exit 2; }
git clone -q --shared --no-checkout "$SRC" "$T" || exit 2
G="git -C $T -c user.name=e199-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /workloads/sparsity/ || exit 2
$G checkout -q -B main "$REG" || exit 2
$G branch -q up "$REG"; $G branch -q --set-upstream-to=up main 2>/dev/null
( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E; git ls-files -- $E ) | sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
mkdir -p "$T/$E/logs"
for spec in "desktest-realpath-e199.txt DESKTEST-REALPATH-E199 1 of 1 PASS" "selftest-rb-e199.txt SELFTEST-RB-E199 1 of 1 PASS" \
            "selftest-rest-e199.txt SELFTEST-REST-E199 1 of 1 PASS" "realbytes-e199.txt REALBYTES-E199 1 of 1 PASS" \
            "realbuild-e199.txt REALBUILD-E199 1 of 1 PASS" "dry-audit-e199.txt DRY-AUDIT-E199 1 of 1 COVERED" \
            "dry-listing-e199.txt dry listing: 13 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e199.txt PLAIN-CHAIN: GO (stand-in)"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"     # always the stand-in line: step 2's mechanics are tested, not the logs
done
mkkit() {  # the stand-in kit list: every e199 file but the registration's, the list itself and step 2 (outside the list)
  ( cd "$T" && git show "$REG" --name-only --format= -- $E ) > "$S/reg-files.txt"
  ( cd "$T" && find $E -type f ! -name 'SHA256SUMS-e199-kit' ! -path "$E/rb/s03_desk_e199.sh" ! -name '*.pyc' ! -path '*/__pycache__/*' | LC_ALL=C sort |
    while IFS= read -r f; do sha256sum "$f"; done ) | grep -v -F -f "$S/reg-files.txt" > "$S/kit-standin.txt"
  KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e199-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^KITPIN=$E/SHA256SUMS-e199-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e199-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e199.sh"
}
mkkit
$G add -A $E && $G commit -q -m "E199 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; exit 2; }
$G branch -q -f up HEAD
echo "scratch repository: a shared sparse clone at the registration ${REG:0:12}, the kit as one stand-in commit $($G rev-parse --short=12 HEAD); the kit list's stand-in $KITN files"
# ---- the stand-ins
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry1) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: refusing the command '\$cmd'" >&2; exit 97; }
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; echo "To authenticate, visit: https://login.tailscale.com/a/e199desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
if [ -e "$S/ssh-cut" ]; then rm -f "$S/ssh-cut"; cat > /dev/null; echo "ssh: connection closed (desk-test stand-in)" >&2; exit 255; fi
cd "$B/\$host" && HOME="$B/\$host" PATH="$BB:\$PATH" exec bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry1) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/bash\nexec -a et-who /usr/bin/python3 -I -B %s etwho "$@"\n' "$SRC/$E/desk/standin_e199.py" > "$BB/et-who"
printf '#!/bin/bash\nif [ "${1:-}" = -s ]; then cat "%s/boot-time" 2>/dev/null || echo "2026-10-26 15:02:04"; else /usr/bin/uptime "$@"; fi\n' "$S" > "$BB/uptime"
printf '#!/bin/sh\necho "et-lab-manifest (desk-test stand-in): sysfs and files only"\n' > "$BB/et-lab-manifest"
cat > "$BB/pgrep" <<EOF
#!/bin/bash
anc=" "; p=\$PPID
while [ -n "\$p" ] && [ "\$p" -gt 1 ] 2>/dev/null; do anc="\$anc\$p "; p=\$(awk '{print \$4}' /proc/\$p/stat 2>/dev/null); done
out=""; for q in \$("$REAL_PGREP" "\$@"); do case "\$anc" in *" \$q "*) ;; *) out="\$out\$q
"; esac; done
[ -n "\$out" ] || exit 1
printf '%s' "\$out"
EOF
printf '#!/bin/sh\nexec "$@"\n' > "$BB/setsid"
for n in ssh rsync scp sudo; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$BB/$n"; done
chmod +x "$BIN"/* "$BB"/*
for role in "build/ettelem/ettelem sampler" "build/sparsity/host/sparsity_host heater"; do
  p=${role% *}; mkdir -p "$BOXT/$(dirname "$p")"
  printf '#!/bin/bash\n# stand-in: honours ET_DEVICES\nexec -a "$0" /usr/bin/python3 -I -B %s %s "$@"\n' "$SRC/$E/desk/standin_e199.py" "${role#* }" > "$BOXT/$p"; chmod +x "$BOXT/$p"
done
mkdir -p "$BOXT/build/claims-v3/aifoundry1-c1/e157/p15712"; echo '{"status":"ok","note":"another run (desk test)"}' > "$BOXT/build/claims-v3/aifoundry1-c1/e157/p15712/block.json"
OTHER=$(sha256sum "$BOXT/build/claims-v3/aifoundry1-c1/e157/p15712/block.json" | cut -d' ' -f1)
: > /run/lock/etsoc-shire0.lock; : > /run/lock/etsoc-shire1.lock
export E199_STANDIN_DIR="$S/sd" E199_STANDIN_TABLE="$SRC/tools/claims-v3/e192/desk/arm-table-e192.jsonl"
echo '{}' > "$S/sd/scenario.json"
# the desk-only variables the stand-in ssh passes on to the box's scripts (the real ssh passes none): the short window budget, the
# build's selection reported (aifoundry2's /opt/et has no ET_DEVICES), the session's desk test with the stand-in reader's sha256
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_DESKTEST=1 E199_DESK_BUDGET_S=60 USER="$(id -un)" \
  E199_SELECTION_REPORT_ONLY=1 E199_DESKTEST=1 E199_READER_SHA256="$(sha256sum "$BOXT/build/ettelem/ettelem" | cut -d' ' -f1)" \
  E199_CAP_S=600 E199_D0_S=60     # the session's desk cap: the desk window (today 23:58-23:59) may be less than 65 minutes away
: > "$S/calls.log"; : > "$S/gitlock"
if [ -n "$LOCKFROM" ]; then cp "$LOCKFROM" "$RB_LOCK"; else : > "$RB_LOCK"; fi
LOCK0=$(grep -c . "$RB_LOCK"); LOCKH=$(sha256sum < "$LOCKFROM" 2>/dev/null | cut -d' ' -f1)
echo "RB_LOCK: $([ -n "$LOCKFROM" ] && echo "a copy of the given lock file of checks, $LOCK0 lines" || echo "an empty file")"
R=$T/$E/rb; K6=$T/tools/claims-v3/q141k-runbook/k6
TODAY=$(TZ=America/Los_Angeles date +%F)
cd "$T" || exit 2
win() { mkdir -p "$1"; RB_OUT="$1" bash "$R/s02_window_e199.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1; }

step "A. the dry listing"
bash "$R/list_steps_e199.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
tail -n 1 "$S/dry-listing.txt"
ok "$rc.$(grep -c . "$S/calls.log")" "0.0" "A every step 0, no call to the stand-ins"

step "K, W1-W3, G. the window rule; RB_GITLOCK required"
RB_OUT="$S/out-k" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/k.txt" 2>&1; k=$?
win "$S/out-w"; touch -d '-1 day' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/w1.txt" 2>&1; w1=$?
win "$S/out-w"; sedi -e 's/^RB_PLAN=e199$/RB_PLAN=e189/' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/w2.txt" 2>&1; w2=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e199.sh" "$(date -d '+1 day' +%F)" 10:00 12:00 > "$S/w3.txt" 2>&1; w3=$?
win "$S/out-p"
RB_OUT="$S/out-p" bash "$R/s03_desk_e199.sh" > "$S/g.txt" 2>&1; g=$?
ok "$k.$(has 'no window in RB_OUT' "$S/k.txt").$w1.$(has 'not written today' "$S/w1.txt").$w2.$(has 'written for e189' "$S/w2.txt").$w3.$(has 'is not today' "$S/w3.txt").$g.$(has 'RB_GITLOCK is not set' "$S/g.txt")" \
  "10.1.10.1.10.1.10.1.10.1" "K, W1-W3, G each refused (10) before any call"

step "N. step 2 run inside the lab-git lock (nested)"
RB_GITLOCK_T=2 /usr/bin/flock -n -E 75 "$S/gitlock" env RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/n.txt" 2>&1; n=$?
stopline "$S/n.txt"
ok "$n.$(has 'pull' "$S/n.txt")" "16.1" "N a nested step 2 stops with 16 naming its pull"

step "P1. step 2 on the scratch repository"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check:|STOP' "$S/p1.txt" | cut -c1-500
ok "$p1.$(has "the lists at their pinned counts and bytes (E199's 17; E192's 30 and its kit's 35;" "$S/p1.txt").$(has 'sealed card-1 freeze lines: E199.md line 2 1c5d8fa3efa054272451017538cd42018b589050493b9e504a5d5d90bc1009c3 (registered); the later note: none' "$S/p1.txt").$(has 'no E199 datum in any ref' "$S/p1.txt")" "0.1.1.1" "P1 step 2 passes at every pin, HISTORY OK, the two freeze lines (E199.md's line 2 printed), no later note (none), no E199 datum, the preflight GO"

step "SN1, SN2, SN3. THE SEALED CARD-1 NOTE outside the pinned subtree: committed; untracked; edited after its add"
mkdir -p "$T/tools/claims-v3/sealed-card1"
SH1=$(printf 'e199 sealed desk test' | sha256sum | cut -d' ' -f1)
printf '# E199: the model session'"'"'s sealed card-1 forecast (a dated note; desk test)\n\nsha256 %s\n' "$SH1" > "$T/tools/claims-v3/sealed-card1/e199-freeze-lines.md"
cp "$T/tools/claims-v3/sealed-card1/e199-freeze-lines.md" "$S/note.keep"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/sn2.txt" 2>&1; sn2=$?
$G add --sparse -f tools/claims-v3/sealed-card1/e199-freeze-lines.md; $G commit -q -m "desk test: the sealed card-1 note, committed"; $G branch -q -f up HEAD
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/sn1.txt" 2>&1; sn1=$?
printf 'an edit after the add\n' >> "$T/tools/claims-v3/sealed-card1/e199-freeze-lines.md"; $G commit -q -am "desk test: the note edited after its add"; $G branch -q -f up HEAD
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/sn3.txt" 2>&1; sn3=$?
$G reset -q --hard HEAD~2; $G branch -q -f up HEAD
grep -E 'desk check:|STOP' "$S/sn1.txt" "$S/sn2.txt" "$S/sn3.txt" | cut -c1-260
ok "$sn1.$(has "the later note: the dated note e199-freeze-lines.md (added" "$S/sn1.txt").$(has "$SH1" "$S/sn1.txt").$(has "the later note: the dated note" "$S/out-p/runbook.log").$sn2.$(has 'sealed-note-untracked' "$S/sn2.txt").$sn3.$(has 'sealed-note-edited' "$S/sn3.txt")" \
  "0.1.1.1.16.1.16.1" "SN1 a committed note: step 2 passes and prints its sha256 as a sealed card-1 freeze line (and logs it); SN2 the note untracked: 16; SN3 edited after its add: 16 (a dated note is touched by one commit)"

step "P2, P3, H1, H2, H3, D1. a short list; the kit's list short; an edited registered file; two shadows; an E199 datum in a ref"
sedi -e '$d' "$T/$E/SHA256SUMS-e199-registration"; $G commit -q -am "desk test: the registration's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/p2.txt" 2>&1; p2=$?; $G reset -q --hard HEAD~1
sedi -e '$d' "$T/$E/SHA256SUMS-e199-kit"; $G commit -q -am "desk test: the kit's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/p3.txt" 2>&1; p3=$?; $G reset -q --hard HEAD~1
printf '\n' >> "$T/tools/claims-v3/e192/proposal/src/run_block.py"; $G commit -q -am "desk test: E192's registered run_block.py edited"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/h1.txt" 2>&1; h1=$?; $G reset -q --hard HEAD~1
printf '# desk test: would shadow json for run_block.py\n' > "$T/tools/claims-v3/e192/proposal/src/json.py"; $G add tools/claims-v3/e192/proposal/src/json.py; $G commit -q -m "desk test: a shadow in the reference session's folder"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/h2.txt" 2>&1; h2=$?
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e199.py tree ) > "$S/h2b.txt" 2>&1; $G reset -q --hard HEAD~1
printf '# desk test\n' > "$T/tools/claims-v3/e89/random.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e199.py tree ) > "$S/h3.txt" 2>&1; h3=$?; rm -f "$T/tools/claims-v3/e89/random.py"
$G checkout -q -b side; mkdir -p "$T/docs/reports/data/2026-11-14-e199-intbits-aifoundry1-c1"; echo x > "$T/docs/reports/data/2026-11-14-e199-intbits-aifoundry1-c1/README.md"
$G add --sparse -f docs/reports/data/2026-11-14-e199-intbits-aifoundry1-c1/README.md; $G commit -q -m "desk test: an E199 datum on a side branch"; $G checkout -q main
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e199.sh" > "$S/d1.txt" 2>&1; d1=$?; $G branch -q -D side
cut -c1-300 "$S/h2b.txt" "$S/h3.txt"
ok "$p2.$(has 'SHA256SUMS-e199-registration' "$S/p2.txt").$p3.$(has 'SHA256SUMS-e199-kit' "$S/p3.txt").$h1.$(has 'history' "$S/h1.txt").$h2.$(has 'proposal/src/json.py (as json)' "$S/h2b.txt").$h3.$(has 'e89/random.py' "$S/h3.txt").$d1.$(has 'E199-datum' "$S/d1.txt")" \
  "16.1.16.1.16.1.16.1.16.1.16.1" "P2, P3, H1, H2, H3, D1 each refused and named"

step "S. step 5, the sync"
RB_OUT="$S/out-p" bash "$R/s07_a1_sync_e199.sh" > "$S/s.txt" 2>&1; s=$?
grep -E 'synced to|STOP' "$S/s.txt" | cut -c1-300
ok "$s.$(has 'BOX-PINS OK' "$S/out-p/calls/"*boxpins*.out 2>/dev/null || echo 0).$([ -f "$BOXT/build/claims-v3/aifoundry1-c1/e199/$E/session_e199.sh" ] && echo 1).$([ "$(sha256sum "$BOXT/build/claims-v3/aifoundry1-c1/e157/p15712/block.json" | cut -d' ' -f1)" = "$OTHER" ] && echo 1).$([ -e "$BOXT/tools" ] && echo 0 || echo 1)" \
  "0.1.1.1.1" "S E199's files in E199's root at their pins; another run's file untouched; nothing outside E199's root"

step "B, X, T. step 6: a real build, the wait, the box's tools; a second start; NO-THIRD-BUILD"
RB_OUT="$S/out-p" bash "$R/s08_a1_build_e199.sh" start > "$S/b1.txt" 2>&1; b1=$?
RB_WAIT_LOOP_S=2 RB_OUT="$S/out-p" bash "$R/s08_a1_build_e199.sh" wait > "$S/b2.txt" 2>&1; b2=$?
RB_OUT="$S/out-p" bash "$R/s08_a1_build_e199.sh" wait > "$S/b3.txt" 2>&1; b3=$?
[ "$b3" = 17 ] && { RB_OUT="$S/out-p" bash "$R/s08_a1_build_e199.sh" wait > "$S/b3.txt" 2>&1; b3=$?; }
grep -E 'INTBITS|BOXCHECK|built today|STOP|kernel_' "$S/b3.txt" | cut -c1-220
b2w=$([ "$b2" = 17 ] || [ "$b2" = 0 ] && echo ok)   # 17 while it runs, or 0 when the build (about 2 s on this desk) ended inside the 2 s wait
echo "   (the first wait, bounded at 2 s: exit $b2)"
ok "$b1.$b2w.$b3.$(has 'INTBITS-BUILT rc=0' "$S/b3.txt").$([ -s "$S/out-p/e199-built.txt" ] && echo 1)" "0.ok.0.1.1" "B the build job: started; the bounded wait 17 while it runs (or 0 once ended); then 0 with INTBITS-BUILT and the box's tools and pins OK"
RB_OUT="$S/out-p" bash "$R/s08_a1_build_e199.sh" start > "$S/x.txt" 2>&1; x=$?
ER=$BOXT/build/claims-v3/aifoundry1-c1/e199
cp "$ER/build-attempts.txt" "$S/attempts.keep"; mv "$BOXT/build/q141k/jobs/a1-build-e199.out" "$S/job.out.keep"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a1-build-e199 started" >> "$ER/build-attempts.txt"
RB_OUT="$S/out-p" bash "$R/s08_a1_build_e199.sh" start > "$S/t.txt" 2>&1; t=$?
cp "$S/attempts.keep" "$ER/build-attempts.txt"; mv "$S/job.out.keep" "$BOXT/build/q141k/jobs/a1-build-e199.out"
ok "$x.$(has 'was built today' "$S/x.txt").$t.$(has 'NO-THIRD-BUILD' "$S/t.txt")" "10.1.16.1" "X a second start after a build: 10; T a third start: NO-THIRD-BUILD 16"

step "L1, L2, L3. the login check; a hang; a cut wait"
n0=$(grep -c 'aifoundry1 needs a check' "$RB_LOCK")
: > "$S/ssh-login"; RB_OUT="$S/out-p" bash "$R/s05_look_e199.sh" > "$S/l1.txt" 2>&1; l1=$?
n1=$(grep -c 'aifoundry1 needs a check' "$RB_LOCK"); kept=$( [ "$(head -n "$LOCK0" "$RB_LOCK" | sha256sum | cut -d' ' -f1)" = "$( [ -n "$LOCKFROM" ] && echo "$LOCKH" || printf '' | sha256sum | cut -d' ' -f1)" ] && echo 1 || echo 0)
echo "   RB_LOCK: $((n1 - n0)) line appended ('$(tail -n 1 "$RB_LOCK")'); its first $LOCK0 lines kept: $kept"
touch "$S/ssh-hang"; RB_READ_S=3 RB_OUT="$S/out-p" bash "$R/s05_look_e199.sh" > "$S/l2.txt" 2>&1; l2=$?
touch "$S/ssh-cut"; RB_OUT="$S/out-p" bash "$R/s08_a1_build_e199.sh" wait > "$S/l3.txt" 2>&1; l3=$?
ok "$l1.$((n1 - n0)).$kept.$l2.$l3" "11.1.1.13.14" "L1 a login link: 11, one line appended to RB_LOCK and the rest kept; L2 a hang: 13; L3 a cut wait: 14"
rm -f "$S/ssh-login" "$S/ssh-hang" "$S/ssh-cut"

step "LK, RG. the look on aifoundry1 (both cards); THE REBOOT GATE"
RB_OUT="$S/out-p" bash "$R/s05_look_e199.sh" > "$S/lk.txt" 2>&1; lk=$?
echo "2026-11-13 16:53:28" > "$S/boot-time"
RB_OUT="$S/out-g" bash "$R/s02_window_e199.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1
RB_OUT="$S/out-g" bash "$R/s05_look_e199.sh" > "$S/rg1.txt" 2>&1; rg1=$?
cp "$S/out-p/e199-built.txt" "$S/out-g/"
RB_OUT="$S/out-g" bash "$R/s11_a1_session_e199.sh" FULL > "$S/rg2.txt" 2>&1; rg2=$?
rm -f "$S/boot-time"
grep -E 'FREE|STOP|IDENTITY' "$S/lk.txt" "$S/rg1.txt" "$S/rg2.txt" | cut -c1-220
ok "$lk.$(has 'FREE on both cards' "$S/lk.txt").$([ -s "$S/out-p/box-login-aifoundry1.txt" ] && echo 1).$rg1.$(has 'booted after E82' "$S/rg1.txt").$rg2.$(has 'IDENTITY-STOP' "$S/rg2.txt").$([ -e "$S/out-g/e199-T0.txt" ] && echo 0 || echo 1)" \
  "0.1.1.16.1.16.1.1" "LK the look: FREE on both cards, the box login recorded; RG a box booted after E82's firmware read: the look 16; step 9's guard IDENTITY-STOP 16, nothing launched"

step "R7a, R7b. step 7, the reads: refused before the rest opens (no config read sent); then card 1's read through E199's guard"
now7=$(date +%s); t7=$((now7 - 600)); mkdir -p "$BOXT/build/e191/T$((t7 - 900))"
printf '%s session start (T0 %s = x; plan FULL; kit note 2)\n%s session end (T0 %s)\n' "$(date -d @$((t7 - 900)) '+%F %T %Z')" $((t7 - 900)) "$(date -d @$t7 '+%F %T %Z')" $((t7 - 900)) > "$BOXT/build/e191/T$((t7 - 900))/session.log"
n7=$(grep -c '"event": "config"' "$S/sd/calls/sampler.log" 2>/dev/null); n7=${n7:-0}
RB_OUT="$S/out-p" bash "$R/s09_a1_reads_e199.sh" > "$S/r7a.txt" 2>&1; r7a=$?
n7b=$(grep -c '"event": "config"' "$S/sd/calls/sampler.log" 2>/dev/null); n7b=${n7b:-0}
rm -rf "${BOXT:?}/build/e191"
RB_OUT="$S/out-p" bash "$R/s09_a1_reads_e199.sh" > "$S/r7b.txt" 2>&1; r7b=$?
grep -E 'REFUSED|STOP|card 1, after|IDENT' "$S/r7a.txt" "$S/r7b.txt" | cut -c1-220
ok "$r7a.$(has 'REFUSED: 10 minutes since E191' "$S/r7a.txt").$((n7b - n7)).$r7b.$(has 'IDENT-A OK: /dev/et1_mgmt' "$S/r7b.txt")" "10.1.0.0.1" "R7a step 7 before the rest opens: REFUSED (10), no config read sent; R7b after it: card 1's read OK through E199's guard (the runtime line dropped)"

# from here the box's built host (the real desk build, whose linked /opt/et layer on aifoundry2 carries no ET_DEVICES) is replaced by the
# stand-in host (it carries the word, as aifoundry1's build does), so the session's own selection check passes; it is put back after C2
RHOST=$ER/build/intbits/host/intbits_host; cp -p "$RHOST" "$S/real-host.keep"
printf '#!/bin/bash\n# stand-in: honours ET_DEVICES\nexec -a "$0" /usr/bin/python3 -I -B %s host "$@"\n' "$SRC/$E/desk/standin_e199.py" > "$RHOST"
step "DR. step 8, the box's dry pass"
RB_OUT="$S/out-p" bash "$R/s10_a1_dry_e199.sh" start > "$S/dr1.txt" 2>&1; dr1=$?
RB_OUT="$S/out-p" bash "$R/s10_a1_dry_e199.sh" wait > "$S/dr2.txt" 2>&1; dr2=$?
grep -E 'E199-DRY|STOP' "$S/dr2.txt" | cut -c1-240 | head -n 3
ok "$dr1.$dr2.$(has 'E199-DRY OK: 328 device calls' "$S/dr2.txt")" "0.0.1" "DR the dry pass on the stand-in box: 0, E199-DRY OK"

step "RS, LA. the rest rule through step 9; then the launch"
now=$(date +%s); t1=$((now - 600)); mkdir -p "$BOXT/build/e189/T$((t1 - 3000))"
printf '%s session start (T0 %s = x; plan FULL)\n%s session end (T0 %s)\n' "$(date -d @$((t1 - 3000)) '+%F %T %Z')" $((t1 - 3000)) "$(date -d @$t1 '+%F %T %Z')" $((t1 - 3000)) > "$BOXT/build/e189/T$((t1 - 3000))/session.log"
RB_OUT="$S/out-p" bash "$R/s11_a1_session_e199.sh" FULL --plain-sampler > "$S/rs.txt" 2>&1; rs=$?
rm -rf "${BOXT:?}/build/e189"
t2=$((now - 2700)); mkdir -p "$BOXT/build/e183"
printf '%s session start (T0 %s = x; plan FULL)\n%s session end (T0 %s)\n' "$(date -d @$((t2 - 3000)) '+%F %T %Z')" $((t2 - 3000)) "$(date -d @$t2 '+%F %T %Z')" $((t2 - 3000)) > "$BOXT/build/e183/session-t$((t2 - 3000)).log"
echo '{"scale": 0.25}' > "$S/sd/scenario.json"
RB_OUT="$S/out-p" bash "$R/s11_a1_session_e199.sh" FULL --plain-sampler > "$S/la.txt" 2>&1; la=$?
grep -E 'LAUNCHED|rest:|REFUSED|STOP' "$S/rs.txt" "$S/la.txt" | cut -c1-260
ok "$rs.$(has 'REFUSED: 10 minutes since E189' "$S/rs.txt").$la.$(has 'LAUNCHED e199 T0' "$S/la.txt")" "10.1.0.1" "RS a session 10 min ago: refused (10), nothing launched; LA 45 min ago: launched"
T0=$(cat "$S/out-p/e199-T0.txt" 2>/dev/null)
RB_WAIT_LOOP_S=3 RB_OUT="$S/out-p" bash "$R/s20_wait_e199.sh" > "$S/w1r.txt" 2>&1; w1r=$?
ok "$w1r.$(has 'RUN-RUNNING e199' "$S/w1r.txt")" "17.1" "W1r step 10 while the real session_e199.sh runs: RUN-RUNNING (17)"
# the stop by hand once pass 0 is done (bounded: at most 8 minutes)
lim=$(( $(date +%s) + 480 ))
until [ "$(date +%s)" -ge "$lim" ] || /usr/bin/python3 -I -B - "$BOXT/build/e199/T$T0/run/marks.jsonl" <<'PY'
import json, sys
try:
    ms = [json.loads(l) for l in open(sys.argv[1]) if l.strip().startswith('{')]
except OSError:
    sys.exit(1)
sys.exit(0 if any(m.get('kind') == 'idle' and m.get('label') == 'after' and m.get('pass') == 0 for m in ms) else 1)
PY
do sleep 2; done
printf '{"by": "hand", "why": "desk test: by hand after pass 0", "t_ms": %s}\n' "$(date +%s%3N)" > "$BOXT/build/e199/T$T0/run/STOP"
lim=$(( $(date +%s) + 180 ))
until grep -q "session end (T0 $T0)" "$BOXT/build/e199/T$T0/session.log" 2>/dev/null || [ "$(date +%s)" -ge "$lim" ]; do sleep 2; done
RB_OUT="$S/out-p" bash "$R/s20_wait_e199.sh" > "$S/w2r.txt" 2>&1; w2r=$?
grep -E 'passes complete|RUN-|MANIFEST|STOP' "$S/w2r.txt" | cut -c1-200
ok "$w2r.$(has 'RUN-ENDED e199' "$S/w2r.txt").$(has 'MANIFEST-WRITTEN' "$S/w2r.txt").$(has 'passes complete: 1 of 9' "$S/w2r.txt")" "0.1.1.1" "W2r step 10 after the stop by hand: RUN-ENDED, MANIFEST-WRITTEN, 1 pass complete"

step "WN. a decoy session_e1990.sh that outlives the wait's bound, and a session log with no end"
cp "$S/out-p/e199-T0.txt" "$S/t0.keep"; cp "$BOXT/build/q141k/e199.T0" "$S/boxt0.keep"
T9=$((T0 + 5)); mkdir -p "$BOXT/build/e199/T$T9"; echo "$(date '+%F %T %Z') session start (T0 $T9 = x; E199)" > "$BOXT/build/e199/T$T9/session.log"
echo "$T9" > "$S/out-p/e199-T0.txt"; echo "$T9" > "$BOXT/build/q141k/e199.T0"
printf '#!/bin/bash\nfor i in $(seq 1 150); do sleep 1; done\n' > "$S/session_e1990.sh"; bash "$S/session_e1990.sh" &
DEC=$!
t0w=$(date +%s)
RB_WAIT_LOOP_S=40 RB_OUT="$S/out-p" bash "$R/s20_wait_e199.sh" > "$S/wn.txt" 2>&1; wn=$?
dtw=$(( $(date +%s) - t0w ))
kill "$DEC" 2>/dev/null; wait "$DEC" 2>/dev/null
rm -rf "${BOXT:?}/build/e199/T$T9"; cp "$S/t0.keep" "$S/out-p/e199-T0.txt"; cp "$S/boxt0.keep" "$BOXT/build/q141k/e199.T0"
ok "$wn.$(has 'RUN-GONE e199' "$S/wn.txt").$([ "$dtw" -lt 17 ] && echo 1 || echo 0)" "14.1.1" "WN a decoy named session_e1990.sh, alive past the wait's 40 s bound: RUN-GONE (14) within one loop ($dtw s): the pattern matches the real name only"

step "C. step 11, the collection"
id -un > "$S/out-p/box-login-aifoundry1.txt"
RB_OUT="$S/out-p" bash "$R/s22_collect_e199.sh" > "$S/c.txt" 2>&1; c=$?
grep -E 'COLLECTED|STOP|COPY|ASSEMBLED|SCRUB' "$S/c.txt" | cut -c1-260
DD=$S/out-p/e199-out/$TODAY-e199-intbits-aifoundry1-c1
ok "$c.$(has 'COPY EXACT' "$S/c.txt").$([ -f "$DD/run/telemetry.jsonl.gz" ] && [ -f "$DD/facts-e199.json" ] && echo 1).$( (cd "$DD" && sha256sum -c --quiet SHA256SUMS) > /dev/null 2>&1 && echo 1)" "0.1.1.1" "C COPY EXACT, the gates, the data directory and its SHA256SUMS: 0"

step "R. the data directory committed (in the scratch repository), then step 13 (the reduction and the transport scorer)"
mkdir -p "$T/docs/reports/data"; cp -r "$DD" "$T/docs/reports/data/"
$G add --sparse -f "docs/reports/data/$TODAY-e199-intbits-aifoundry1-c1"; $G commit -q -m "desk test: the stand-in session's data directory"
RB_OUT="$S/out-p" bash "$R/s24_score_e199.sh" "docs/reports/data/$TODAY-e199-intbits-aifoundry1-c1" > "$S/r.txt" 2>&1; rr=$?
grep -E 'scored|STOP|CHECKS|E199-T1|REFUSED' "$S/r.txt" | cut -c1-300
ok "$rr.$(has 'CHECKS-E192: ' "$S/r.txt").$([ -s "$S/out-p/intbits-e199.json" ] && [ -s "$S/out-p/scores-e199.json" ] && [ -s "$S/out-p/intbits-e199-unfiltered.json" ] && echo 1)" "0.1.1" "R step 13 on the committed data: E151's filter, E192's reducer, E192's checker, THE TRANSPORT SCORER, the unfiltered reduction: 0"
$G reset -q --hard HEAD~1

step "C2. one byte of a box file changed after the session's manifest"
mv "$S/out-p/e199-raw" "$S/raw.c1"; mv "$S/out-p/e199-out" "$S/out.c1"
echo "x" >> "$BOXT/build/e199/T$T0/run/gate.jsonl"
RB_OUT="$S/out-p" bash "$R/s22_collect_e199.sh" > "$S/c2.txt" 2>&1; c2=$?
ok "$c2.$(has 'COPY NOT EXACT' "$S/c2.txt")" "16.1" "C2 the session's own manifest no longer holds: COPY NOT EXACT, 16"
cp "$S/real-host.keep" "$RHOST"

step "Z"
left=$(ls /proc | grep -E '^[0-9]+$' | while read -r p; do tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | grep -E 'standin_e199|session_e199|run_session|gate_e199|stopwatch|run_block' | grep -v grep; done | head -n 3)
ok "$([ -z "$left" ] && echo 1)" "1" "Z no process of this test left ($left)"
echo; echo "SELFTEST-RB-E199 $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
