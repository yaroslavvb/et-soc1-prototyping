#!/usr/bin/env bash
# E198 (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): the desk test of E198's runbook with a FAKE ssh and rsync on a
# STAND-IN aifoundry1, E193's runbook desk test's form (rb/selftest_rb_e193.sh, unchanged beside it). It re-runs itself in a sandbox
# (bubblewrap, inside W/nodev.sh) whose /dev holds /dev/null bound at /dev/et0_ops, /dev/et0_mgmt, /dev/et1_ops and /dev/et1_mgmt (the
# two-card box's character devices; opening one opens /dev/null), a scratch /run/lock, a private PID namespace and a stand-in /etc/passwd
# naming our uid 'boxuser'. Its scratch repository is a shared, sparse clone of the lab clone this test runs from, at E198's registration
# commit, with every kit file committed on top as one stand-in kit commit; two lines change in that scratch only, each stated: step 2's
# KITPIN (the kit list made here, by the real list's rule) and harness_e198.py's pin for the box's reader (the stand-in reader's sha256,
# so that the box's tree check reads the stand-in as the box's reader). The stand-in box is aifoundry1's home under the scratch (its tree
# ~/nekko); the stand-in ssh serves it with `bash -s` (its host name aifoundry1 from a stand-in `hostname` on the box's PATH; its boot time
# from a stand-in `uptime -s`) and refuses any other host or command; the stand-in rsync rewrites aifoundry1: paths onto it; the box's
# device tools are fake_card_e198.py's (the reader through the box's own copy of E191's guard, et-who). THE BOX'S BUILD IS REAL: step 6 runs
# build_e198.sh there (cmake with this desk's /opt/et, whose riscv gcc reads "() 15.1.0" as aifoundry1's does; THE KERNEL GATE on E193's
# registered .text, the bodies check, the host's refusals, the listing SAME x3). No lab box is reached; no simulator; no real card.
#   A    the dry listing on the scratch: every step 0, no call to the stand-ins
#   W1-W6  THE WINDOW FROM G: G 09:00:00 gives last start 10:30, last end 12:30 (0); G 20:29:00 gives last end 23:59 (0); G 20:29:30
#        (last end 00:00 the next day) and G 21:00:00 refused (16); step 2 with no window (10); step 9 for B with A's window (10)
#   P1   step 2 on the scratch: 0 (the lists at their counts and bytes, HISTORY OK, the registration and the kit found by their content);
#   SE   THE SEALED CARD-1 NOTE: a dated note committed at tools/claims-v3/sealed-card1/e198-freeze-lines.md: step 2 still 0, the note
#        reported by its sha256;  D1  an E198 datum before sitting A (sitting A's data path committed): 16
#   SC   the committed note changed by a later commit: step 2 refuses (16), the history check naming the change and its commit (added
#        before the land, Mon 16 Nov 2026, Q191 lane fix-e198: verify-e198's finding 2)
#   LK   the look on both cards: FREE (0), the box's login written;  LKH  another login's card-0 holder: HELD (17);  RG  the box booted
#        after E82's firmware read: the reboot gate (16)
#   SY   step 5: the sync into E198's root and the tree's E191 guard: 0, HARNESS OK and TREE OK on the box
#   BU   step 6 start, then wait: THE REAL BUILD on the stand-in box: X04-BUILT, RB_OUT/e198-built.txt
#   R0   STEP 7 BEFORE THE REST OPENS: an E198 session on the box ended 10 minutes ago: 17, and no config read was made;  R1  the same
#        session 45 minutes back: 0 (TDP 65 W / 65 C / 600 MHz, minion_mv 499, /dev/et1_mgmt and device ID 1, from the stand-in reader
#        with the real committed card-1 stderr)
#   DP   step 8, the dry pass: the session itself with DRY=1 on the box (its private /dev listed): both listings SAME (0)
#   L4   THE WAIT FINDS THE SESSION BY ITS REAL SCRIPT NAME: step 9 launches the REAL session_e198.sh (its first holder check held 28 s by
#        the stand-in et-who, inside the session's 30 s bound); step 10 with a 4 s loop reads RUN-RUNNING (17); after the session's own gate stop (identity (a): a config
#        at TDP 0 W), step 10 reads GATE-STOPPED (16);  L4N  a process named session-e198.sh (not the real name) and no session end:
#        RUN-GONE (14)
#   C    step 11 on the gate-stopped session: its gate stop's record under docs/reports/gate-stops/ (k6's desk-path gate after the scrub)
#   BA   step 9 for sitting B with no sitting A whose main run started (its dry pass faked as done): 10;  RS  step 9 for sitting A right
#        after L4's session: THE REST RULE refuses (10), nothing launched
#   BW, BD  step 9 for sitting B after a stand-in sitting A (50 minutes back) whose main run started and ended with a watch hit
#        (holderd/WATCH-STOP), or that stopped on a device process that did not finish ("tell the lab admin"): 10 each, nothing launched
#        (added before the land, fix-e198: verify-e198's finding 3)
#   CR   step 13 on the real-path test's collected sitting (when its scratch is given): the data committed in the scratch, the registered
#        reducer and E193's checker (0), then the transport scorer (0)
#   Z    no process of this test left on the stand-in box
#   bash slot.sh bash nodev.sh bash tools/claims-v3/e198/rb/selftest_rb_e198.sh <scratch dir> [<the real-path test's scratch dir>] > <log>
#   (prints SELFTEST-RB-E198 <n> of <m> PASS or FAIL). Run it so that it ends before midnight Pacific or starts after it (a window
#   serves its own day); past 20:29 the cases after W take a stand-in window in step 1's own form (step 1 refuses that G, W3 and W4).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
SELF=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")
if [ "${E198_RB_INNER:-}" != 1 ]; then
  S=${1:?a scratch directory outside the repository}
  case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
  for p in /dev/et*; do [ -c "$p" ] && { echo "REFUSED: $p is a character device here: run this test inside the no-device sandbox"; exit 2; }; done
  mkdir -p "$S" && [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
  S=$(cd "$S" && pwd)
  mkdir -p "$S/runlock"
  awk -F: -v u="$(id -u)" '$3 != u' /etc/passwd > "$S/accounts"
  echo "boxuser:x:$(id -u):$(id -g):stand-in:$S/box/aifoundry1:/bin/bash" >> "$S/accounts"
  exec /usr/bin/bwrap --dev-bind / / --dev /dev --dev-bind /dev/null /dev/et0_ops --dev-bind /dev/null /dev/et0_mgmt \
    --dev-bind /dev/null /dev/et1_ops --dev-bind /dev/null /dev/et1_mgmt --bind "$S/runlock" /run/lock --bind "$S/accounts" /etc/passwd \
    --proc /proc --unshare-pid --die-with-parent -- env E198_RB_INNER=1 bash "$SELF" "$S" "${2:-}"
fi
S=$1; RP=${2:-}
T=$S/tree; BOXH=$S/box/aifoundry1; TREE=$BOXH/nekko; BIN=$S/bin; BB=$S/boxbin; ST=$S/box-state
mkdir -p "$TREE/build" "$BIN" "$BB" "$ST"
E=tools/claims-v3/e198
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aqE -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP\|SAY\|\] ' "$1" | tail -n 2 | cut -c1-260; }
echo "E198 runbook desk test, $(date '+%F %T %Z'), $(/usr/bin/python3 --version 2>&1), $(cmake --version | head -n 1), $(/usr/bin/bwrap --version); in its sandbox (two-card stand-in nodes, pid namespace)"
[ "$(TZ=America/Los_Angeles date +%H%M)" -lt 2345 ] || { echo "REFUSED: start before 23:45 Pacific or after midnight (a window serves its own day)"; exit 2; }
# ---- the scratch repository
REG=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/E198.md | tail -n 1)
[ -n "$REG" ] || { echo "no registration commit in the lab clone's history"; exit 2; }
git clone -q --shared --no-checkout "$SRC" "$T" || exit 2
G="git -C $T -c user.name=e198-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ || exit 2
$G checkout -q -B main "$REG" || exit 2
$G branch -q -f e198-desktest-registration "$REG" && $G branch -q --set-upstream-to=e198-desktest-registration || exit 2
( cd "$SRC" && git show "$REG" --name-only --format= -- $E ) > "$S/reg-files.txt"
( cd "$SRC" && git ls-files --cached --others --exclude-standard -- $E | grep -v -x -F -f "$S/reg-files.txt" ) | sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
[ -f "$T/$E/session_e198.sh" ] && [ -f "$T/$E/rb/s03_desk_e198.sh" ] || { echo "the kit's files did not reach the scratch tree"; exit 2; }
mkdir -p "$T/$E/logs"
for spec in "desktest-realpath-e198.txt DESKTEST-REALPATH-E198 0 of 0 PASS" "realbytes-e198.txt REALBYTES-E198 0 of 0 PASS" \
            "selftest-rb-e198.txt SELFTEST-RB-E198 0 of 0 PASS" "ident-selfcheck-e198.txt E198-IDENT SELF-CHECK PASS: stand-in" \
            "dry-listing-e198.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e198.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}; printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"
