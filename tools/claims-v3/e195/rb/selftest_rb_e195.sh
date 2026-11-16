#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): the desk test of E195's runbook with a FAKE ssh and rsync on a
# stand-in box, E192's runbook desk test's form (rb/selftest_rb_e192.sh). Its scratch repository is a shared, sparse clone of the lab clone
# this test runs from, at E195's registration commit (found by its content), with the kit's files committed on top as one stand-in kit
# commit, the kit list a stand-in made here and pinned in the scratch copy of step 2's KITPIN line (the one line this test changes in a
# copy: the real list holds this test's log). The stand-in box is aifoundry3's ~/aifoundry at /srv/e195rb/aifoundry3/aifoundry inside this
# test's own sandbox (a tmpfs /srv: the box's absolute paths, which the registered runner writes into every pass's configs.json and text
# hashes, are then outside the desk's home, as the box account's own tree is on the card day, so the desk-path gate reads them as the box's).
# The stand-in ssh serves only `bash -s` (and the probe's `true`) and refuses any other host or command; the stand-in rsync rewrites
# aifoundry3: paths onto the stand-in box. THE BOX'S BUILD IS REAL: build_e195.sh with this desk's /opt/et (cmake, check_elf.py, the built
# host's --list --json and --list, make_x09.py --check --no-ms with numpy, the heater's parser on the stand-in heater). The box's sampler,
# heater and anchor are fake_card_e195.py; et-who and the holder helper answer free; the card lock is a file in the sandbox's /run/lock;
# after the real build, the built host is swapped for the stand-in host (which prints X09MEM lines at the host's real launch timing) and
# the box's build record's host line rewritten to it (the session checks the host against the record). No lab box is reached. Cases:
#   A   the dry listing: every step exits 0, no call reaches the stand-ins;
#   K   step 2 with no window: 10;  W1 a window written yesterday: 10;  W2 one written for E192: 10;  W3 step 1 for another day: 10;
#   G   step 2 without RB_GITLOCK: 10;  N step 2 run INSIDE the lab-git lock (nested): 16 naming its pull;
#   P1  step 2 on the scratch repository: 0 (the lists at their pins, HISTORY OK, the freeze line, the harness, PORT CHECK PASS,
#       DRYLISTING-E195 PASS, no E195 datum, the preflight GO, the desk tests' logs);
#   P2  the registration's list one line short: 16;  P3 the kit's list one line short: 16;  H1 a committed edit of a registered file: 16;
#   H2  an added tools/claims-v3/e195/json.py (runitems_e195.py runs there without -I on the box): 16 naming it;
#   H3  an untracked tools/claims-v3/random.py (dmcmd_audit.py's folder): 16;  D1 an E195 data folder on a side branch: 16;
#   S   step 5: the harness's files into E195's root on the box, at their pins (HARNESS OK on the box); another run's file untouched;
#   B   step 6 start, a 2 s bounded wait (17 while it runs, or 0), then 0: X09MEM-BUILT by a real build, the box's pins and tools OK,
#       RB_OUT/e195-built.txt;  X a second start after a build today: 10;  T NO-THIRD-BUILD: two starts recorded today and no build: 16;
#   L1  THE LOGIN CHECK: a login link at a read: 11, "<HH:MM:SS> aifoundry3 needs a check" appended to RB_LOCK, nothing retried;
#   L2  a read that hangs: killed at its bound (the read class's bound shortened for this case only): 13;  L3 a cut wait (ssh 255): 14;
#   RT  STEP 7'S REST GATE: an E188-form session ended 10 minutes ago on the box: 10, no config read sent (k6's reads not run); then
#       ended 45 minutes ago: the rest reads open and k6's reads run (the config through E128's guard, the stand-in's): 0;
#   DR  step 8 (session_e195.sh --dry on the stand-in box, the real built host's --list): 0, E195-DRY OK (288 device calls);
#   RS  THE REST RULE THROUGH STEP 9: an E193-form session ended 10 minutes ago on the box: 10, nothing launched;
#   SF  a stop file left in E195's root (build/x09-STOP): step 9 refuses (10), nothing launched;
#   LA  the sessions 45 minutes old: step 9 launches the REAL session_e195.sh on the stand-in box (the stand-in host at real timing);
#   W1r step 10 while it runs: 17 (the session-name pattern matches the real script's name: RUN-RUNNING); the operator's stop file once
#       pass 911 has ended;  W2r step 10 again: 0, RUN-ENDED, MANIFEST-WRITTEN, 2 passes complete;
#   WN  a decoy session_e1950.sh running and a session log with no end: 14 (RUN-GONE: the pattern does not match a longer name);
#   SD  a second launch the same day after the session that opened the card: 10 (no second E195 session that day);
#   C   step 11 on the session: COPY EXACT, the desk-path gate, the data directory, SCRUB-CHECK OK, the login scrub, NO-DATUM OK: 0;
#   R   the data directory committed in the scratch repository: step 13 (the registered reducer on the main passes, then the leftover
#       checker): 0;  C2 one byte of a box file changed after the session's manifest: COPY NOT EXACT, 16;
#   GS  A GATE STOP COLLECTED AS ITS RECORD: a launch that met another user's holder (GATE-STOP, no device opened), from a new RB_OUT:
#       step 10 says GATE-STOPPED (16) and step 11 assembles it under gate-stops/, never a data directory;
#   Z   no process of this test left running;
#   AUDIT-RB (Q191, lane fix-e195, verify-e195's nit 7) every line of the runbook that reads RB_DRY (rb_e195.sh, the ten steps, k6's
#       rb_common.sh) has a row in rb/dry-branches-rb-e195.tsv whose text is the line's and whose named cases passed in THIS run
#       (rb/drybranches_rb_e195.py --check on <scratch>/ok-results.txt, where ok() writes each ok line's result by its first word).
#   bash tools/claims-v3/e195/rb/selftest_rb_e195.sh <scratch dir> [<a lock file of checks to copy as RB_LOCK>] > <log>
#       (prints SELFTEST-RB-E195 <n> of <m> PASS or FAIL; with the second argument RB_LOCK starts as a COPY of that file, which is never
#       written, and L1 counts the one line it appends to the copy)
# On aifoundry2 run it ONLY inside W/nodev.sh: it re-executes itself in bubblewrap (a private /dev with a regular file named /dev/et0_ops,
# a private /run/lock, a private PID namespace and /proc, the host name aifoundry3, a tmpfs /srv holding the stand-in box).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd -P)
S=${1:?a scratch directory outside the repository}
LOCKFROM=${2:-}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
[ -z "$LOCKFROM" ] || [ -f "$LOCKFROM" ] || { echo "no lock file $LOCKFROM to copy"; exit 2; }
if [ -z "${E195_RB_INNER:-}" ]; then
  for d in /dev/et*; do [ -e "$d" ] || continue; if [ -c "$d" ] || [ -b "$d" ]; then echo "REFUSED: $d is a device node: run inside W/nodev.sh"; exit 2; fi; done
  mkdir -p "$S" && S=$(cd "$S" && pwd -P); [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
  : > "$S/et0_ops.regular-file"; mkdir -p "$S/box"
  exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --bind "$S/et0_ops.regular-file" /dev/et0_ops \
    --tmpfs /srv --bind "$S/box" /srv/e195rb --unshare-pid --proc /proc \
    --unshare-uts --hostname aifoundry3 --die-with-parent --setenv E195_RB_INNER 1 -- /bin/bash "$SRC/tools/claims-v3/e195/rb/selftest_rb_e195.sh" "$S" "$LOCKFROM"
fi
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK; do [ -z "${!v:-}" ] || { echo "$v is set"; exit 2; }; done
sedi() { local f=${!#} t; t=$(mktemp "$S/sedi.XXXXXX") || return 2; sed "${@:1:$(($# - 1))}" "$f" > "$t" && cat "$t" > "$f"; local r=$?; rm -f "$t"; return "$r"; }
REAL_RSYNC=$(command -v rsync); REAL_PGREP=$(command -v pgrep)
T=$S/tree; B=/srv/e195rb; BIN=$S/bin; BB=$S/boxbin; BOXT=$B/aifoundry3/aifoundry
mkdir -p "$BOXT/build/claims-v3/aifoundry3" "$BIN" "$BB" "$S/sd"
E=tools/claims-v3/e195
ER=$BOXT/build/claims-v3/aifoundry3/e195
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); local k=${3%% *}; k=${k%,}
  if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; echo "PASS $k" >> "$S/ok-results.txt"
  else echo "-> FAIL ($3: got $1, want $2)"; echo "FAIL $k" >> "$S/ok-results.txt"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
echo "E195 runbook desk test (kit-e195), $(date '+%F %T %Z'); bash ${BASH_VERSION}; $(rsync --version | head -n 1 | cut -c1-40); Python $(/usr/bin/python3 -V 2>&1); host name $(hostname)"
# ---- the scratch repository: a shared sparse clone at the registration, then the kit's files as one stand-in commit
REG=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/E195.md | tail -n 1)
[ -n "$REG" ] || { echo "no registration commit in the lab clone's history"; exit 2; }
git clone -q --shared --no-checkout "$SRC" "$T" || exit 2
G="git -C $T -c user.name=e195-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ || exit 2
$G checkout -q -B main "$REG" || exit 2
$G branch -q up "$REG"; $G branch -q --set-upstream-to=up main 2>/dev/null
( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E; git ls-files -- $E ) | sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
mkdir -p "$T/$E/logs"
for spec in "desktest-realpath-e195.txt DESKTEST-REALPATH-E195 1 of 1 PASS" "realbytes-e195.txt REALBYTES-E195 1 of 1 PASS" \
            "selftest-rb-e195.txt SELFTEST-RB-E195 1 of 1 PASS" "selftest-rest-e195.txt SELFTEST-REST-E195 1 of 1 PASS" \
            "dry-listing-e195.txt dry listing: 13 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e195.txt dmcmd_audit: GO (stand-in)" \
            "checks-e195.txt CHECKS-E195 1 of 1 PASS"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"      # stand-in lines (the real logs are read by the real step 2)
done
mkkit() {  # the stand-in kit list: every e195 file but the registration's, the list itself and step 2 (outside the list)
  ( cd "$T" && git show "$REG" --name-only --format= -- $E ) > "$S/reg-files.txt"
  ( cd "$T" && find $E -type f ! -name 'SHA256SUMS-e195-kit' ! -path "$E/rb/s03_desk_e195.sh" ! -name '*.pyc' ! -path '*/__pycache__/*' | LC_ALL=C sort |
    while IFS= read -r f; do sha256sum "$f"; done ) | grep -v -F -f "$S/reg-files.txt" > "$S/kit-standin.txt"
  KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e195-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
  sedi -e "s#^KITPIN=$E/SHA256SUMS-e195-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e195-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e195.sh"
}
mkkit
$G add -A $E && $G commit -q -m "E195 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; exit 2; }
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
if [ -e "$S/ssh-login" ]; then rm -f "$S/ssh-login"; echo "To authenticate, visit: https://login.tailscale.com/a/e195desktest" >&2; sleep 30; exit 1; fi
if [ -e "$S/ssh-hang" ]; then rm -f "$S/ssh-hang"; cat > /dev/null; sleep 120; exit 0; fi
if [ -e "$S/ssh-cut" ]; then rm -f "$S/ssh-cut"; cat > /dev/null; echo "ssh: connection closed (desk-test stand-in)" >&2; exit 255; fi
cd "$B/\$host" && HOME="$B/\$host" PATH="$BB:\$PATH" E195_FAKE_STATE="$S/sd" E195_FAKE_LOGIN="\$(id -un)" exec bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
FK=$T/$E/fake_card_e195.py
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s etwho "$@"\n' "$FK" > "$BB/et-who"
printf '#!/bin/bash\nif [ "$1" = -n ] && [ "$2" = /usr/local/sbin/et-holders ] && [ $# -eq 2 ]; then exec /usr/bin/python3 -I -B %s holders; fi\necho "BOX STAND-IN: sudo refused" >&2\nexit 97\n' "$FK" > "$BB/sudo"
printf '#!/bin/sh\necho "host stand-in (E195 runbook desk test)"\n' > "$BB/et-lab-manifest"
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
for n in ssh rsync scp; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$BB/$n"; done
chmod +x "$BIN"/* "$BB"/*
for role in "build/ettelem/ettelem ettelem" "build/sparsity/host/sparsity_host sparsity"; do
  p=${role% *}; mkdir -p "$BOXT/$(dirname "$p")"; printf '#!/bin/bash\n# stand-in (E195 runbook desk test); it takes --stop-file\nexec /usr/bin/python3 -I -B %s %s "$@"\n' "$FK" "${role#* }" > "$BOXT/$p"; chmod +x "$BOXT/$p"
done
mkdir -p "$BOXT/.venv/bin"; ln -s /usr/bin/python3 "$BOXT/.venv/bin/python3"      # the tree's numpy (lib.sh's .venv), for the generator check
mkdir -p "$BOXT/build/claims-v3/aifoundry3/e183-smoke/p18301"; echo '{"status":"ok","note":"another run (desk test)"}' > "$BOXT/build/claims-v3/aifoundry3/e183-smoke/p18301/block.json"
OTHER=$(sha256sum "$BOXT/build/claims-v3/aifoundry3/e183-smoke/p18301/block.json" | cut -d' ' -f1)
: > /run/lock/etsoc-shire0.lock
touch "$S/sd/fast" "$S/sd/slow_host"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_DESKTEST=1 E195_DESK_CAP_S=1800 USER="$(id -un)"   # USER as the box's ssh login sets it
: > "$S/calls.log"; : > "$S/gitlock"
if [ -n "$LOCKFROM" ]; then cp "$LOCKFROM" "$RB_LOCK"; else : > "$RB_LOCK"; fi
LOCK0=$(grep -c . "$RB_LOCK"); LOCKH=$(sha256sum < "$LOCKFROM" 2>/dev/null | cut -d' ' -f1)
echo "RB_LOCK: $([ -n "$LOCKFROM" ] && echo "a copy of the given lock file of checks, $LOCK0 lines" || echo "an empty file")"
R=$T/$E/rb; K6=$T/tools/claims-v3/q141k-runbook/k6
TODAY=$(TZ=America/Los_Angeles date +%F)
cd "$T" || exit 2
win() { mkdir -p "$1"; RB_OUT="$1" bash "$R/s02_window_e195.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1; }
slog() {  # slog <box session dir> <run words> <ended minutes ago>: a session log of ours in the kits' T0 form, on the stand-in box
  local d=$1 w=$2 m=$3 now t
  now=$(date +%s); t=$((now - m * 60)); mkdir -p "$d"
  printf '%s session start (T0 %s; %s)\n%s session end (T0 %s)\n' "$(date -d @$((t - 1800)) '+%F %T %Z')" $((t - 1800)) "$w" "$(date -d @$t '+%F %T %Z')" $((t - 1800)) > "$d/session.log"
  touch -d @"$t" "$d/session.log"
}

step "A. the dry listing"
bash "$R/list_steps_e195.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
tail -n 1 "$S/dry-listing.txt"
ok "$rc.$(grep -c . "$S/calls.log")" "0.0" "A every step 0, no call to the stand-ins"

step "K, W1-W3, G. the window rule; RB_GITLOCK required"
RB_OUT="$S/out-k" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e195.sh" > "$S/k.txt" 2>&1; k=$?
win "$S/out-w"; touch -d '-1 day' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e195.sh" > "$S/w1.txt" 2>&1; w1=$?
win "$S/out-w"; sedi -e 's/^RB_PLAN=e195$/RB_PLAN=e192/' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e195.sh" > "$S/w2.txt" 2>&1; w2=$?
RB_OUT="$S/out-w" bash "$R/s02_window_e195.sh" "$(date -d '+1 day' +%F)" 10:00 12:00 > "$S/w3.txt" 2>&1; w3=$?
win "$S/out-p"
RB_OUT="$S/out-p" bash "$R/s03_desk_e195.sh" > "$S/g.txt" 2>&1; g=$?
ok "$k.$(has 'no window in RB_OUT' "$S/k.txt").$w1.$(has 'not written today' "$S/w1.txt").$w2.$(has 'written for e192' "$S/w2.txt").$w3.$(has 'is not today' "$S/w3.txt").$g.$(has 'RB_GITLOCK is not set' "$S/g.txt")" \
  "10.1.10.1.10.1.10.1.10.1" "K, W1-W3, G each refused (10) before any call"

step "N. step 2 run inside the lab-git lock (nested)"
RB_GITLOCK_T=2 /usr/bin/flock -n -E 75 "$S/gitlock" env RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e195.sh" > "$S/n.txt" 2>&1; n=$?
stopline "$S/n.txt"
ok "$n.$(has 'pull' "$S/n.txt")" "16.1" "N a nested step 2 stops with 16 naming its pull"

step "P1. step 2 on the scratch repository"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e195.sh" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check:|STOP' "$S/p1.txt" | cut -c1-600
ok "$p1.$(has 'the lists at their pinned counts and bytes (41;' "$S/p1.txt").$(has 'PORT CHECK PASS; DRYLISTING-E195 PASS; no E195 datum in any ref' "$S/p1.txt")" "0.1.1" "P1 step 2 passes at every pin, HISTORY OK, the freeze line, the harness, the ports, the dry listing, no E195 datum, the preflight GO"

step "P2, P3, H1, H2, H3, D1. a short list; the kit's list short; an edited registered file; two shadows; an E195 datum in a ref"
sedi -e '$d' "$T/$E/SHA256SUMS-e195-registration"; $G commit -q -am "desk test: the registration's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e195.sh" > "$S/p2.txt" 2>&1; p2=$?; $G reset -q --hard HEAD~1
sedi -e '$d' "$T/$E/SHA256SUMS-e195-kit"; $G commit -q -am "desk test: the kit's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e195.sh" > "$S/p3.txt" 2>&1; p3=$?; $G reset -q --hard HEAD~1
printf '\n' >> "$T/$E/proposal/src/watch_x09.py"; $G commit -q -am "desk test: a registered file edited"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e195.sh" > "$S/h1.txt" 2>&1; h1=$?; $G reset -q --hard HEAD~1
printf '# desk test: would shadow json for runitems_e195.py\n' > "$T/$E/json.py"; $G add $E/json.py; $G commit -q -m "desk test: a shadow in the runner's folder"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e195.sh" > "$S/h2.txt" 2>&1; h2=$?
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e195.py tree ) > "$S/h2b.txt" 2>&1; $G reset -q --hard HEAD~1
printf '# desk test\n' > "$T/tools/claims-v3/random.py"
( cd "$T" && /usr/bin/python3 -I -B $E/rb/check_history_e195.py tree ) > "$S/h3.txt" 2>&1; h3=$?; rm -f "$T/tools/claims-v3/random.py"
$G checkout -q -b side; mkdir -p "$T/docs/reports/data/2026-11-15-e195-x09-dramtoggle-aifoundry3"; echo x > "$T/docs/reports/data/2026-11-15-e195-x09-dramtoggle-aifoundry3/README.md"
$G add --sparse -f docs/reports/data/2026-11-15-e195-x09-dramtoggle-aifoundry3/README.md; $G commit -q -m "desk test: an E195 datum on a side branch"; $G checkout -q main
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e195.sh" > "$S/d1.txt" 2>&1; d1=$?; $G branch -q -D side
cut -c1-300 "$S/h2b.txt" "$S/h3.txt"
ok "$p2.$(has 'SHA256SUMS-e195-registration' "$S/p2.txt").$p3.$(has 'SHA256SUMS-e195-kit' "$S/p3.txt").$h1.$(has 'history' "$S/h1.txt").$h2.$(has 'e195/json.py (as json)' "$S/h2b.txt").$h3.$(has 'claims-v3/random.py' "$S/h3.txt").$d1.$(has 'E195-datum' "$S/d1.txt")" \
  "16.1.16.1.16.1.16.1.16.1.16.1" "P2, P3, H1, H2, H3, D1 each refused and named"

step "S. step 5, the sync"
RB_OUT="$S/out-p" bash "$R/s07_a3_sync_e195.sh" > "$S/s.txt" 2>&1; s=$?
grep -E 'synced to|STOP' "$S/s.txt" | cut -c1-300
ok "$s.$(has 'HARNESS OK' "$S/s.txt").$([ -f "$ER/$E/session_e195.sh" ] && echo 1).$([ "$(sha256sum "$BOXT/build/claims-v3/aifoundry3/e183-smoke/p18301/block.json" | cut -d' ' -f1)" = "$OTHER" ] && echo 1).$([ -e "$BOXT/tools" ] && echo 0 || echo 1)" \
  "0.1.1.1.1" "S E195's files in E195's root at their pins (HARNESS OK on the box); another run's file untouched; nothing outside E195's root"

step "B, X, T. step 6: a real build, the wait, the box's pins and tools; a second start; NO-THIRD-BUILD"
RB_OUT="$S/out-p" bash "$R/s08_a3_build_e195.sh" start > "$S/b1.txt" 2>&1; b1=$?
RB_WAIT_LOOP_S=2 RB_OUT="$S/out-p" bash "$R/s08_a3_build_e195.sh" wait > "$S/b2.txt" 2>&1; b2=$?
RB_OUT="$S/out-p" bash "$R/s08_a3_build_e195.sh" wait > "$S/b3.txt" 2>&1; b3=$?
[ "$b3" = 17 ] && { RB_OUT="$S/out-p" bash "$R/s08_a3_build_e195.sh" wait > "$S/b3.txt" 2>&1; b3=$?; }
grep -E 'X09MEM|BOXCHECK|built today|STOP|kernel|generator|heater' "$S/b3.txt" | cut -c1-220
b2w=$([ "$b2" = 17 ] || [ "$b2" = 0 ] && echo ok)
echo "   (the first wait, bounded at 2 s: exit $b2)"
ok "$b1.$b2w.$b3.$(has 'X09MEM-BUILT rc=0' "$S/b3.txt").$(has 'generator CHECK OK: 31 arms' "$S/b3.txt").$([ -s "$S/out-p/e195-built.txt" ] && echo 1)" "0.ok.0.1.1.1" \
  "B the build job: started; the bounded wait 17 while it runs (or 0); then 0 with X09MEM-BUILT (the generator's check from the host's bytes), the box's pins and tools OK"
RB_OUT="$S/out-p" bash "$R/s08_a3_build_e195.sh" start > "$S/x.txt" 2>&1; x=$?
cp "$ER/build-attempts.txt" "$S/attempts.keep"; mv "$BOXT/build/q141k/jobs/a3-build-e195.out" "$S/job.out.keep"
echo "$(TZ=America/Los_Angeles date '+%F %T %Z') a3-build-e195 started" >> "$ER/build-attempts.txt"
RB_OUT="$S/out-p" bash "$R/s08_a3_build_e195.sh" start > "$S/t.txt" 2>&1; t=$?
cp "$S/attempts.keep" "$ER/build-attempts.txt"; mv "$S/job.out.keep" "$BOXT/build/q141k/jobs/a3-build-e195.out"
ok "$x.$(has 'was built today' "$S/x.txt").$t.$(has 'NO-THIRD-BUILD' "$S/t.txt")" "10.1.16.1" "X a second start after a build: 10; T a third start: NO-THIRD-BUILD 16"

step "L1, L2, L3. the login check; a hang; a cut wait"
n0=$(grep -c 'aifoundry3 needs a check' "$RB_LOCK")
: > "$S/ssh-login"; RB_OUT="$S/out-p" bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/l1.txt" 2>&1; l1=$?
n1=$(grep -c 'aifoundry3 needs a check' "$RB_LOCK"); kept=$( [ "$(head -n "$LOCK0" "$RB_LOCK" | sha256sum | cut -d' ' -f1)" = "$( [ -n "$LOCKFROM" ] && echo "$LOCKH" || printf '' | sha256sum | cut -d' ' -f1)" ] && echo 1 || echo 0)
echo "   RB_LOCK: $((n1 - n0)) line appended ('$(tail -n 1 "$RB_LOCK")'); its first $LOCK0 lines kept: $kept"
touch "$S/ssh-hang"; RB_READ_S=3 RB_OUT="$S/out-p" bash "$K6/s05_look_k6.sh" aifoundry3 > "$S/l2.txt" 2>&1; l2=$?
touch "$S/ssh-cut"; RB_OUT="$S/out-p" bash "$R/s08_a3_build_e195.sh" wait > "$S/l3.txt" 2>&1; l3=$?
ok "$l1.$((n1 - n0)).$kept.$l2.$l3" "11.1.1.13.14" "L1 a login link: 11, one line appended to RB_LOCK and the rest kept; L2 a hang: 13; L3 a cut wait: 14"
rm -f "$S/ssh-login" "$S/ssh-hang" "$S/ssh-cut"

step "RT. step 7's rest gate before its config read"
mkdir -p "$BOXT/tools/claims-v3/e128"; cp "$T/tools/claims-v3/e128/ettelem_guard.sh" "$BOXT/tools/claims-v3/e128/"   # the box tree's own copy (k6's step 7 runs it there)
slog "$BOXT/build/e188/T1794790000" "E188" 10
c0=$(grep -c 'ettelem config' "$S/sd/calls.log" 2>/dev/null)
RB_OUT="$S/out-p" bash "$R/s09_a3_reads_e195.sh" > "$S/rt1.txt" 2>&1; rt1=$?
c1=$(grep -c 'ettelem config' "$S/sd/calls.log" 2>/dev/null)
slog "$BOXT/build/e188/T1794790000" "E188" 45
RB_OUT="$S/out-p" bash "$R/s09_a3_reads_e195.sh" > "$S/rt2.txt" 2>&1; rt2=$?
c2=$(grep -c 'ettelem config' "$S/sd/calls.log" 2>/dev/null)
grep -E 'rest|REFUSED|config|STOP|aifoundry3:' "$S/rt1.txt" "$S/rt2.txt" | cut -c1-240
ok "$rt1.$(has 'the rest has not run: REFUSED: 10 minutes since E188' "$S/rt1.txt").$((c1 - c0)).$rt2.$((c2 - c1)).$(has 'config TDP 0 W / 65 C / 600 MHz' "$S/rt2.txt")" "10.1.0.0.1.1" \
  "RT the rest 10 min old: 10, no config read sent; 45 min old: the rest open, k6's reads ran (one config read through the guard)"

step "DR. step 8, the box's dry pass"
RB_OUT="$S/out-p" bash "$R/s10_a3_dry_e195.sh" start > "$S/dr1.txt" 2>&1; dr1=$?
dr2=17; for i in 1 2 3; do RB_OUT="$S/out-p" bash "$R/s10_a3_dry_e195.sh" wait > "$S/dr2.txt" 2>&1; dr2=$?; [ "$dr2" = 17 ] || break; done
grep -E 'E195-DRY|STOP' "$S/dr2.txt" | cut -c1-240 | head -n 3
ok "$dr1.$dr2.$(has 'E195-DRY OK: 288 device calls' "$S/dr2.txt")" "0.0.1" "DR the dry pass on the stand-in box: 0, E195-DRY OK"

step "RS, SF, LA. the rest rule and a left stop file through step 9; then the launch"
slog "$BOXT/build/e193/T1794780000" "E193 sitting B" 10
RB_OUT="$S/out-p" bash "$R/s11_a3_session_e195.sh" FULL > "$S/rs.txt" 2>&1; rs=$?
slog "$BOXT/build/e193/T1794780000" "E193 sitting B" 45
echo "left from before (desk test)" > "$ER/build/x09-STOP"
RB_OUT="$S/out-p" bash "$R/s11_a3_session_e195.sh" FULL > "$S/sf.txt" 2>&1; sf=$?
mv "$ER/build/x09-STOP" "$S/x09-STOP.sf"
# the session runs the stand-in host: the built host swapped for it, and the build record's host line rewritten (the session checks it)
RHOST=$ER/build/x09mem/host/x09mem_host; cp -p "$RHOST" "$S/real-host.keep"
printf '#!/bin/bash\n# stand-in host (E195 runbook desk test): it prints X09MEM {json} lines; it launches %s\nexec /usr/bin/python3 -I -B %s host "$@"\n' "$ER/build/x09mem/kernel/x09mem.elf" "$FK" > "$RHOST"
sedi -e "s#^host [0-9a-f]*\$#host $(sha256sum "$RHOST" | cut -d' ' -f1)#" "$ER/build/x09mem-built.txt"
RB_OUT="$S/out-p" bash "$R/s11_a3_session_e195.sh" FULL > "$S/la.txt" 2>&1; la=$?
grep -E 'LAUNCHED|rest:|REFUSED|STOP' "$S/rs.txt" "$S/sf.txt" "$S/la.txt" | cut -c1-260
ok "$rs.$(has 'REFUSED: 10 minutes since E193' "$S/rs.txt").$sf.$(has 'x09-STOP exists in E195' "$S/sf.txt").$la.$(has 'LAUNCHED e195 T0' "$S/la.txt")" "10.1.10.1.0.1" \
  "RS a session 10 min ago: refused (10); SF a stop file left: refused (10); LA launched"
T0=$(cat "$S/out-p/e195-T0.txt" 2>/dev/null)
RB_WAIT_LOOP_S=3 RB_OUT="$S/out-p" bash "$R/s20_wait_e195.sh" > "$S/w1r.txt" 2>&1; w1r=$?
ok "$w1r.$(has 'RUN-RUNNING e195' "$S/w1r.txt")" "17.1" "W1r step 10 while the real session_e195.sh runs: RUN-RUNNING (17)"
lim=$(( $(date +%s) + 1500 ))     # the stop by hand once pass 911 has ended (bounded)
until grep -q 'p911 rc=' "$BOXT/build/e195/T$T0/session.log" 2>/dev/null || grep -q 'session end' "$BOXT/build/e195/T$T0/session.log" 2>/dev/null || [ "$(date +%s)" -ge "$lim" ]; do sleep 3; done
echo "the operator, after p911 (desk test)" > "$ER/build/x09-STOP"
lim=$(( $(date +%s) + 300 ))
until grep -q "session end (T0 $T0)" "$BOXT/build/e195/T$T0/session.log" 2>/dev/null || [ "$(date +%s)" -ge "$lim" ]; do sleep 2; done
RB_OUT="$S/out-p" bash "$R/s20_wait_e195.sh" > "$S/w2r.txt" 2>&1; w2r=$?
grep -E 'passes complete|RUN-|MANIFEST|STOP|SESSION-RC' "$S/w2r.txt" | cut -c1-200
ok "$w2r.$(has 'RUN-ENDED e195' "$S/w2r.txt").$(has 'MANIFEST-WRITTEN' "$S/w2r.txt").$(has 'passes complete: 2 of 8' "$S/w2r.txt")" "0.1.1.1" "W2r step 10 after the stop by hand: RUN-ENDED, MANIFEST-WRITTEN, 2 passes complete"

step "WN. a decoy session_e1950.sh, and a session log with no end"
cp "$S/out-p/e195-T0.txt" "$S/t0.keep"; cp "$BOXT/build/q141k/e195.T0" "$S/boxt0.keep"
T9=$((T0 + 5)); mkdir -p "$BOXT/build/e195/T$T9"; echo "$(date '+%F %T %Z') session start (T0 $T9; E195)" > "$BOXT/build/e195/T$T9/session.log"
echo "$T9" > "$S/out-p/e195-T0.txt"; echo "$T9" > "$BOXT/build/q141k/e195.T0"
printf '#!/bin/bash\nsleep 60\n' > "$S/session_e1950.sh"; bash "$S/session_e1950.sh" &
DEC=$!
RB_OUT="$S/out-p" bash "$R/s20_wait_e195.sh" > "$S/wn.txt" 2>&1; wn=$?
kill "$DEC" 2>/dev/null; wait "$DEC" 2>/dev/null
mv "$BOXT/build/e195/T$T9" "$S/wn-T$T9.moved"; cp "$S/t0.keep" "$S/out-p/e195-T0.txt"; cp "$S/boxt0.keep" "$BOXT/build/q141k/e195.T0"
ok "$wn.$(has 'RUN-GONE e195' "$S/wn.txt")" "14.1" "WN a decoy named session_e1950.sh: RUN-GONE (14), the pattern matches the real name only"

step "SD. a second launch the same day after the session that opened the card"
mv "$ER/build/x09-STOP" "$S/x09-STOP.la"
RB_OUT="$S/out-p" bash "$R/s11_a3_session_e195.sh" FULL > "$S/sd.txt" 2>&1; sdr=$?
ok "$sdr.$(has 'no second E195 session today' "$S/sd.txt")" "10.1" "SD a second launch after a session that opened the card: refused (10)"

step "C. step 11, the collection"
id -un > "$S/out-p/box-login-aifoundry3.txt"
RB_OUT="$S/out-p" bash "$R/s22_collect_e195.sh" > "$S/c.txt" 2>&1; c=$?
grep -E 'COLLECTED|STOP|COPY|ASSEMBLED|SCRUB' "$S/c.txt" | cut -c1-260
DD=$S/out-p/e195-out/$TODAY-e195-x09-dramtoggle-aifoundry3
ok "$c.$(has 'COPY EXACT' "$S/c.txt").$([ -f "$DD/passes/p911/telemetry.jsonl.gz" ] && [ -f "$DD/facts-e195.json" ] && echo 1).$( (cd "$DD" && sha256sum -c --quiet SHA256SUMS) > /dev/null 2>&1 && echo 1).$(grep -rlI "$(id -un)" "$DD" --exclude=runs.jsonl --exclude=marks.jsonl | wc -l)" \
  "0.1.1.1.0" "C COPY EXACT, the gates, the data directory and its SHA256SUMS, our login masked: 0"

step "R. the data directory committed (in the scratch repository), then step 13"
mkdir -p "$T/docs/reports/data"; cp -r "$DD" "$T/docs/reports/data/"
$G add --sparse -f "docs/reports/data/$TODAY-e195-x09-dramtoggle-aifoundry3"; $G commit -q -m "desk test: the stand-in session's data directory"
RB_OUT="$S/out-p" bash "$R/s24_reduce_e195.sh" "docs/reports/data/$TODAY-e195-x09-dramtoggle-aifoundry3" > "$S/r.txt" 2>&1; rr=$?
grep -E 'reduced|STOP|LEFTOVER-E195:' "$S/r.txt" "$S/out-p/leftover-e195.txt" 2>/dev/null | cut -c1-300
ok "$rr.$([ -s "$S/out-p/x09-e195.json" ] && echo 1).$(has 'LEFTOVER-E195: headline passes \[911\]' "$S/out-p/leftover-e195.txt").$(grep -c '"band_score"' "$S/out-p/x09-e195.json")" "0.1.1.0" \
  "R the registered reducer on the committed main passes (--warmup 910, never --forecast), then the leftover checker: 0"
$G reset -q --hard HEAD~1

step "C2. one byte of a box file changed after the session's manifest"
mv "$S/out-p/e195-raw" "$S/raw.c1"; mv "$S/out-p/e195-out" "$S/out.c1"
echo "x" >> "$BOXT/build/e195/T$T0/smoke-gate.txt"
RB_OUT="$S/out-p" bash "$R/s22_collect_e195.sh" > "$S/c2.txt" 2>&1; c2=$?
ok "$c2.$(has 'COPY NOT EXACT' "$S/c2.txt")" "16.1" "C2 the session's own manifest no longer holds: COPY NOT EXACT, 16"

step "GS. a gate stop collected as its record, from a new RB_OUT"
win "$S/out-g"; id -un > "$S/out-g/box-login-aifoundry3.txt"
echo "lock:etsoc-shire0.lock <another-user> 4244 00:03 someone-elses-block.sh" > "$S/sd/foreign"   # E178's scrubbed form: the scrub check passes it
TG=$(date +%s); echo "$TG" > "$BOXT/build/q141k/e195.T0"; echo "$TG" > "$S/out-g/e195-T0.txt"
( cd "$BOXT" && HOME="$B/aifoundry3" PATH="$BB:$PATH" E195_FAKE_STATE="$S/sd" E195_T0=$TG X9_LATEST_START=@$((TG + 600)) X9_DEADLINE=@$((TG + 3600)) \
  E195_HARNESS_SHA256=$(sha256sum "$ER/$E/harness-e195.json" | cut -d' ' -f1) bash "$ER/$E/session_e195.sh" > "build/e195/launch-T$TG.out" 2>&1 )
rm -f "$S/sd/foreign"
RB_OUT="$S/out-g" bash "$R/s20_wait_e195.sh" > "$S/gs1.txt" 2>&1; gs1=$?
RB_OUT="$S/out-g" bash "$R/s22_collect_e195.sh" > "$S/gs2.txt" 2>&1; gs2=$?
grep -E 'GATE|ASSEMBLED|COLLECTED|STOP' "$S/gs1.txt" "$S/gs2.txt" | cut -c1-240
ok "$gs1.$(has 'GATE-STOPPED e195' "$S/gs1.txt").$gs2.$(has 'ASSEMBLED gate-stops/' "$S/gs2.txt").$([ -d "$S/out-g/e195-out/gate-stops/$TODAY-e195-x09-dramtoggle-T$TG-aifoundry3" ] && echo 1)" "16.1.0.1.1" \
  "GS step 10: GATE-STOPPED (16); step 11: its gate stop's record under gate-stops/, never a data directory"
cp "$S/real-host.keep" "$RHOST"

step "Z"
left=$(ls /proc | grep -E '^[0-9]+$' | while read -r p; do tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | grep -E 'fake_card_e195|session_e195|block_e195|runitems_e195|watch_x09' | grep -v grep; done | head -n 3)
ok "$([ -z "$left" ] && echo 1)" "1" "Z no process of this test left ($left)"

step "AUDIT-RB the runbook's dry branches (rb/dry-branches-rb-e195.tsv) against the files, with this run's results"
/usr/bin/python3 -I -B "$SRC/$E/rb/drybranches_rb_e195.py" --check "$S/ok-results.txt" > "$S/audit-rb.txt" 2>&1; ar=$?
cut -c1-400 "$S/audit-rb.txt"
ok "$ar.$(has '^AUDIT-RB-E195 OK' "$S/audit-rb.txt")" "0.1" "AUDIT-RB every line of the runbook that reads RB_DRY has a row whose cases passed in this run"
echo; echo "SELFTEST-RB-E195 $npass of $ncase $([ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
