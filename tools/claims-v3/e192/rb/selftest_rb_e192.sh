#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): the desk test of E192's runbook with a FAKE ssh and rsync on a
# stand-in box, E189's runbook desk test's form (rb/selftest_rb_e189.sh). Its scratch repository is a shared, sparse clone of the lab
# clone this test runs from, at E192's registration commit (found by its content), with the kit's files committed on top as one stand-in kit
# commit, the kit list a stand-in made here and pinned in the scratch copy of step 2's KITPIN line (the one line this test changes in a
# copy: the real list holds this test's log). The stand-in box is aifoundry3's ~/aifoundry under the scratch; the stand-in ssh serves only
# `bash -s` (and the probe's `true`) and refuses any other host or command; the stand-in rsync rewrites aifoundry3: paths onto it. The box's
# build is REAL: cmake with this desk's /opt/et, check_elf.py, the built host's --list (no device). The box's sampler and heater are
# desk/standin_e192.py; et-who answers free; the card lock is a file in the sandbox's /run/lock. No lab box is reached. Cases:
#   A   the dry listing: every step exits 0, no call reaches the stand-ins;
#   K   step 2 with no window: 10;  W1 a window written yesterday: 10;  W2 one written for E189: 10;  W3 step 1 for another day: 10;
#   G   step 2 without RB_GITLOCK: 10;  N step 2 run INSIDE the lab-git lock (nested): 16 naming its pull;
#   P1  step 2 on the scratch repository: 0 (the lists at their pins, HISTORY OK, both freeze lines, no E192 datum, the preflight GO);
#   P2  the registration's list one line short: 16;  P3 the kit's list one line short: 16;  H1 a committed edit of a registered file: 16;
#   H2  an added tools/claims-v3/e192/proposal/src/json.py (run_block.py runs there without -I on the box): 16 naming it;
#   H3  an untracked tools/claims-v3/e89/random.py (pvt_sample.py's folder): 16;  D1 an E192 data folder on a side branch: 16;
#   S   step 5: E192's files into E192's root on the box, at their pins (BOX-PINS OK); another run's files on the box untouched;
#   B   step 6 start, a 2 s bounded wait (17 while it runs, or 0 once it ended), then 0: INTBITS-BUILT by a real build, the box's tools
#       and pins OK, RB_OUT/e192-built.txt;
#   X   a second start after a build today: 10;  T NO-THIRD-BUILD: two starts recorded today and no build: 16;
#   L1  THE LOGIN CHECK: a login link at a read: 11, "<HH:MM:SS> aifoundry3 needs a check" appended to RB_LOCK, nothing retried;
#   L2  a read that hangs: killed at its bound (the read class's bound shortened for this case only): 13;  L3 a cut wait (ssh 255): 14;
#   DR  step 8 (session_e192.sh --dry on the stand-in box): 0, E192-DRY OK;
#   RS  THE REST RULE THROUGH STEP 9: an E189-form session ended 10 minutes ago on the box: 10, nothing launched;
#   LA  an E183-form session ended 45 minutes ago instead: step 9 launches the REAL session_e192.sh (--plain-sampler) on the stand-in box;
#   W1r step 10 while it runs: 17 (the session-name pattern matches the real script's name: RUN-RUNNING); the stand-in host at a quarter of
#       its length; a stop by hand once pass 0 is done;  W2r step 10 again: 0, RUN-ENDED, MANIFEST-WRITTEN, 1 pass complete;
#   WN  a decoy session_e1920.sh running and a session log with no end: 14 (RUN-GONE: the pattern does not match a longer name);
#   C   step 11 on the session: COPY EXACT, the desk-path gate, the data directory, SCRUB-CHECK OK, the login scrub, NO-DATUM OK: 0;
#   R   the data directory committed in the scratch repository: step 13 (the registered reducer, then the section 7 checker): 0;
#   C2  one byte of a box file changed after the session's manifest: COPY NOT EXACT, 16;
#   Z   no process of this test left running.
#   bash tools/claims-v3/e192/rb/selftest_rb_e192.sh <scratch dir> [<a lock file of checks to copy as RB_LOCK>] > <log>
#       (prints SELFTEST-RB-E192 <n> of <m> PASS or FAIL; with the second argument RB_LOCK starts as a COPY of that file, which is never
#       written, and L1 counts the one line it appends to the copy)
# On aifoundry2 run it ONLY inside W/nodev.sh: it re-executes itself in bubblewrap (a private /dev with two regular files named
# /dev/et0_ops and /dev/et0_mgmt, a private /run/lock, a private PID namespace and /proc, the host name aifoundry3; fix-e192 added
# /dev/et0_mgmt, which the wrapper's node count now requires before it opens anything). SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
LOCKFROM=${2:-}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
[ -z "$LOCKFROM" ] || [ -f "$LOCKFROM" ] || { echo "no lock file $LOCKFROM to copy"; exit 2; }
if [ -z "${E192_RB_INNER:-}" ]; then
  for d in /dev/et*; do [ -e "$d" ] || continue; if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node: run inside W/nodev.sh"; exit 2; fi; done
  mkdir -p "$S" && S=$(cd "$S" && pwd -P); [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
  : > "$S/et0_ops.regular-file"; : > "$S/et0_mgmt.regular-file"
  exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --bind "$S/et0_ops.regular-file" /dev/et0_ops \
    --bind "$S/et0_mgmt.regular-file" /dev/et0_mgmt --unshare-pid --proc /proc \
    --unshare-uts --hostname aifoundry3 --die-with-parent --setenv E192_RB_INNER 1 -- /bin/bash "$SRC/tools/claims-v3/e192/rb/selftest_rb_e192.sh" "$S" "$LOCKFROM"
fi
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK; do [ -z "${!v:-}" ] || { echo "$v is set"; exit 2; }; done
sedi() { local f=${!#} t; t=$(mktemp "$S/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
REAL_RSYNC=$(command -v rsync); REAL_PGREP=$(command -v pgrep)
T=$S/tree; B=$S/box; BIN=$S/bin; BB=$S/boxbin; BOXT=$B/aifoundry3/aifoundry
mkdir -p "$BOXT/build/claims-v3/aifoundry3" "$BIN" "$BB" "$S/sd"
E=tools/claims-v3/e192
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
echo "E192 runbook desk test (kit-e192), $(date '+%F %T %Z'); bash ${BASH_VERSION}; $(rsync --version | head -n 1 | cut -c1-40); Python $(/usr/bin/python3 -V 2>&1); host name $(hostname)"
# ---- the scratch repository: a shared sparse clone at the registration, then the kit's files as one stand-in commit
REG=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/E192.md | tail -n 1)
[ -n "$REG" ] || { echo "no registration commit in the lab clone's history"; exit 2; }
git clone -q --shared --no-checkout "$SRC" "$T" || exit 2
G="git -C $T -c user.name=e192-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /workloads/sparsity/ || exit 2
$G checkout -q -B main "$REG" || exit 2
$G branch -q up "$REG"; $G branch -q --set-upstream-to=up main 2>/dev/null
( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E; git ls-files -- $E ) | sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
mkdir -p "$T/$E/logs"
for spec in "desktest-realpath-e192.txt DESKTEST-REALPATH-E192 1 of 1 PASS" "selftest-rb-e192.txt SELFTEST-RB-E192 1 of 1 PASS" \
            "selftest-rest-e192.txt SELFTEST-REST-E192 1 of 1 PASS" "dry-listing-e192.txt dry listing: 13 steps listed, 0 exited non-zero, 0 box calls" \
            "dmcmd-audit-e192.txt PLAIN-CHAIN: GO (stand-in)"; do
  f=${spec%% *}; [ -f "$T/$E/logs/$f" ] || printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"
done
mkkit() {  # the stand-in kit list: every e192 file but the registration's, the list itself and step 2 (outside the list)
  ( cd "$T" && git show "$REG" --name-only --format= -- $E ) > "$S/reg-files.txt"
  ( cd "$T" && find $E -type f ! -name 'SHA256SUMS-e192-kit' ! -path "$E/rb/s03_desk_e192.sh" ! -name '*.pyc' ! -path '*/__pycache__/*' | LC_ALL=C sort |
    while IFS= read -r f; do sha256sum "$f"; done ) | grep -v -F -f "$S/reg-files.txt" > "$S/kit-standin.txt"
  KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e192-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^KITPIN=$E/SHA256SUMS-e192-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e192-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e192.sh"
}
mkkit
$G add -A $E && $G commit -q -m "E192 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; exit 2; }
$G branch -q -f up HEAD
echo "scratch repository: a shared sparse clone at the registration ${REG:0:12}, the kit as one stand-in commit $($G rev-parse --short=12 HEAD); the kit list's stand-in $KITN files"
# ---- the stand-ins
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: refusing the command '\$cmd'" >&2; exit 97; }
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; echo "To authenticate, visit: https://login.tailscale.com/a/e192desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
if [ -e "$S/ssh-cut" ]; then rm -f "$S/ssh-cut"; cat > /dev/null; echo "ssh: connection closed (desk-test stand-in)" >&2; exit 255; fi
cd "$B/\$host" && HOME="$B/\$host" PATH="$BB:\$PATH" exec bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\nif [ -e "%s/etwho-held" ]; then echo "/dev/et0_ops otheruser 4242 foo_host"; [ "$1" = --check ] && exit 1; exit 0; fi\necho "No process holds an ET-SoC-1 device node or card lock."\nexit 0\n' "$S" > "$BB/et-who"
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
  p=${role% *}; mkdir -p "$BOXT/$(dirname "$p")"; printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s %s "$@"\n' "$SRC/$E/desk/standin_e192.py" "${role#* }" > "$BOXT/$p"; chmod +x "$BOXT/$p"
done
mkdir -p "$BOXT/build/claims-v3/aifoundry3/e183-smoke/p18301"; echo '{"status":"ok","note":"another run (desk test)"}' > "$BOXT/build/claims-v3/aifoundry3/e183-smoke/p18301/block.json"
OTHER=$(sha256sum "$BOXT/build/claims-v3/aifoundry3/e183-smoke/p18301/block.json" | cut -d' ' -f1)
: > /run/lock/etsoc-shire0.lock
export E192_STANDIN_DIR="$S/sd" E192_STANDIN_TABLE="$SRC/$E/desk/arm-table-e192.jsonl"
echo '{}' > "$S/sd/scenario.json"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_DESKTEST=1 E192_DESK_BUDGET_S=60 USER="$(id -un)"   # USER as the box's ssh login sets it
: > "$S/calls.log"; : > "$S/gitlock"
if [ -n "$LOCKFROM" ]; then cp "$LOCKFROM" "$RB_LOCK"; else : > "$RB_LOCK"; fi
LOCK0=$(grep -c . "$RB_LOCK"); LOCKH=$(sha256sum < "$LOCKFROM" 2>/dev/null | cut -d' ' -f1)
echo "RB_LOCK: $([ -n "$LOCKFROM" ] && echo "a copy of the given lock file of checks, $LOCK0 lines" || echo "an empty file")"
R=$T/$E/rb; K6=$T/tools/claims-v3/q141k-runbook/k6
TODAY=$(TZ=America/Los_Angeles date +%F)
cd "$T" || exit 2
win() { mkdir -p "$1"; RB_OUT="$1" bash "$R/s02_window_e192.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1; }

step "A. the dry listing"
bash "$R/list_steps_e192.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
tail -n 1 "$S/dry-listing.txt"
ok "$rc.$(grep -c . "$S/calls.log")" "0.0" "A every step 0, no call to the stand-ins"

step "K, W1-W3, G. the window rule; RB_GITLOCK required"
RB_OUT="$S/out-k" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e192.sh" > "$S/k.txt" 2>&1; k=$?
win "$S/out-w"; touch -d '-1 day' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e192.sh" > "$S/w1.txt" 2>&1; w1=$?
win "$S/out-w"; sedi -e 's/^RB_PLAN=e192$/RB_PLAN=e189/' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e192.sh" > "$S/w2.txt" 2>&1; w2=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e192.sh" "$(date -d '+1 day' +%F)" 10:00 12:00 > "$S/w3.txt" 2>&1; w3=$?
win "$S/out-p"
RB_OUT="$S/out-p" bash "$R/s03_desk_e192.sh" > "$S/g.txt" 2>&1; g=$?
ok "$k.$(has 'no window in RB_OUT' "$S/k.txt").$w1.$(has 'not written today' "$S/w1.txt").$w2.$(has 'written for e189' "$S/w2.txt").$w3.$(has 'is not today' "$S/w3.txt").$g.$(has 'RB_GITLOCK is not set' "$S/g.txt")" \
  "10.1.10.1.10.1.10.1.10.1" "K, W1-W3, G each refused (10) before any call"

step "N. step 2 run inside the lab-git lock (nested)"
RB_GITLOCK_T=2 /usr/bin/flock -n -E 75 "$S/gitlock" env RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e192.sh" > "$S/n.txt" 2>&1; n=$?
stopline "$S/n.txt"
ok "$n.$(has 'pull' "$S/n.txt")" "16.1" "N a nested step 2 stops with 16 naming its pull"

step "P1. step 2 on the scratch repository"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e192.sh" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check:|STOP' "$S/p1.txt" | cut -c1-500
ok "$p1.$(has 'the lists at their pinned counts and bytes (30;' "$S/p1.txt").$(has 'no E192 datum in any ref' "$S/p1.txt")" "0.1.1" "P1 step 2 passes at every pin, HISTORY OK, both freeze lines, no E192 datum, the preflight GO"

step "P2, P3, H1, H2, H3, D1. a short list; the kit's list short; an edited registered file; two shadows; an E192 datum in a ref"
sedi -e '$d' "$T/$E/SHA256SUMS-e192-registration"; $G commit -q -am "desk test: the registration's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e192.sh" > "$S/p2.txt" 2>&1; p2=$?; $G reset -q --hard HEAD~1
sedi -e '$d' "$T/$E/SHA256SUMS-e192-kit"; $G commit -q -am "desk test: the kit's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e192.sh" > "$S/p3.txt" 2>&1; p3=$?; $G reset -q --hard HEAD~1
printf '\n' >> "$T/$E/proposal/src/run_block.py"; $G commit -q -am "desk test: a registered file edited"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e192.sh" > "$S/h1.txt" 2>&1; h1=$?; $G reset -q --hard HEAD~1
printf '# desk test: would shadow json for run_block.py\n' > "$T/$E/proposal/src/json.py"; $G add $E/proposal/src/json.py; $G commit -q -m "desk test: a shadow in the reference session's folder"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e192.sh" > "$S/h2.txt" 2>&1; h2=$?
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e192.py tree ) > "$S/h2b.txt" 2>&1; $G reset -q --hard HEAD~1
printf '# desk test\n' > "$T/tools/claims-v3/e89/random.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e192.py tree ) > "$S/h3.txt" 2>&1; h3=$?; rm -f "$T/tools/claims-v3/e89/random.py"
$G checkout -q -b side; mkdir -p "$T/docs/reports/data/2026-11-14-e192-intbits-aifoundry3"; echo x > "$T/docs/reports/data/2026-11-14-e192-intbits-aifoundry3/README.md"
$G add --sparse -f docs/reports/data/2026-11-14-e192-intbits-aifoundry3/README.md; $G commit -q -m "desk test: an E192 datum on a side branch"; $G checkout -q main
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e192.sh" > "$S/d1.txt" 2>&1; d1=$?; $G branch -q -D side
cut -c1-300 "$S/h2b.txt" "$S/h3.txt"
ok "$p2.$(has 'SHA256SUMS-e192-registration' "$S/p2.txt").$p3.$(has 'SHA256SUMS-e192-kit' "$S/p3.txt").$h1.$(has 'history' "$S/h1.txt").$h2.$(has 'proposal/src/json.py (as json)' "$S/h2b.txt").$h3.$(has 'e89/random.py' "$S/h3.txt").$d1.$(has 'E192-datum' "$S/d1.txt")" \
  "16.1.16.1.16.1.16.1.16.1.16.1" "P2, P3, H1, H2, H3, D1 each refused and named"

step "S. step 5, the sync"
RB_OUT="$S/out-p" bash "$R/s07_a3_sync_e192.sh" > "$S/s.txt" 2>&1; s=$?
grep -E 'synced to|STOP' "$S/s.txt" | cut -c1-300
ok "$s.$(has 'BOX-PINS OK' "$S/out-p/calls/"*boxpins*.out 2>/dev/null || echo 0).$([ -f "$BOXT/build/claims-v3/aifoundry3/e192/$E/session_e192.sh" ] && echo 1).$([ "$(sha256sum "$BOXT/build/claims-v3/aifoundry3/e183-smoke/p18301/block.json" | cut -d' ' -f1)" = "$OTHER" ] && echo 1).$([ -e "$BOXT/tools" ] && echo 0 || echo 1)" \
  "0.1.1.1.1" "S E192's files in E192's root at their pins; another run's file untouched; nothing outside E192's root"

step "B, X, T. step 6: a real build, the wait, the box's tools; a second start; NO-THIRD-BUILD"
RB_OUT="$S/out-p" bash "$R/s08_a3_build_e192.sh" start > "$S/b1.txt" 2>&1; b1=$?
RB_WAIT_LOOP_S=2 RB_OUT="$S/out-p" bash "$R/s08_a3_build_e192.sh" wait > "$S/b2.txt" 2>&1; b2=$?
RB_OUT="$S/out-p" bash "$R/s08_a3_build_e192.sh" wait > "$S/b3.txt" 2>&1; b3=$?
[ "$b3" = 17 ] && { RB_OUT="$S/out-p" bash "$R/s08_a3_build_e192.sh" wait > "$S/b3.txt" 2>&1; b3=$?; }
grep -E 'INTBITS|BOXCHECK|built today|STOP|kernel_' "$S/b3.txt" | cut -c1-220
b2w=$([ "$b2" = 17 ] || [ "$b2" = 0 ] && echo ok)   # 17 while it runs, or 0 when the build (about 2 s on this desk) ended inside the 2 s wait
echo "   (the first wait, bounded at 2 s: exit $b2)"
ok "$b1.$b2w.$b3.$(has 'INTBITS-BUILT rc=0' "$S/b3.txt").$([ -s "$S/out-p/e192-built.txt" ] && echo 1)" "0.ok.0.1.1" "B the build job: started; the bounded wait 17 while it runs (or 0 once ended); then 0 with INTBITS-BUILT and the box's tools and pins OK"
RB_OUT="$S/out-p" bash "$R/s08_a3_build_e192.sh" start > "$S/x.txt" 2>&1; x=$?
ER=$BOXT/build/claims-v3/aifoundry3/e192
cp "$ER/build-attempts.txt" "$S/attempts.keep"; mv "$BOXT/build/q141k/jobs/a3-build-e192.out" "$S/job.out.keep"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e192 started" >> "$ER/build-attempts.txt"
RB_OUT="$S/out-p" bash "$R/s08_a3_build_e192.sh" start > "$S/t.txt" 2>&1; t=$?
cp "$S/attempts.keep" "$ER/build-attempts.txt"; mv "$S/job.out.keep" "$BOXT/build/q141k/jobs/a3-build-e192.out"
ok "$x.$(has 'was built today' "$S/x.txt").$t.$(has 'NO-THIRD-BUILD' "$S/t.txt")" "10.1.16.1" "X a second start after a build: 10; T a third start: NO-THIRD-BUILD 16"

step "L1, L2, L3. the login check; a hang; a cut wait"
n0=$(grep -c 'aifoundry3 needs a check' "$RB_LOCK")
: > "$S/ssh-login"; RB_OUT="$S/out-p" bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/l1.txt" 2>&1; l1=$?
n1=$(grep -c 'aifoundry3 needs a check' "$RB_LOCK"); kept=$( [ "$(head -n "$LOCK0" "$RB_LOCK" | sha256sum | cut -d' ' -f1)" = "$( [ -n "$LOCKFROM" ] && echo "$LOCKH" || printf '' | sha256sum | cut -d' ' -f1)" ] && echo 1 || echo 0)
echo "   RB_LOCK: $((n1 - n0)) line appended ('$(tail -n 1 "$RB_LOCK")'); its first $LOCK0 lines kept: $kept"
touch "$S/ssh-hang"; RB_READ_S=3 RB_OUT="$S/out-p" bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/l2.txt" 2>&1; l2=$?
touch "$S/ssh-cut"; RB_OUT="$S/out-p" bash "$R/s08_a3_build_e192.sh" wait > "$S/l3.txt" 2>&1; l3=$?
ok "$l1.$((n1 - n0)).$kept.$l2.$l3" "11.1.1.13.14" "L1 a login link: 11, one line appended to RB_LOCK and the rest kept; L2 a hang: 13; L3 a cut wait: 14"
rm -f "$S/ssh-login" "$S/ssh-hang" "$S/ssh-cut"

step "DR. step 8, the box's dry pass"
RB_OUT="$S/out-p" bash "$R/s10_a3_dry_e192.sh" start > "$S/dr1.txt" 2>&1; dr1=$?
RB_OUT="$S/out-p" bash "$R/s10_a3_dry_e192.sh" wait > "$S/dr2.txt" 2>&1; dr2=$?
grep -E 'E192-DRY|STOP' "$S/dr2.txt" | cut -c1-240 | head -n 3
ok "$dr1.$dr2.$(has 'E192-DRY OK: 328 device calls' "$S/dr2.txt")" "0.0.1" "DR the dry pass on the stand-in box: 0, E192-DRY OK"

step "RS, LA. the rest rule through step 9; then the launch"
now=$(date +%s); t1=$((now - 600)); mkdir -p "$BOXT/build/e189/T$((t1 - 3000))"
printf '%s session start (T0 %s = x; plan FULL)\n%s session end (T0 %s)\n' "$(date -d @$((t1 - 3000)) '+%F %T %Z')" $((t1 - 3000)) "$(date -d @$t1 '+%F %T %Z')" $((t1 - 3000)) > "$BOXT/build/e189/T$((t1 - 3000))/session.log"
RB_OUT="$S/out-p" bash "$R/s11_a3_session_e192.sh" FULL --plain-sampler > "$S/rs.txt" 2>&1; rs=$?
rm -rf "${BOXT:?}/build/e189"
t2=$((now - 2700)); mkdir -p "$BOXT/build/e183"
printf '%s session start (T0 %s = x; plan FULL)\n%s session end (T0 %s)\n' "$(date -d @$((t2 - 3000)) '+%F %T %Z')" $((t2 - 3000)) "$(date -d @$t2 '+%F %T %Z')" $((t2 - 3000)) > "$BOXT/build/e183/session-t$((t2 - 3000)).log"
echo '{"scale": 0.25}' > "$S/sd/scenario.json"
RHOST=$ER/build/intbits/host/intbits_host; cp -p "$RHOST" "$S/real-host.keep"
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s host "$@"\n' "$SRC/$E/desk/standin_e192.py" > "$RHOST"
RB_OUT="$S/out-p" bash "$R/s11_a3_session_e192.sh" FULL --plain-sampler > "$S/la.txt" 2>&1; la=$?
grep -E 'LAUNCHED|rest:|REFUSED|STOP' "$S/rs.txt" "$S/la.txt" | cut -c1-260
ok "$rs.$(has 'REFUSED: 10 minutes since E189' "$S/rs.txt").$la.$(has 'LAUNCHED e192 T0' "$S/la.txt")" "10.1.0.1" "RS a session 10 min ago: refused (10), nothing launched; LA 45 min ago: launched"
T0=$(cat "$S/out-p/e192-T0.txt" 2>/dev/null)
RB_WAIT_LOOP_S=3 RB_OUT="$S/out-p" bash "$R/s20_wait_e192.sh" > "$S/w1r.txt" 2>&1; w1r=$?
ok "$w1r.$(has 'RUN-RUNNING e192' "$S/w1r.txt")" "17.1" "W1r step 10 while the real session_e192.sh runs: RUN-RUNNING (17)"
# the stop by hand once pass 0 is done (bounded: at most 8 minutes)
lim=$(( $(date +%s) + 480 ))
until [ "$(date +%s)" -ge "$lim" ] || /usr/bin/python3 -I -B - "$BOXT/build/e192/T$T0/run/marks.jsonl" <<'PY'
import json, sys
try:
    ms = [json.loads(l) for l in open(sys.argv[1]) if l.strip().startswith('{')]
except OSError:
    sys.exit(1)
sys.exit(0 if any(m.get('kind') == 'idle' and m.get('label') == 'after' and m.get('pass') == 0 for m in ms) else 1)
PY
do sleep 2; done
printf '{"by": "hand", "why": "desk test: by hand after pass 0", "t_ms": %s}\n' "$(date +%s%3N)" > "$BOXT/build/e192/T$T0/run/STOP"
lim=$(( $(date +%s) + 180 ))
until grep -q "session end (T0 $T0)" "$BOXT/build/e192/T$T0/session.log" 2>/dev/null || [ "$(date +%s)" -ge "$lim" ]; do sleep 2; done
RB_OUT="$S/out-p" bash "$R/s20_wait_e192.sh" > "$S/w2r.txt" 2>&1; w2r=$?
grep -E 'passes complete|RUN-|MANIFEST|STOP' "$S/w2r.txt" | cut -c1-200
ok "$w2r.$(has 'RUN-ENDED e192' "$S/w2r.txt").$(has 'MANIFEST-WRITTEN' "$S/w2r.txt").$(has 'passes complete: 1 of 9' "$S/w2r.txt")" "0.1.1.1" "W2r step 10 after the stop by hand: RUN-ENDED, MANIFEST-WRITTEN, 1 pass complete"

step "WN. a decoy session_e1920.sh, and a session log with no end"
cp "$S/out-p/e192-T0.txt" "$S/t0.keep"; cp "$BOXT/build/q141k/e192.T0" "$S/boxt0.keep"
T9=$((T0 + 5)); mkdir -p "$BOXT/build/e192/T$T9"; echo "$(date '+%F %T %Z') session start (T0 $T9 = x; E192)" > "$BOXT/build/e192/T$T9/session.log"
echo "$T9" > "$S/out-p/e192-T0.txt"; echo "$T9" > "$BOXT/build/q141k/e192.T0"
printf '#!/bin/bash\nsleep 60\n' > "$S/session_e1920.sh"; bash "$S/session_e1920.sh" &
DEC=$!
RB_OUT="$S/out-p" bash "$R/s20_wait_e192.sh" > "$S/wn.txt" 2>&1; wn=$?
kill "$DEC" 2>/dev/null; wait "$DEC" 2>/dev/null
rm -rf "${BOXT:?}/build/e192/T$T9"; cp "$S/t0.keep" "$S/out-p/e192-T0.txt"; cp "$S/boxt0.keep" "$BOXT/build/q141k/e192.T0"
ok "$wn.$(has 'RUN-GONE e192' "$S/wn.txt")" "14.1" "WN a decoy named session_e1920.sh: RUN-GONE (14), the pattern matches the real name only"

step "C. step 11, the collection"
id -un > "$S/out-p/box-login-aifoundry3.txt"
RB_OUT="$S/out-p" bash "$R/s22_collect_e192.sh" > "$S/c.txt" 2>&1; c=$?
grep -E 'COLLECTED|STOP|COPY|ASSEMBLED|SCRUB' "$S/c.txt" | cut -c1-260
DD=$S/out-p/e192-out/$TODAY-e192-intbits-aifoundry3
ok "$c.$(has 'COPY EXACT' "$S/c.txt").$([ -f "$DD/run/telemetry.jsonl.gz" ] && [ -f "$DD/facts-e192.json" ] && echo 1).$( (cd "$DD" && sha256sum -c --quiet SHA256SUMS) > /dev/null 2>&1 && echo 1)" "0.1.1.1" "C COPY EXACT, the gates, the data directory and its SHA256SUMS: 0"

step "R. the data directory committed (in the scratch repository), then step 13"
mkdir -p "$T/docs/reports/data"; cp -r "$DD" "$T/docs/reports/data/"
$G add --sparse -f "docs/reports/data/$TODAY-e192-intbits-aifoundry3"; $G commit -q -m "desk test: the stand-in session's data directory"
RB_OUT="$S/out-p" bash "$R/s24_reduce_e192.sh" "docs/reports/data/$TODAY-e192-intbits-aifoundry3" > "$S/r.txt" 2>&1; rr=$?
grep -E 'reduced|STOP|CHECKS' "$S/r.txt" | cut -c1-300
ok "$rr.$(has 'CHECKS-E192: ' "$S/r.txt").$([ -s "$S/out-p/intbits-e192.json" ] && echo 1)" "0.1.1" "R the registered reducer on the committed data, then the checker: 0"
$G reset -q --hard HEAD~1

step "C2. one byte of a box file changed after the session's manifest"
mv "$S/out-p/e192-raw" "$S/raw.c1"; mv "$S/out-p/e192-out" "$S/out.c1"
echo "x" >> "$BOXT/build/e192/T$T0/run/gate.jsonl"
RB_OUT="$S/out-p" bash "$R/s22_collect_e192.sh" > "$S/c2.txt" 2>&1; c2=$?
ok "$c2.$(has 'COPY NOT EXACT' "$S/c2.txt")" "16.1" "C2 the session's own manifest no longer holds: COPY NOT EXACT, 16"
cp "$S/real-host.keep" "$RHOST"

step "Z"
left=$(ls /proc | grep -E '^[0-9]+$' | while read -r p; do tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | grep -E 'standin_e192|session_e192|run_session|gate_e192|stopwatch|run_block' | grep -v grep; done | head -n 3)
ok "$([ -z "$left" ] && echo 1)" "1" "Z no process of this test left ($left)"
echo; echo "SELFTEST-RB-E192 $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