done
FAKE=$T/$E/fake_card_e198.py
mkdir -p "$TREE/tools/claims-v3/e191" "$TREE/build/ettelem"
cp -p "$T/tools/claims-v3/e191/ettelem_guard_e191.sh" "$TREE/tools/claims-v3/e191/ettelem_guard_e191.sh"
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s ettelem "$@"\n' "$FAKE" > "$TREE/build/ettelem/ettelem"; chmod +x "$TREE/build/ettelem/ettelem"
RS=$(sha256sum "$TREE/build/ettelem/ettelem" | cut -d' ' -f1)
sed -i "s#\"build/ettelem/ettelem\": \"8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325\"#\"build/ettelem/ettelem\": \"$RS\"#" "$T/$E/harness_e198.py"
grep -q "$RS" "$T/$E/harness_e198.py" || { echo "the scratch harness's reader pin was not set"; exit 2; }
( cd "$T" && /usr/bin/python3 -I -B $E/harness_e198.py --make > /dev/null )
rm -f "$T/$E/SHA256SUMS-e198-kit"
( cd "$T" && find $E -type f ! -name 'SHA256SUMS-e198-kit' ! -path "$E/rb/s03_desk_e198.sh" ! -name '*.pyc' | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) |
  grep -v -F -f "$S/reg-files.txt" > "$S/kit-standin.txt"
