#!/usr/bin/env bash
# E191's kit, dated note 2 (Q184, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12 PST, and after
# E191's first session stopped at its smoke gate by a kit defect (1a4bc1e3), before any E191 pass datum; KIT.md.dated-note-2.md): THE
# RUNBOOK DESK TEST v2, E191.md's dated amendment A1's SECOND SESSION whole on a stand-in aifoundry1, in rb/selftest_rb_e191.sh's form
# (unchanged beside it: its scratch repository with its own upstream, its fake ssh and rsync serving a stand-in ~/nekko, its stand-in
# hostname, uptime, et-who, cmake and objcopy; RB_DESKTEST=1 with the same stand-in pins). The scratch repository is a shared sparse clone
# at the commit before E191's kit, with E191's files (kit and note 2) and the FIRST SESSION'S RECORD (1a4bc1e3's directory) committed on top
# as one stand-in commit; kit note 2's two lists are made from the scratch's own files (stand-ins, as v1's kit list was) and step 2 v2's
# pins set to them; v1's kit list is the real one. No lab box is reached. Cases (verdicts stated first):
#   A2   the dry listing v2: every step 0, no call reaches the stand-ins; its command lines pass note 1's item 4 (drylisting_check_e191_v2.py);
#   P1v2 step 2 v2 on the scratch repository: 0, every list at its pin (the first session's record's own SHA256SUMS among them), NEVER RAN (c)
#        in kit note 2's form (E191 data only in the first session's record, no pass in it);
#   P2v2 note 2's list one line short: 16;  H4v2 E191 data outside the first session's record in a ref: 16;  H5v2 a passes/ file inside that
#        record in a ref: 16;
#   F1   THE FIRST SESSION on the stand-in box (its window, the look, step 5 v1, step 6 start and wait: one build start, step 8 v1, and the
#        committed record's session directory placed at build/e191/T1794766494 with its T0 file): the box as the day left it;
#   S5v2 the second session, in a NEW RB_OUT: its window, the look, then step 5 v2: both harnesses read on the box (HARNESS OK and HARNESS-V2 OK);
#   B6   step 6's WAIT ALONE (A1's build rule: no start): 0, this RB_OUT's e191-built.txt "ledger,spp", the box's start count still 1 today;
#   G1   step 9 v2 with only the first session's dry job today (a1-dry-e191): 10, nothing launched;
#   D2   step 8 v2 (runner v2's dry pass on the stand-in box): 0, its line E191-DRY-V2 with note2=1 and the runtime line dropped in the smoke;
#   G2   step 9 v2 from the FIRST session's RB_OUT (its T0 a session that sent card commands): 10 by the box read, nothing launched;
#   WT0  THE NEGATIVE CONTROL: v1's step 10 (s20_wait_e191.sh) on a stand-in session_e191_v2.sh still running: RUN-GONE (14), E183's lesson;
#   WT1-WT4 step 10 v2 on it: RUN-RUNNING (17, NOTE2-SESSION yes), then ended with its manifest (0), BOUND (16), and a T0 whose log does
#        not name kit note 2 (10);
#   RS2  THE REST RULE through step 9 v2: a session of ours ended 10 minutes ago: 10 naming it, nothing launched;
#   LL2a THE LAST LAUNCH (added before the land, after the note's verifier, finding 2): RB_OUT holds no T0 but the box's last E191 launch
#        is not the first session's (a launch whose ssh call was lost): 10 by the box read, before the rest rule; nothing launched;
#   LA2  step 9 v2 launches the REAL session_e191_v2.sh and run_e191_v2.py (stopped at their box check before any device: this desk is not
#        aifoundry1); step 10 v2 reads the gate (16), the manifest and "kit note 2";
#   LL2b THE LAST LAUNCH with a T0 in RB_OUT: the box's last launch is not that T0 (a relaunch whose ssh call was lost): 10, no "relaunch:",
#        nothing launched, no e191-relaunch.txt;
#   G4a  THE RELAUNCH RULE: step 9 v2 again from that RB_OUT (its T0 opened no device): 0, "relaunch:", a new T0, e191-relaunch.txt;
#   G4b  a third launch from it: 10 before any call;
#   C3v2 step 11 v2 on the first session's T0 (its log names no kit note 2): 10, nothing written;
#   C2v2 step 11 v2 on the relaunched session: COPY-BACK EXACT, COLLECTED into ...-c1-s2, SHA256SUMS and FILES.txt, no home path or login;
#   C4v2 step 11 v2 again: ...-c1-s2 exists: 10;
#   SC0v2 step 13 v2 before the data commit: 10;  SC3v2 committed and clean: 0, scored, scores-e191.json;
#   Z    no process of this test left running.
#   bash tools/claims-v3/e191/rb/selftest_rb_e191_v2_ns.sh <scratch dir> > <log>   (prints SELFTEST-RB-E191-V2 <n> of <m> PASS or FAIL)
# On a box with a card (aifoundry2) run it ONLY inside a sandbox with no /dev/et* and an empty /run/lock: case LA2 runs the real runner.
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
T=$S/tree; B=$S/box; BIN=$S/bin; BOXT=$B/aifoundry1/nekko
mkdir -p "$BOXT" "$BIN" "$S/boxbin" "$S/standin"
E=tools/claims-v3/e191
FIRST=docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1
FT0=1794766494
main() {
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
echo "selftest_rb_e191_v2: $(date '+%F %T %Z'), processes visible: $(ls /proc | grep -c '^[0-9]')"
# ---- the scratch repository: v1's form, with note 2's files and the first session's record in the stand-in commit
KITC=$(git -C "$SRC" log --diff-filter=A --format=%H -- $E/KIT.md | tail -n 1)
if [ -n "$KITC" ]; then BASE=$(git -C "$SRC" rev-parse "$KITC^"); else BASE=$(git -C "$SRC" rev-parse HEAD); fi
git clone -q --shared --no-checkout "$SRC" "$T" || return 2
G="git -C $T -c user.name=e191-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /workloads/ /docs/reports/data/2026-11-12-q166-progs/ /docs/reports/data/2026-11-12-q166-ledger-v2/ \
  /docs/reports/data/2026-11-12-q166-counter-sparseparity/ /docs/reports/data/2026-09-23-energy-manual/ /docs/reports/data/2026-10-26-load-model/ \
  /docs/reports/data/2026-11-13-e190-large-gemm/ /docs/reports/data/2026-11-08-e184-sensor-validation/raw/aifoundry1-c1/logs/ \
  /docs/reports/data/2026-11-04-e170-blind7-card0/ /docs/reports/data/2026-11-14-e189-blind-day-aifoundry3/session/ \
  '/docs/reports/data/*-e191-*/' || return 2
$G checkout -q -B main "$BASE" || return 2
( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E; git ls-files -- $E ) | sort -u | while IFS= read -r f; do
  [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
mkdir -p "$T/$FIRST"; cp -rp "$SRC/$FIRST/." "$T/$FIRST/"
mkdir -p "$T/$E/logs"
for spec in "selftest-run-e191.txt SELFTEST-RUN-E191 0 of 0 PASS" "realpath-e191.txt REALPATH-E191 0 of 0 PASS" \
            "dry-audit-e191.txt DRY-AUDIT-E191 0 of 0 COVERED" "selftest-rest-e191.txt SELFTEST-REST-E191 0 of 0 PASS" \
            "selftest-rb-e191.txt SELFTEST-RB-E191 0 of 0 PASS" "selftest-wait-e191.txt SELFTEST-WAIT-E191 0 of 0 PASS" \
            "etdevices-e191.txt ETDEVICES-E191 0 of 0 PASS" "checks-e191.txt CHECKS-E191 0 of 0 PASS" \
            "dry-listing-e191.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e191.txt dmcmd_audit: GO (stand-in)"; do
  f=${spec%% *}; [ -f "$T/$E/logs/$f" ] || printf '%s\n' "${spec#* }" > "$T/$E/logs/$f"      # v1's logs: as committed (v1's kit list pins them)
done
for spec in "realbytes-e191.txt REALBYTES-E191 0 of 0 PASS" "realpath-e191-v2.txt REALPATH-E191-V2 0 of 0 PASS" \
            "selftest-run-e191-v2.txt SELFTEST-RUN-E191-V2 0 of 0 PASS" "dry-audit-e191-v2.txt DRY-AUDIT-E191-V2 0 of 0 COVERED" \
            "selftest-rb-e191-v2.txt SELFTEST-RB-E191-V2 0 of 0 PASS" "checks-e191-v2.txt CHECKS-E191-V2 0 of 0 PASS" \
            "dry-listing-e191-v2.txt dry listing: 0 steps listed, 0 exited non-zero, 0 box calls" "dmcmd-audit-e191-v2.txt dmcmd_audit: GO (stand-in)"; do
  printf '%s\n' "${spec#* }" > "$T/$E/logs/${spec%% *}"      # note 2's logs: stand-ins always (this test makes one of them; the lists are stand-ins too)
done
# kit note 2's two lists as stand-ins made from the scratch's own files (the real ones pin this test's own log); step 2 v2's pins set to them
( cd "$T" && git -C "$SRC" ls-tree -r --name-only 1a4bc1e3 -- $E > "$S/e191-at-record.txt"
  find $E -type f ! -name '*.pyc' ! -name 'SHA256SUMS-e191-kit-note2' ! -name 'SHA256SUMS-e191-a1' ! -path "$E/rb/s03_desk_e191_v2.sh" | LC_ALL=C sort |
    grep -v -x -F -f "$S/e191-at-record.txt" | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/note2-standin.txt"
( cd "$T" && for f in $E/E191.md.dated-amendment-A1.md $E/E191.md $E/SHA256SUMS-e191-registration $E/KIT.md.dated-note-2.md; do [ -f "$f" ] && sha256sum "$f"; done ) > "$S/a1-standin.txt"
cp "$S/note2-standin.txt" "$T/$E/SHA256SUMS-e191-kit-note2"; cp "$S/a1-standin.txt" "$T/$E/SHA256SUMS-e191-a1"
NOTELIST_COUNT=$(grep -c . "$S/note2-standin.txt"); NOTELIST_SHA=$(sha256sum "$S/note2-standin.txt" | cut -c1-64)
A1_COUNT=$(grep -c . "$S/a1-standin.txt"); A1_SHA=$(sha256sum "$S/a1-standin.txt" | cut -c1-64)
sedi -e "s#^NOTE2PIN=$E/SHA256SUMS-e191-kit-note2:[^ ]*#NOTE2PIN=$E/SHA256SUMS-e191-kit-note2:$NOTELIST_COUNT:$NOTELIST_SHA:top#" \
     -e "s#^A1PIN=$E/SHA256SUMS-e191-a1:[^ ]*#A1PIN=$E/SHA256SUMS-e191-a1:$A1_COUNT:$A1_SHA:top#" "$T/$E/rb/s03_desk_e191_v2.sh"
grep -q "^NOTE2PIN=$E/SHA256SUMS-e191-kit-note2:$NOTELIST_COUNT:$NOTELIST_SHA:top" "$T/$E/rb/s03_desk_e191_v2.sh" || { echo "the scratch step 2 v2's NOTE2PIN was not set"; return 2; }
$G add -A $E && $G add --sparse -A "$FIRST" && $G commit -q -m "E191 runbook desk test v2: the kit's and note 2's files and the first session's record (stand-in commit)" || { echo "the scratch commit failed"; return 2; }
git clone -q --bare "$T" "$S/origin.git" && $G remote set-url origin "$S/origin.git" && $G fetch -q origin && $G branch -q -u origin/main main || return 2
for r in $($G for-each-ref --format='%(refname)' refs/remotes/origin | grep -v -e '/main$' -e '/HEAD$'); do $G update-ref -d "$r"; done
echo "scratch repository: a shared sparse clone at ${BASE:0:12} (the commit before E191's kit), the stand-in commit $($G rev-parse --short=12 HEAD) (the kit, note 2's $NOTELIST_COUNT new files, the first session's record), its own upstream; note 2's list stand-in $NOTELIST_COUNT files, A1's $A1_COUNT"
# ---- the stand-ins (v1's)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry1) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" FAKE_CMAKE_REPO="$T" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry1) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho aifoundry1\n' > "$S/boxbin/hostname"
cat > "$S/boxbin/uptime" <<EOF
#!/bin/sh
if [ "\$1" = -s ]; then echo "2026-10-26 15:02:04"; exit 0; fi
exec /usr/bin/uptime "\$@"
EOF
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
printf '#!/bin/sh\necho "No process holds an ET-SoC-1 device node or card lock."\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\necho "et-lab-manifest (desk-test stand-in): sysfs and files only"\n' > "$S/boxbin/et-lab-manifest"
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$REAL_TIMEOUT" > "$S/boxbin/timeout"
printf '#!/bin/sh\n[ "$1" = "-O" ] && [ "$6" = /dev/stdout ] && exec cat "$5"\nexit 2\n' > "$S/boxbin/objcopy"
printf '#!/bin/sh\nexec bash "%s" "$@"\n' "$SRC/$E/rb/fake_cmake_e191.sh" > "$S/boxbin/cmake"
for n in ssh rsync scp sudo; do printf '#!/bin/sh\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$S/boxbin/$n"; done
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
printf 'lib stand-in ET_DEVICES\n' > "$S/devicelayer-standin.a"
ledpin=$(printf 'E189 desk-test stand-in kernel: ledger\n' | sha256sum | cut -c1-64); spppin=$(printf 'E189 desk-test stand-in kernel: sparse parity\n' | sha256sum | cut -c1-64)
printf '{"kernels": {"ledger": {"elf_sha256": "%s", "text_sha256": "%s"}, "spp": {"elf_sha256": "%s", "text_sha256": "%s"}}}\n' "$ledpin" "$ledpin" "$spppin" "$spppin" > "$S/standin-pins.json"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_DESKTEST=1 E191_KERNEL_PINS="$S/standin-pins.json" E191_OBJCOPY="$S/boxbin/objcopy" \
  E191_DEVICELAYER="$S/devicelayer-standin.a" E191_DESK_BUDGET_S=60
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/gitlock"
R=$T/$E/rb
TODAY=$(TZ=America/Los_Angeles date +%F)
cd "$T" || return 2

step "A2. the dry listing v2 (the second session's order), and its command lines (note 1, item 4)"
bash "$R/list_steps_e191_v2.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
/usr/bin/python3 -I -B "$T/$E/desk/drylisting_check_e191_v2.py" "$S/dry-listing.txt" > "$S/dry-check.txt" 2>&1; dc=$?
tail -n 1 "$S/dry-listing.txt"; tail -n 1 "$S/dry-check.txt"
ok "$rc.$(grep -c . "$S/calls.log").$dc.$(has 's03_desk_e191_v2.sh' "$S/dry-listing.txt").$(has 'session_e191_v2.sh' "$S/dry-listing.txt")" "0.0.0.1.1" \
  "A2 every step 0, no call to the stand-ins; step 2 v2 and session v2 listed; every device-opening line carries ET_DEVICES=1, none of card 0"

step "P1v2. step 2 v2 on the scratch repository"
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e191.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e191_v2.sh" > "$S/p1.txt" 2>&1; p1=$?
grep -E 'desk check|STOP' "$S/p1.txt" | cut -c1-600
ok "$p1.$(has 'desk check v2 (kit note 2)' "$S/p1.txt").$(has "note 2's ($NOTELIST_COUNT)" "$S/p1.txt").$(has "the first session's record 22" "$S/p1.txt").$(has 'E191 data only in the first session' "$S/p1.txt")" "0.1.1.1.1" \
  "P1v2 step 2 v2 passes at every pin (the first session's record's own list among them), the never-run check (c) in kit note 2's form"

step "P2v2, H4v2, H5v2. note 2's list one line short; E191 data outside the first record in a ref; a pass inside it in a ref"
sedi -e '$d' "$T/$E/SHA256SUMS-e191-kit-note2"; $G commit -q -am "desk test: note 2's list one line short"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e191_v2.sh" > "$S/p2.txt" 2>&1; p2=$?; $G reset -q --hard HEAD~1
$G branch -q e191-data-standin; $G checkout -q e191-data-standin; mkdir -p "$T/docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2"
echo x > "$T/docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/README.md"
$G add --sparse docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/README.md; $G commit -q -m "desk test: E191 data outside the first record"; $G checkout -q main
rm -rf "${T:?}/docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e191_v2.sh" > "$S/h4.txt" 2>&1; h4=$?; $G branch -q -D e191-data-standin
$G branch -q e191-pass-standin; $G checkout -q e191-pass-standin; mkdir -p "$T/$FIRST/passes/copy-zeros/p1"; echo x > "$T/$FIRST/passes/copy-zeros/p1/pass.json"
$G add --sparse "$FIRST/passes/copy-zeros/p1/pass.json"; $G commit -q -m "desk test: a pass in the first record"; $G checkout -q main
rm -rf "${T:?}/$FIRST/passes"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e191_v2.sh" > "$S/h5.txt" 2>&1; h5=$?; $G branch -q -D e191-pass-standin
ok "$p2.$(has "SHA256SUMS-e191-kit-note2($((NOTELIST_COUNT - 1)) OK of $((NOTELIST_COUNT - 1)); pinned $NOTELIST_COUNT" "$S/p2.txt").$h4.$(has 'never-ran(c: 1 E191 data path(s) outside' "$S/h4.txt").$h5.$(has 'never-ran(c: 0 E191 data path(s) outside the first session.s record, 1 under its passes/)' "$S/h5.txt")" \
  "16.1.16.1.16.1" "P2v2 note 2's pin refused and named; H4v2 E191 data outside the first record refused; H5v2 a pass in it refused"

step "F1. the first session on the stand-in box: its window, the look, step 5 v1, step 6 start and wait, step 8 v1; its record placed at build/e191/T$FT0"
export RB_OUT="$S/out-1"; mkdir -p "$RB_OUT"
bash "$R/s02_window_e191.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1
bash "$R/s05_look_e191.sh" > "$S/f1-look.txt" 2>&1; f1a=$?
bash "$R/s07_a1_sync_e191.sh" > "$S/f1-s5.txt" 2>&1; f1b=$?
bash "$R/s08_a1_build_e191.sh" start > "$S/f1-s6a.txt" 2>&1; f1c=$?
for i in $(seq 1 30); do bash "$R/s08_a1_build_e191.sh" wait > "$S/f1-s6b.txt" 2>&1; f1d=$?; [ "$f1d" -eq 17 ] || break; done
bash "$R/s10_a1_dry_e191.sh" start > "$S/f1-s8a.txt" 2>&1; f1e=$?
for i in $(seq 1 30); do bash "$R/s10_a1_dry_e191.sh" wait > "$S/f1-s8b.txt" 2>&1; f1f=$?; [ "$f1f" -eq 17 ] || break; done
mkdir -p "$BOXT/build/e191/T$FT0" "$BOXT/build/q141k"
cp -p "$SRC/$FIRST/session/"*.json "$SRC/$FIRST/session/"*.log "$SRC/$FIRST/session/MANIFEST.sha256" "$SRC/$FIRST/session/runner.rc" "$BOXT/build/e191/T$FT0/"
echo "$FT0" > "$BOXT/build/q141k/e191.T0"; echo "$FT0" > "$RB_OUT/e191-T0.txt"
grep -E 'E191-DRY|built today' "$S/f1-s6b.txt" "$S/f1-s8b.txt" | cut -c1-200
ok "$f1a.$f1b.$f1c.$f1d.$f1e.$f1f.$(cat "$RB_OUT/e191-built.txt" 2>/dev/null).$(grep -c 'a1-build-e191 started' "$BOXT/build/e191-build-attempts.txt" 2>/dev/null)" "0.0.0.0.0.0.ledger,spp.1" \
  "F1 the first session's day on the stand-in box: one build start today, v1's dry job, the record's session directory and T0 in place"

step "S5v2. the second session in a NEW RB_OUT: its window, the look, then step 5 v2"
export RB_OUT="$S/out-2"; mkdir -p "$RB_OUT"
bash "$R/s02_window_e191.sh" "$TODAY" 23:58 23:59 > /dev/null 2>&1
bash "$R/s05_look_e191.sh" > "$S/s5-look.txt" 2>&1; lk=$?
bash "$R/s07_a1_sync_e191_v2.sh" > "$S/s5.txt" 2>&1; s5=$?
grep -E 'HARNESS|synced|STOP' "$S/s5.txt" | cut -c1-220
ok "$lk.$s5.$(has 'HARNESS OK and HARNESS-V2 OK on the box' "$S/s5.txt").$(has 'HARNESS-V2 OK: 49 files' "$S/s5.txt")" "0.0.1.1" "S5v2 the look FREE; step 5 v2 synced harness v2's files and read both harnesses on the box"

step "B6. step 6's WAIT ALONE in the new RB_OUT (A1's build rule: the first session's build stands, no start)"
bash "$R/s08_a1_build_e191.sh" wait > "$S/b6.txt" 2>&1; b6=$?
grep -E 'built today|STOP' "$S/b6.txt" | cut -c1-220
ok "$b6.$(cat "$RB_OUT/e191-built.txt" 2>/dev/null).$(grep -c 'a1-build-e191 started' "$BOXT/build/e191-build-attempts.txt")" "0.ledger,spp.1" \
  "B6 today's build re-read into this RB_OUT (records, harness, preflight, self-checks on the box); still one build start today"

step "G1. step 9 v2 with only the first session's dry job today"
bash "$R/s11_a1_session_e191_v2.sh" FULL > "$S/g1.txt" 2>&1; g1=$?; stopline "$S/g1.txt"
ok "$g1.$(has 'a1-dry-e191-v2) has not ended rc 0 today' "$S/g1.txt").$(cat "$BOXT/build/q141k/e191.T0")" "10.1.$FT0" "G1 refused (10): no dry pass of runner v2 today; nothing launched"

step "D2. step 8 v2, runner v2's dry pass on the stand-in box"
bash "$R/s10_a1_dry_e191_v2.sh" start > "$S/d2a.txt" 2>&1; d2a=$?
for i in $(seq 1 30); do bash "$R/s10_a1_dry_e191_v2.sh" wait > "$S/d2b.txt" 2>&1; d2b=$?; [ "$d2b" -eq 17 ] || break; done
grep -E 'E191-DRY|smoke gate|kit note 2' "$S/d2b.txt" | cut -c1-240
ok "$d2a.$d2b.$(grep -qE '^E191-DRY-V2 rc=0 passes=6 dry-check=1 identity-lines=2 note2=1 runtime-dropped=[1-9]' "$S/d2b.txt" && echo 1 || echo 0)" "0.0.1" \
  "D2 runner v2's dry pass: six passes, its dry check, identity lines, 'kit note 2', the runtime line dropped in the smoke; rc 0"

step "G2. step 9 v2 from the FIRST session's RB_OUT (its T0 a session that sent card commands)"
RB_OUT="$S/out-1" bash "$R/s11_a1_session_e191_v2.sh" FULL > "$S/g2.txt" 2>&1; g2=$?; stopline "$S/g2.txt"
ok "$g2.$(has 'sent a card command' "$S/g2.txt").$(cat "$BOXT/build/q141k/e191.T0")" "10.1.$FT0" "G2 refused (10) by the box read: one session an RB_OUT; nothing launched"

step "WT0, WT1-WT4. step 10 v1 (the negative control) and step 10 v2 on a stand-in session_e191_v2.sh"
WT=1794700001; SD=$BOXT/build/e191/T$WT; mkdir -p "$SD" "$S/standin/tools/claims-v3/e191"
printf '#!/bin/bash\nsleep 40\n' > "$S/standin/tools/claims-v3/e191/session_e191_v2.sh"
{ printf '%s session start (T0 %s = 00:00:00 PST; plan FULL; kit note 2; programs ledger+spp; aifoundry1 card 1, ET_DEVICES=1; its files in build/e191/T%s)\n' "$(date '+%F %T %Z')" "$WT" "$WT"
  printf '%s identity (b): et-who with the sampler running: ours on card 1 2 (on /dev/et1_mgmt 1), ours on card 0 0, another login'"'"'s 0; the sampler holds /dev/et1_mgmt only\n' "$(date '+%F %T %Z')"
  printf '%s smoke copy-64m-random: rc 0, ok (0.3 s); the host'"'"'s card: card 1; the host'"'"'s line: 1 runtime line(s) dropped (Opening device 1)\n' "$(date '+%F %T %Z')"; } > "$SD/session.log"
cp "$RB_OUT/e191-T0.txt" "$S/wt-keep-T0" 2>/dev/null; echo "$WT" > "$RB_OUT/e191-T0.txt"; echo "$WT" > "$BOXT/build/q141k/e191.T0"
bash "$S/standin/tools/claims-v3/e191/session_e191_v2.sh" &
sp=$!
RB_WAIT_LOOP_S=3 bash "$R/s20_wait_e191.sh" > "$S/wt0.txt" 2>&1; wt0=$?
RB_WAIT_LOOP_S=3 bash "$R/s20_wait_e191_v2.sh" > "$S/wt1.txt" 2>&1; wt1=$?
printf '%s session end (T0 %s)\n' "$(date '+%F %T %Z')" "$WT" >> "$SD/session.log"; echo "x  session.log" > "$SD/MANIFEST.sha256"
kill "$sp" 2>/dev/null; wait "$sp" 2>/dev/null
RB_WAIT_LOOP_S=3 bash "$R/s20_wait_e191_v2.sh" > "$S/wt2.txt" 2>&1; wt2=$?
printf '%s BOUND: the host process (pid 1) outlived the runner'"'"'s 30 s bound: `timeout 10` did not end it; nothing is killed; the queue stops\n' "$(date '+%F %T %Z')" >> "$SD/session.log"
RB_WAIT_LOOP_S=3 bash "$R/s20_wait_e191_v2.sh" > "$S/wt3.txt" 2>&1; wt3=$?
sedi -e 's/plan FULL; kit note 2; /plan FULL; /' "$SD/session.log"
RB_WAIT_LOOP_S=3 bash "$R/s20_wait_e191_v2.sh" > "$S/wt4.txt" 2>&1; wt4=$?
rm -rf "${SD:?}"; rm -f "$RB_OUT/e191-T0.txt"; echo "$FT0" > "$BOXT/build/q141k/e191.T0"
ok "$wt0.$(has 'RUN-GONE' "$S/wt0.txt").$wt1.$(has 'RUN-RUNNING' "$S/wt1.txt").$(has 'NOTE2-SESSION yes' "$S/wt1.txt").$wt2.$wt3.$(has 'BOUND-SEEN' "$S/wt3.txt").$wt4.$(has 'not kit note 2' "$S/wt4.txt")" \
  "14.1.17.1.1.0.16.1.10.1" "WT0 v1's step 10 reads session v2 as RUN-GONE (14); WT1 v2 RUN-RUNNING (17); WT2 ended (0); WT3 BOUND (16); WT4 a T0 not of kit note 2 (10)"

step "RS2. the rest rule through step 9 v2: a session of ours ended 10 minutes ago"
mkdir -p "$BOXT/build/e190/T1794614924-B"
cp "$SRC/docs/reports/data/2026-11-13-e190-large-gemm/aifoundry1-c1/session.log" "$BOXT/build/e190/T1794614924-B/session.log"
sedi -e "s/^2026-11-13 16:27:55 PST session end/$(TZ=America/Los_Angeles date -d '-10 min' '+%F %T %Z') session end/" "$BOXT/build/e190/T1794614924-B/session.log"
bash "$R/s11_a1_session_e191_v2.sh" FULL > "$S/rs2.txt" 2>&1; rs2=$?; stopline "$S/rs2.txt"
rm -rf "${BOXT:?}/build/e190"
ok "$rs2.$(has 'REFUSED: 10 minutes since E190' "$S/rs2.txt").$(cat "$BOXT/build/q141k/e191.T0")" "10.1.$FT0" "RS2 refused (10) naming E190, nothing launched"

step "LL2a. THE LAST LAUNCH, RB_OUT with no T0: the box's last E191 launch is not the first session's (a launch whose ssh call was lost)"
echo 1794700002 > "$BOXT/build/q141k/e191.T0"
bash "$R/s11_a1_session_e191_v2.sh" FULL > "$S/ll2a.txt" 2>&1; ll2a=$?; stopline "$S/ll2a.txt"
ll2at=$(cat "$BOXT/build/q141k/e191.T0"); ll2ar=$([ -e "$RB_OUT/e191-T0.txt" ] && echo 1 || echo 0)
echo "$FT0" > "$BOXT/build/q141k/e191.T0"
ok "$ll2a.$(has "reads 1794700002, not $FT0, the first session" "$S/ll2a.txt").$(has 'a launch went out that this RB_OUT did not record' "$S/ll2a.txt").$(has 'rest: ' "$S/ll2a.txt").$ll2at.$ll2ar" \
  "10.1.1.0.1794700002.0" "LL2a refused (10) by the box read before the rest rule: the box's last launch is not the first session's; nothing launched, no T0 written"

step "LA2. step 9 v2 launches the REAL session_e191_v2.sh (its box check stops it: this desk is not aifoundry1); step 10 v2 reads the gate"
bash "$R/s11_a1_session_e191_v2.sh" FULL > "$S/la2.txt" 2>&1; la2=$?
grep -E 'LAUNCHED|rest:|relaunch' "$S/la2.txt" | cut -c1-220
sleep 3
for i in 1 2 3 4; do RB_WAIT_LOOP_S=20 bash "$R/s20_wait_e191_v2.sh" > "$S/la2w.txt" 2>&1; w=$?; [ "$w" -eq 17 ] || break; done
grep -E 'box check|GATE|MANIFEST|NOTE2' "$S/la2w.txt" | cut -c1-220
t1=$(cat "$RB_OUT/e191-T0.txt" 2>/dev/null)
ok "$la2.$(has 'session v2, kit note 2' "$S/la2.txt").$(has "rest: " "$S/la2.txt").$w.$(has 'MANIFEST-WRITTEN' "$S/la2w.txt").$(has 'NOTE2-SESSION yes' "$S/la2w.txt").$(has 'the box check: this host is' "$S/la2w.txt").$(grep -c 'plan FULL; kit note 2;' "$BOXT/build/e191/T$t1/session.log" 2>/dev/null)" \
  "0.1.1.16.1.1.1.1" "LA2 session v2 launched after the rest; the real runner v2 stopped at its box check before any device, with its manifest; step 10 v2 reads the gate (16)"

step "LL2b. THE LAST LAUNCH, RB_OUT with a T0: the box's last launch is not that T0 (a relaunch whose ssh call was lost)"
t1x=$((${t1:-0} + 7)); echo "$t1x" > "$BOXT/build/q141k/e191.T0"
bash "$R/s11_a1_session_e191_v2.sh" FULL > "$S/ll2b.txt" 2>&1; ll2b=$?; stopline "$S/ll2b.txt"
ll2bt=$(cat "$BOXT/build/q141k/e191.T0"); ll2br=$([ -e "$RB_OUT/e191-relaunch.txt" ] && echo 1 || echo 0); ll2bk=$(cat "$RB_OUT/e191-T0.txt" 2>/dev/null)
echo "$t1" > "$BOXT/build/q141k/e191.T0"
ok "$ll2b.$(has "reads $t1x, not $t1, this RB_OUT's e191-T0.txt" "$S/ll2b.txt").$(has 'relaunch: ' "$S/ll2b.txt").$ll2bt.$ll2br.$ll2bk" \
  "10.1.0.$t1x.0.$t1" "LL2b refused (10): the box's last launch is not this RB_OUT's T0; no relaunch, nothing launched, no e191-relaunch.txt"

step "G4a, G4b. THE RELAUNCH RULE: step 9 v2 again from that RB_OUT (its T0 opened no device), then a third time"
bash "$R/s11_a1_session_e191_v2.sh" FULL > "$S/g4a.txt" 2>&1; g4a=$?
grep -E 'LAUNCHED|relaunch' "$S/g4a.txt" | cut -c1-240
t2=$(cat "$RB_OUT/e191-T0.txt" 2>/dev/null)
sleep 3
for i in 1 2 3 4; do RB_WAIT_LOOP_S=20 bash "$R/s20_wait_e191_v2.sh" > "$S/g4aw.txt" 2>&1; w2=$?; [ "$w2" -eq 17 ] || break; done
bash "$R/s11_a1_session_e191_v2.sh" FULL > "$S/g4b.txt" 2>&1; g4b=$?; stopline "$S/g4b.txt"
ok "$g4a.$(has "relaunch: this RB_OUT's launch T0 $t1 opened no device" "$S/g4a.txt").$([ -n "$t2" ] && [ "$t2" != "$t1" ] && echo 1 || echo 0).$(grep -c "^$t1 relaunch:" "$RB_OUT/e191-relaunch.txt" 2>/dev/null).$w2.$g4b.$(has 'launched twice already' "$S/g4b.txt").$(cat "$BOXT/build/q141k/e191.T0")" \
  "0.1.1.1.16.10.1.$t2" "G4a one launch more after a launch that opened no device (a new T0, e191-relaunch.txt); G4b a third launch refused (10) before any call"

step "C3v2. step 11 v2 on the first session's T0 (its log names no kit note 2)"
RB_OUT="$S/out-1" bash "$R/s22_collect_e191_v2.sh" > "$S/c3.txt" 2>&1; c3=$?; stopline "$S/c3.txt"
D2=docs/reports/data/$TODAY-e191-blind-day-aifoundry1-c1-s2
ok "$c3.$(has 'is not a kit note 2 session' "$S/c3.txt").$([ -e "$T/$D2" ] && echo 1 || echo 0)" "10.1.0" "C3v2 refused (10): step 11 v2 collects session v2 only; nothing written"

step "C2v2, C4v2. step 11 v2 on the relaunched session, then again"
bash "$R/s22_collect_e191_v2.sh" > "$S/c2.txt" 2>&1; c2=$?
grep -E 'COPY-BACK|COLLECTED|HISTORY|STOP' "$S/c2.txt" | cut -c1-220
bash "$R/s22_collect_e191_v2.sh" > "$S/c4.txt" 2>&1; c4=$?
ok "$c2.$(has 'COPY-BACK EXACT' "$S/c2.txt").$(has "COLLECTED $D2" "$S/c2.txt").$([ -f "$T/$D2/SHA256SUMS" ] && [ -f "$T/$D2/FILES.txt" ] && echo 1 || echo 0).$(grep -rlE "/home/|(^|[^A-Za-z0-9_.-])$(id -un)([^A-Za-z0-9_-]|$)" "$T/$D2" 2>/dev/null | grep -c .).$c4.$(has 'exists already' "$S/c4.txt")" \
  "0.1.1.1.0.10.1" "C2v2 collected exactly into ...-c1-s2 (the first session's directory untouched), no home path or login; C4v2 refused (10) the second time"

step "SC0v2, SC3v2. step 13 v2 before the data commit, then committed and clean"
bash "$R/s24_score_e191_v2.sh" > "$S/sc0.txt" 2>&1; sc0=$?
$G add --sparse "$D2" > /dev/null 2>&1 && $G commit -q -m "desk test: the second session's collected data directory" > /dev/null 2>&1 || echo "data commit failed"
bash "$R/s24_score_e191_v2.sh" > "$S/sc3.txt" 2>&1; sc3=$?
grep -E 'scored:|STOP' "$S/sc3.txt" | cut -c1-200
ok "$sc0.$sc3.$(has 'scored:' "$S/sc3.txt").$([ -s "$RB_OUT/scores-e191.json" ] && echo 1 || echo 0).$(git -C "$T" status --short -- "$FIRST" | grep -c .)" "10.0.1.1.0" \
  "SC0v2 not committed: 10; SC3v2 committed and clean: scored, scores-e191.json; the first session's record unchanged"

step "Z. no process of this test left running"
sleep 1
z=$(pgrep -f "$S/" 2>/dev/null | grep -c .)
ok "$z" "0" "Z nothing left"
echo
echo "SELFTEST-RB-E191-V2 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<lab clone>#g"
exit "${PIPESTATUS[0]}"