KITN=$(grep -c . "$S/kit-standin.txt"); cp "$S/kit-standin.txt" "$T/$E/SHA256SUMS-e198-kit"; KITH=$(sha256sum "$S/kit-standin.txt" | cut -d' ' -f1)
sed -i -e "s#^KITPIN=$E/SHA256SUMS-e198-kit:[^ ]*#KITPIN=$E/SHA256SUMS-e198-kit:$KITN:$KITH:top#" "$T/$E/rb/s03_desk_e198.sh"
grep -q "^KITPIN=$E/SHA256SUMS-e198-kit:$KITN:$KITH:top" "$T/$E/rb/s03_desk_e198.sh" || { echo "the scratch step 2's KITPIN was not set"; exit 2; }
$G add -A $E && $G commit -q -m "E198 runbook desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; exit 2; }
echo "scratch repository: at the registration ${REG:0:12}, the kit as one stand-in commit $($G rev-parse --short=12 HEAD); the stand-in reader's pin ${RS:0:16} in the scratch's harness; KITPIN $KITN entries"
# ---- the stand-ins
REAL_RSYNC=$(command -v rsync); REAL_PGREP=$(command -v pgrep)
RT=$S/runtime-line.bin; CE=$S/config-card1.err
git -C "$SRC" show 1a4bc1e3:docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1/session/smoke/copy-64m-random/stdout.txt | grep -a -o 'Opening device 1' | head -n 1 > "$RT"
git -C "$SRC" show 7156ac15:docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/session/config-start.err > "$CE"
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry1) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'true' and 'bash -s', not '\$cmd'" >&2; exit 97; }
cd "$BOXH" || exit 1
exec /usr/bin/env HOME="$BOXH" PATH="$BB:/usr/bin:/bin" E198_FAKE_STATE="$ST" E198_FAKE_RTFILE="$RT" E198_FAKE_CFGERR="$CE" USER=boxuser LOGNAME=boxuser \${RB_WAIT_LOOP_S:+RB_WAIT_LOOP_S=\$RB_WAIT_LOOP_S} bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry1) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$BOXH/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s etwho "$@"\n' "$FAKE" > "$BB/et-who"
printf '#!/bin/sh\necho "et-lab-manifest: a desk-test stand-in (no sysfs read)"\n' > "$BB/et-lab-manifest"
printf '#!/bin/sh\necho aifoundry1\n' > "$BB/hostname"
printf '#!/bin/sh\nif [ "${1:-}" = -s ]; then if [ -e "%s/booted-late" ]; then echo "2026-11-13 16:53:28"; else echo "2026-10-26 15:02:04"; fi; else exec /usr/bin/uptime "$@"; fi\n' "$ST" > "$BB/uptime"
cat > "$BB/pgrep" <<EOF
#!/bin/bash
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
[ "\$*" = "-eo uid=,pid=,comm=" ] || exec /usr/bin/ps "\$@"
/usr/bin/ps -eo uid=,pid=,comm= | while read -r u p c; do d=\$(readlink "/proc/\$p/cwd" 2>/dev/null) || continue; case "\$d/" in "$BOXH"/*) echo "\$u \$p \$c" ;; esac; done
EOF_PS
for n in ssh rsync scp sudo; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$BB/$n"; done
chmod +x "$BIN"/* "$BB"/*
: > "$S/lock.txt"; : > "$S/calls.log"; : > "$S/gitlock"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt"
R=$T/$E/rb
TODAY=$(TZ=America/Los_Angeles date +%F)
NOWG=$(TZ=America/Los_Angeles date -d '-1 min' +%H:%M:%S)
cd "$T" || exit 2
win() {  # win <RB_OUT> <A|B> [<G>]: step 1 itself; past 20:29 Pacific (step 1 refuses a G whose last end leaves its day, by design: W3,
  #        W4) the cases after W get a STAND-IN window.env in step 1's own form (G = a minute ago), said so in this log
  mkdir -p "$1"; RB_OUT="$1" bash "$R/s02_window_e198.sh" "$2" "$TODAY" "${3:-$NOWG}" > "$1/win.txt" 2>&1; local r=$?
  if [ "$r" -eq 16 ] && [ -z "${3:-}" ]; then
    local g ls le; g=$(date -d '-1 min' +%s); ls=$(( (g + 5400 + 59) / 60 * 60 )); le=$(( (g + 12600 + 59) / 60 * 60 ))
    { echo "# a STAND-IN window for the desk test (G past 20:29 Pacific)"; echo "RB_DAY=$TODAY"; echo "RB_G=$NOWG"; echo "RB_G_EPOCH=$g"
      echo "RB_LAST_START='$(date -d @$ls '+%F %H:%M %Z')'"; echo "RB_LAST_END='$(date -d @$le '+%F %H:%M %Z')'"
      echo "RB_LAST_START_EPOCH=$ls"; echo "RB_LAST_END_EPOCH=$le"; echo "RB_LAST_START_HM=$(date -d @$ls +%H:%M)"; echo "RB_LAST_END_HM=$(date -d @$le +%H:%M)"
      echo "RB_PLAN=e198"; echo "RB_SITTING=$2"; echo "RB_GO_EPOCH=$(date +%s)"; } > "$1/window.env"
    echo "   (a stand-in window in $(basename "$1"): step 1 refused G $NOWG, past 20:29 Pacific)"; r=0
  fi
  return "$r"
}

step "A. the dry listing on the scratch"
bash "$R/list_steps_e198.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
tail -n 1 "$S/dry-listing.txt"
ok "$rc/$(grep -c . "$S/calls.log")" "0/0" "A every step 0, no call to the stand-ins"

step "W1-W6. THE WINDOW FROM G"
win "$S/out-w1" A 09:00:00; w1=$?; . "$S/out-w1/window.env"; w1v="$RB_LAST_START_HM-$RB_LAST_END_HM"
win "$S/out-w2" A 20:29:00; w2=$?; . "$S/out-w2/window.env"; w2v="$RB_LAST_END_HM"
win "$S/out-w3" A 20:29:30; w3=$?
win "$S/out-w4" A 21:00:00; w4=$?
RB_OUT="$S/out-k" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e198.sh" > "$S/w5.txt" 2>&1; w5=$?
win "$S/out-w6" A
RB_OUT="$S/out-w6" bash "$R/s11_a1_session_e198.sh" B > "$S/w6.txt" 2>&1; w6=$?
ok "$w1/$w1v/$w2/$w2v/$w3/$w4/$w5/$(has 'no window in RB_OUT' "$S/w5.txt")/$w6/$(has "sitting A's, not sitting B's" "$S/w6.txt")" \
  "0/10:30-12:30/0/23:59/16/16/10/1/10/1" "W1-W6 G 09:00:00 -> 10:30/12:30; 20:29:00 -> 23:59; 20:29:30 and 21:00:00 refused; no window, a wrong sitting refused"

step "P1, SE, D1. step 2 on the scratch: the lists, the history, the sealed note, an E198 datum"
win "$S/out-p" A
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e198.sh" > "$S/p1.txt" 2>&1; p1=$?
stopline "$S/p1.txt"
mkdir -p "$T/tools/claims-v3/sealed-card1"
printf '# E198: the model session'"'"'s sealed card-1 forecast, a dated note (desk-test stand-in)\n\nsha256 %s\n' "$(printf stand-in | sha256sum | cut -d' ' -f1)" > "$T/tools/claims-v3/sealed-card1/e198-freeze-lines.md"
$G add tools/claims-v3/sealed-card1 && $G commit -q -m "stand-in: the sealed card-1 note" || exit 2
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e198.sh" > "$S/se.txt" 2>&1; se=$?
D=docs/reports/data/$TODAY-e198-x04-clock-sitting-a-aifoundry1-c1
mkdir -p "$T/$D"; echo "stand-in E198 datum" > "$T/$D/README.md"
$G sparse-checkout add "/$D/" && $G add -f "$D/README.md" && $G commit -q -m "stand-in: an E198 datum" || exit 2
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e198.sh" > "$S/d1.txt" 2>&1; d1=$?
$G reset -q --hard HEAD~1 || exit 2
ok "$p1/$se/$(has 'the sealed card-1 note: [0-9a-f]{16}\.\.\. committed' "$S/out-p/runbook.log")/$d1/$(has 'e198-datum\(1 paths before sitting A\)' "$S/d1.txt")" \
  "0/0/1/16/1" "P1 step 2 holds; SE the sealed note accepted and reported; D1 an E198 datum before sitting A: 16"

step "SC. the committed sealed note changed by a later commit (added before the land, fix-e198: verify-e198's finding 2)"
printf 'a line added after the commit (desk-test stand-in)\n' >> "$T/tools/claims-v3/sealed-card1/e198-freeze-lines.md"
$G add tools/claims-v3/sealed-card1 && $G commit -q -m "stand-in: the sealed card-1 note changed" || exit 2
win "$S/out-sc" A
RB_OUT="$S/out-sc" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e198.sh" > "$S/sc.txt" 2>&1; sc=$?
stopline "$S/sc.txt"
sch=$(cat "$S/out-sc/calls/"* 2>/dev/null | grep -acE 'HISTORY FAIL: .*changed or removed by a commit since f74c81e3: M tools/claims-v3/sealed-card1/e198-freeze-lines.md')
$G reset -q --hard HEAD~1 || exit 2
ok "$sc/$(has 'the desk check failed:.*history' "$S/sc.txt")/$sch" "16/1/1" \
  "SC a committed sealed note changed by a later commit: step 2 refuses (16); the history check names the change (M) and its commit"

step "LK, LKH, RG. the look on both cards"
mkdir -p "$S/out-a"; win "$S/out-a" A
RB_OUT="$S/out-a" bash "$R/s05_look_e198.sh" > "$S/lk.txt" 2>&1; lk=$?
printf '/dev/et0_ops   otheruser          777       01:00 someone-elses_host\n' > "$ST/foreign"
RB_OUT="$S/out-lkh" bash "$R/s05_look_e198.sh" > "$S/lkh.txt" 2>&1; lkh=$?
rm -f "$ST/foreign"; touch "$ST/booted-late"
RB_OUT="$S/out-rg" bash "$R/s05_look_e198.sh" > "$S/rg.txt" 2>&1; rg=$?
rm -f "$ST/booted-late"
ok "$lk/$([ -s "$S/out-a/box-login-aifoundry1.txt" ] && echo 1)/$lkh/$(has "another login's 1" "$S/lkh.txt")/$rg/$(has 'booted after E82' "$S/rg.txt")" \
  "0/1/17/1/16/1" "LK FREE on both cards; LKH a card-0 holder of another login: HELD; RG booted after E82's read: the reboot gate"

step "SY. step 5: the sync"
RB_OUT="$S/out-a" bash "$R/s07_a1_sync_e198.sh" > "$S/sy.txt" 2>&1; sy=$?
stopline "$S/sy.txt"
ok "$sy/$(has 'HARNESS OK and TREE OK on the box' "$S/sy.txt")" "0/1" "SY synced into E198's root and the tree's E191 guard; HARNESS OK and TREE OK on the box"

step "BU. step 6: THE REAL BUILD on the stand-in box"
RB_OUT="$S/out-a" bash "$R/s08_a1_build_e198.sh" start > "$S/bu1.txt" 2>&1; b1=$?
bw=17; k=0
while [ "$bw" -eq 17 ] && [ "$k" -lt 40 ]; do RB_OUT="$S/out-a" bash "$R/s08_a1_build_e198.sh" wait > "$S/bu2.txt" 2>&1; bw=$?; k=$((k + 1)); done
grep -E '^    (ELF|BODIES|HOST|LISTING|X04|READER|ETDEVICES)' "$S/bu2.txt" | cut -c1-200
ok "$b1/$bw/$(has '^X04-BUILT rc=0' "$S/out-a/e198-built.txt")" "0/0/1" "BU the real build: X04-BUILT (the kernel gate, the bodies, the refusals, the listing SAME x3)"

step "R0, R1. STEP 7 BEFORE AND AFTER THE REST OPENS"
mkdir -p "$TREE/build/e198/T1794000000"
L=$TREE/build/e198/T1794000000/session.log
mk() { local a; a=$(date -d "-$1 min" '+%Y-%m-%d %H:%M:%S %Z'); printf '%s session start (T0 1794000000 = stand-in; E198 sitting A, blocks S,D,W,T, cap 60 card-minutes; kit-e198)\n%s start config read (inside the private /dev): IDENT-A OK\n%s session end (T0 1794000000)\n' "$a" "$a" "$a" > "$L"; touch -d "-$1 min" "$L"; }
mk 10; c0=$(grep -c 'ettelem config' "$ST/calls.log" 2>/dev/null)
RB_OUT="$S/out-a" bash "$R/s09_a1_reads_e198.sh" > "$S/r0.txt" 2>&1; r0=$?
c1=$(grep -c 'ettelem config' "$ST/calls.log" 2>/dev/null)
mk 45
RB_OUT="$S/out-a" bash "$R/s09_a1_reads_e198.sh" > "$S/r1.txt" 2>&1; r1=$?
stopline "$S/r1.txt"
ok "$r0/$(has 'THE REST RULE: the 40-minute rest' "$S/r0.txt")/$((c1 - c0))/$r1/$(has 'minion_mv 499, identity /dev/et1_mgmt and device ID 1' "$S/r1.txt")" "17/1/0/0/1" \
  "R0 the rest not open: 17, no config read; R1 45 minutes back: card 1's config and identity read"

step "DP. step 8: the dry pass on the box"
RB_OUT="$S/out-a" bash "$R/s10_a1_dry_e198.sh" start > "$S/dp1.txt" 2>&1; d1=$?
dw=17; k=0
while [ "$dw" -eq 17 ] && [ "$k" -lt 20 ]; do RB_OUT="$S/out-a" bash "$R/s10_a1_dry_e198.sh" wait > "$S/dp2.txt" 2>&1; dw=$?; k=$((k + 1)); done
grep -a 'E198-DRY\|LISTING' "$S/dp2.txt" | cut -c1-200
ok "$d1/$dw/$(has 'E198-DRY sitting A rc=0 smoke=0 main=0' "$S/dp2.txt")" "0/0/1" "DP the dry pass: the session with DRY=1 on the box, both listings SAME"

step "BA. step 9 for sitting B with no sitting A whose main run started"
mkdir -p "$S/out-b"; win "$S/out-b" B
mkdir -p "$TREE/build/q141k/jobs"; echo 0 > "$TREE/build/q141k/jobs/a1-dry-e198-B.rc"     # its dry pass, faked as ended rc 0 today
RB_OUT="$S/out-b" bash "$R/s08_a1_build_e198.sh" wait > "$S/ba-built.txt" 2>&1        # step 6's wait from B's RB_OUT: the day's build
RB_OUT="$S/out-b" bash "$R/s11_a1_session_e198.sh" B > "$S/ba.txt" 2>&1; ba=$?
rm -f "$TREE/build/q141k/jobs/a1-dry-e198-B.rc"
ok "$ba/$(has 'B never runs before A' "$S/ba.txt")" "10/1" "BA sitting B before any sitting A: 10, nothing launched"

step "BW, BD. step 9 for B after a sitting A with a watch hit, or with a device process that did not finish (added before the land, fix-e198: verify-e198's finding 3)"
sa() {  # sa <T0> <the main run's end line>: a stand-in E198 sitting A on the box, 50 minutes back, whose main run started and ended
  local d=$TREE/build/e198/T$1 a; a=$(date -d '-50 min' '+%Y-%m-%d %H:%M:%S %Z'); mkdir -p "$d/holderd" "$d/x04"
  printf '%s session start (T0 %s = stand-in; E198 sitting A, blocks S,D,W,T, cap 60 card-minutes; kit-e198)\n%s main run start: run_x04.py (stand-in)\n%s %s\n%s session end (T0 %s)\n' \
    "$a" "$1" "$a" "$a" "$2" "$a" "$1" > "$d/session.log"
}
echo 0 > "$TREE/build/q141k/jobs/a1-dry-e198-B.rc"     # its dry pass, faked as ended rc 0 today (as BA)
sa 1794000100 "main run end: runner rc 0, every pass (no stop: done)"
echo "WATCH-HIT: process 4242 (stand-in) of this sitting holds /dev/et0_mgmt, not card 1's node(s) only" > "$TREE/build/e198/T1794000100/holderd/WATCH-STOP"
find "$TREE/build/e198/T1794000100" -exec touch -d '-50 min' {} +
RB_OUT="$S/out-b" bash "$R/s11_a1_session_e198.sh" B > "$S/bw.txt" 2>&1; bw=$?
stopline "$S/bw.txt"
rm -rf "${TREE:?}/build/e198/T1794000100"
sa 1794000200 "main run stopped: runner rc 1; stop: spin2: device process exit 1 (a launch that did not finish: tell the lab admin); the passes done stand (E198.md 13)"
echo "spin2: device process exit 1 (a launch that did not finish: tell the lab admin)" > "$TREE/build/e198/T1794000200/x04/STOPPED"
find "$TREE/build/e198/T1794000200" -exec touch -d '-50 min' {} +
RB_OUT="$S/out-b" bash "$R/s11_a1_session_e198.sh" B > "$S/bd.txt" 2>&1; bd=$?
stopline "$S/bd.txt"
rm -rf "${TREE:?}/build/e198/T1794000200"
rm -f "$TREE/build/q141k/jobs/a1-dry-e198-B.rc"
ok "$bw/$(has 'REFUSED: an earlier E198 sitting had a watch hit' "$S/bw.txt")/$bd/$(has 'REFUSED: an earlier E198 sitting stopped on a device process that did not finish' "$S/bd.txt")/$(grep -c 'LAUNCHED e198-B' "$S/bw.txt" "$S/bd.txt" | awk -F: '{s += $2} END {print s}')" \
  "10/1/10/1/0" "BW a watch hit in sitting A: step 9 for B refuses (10); BD a device process that did not finish in A: 10; nothing launched"

step "L4, L4N. THE WAIT FINDS THE SESSION BY ITS REAL SCRIPT NAME"
echo 28 > "$ST/etwho-sleep"
echo '{"tdp_w": 0, "temp_threshold_c": 65, "power_state": 3, "minion_mhz": 600, "minion_mv": 499}' > "$ST/config.json"
RB_OUT="$S/out-a" bash "$R/s11_a1_session_e198.sh" A > "$S/l4.txt" 2>&1; l4=$?
stopline "$S/l4.txt"
RB_WAIT_LOOP_S=4 RB_OUT="$S/out-a" bash "$R/s20_wait_e198.sh" A > "$S/l4w1.txt" 2>&1; w1=$?
k=0; while [ "$k" -lt 60 ]; do grep -q 'session end' "$TREE"/build/e198/T"$(cat "$S/out-a/e198-A-T0.txt" 2>/dev/null)"/session.log 2>/dev/null && break; sleep 1; k=$((k + 1)); done
sleep 2
RB_WAIT_LOOP_S=4 RB_OUT="$S/out-a" bash "$R/s20_wait_e198.sh" A > "$S/l4w2.txt" 2>&1; w2=$?
rm -f "$ST/config.json"
TB=$(( $(date +%s) - 5 )); mkdir -p "$TREE/build/e198/T$TB" "$TREE/build/q141k"
echo "$(date '+%Y-%m-%d %H:%M:%S %Z') session start (T0 $TB; E198 sitting B, a stand-in with no end)" > "$TREE/build/e198/T$TB/session.log"
echo "$TB" > "$TREE/build/q141k/e198-B.T0"; echo "$TB" > "$S/out-b/e198-B-T0.txt"
cp /bin/sleep "$S/session-e198.sh"
( cd "$BOXH" && exec "$S/session-e198.sh" 30 ) &
dec=$!
RB_WAIT_LOOP_S=4 RB_OUT="$S/out-b" bash "$R/s20_wait_e198.sh" B > "$S/l4n.txt" 2>&1; wn=$?
kill "$dec" 2>/dev/null; wait "$dec" 2>/dev/null
rm -rf "${TREE:?}/build/e198/T$TB" "${TREE:?}/build/q141k/e198-B.T0"
ok "$l4/$w1/$(has 'RUN-RUNNING e198-A' "$S/l4w1.txt")/$w2/$(has 'GATE-STOPPED e198-A' "$S/l4w2.txt")/$(has 'THE IDENTITY GATE \(a\)' "$S/l4w2.txt")/$wn/$(has 'RUN-GONE e198-B' "$S/l4n.txt")" \
  "0/17/1/16/1/1/14/1" "L4 the real session found running by its real name (17), then its own gate stop read (16); L4N another name: RUN-GONE (14)"

step "C. step 11 on the gate-stopped session"
RB_OUT="$S/out-a" bash "$R/s22_collect_e198.sh" A > "$S/c.txt" 2>&1; c=$?
stopline "$S/c.txt"
ok "$c/$(has "collected the gate stop's record docs/reports/gate-stops/$TODAY-e198-x04-clock-sitting-a-T[0-9]+-aifoundry1-c1" "$S/c.txt")" "0/1" "C its gate stop's record, k6's desk-path gate clean"

step "RS. step 9 right after L4's session: THE REST RULE"
win "$S/out-rs" A
RB_OUT="$S/out-rs" bash "$R/s08_a1_build_e198.sh" wait > "$S/rs-built.txt" 2>&1      # step 6's wait from this RB_OUT: the day's build
RB_OUT="$S/out-rs" bash "$R/s11_a1_session_e198.sh" A > "$S/rs.txt" 2>&1; rs=$?
ok "$rs/$(has 'REFUSED: [0-9]+ minutes since E198' "$S/rs.txt")" "10/1" "RS the rest rule right after L4's session: 10, nothing launched"

step "CR. step 13 on the real-path test's collected sitting"
if [ -n "$RP" ] && [ -d "$RP/data-PB2" ]; then
  DB=docs/reports/data/$TODAY-e198-x04-clock-sitting-b-aifoundry1-c1
  $G sparse-checkout add "/$DB/" && mkdir -p "$T/$DB" && cp -r "$RP/data-PB2/." "$T/$DB/" && $G add -f "$DB" && $G commit -q -m "stand-in: the real-path test's sitting B" || exit 2
  RB_OUT="$S/out-b" bash "$R/s24_reduce_e198.sh" B > "$S/cr.txt" 2>&1; cr=$?
  stopline "$S/cr.txt"
  RB_OUT="$S/out-b" bash "$R/s24_reduce_e198.sh" score - "$S/out-b/x04-e198-B.json" > "$S/cs.txt" 2>&1; cs=$?
  stopline "$S/cs.txt"
  ok "$cr/$(has 'reduced sitting B' "$S/cr.txt")/$cs/$([ -s "$S/out-b/scores-e198.json" ] && echo 1)" "0/1/0/1" "CR the registered reducer and E193's checker on the committed data, then the transport scorer"
else
  echo "NOT RUN: CR (no real-path scratch with data-PB2 given)"
fi

step "Z. nothing of this test left on the stand-in box"
sleep 1
left=$("$BB/pgrep" -u "$(id -u)" -f . | wc -l)
ok "$left" "0" "Z no process left on the stand-in box"
echo
echo "SELFTEST-RB-E198 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
[ "$fail" -eq 0 ]
