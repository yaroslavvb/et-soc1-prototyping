#!/usr/bin/env bash
# E215's arm B in E213's Amendment A2 form (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum; E213's A2 by Q219's lane a2-e213, landed 8b675547, run by card-e213b2 on Wed 18 Nov 2026): THE DESK TEST OF ARM B'S RUNBOOK AS AMENDED BY A2, in
# the kit's runbook-test form (tools/claims-v3/e215/rb/selftest_rb_e215.sh: a FAKE ssh and rsync, a stand-in aifoundry1 box, k6's bounded runner
# and the kit's own steps unchanged around A2's), with fwgate's desk-test stand-ins as its README requires: FWGATE_DESK_TEST=1 and EVERY stand-in
# (FWGATE_CLI = fwgate's own tests/fwcli-standin, FWGATE_ETWHO = tests/etwho-standin, FWGATE_LOCKDIR a folder holding the two lock files the lab
# makes at boot, FWGATE_LEDGER_DIR under the stand-in box's home, FWGATE_HOSTNAME aifoundry1, FWGATE_BOOT_EPOCH and FWGATE_BOOT_ID the case's boot).
# The stand-in CLI answers with E82's committed raw answer (docs/reports/data/2026-10-31-e82-kinds-aifoundry1/ident/firmware_pre.txt: EQUAL to
# E82's record), or that answer with card 0's PMIC (DIFFERENT), or without its success line (UNREADABLE). The stand-in boxes BOOT AFTER E82'S
# FIRMWARE READ (2026-11-17 16:46:32 PST, aifoundry1's boot now) but in the continuity case (2026-10-26 15:18:24 PDT, before it). Each case has its
# own box tree, lock folder, ledger and RB_OUT. The box shell carries ET_DEVICES=1, so the cases also show that A2's helper removes it from the
# read's environment. No lab box is reached; no card node exists here (run inside the round's nodev.sh); the test re-runs itself in a private
# PID namespace (bubblewrap), so that no other lane's process on this desk is read as a session of ours. Cases:
#   NE  NEEDS-READ, then EQUAL: step 4 (A2) exits 0; the stand-in CLI called ONCE, argv '-m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 1 -u 5000',
#       stdin /dev/null, BOTH cards' locks held by fwgate during the call; the record EQUAL, ET_DEVICES null in it, both locks named; et-who
#       --check called once; the kit's attempt log ATTEMPT then END EQUAL; RB_OUT's copy exact and SCRUB-CHECK CLEAN with the record's ledger
#       path's home masked; the look file "A2-LOOK-B: EQUAL <record>"
#   NC  step 4 again on the same boot the same day: 0, CONTINUITY (this boot's EQUAL of today, read with --extra); the CLI still called once
#   NL  step 9 (A2) after NE: the guard's "identity: ... ok" (this boot's EQUAL read), A2-GUARD, LAUNCHED (the stand-in session started): 0
#   CT  a boot BEFORE E82's read: step 4 exits 0 by CONTINUITY with no read (the CLI never called, no read folder); step 9: identity ok, LAUNCHED
#   DF  DIFFERENT: step 4 exits 16 (the one read did not end EQUAL), CLI once; step 4 again: 16 by fwgate's look (STOPPED), CLI still once;
#       step 9 (a forced look file, so that the launch reaches the box): IDENTITY-STOP, 16, the stand-in session NOT started
#   UR  UNREADABLE: step 4 16, CLI once; step 9 (forced): IDENTITY-STOP, 16, not started
#   CS  a cut-off SENT in fwgate's ledger (a SENT line of this boot with no END): step 4 16 by fwgate's look (STOPPED), the CLI never called;
#       step 9 (forced): IDENTITY-STOP, 16, not started
#   BL  a BUSY LOCK (card 0's lock held by another process): step 4 16 (fwgate's read: held, nothing sent), the CLI never called, the attempt log
#       ATTEMPT then END NOT-SENT-17; with the lock free again, step 4 again: 16 (an attempt of this boot did not end EQUAL: never a second read),
#       the CLI still never called; step 9 (forced): IDENTITY-STOP, 16, not started
#   BW  a BUSY et-who (et-who --check rc 1): step 4 16, the CLI never called; step 9 (forced): IDENTITY-STOP, 16, not started
#   ML  a MISSING LOCK FILE (card 0's): step 4 16, the CLI never called (fwgate never makes one); step 9 (forced): IDENTITY-STOP, 16, not started
#   NG  the guard with NO EQUAL OF THIS BOOT (a boot after the read, no read made, a forced look file): step 9 IDENTITY-STOP, 16, not started
#   SB  A STALE EQUAL OF AN EARLIER BOOT (NE's read in the folder, the box booted again since): step 9 IDENTITY-STOP, 16, not started
#   SD  A STALE EQUAL OF AN EARLIER DAY on the same boot (fwgate's clock a day on): step 9 IDENTITY-STOP, 16, not started
#   RS  THE REST RULE before the read: a session of ours ended 10 minutes ago on the box: step 4 refuses (10) with the rest rule's words, the CLI
#       never called, no attempt written; with that session 50 minutes back: step 4 0, EQUAL
#   PB  the pins on the box: fwgate.py changed on the box after step 4: step 9 IDENTITY-STOP (its pins), 16, not started
#   PD  the pins at the desk: A2's helper changed (uncommitted) in the lab clone: step 4 16 before any call reaches the box
#   AA  arm A is refused by A2's three steps (10), before any call
#   DT  data_e215a2.py (step 12's addition) on a stand-in data directory: (a) NE's copy added as fwgate/, scrubbed (the ledger path's home -> '~'),
#       the record's raw answer at its sha256, SHA256SUMS made again and read back by sha256sum -c; (b) a CONTINUITY day adds nothing, SHA256SUMS
#       byte-identical; (c) a copy changed after step 4: refused, no fwgate/, SHA256SUMS byte-identical; (d) another login's home in the copy: the
#       scrub refuses, no fwgate/, SHA256SUMS byte-identical; (e) a lab path that is not E215 arm B's directory: refused
#   DRY A2's dry listing (rb/list_steps_e215_a2.sh): 15 steps listed, 0 exited non-zero, 0 box calls
#   Z   no process of this test left running
# Added by fix-a2e213 (Q219, before A2 landed; verify-a2e213's finding 2, THE EVIDENCE OF THE ONE CALL, read only, never a gate):
#   NE-EV  after NE: RB_OUT/e215-a2-evidence-B/ holds this boot's ledger lines (SENT, END EQUAL) and attempt-log lines (ATTEMPT, END EQUAL), its
#          sha256 list reads OK, the runbook log and the look file say "one call on this boot, ended EQUAL"
#   NC-EV  after NC (CONTINUITY by that EQUAL): the same lines captured again, still one call
#   CT-EV  a boot before E82's read: the capture holds no line ("no call on this boot")
#   EV     the evidence call fails on the box (a stand-in box python3 that refuses the 'evidence' subcommand alone): step 4 still passes EQUAL,
#          the capture is NOT CAPTURED and said in the runbook log and the look file, no evidence folder made; step 9 launches
#   EVX    the helper's evidence alone on a copy of NE's ledger and attempt log: this boot's lines only (another boot's line left out), a line of
#          another form named (NOT one EQUAL call), a second SENT of this boot (NOT one EQUAL call), another host refused (NOT READ, 16)
#   DT f-h step 12's addition with step 4's evidence: (f) added beside the record, the ledger lines' record paths' home masked as '~',
#          SHA256SUMS read back; (g) evidence changed since step 4: left out and said, the record still added; (h) another login's home in it:
#          the scrub's left-over leaves it out and says so, the record still added
#   bash tools/claims-v3/e215/a2/desk/selftest_a2_e215.sh <scratch dir> > a2/logs/selftest-a2-e215.txt   (prints SELFTEST-A2-E215 <n> of <m> PASS or FAIL)
# On a box with a card (aifoundry2) run it ONLY inside a sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh), and never while THE QUIET
# DESK FLAG stands (its launch cases start a stand-in script named session_e215.sh). SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S RB_DESKTEST RB_GITLOCK RB_DRY RB_WAIT_LOOP_S RB_OUT FWGATE_DESK_TEST FWGATE_CLI \
         FWGATE_ETWHO FWGATE_LOCKDIR FWGATE_LEDGER_DIR FWGATE_HOSTNAME FWGATE_BOOT_EPOCH FWGATE_BOOT_ID FWGATE_NOW_EPOCH; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test sets its own"; exit 2; }
done
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible: run this inside the sandbox (W/nodev.sh)"; exit 3; }
ls /run/lock/etsoc-shire*.lock > /dev/null 2>&1 && { echo "REFUSED: a card lock file is visible in /run/lock: run this inside the sandbox (an empty /run/lock)"; exit 3; }
if [ -z "${E215A2_PIDNS:-}" ]; then
  command -v bwrap > /dev/null || { echo "no bwrap: the test runs in a private PID namespace"; exit 2; }
  echo "(A2's runbook test: re-run in a private PID namespace, so that no other lane's process on this desk is read as a session of ours)"
  exec /usr/bin/bwrap --dev-bind / / --unshare-pid --proc /proc --die-with-parent -- env E215A2_PIDNS=1 bash "$SRC/tools/claims-v3/e215/a2/desk/selftest_a2_e215.sh" "$@"
fi
for c in timeout sha256sum flock rsync git; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
REAL_RSYNC=$(command -v rsync)
mkdir -p "$S"; S=$(cd "$S" && pwd)
for d in tree bin boxbin; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; BIN=$S/bin; BB=$S/boxbin
A=tools/claims-v3/e215/a2; E=tools/claims-v3/e215
mkdir -p "$BIN" "$BB"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aqE -- "$1" "$2" 2>/dev/null && echo 1 || echo 0; }
cnt() { if [ -f "$1" ]; then grep -c . "$1"; else echo 0; fi; }
line() { grep -aE -- "$1" "$2" 2>/dev/null | head -n 1 | cut -c1-"${3:-200}"; }
main() {
# ---- the scratch repository: a shared sparse clone of the lab clone at its HEAD (A2's files committed in it, as on the card day)
git clone -q --shared --no-checkout "$SRC" "$T" || return 2
G="git -C $T -c user.name=e215a2-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G sparse-checkout set --no-cone /tools/ /docs/reports/data/2026-10-31-e82-kinds-aifoundry1/ident/ || return 2
$G checkout -q -B main "$(git -C "$SRC" rev-parse HEAD)" || return 2
if [ ! -f "$T/$A/rb/s05_look_e215_a2.sh" ]; then
  # the kit lane (kit-e215): the kit's files are untracked in the lab clone; taken as one stand-in kit commit, as the kit's runbook test does
  ( cd "$SRC" && git ls-files --others --exclude-standard -- $E; git diff --name-only -- $E ) | sort -u | while IFS= read -r f; do
    [ -f "$SRC/$f" ] || continue; mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
  $G add -A $E && $G commit -q -m "E215 A2-form desk test: the kit's files (stand-in kit commit)" || { echo "the scratch kit commit failed"; return 2; }
  KITFORM="the kit's files untracked in the lab clone, committed in the scratch as one stand-in kit commit"
else
  KITFORM="the kit's files (the A2 form's among them) committed at the lab clone's HEAD"
fi
[ -f "$T/$A/rb/s05_look_e215_a2.sh" ] || { echo "A2's files are not in the scratch repository"; return 2; }
echo "scratch repository: a shared sparse clone of the lab clone at HEAD $(git -C "$SRC" rev-parse --short=12 HEAD); $KITFORM"
E82A=$T/docs/reports/data/2026-10-31-e82-kinds-aifoundry1/ident/firmware_pre.txt
[ -s "$E82A" ] || { echo "E82's committed answer is not in the scratch repository"; return 2; }
cp "$E82A" "$S/answer-equal.txt"
/usr/bin/python3 - "$E82A" "$S/answer-different.txt" "$S/answer-unreadable.txt" <<'PY' || return 2
import sys
t = open(sys.argv[1]).read()
a = "PMIC Firmware versions: Major: 1 Minor: 3 Revision: 0"
assert t.count(a) == 1
open(sys.argv[2], "w").write(t.replace(a, "PMIC Firmware versions: Major: 1 Minor: 6 Revision: 1"))
lines = [x for x in t.split("\n") if "Service request succeeded" not in x]
assert len(lines) < len(t.split("\n"))
open(sys.argv[3], "w").write("\n".join(lines))
PY
# ---- the stand-ins: ssh and rsync serve aifoundry1 only, its tree in the case's own box folder; the box's own commands
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
[ "\$host" = aifoundry1 ] || { echo "STAND-IN SSH: refusing host \$host" >&2; exit 97; }
[ "\$cmd" = true ] && exit 0
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'bash -s' and 'true' are served (got: \$cmd)" >&2; exit 97; }
R=\$(cat "$S/boxroot")
cd "\$R/\$host" || exit 1
set -a; . "$S/fwenv"; set +a
exec env HOME="\$R/\$host" STANDIN_HOST="\$host" STANDIN_S="$S" PATH="$BB:\$PATH" bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
R=\$(cat "$S/boxroot")
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; [ "\$h" = aifoundry1 ] || { echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97; }; a+=("\$R/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
printf '#!/bin/sh\necho "scp refused by the desk test" >&2\nexit 97\n' > "$BIN/scp"
printf '#!/bin/sh\necho "${STANDIN_HOST:-desk}"\n' > "$BB/hostname"
cat > "$BB/uptime" <<EOF
#!/bin/sh
if [ "\${1:-}" = -s ] && [ -n "\${STANDIN_HOST:-}" ]; then cat "$S/boot-text"; exit 0; fi
exec /usr/bin/uptime "\$@"
EOF
cat > "$BB/et-who" <<EOF
#!/bin/sh
if [ "\${1:-}" = --check ]; then exit "\$(cat "$S/box-etwho-check-rc" 2>/dev/null || echo 0)"; fi
echo "No process holds an ET-SoC-1 device node or card lock."
EOF
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$BB/python3"
REAL_PGREP=$(command -v pgrep)
cat > "$BB/pgrep" <<EOF
#!/bin/bash
anc=" "; p=\$\$
while [ -n "\$p" ] && [ "\$p" -gt 1 ]; do anc="\$anc\$p "; p=\$(ps -o ppid= -p "\$p" 2>/dev/null | tr -d ' '); done
"$REAL_PGREP" "\$@" | while IFS= read -r x; do case "\$anc" in *" \${x%% *} "*) ;; *) echo "\$x" ;; esac; done
EOF
chmod +x "$BIN"/* "$BB"/*
export PATH="$BIN:$PATH" RB_LOCK="$S/rb-lock.txt"
TODAY=$(TZ=America/Los_Angeles date +%F)
AFTER_TEXT="2026-11-17 16:46:32"; AFTER=1794962792          # aifoundry1's boot now: after E82's firmware read (2026-10-31 13:45:24 PDT)
BEFORE_TEXT="2026-10-26 15:18:24"; BEFORE=1793053104        # a boot before it (the kit's stand-in boxes' boot)
newcase() {  # newcase <tag> <boot text> <boot epoch> [<answer file>]: a fresh box tree, lock folder, ledger, RB_OUT and window; the fwgate env
  CASE=$1; R="$S/box-$CASE"; O="$S/out-$CASE"; LD="$S/locks-$CASE"; CLI="$S/cli-$CASE.jsonl"; EW="$S/etwho-$CASE.log"
  mkdir -p "$R/aifoundry1/nekko" "$O" "$LD"; : > "$LD/etsoc-shire0.lock"; : > "$LD/etsoc-shire1.lock"
  echo "$R" > "$S/boxroot"; echo "$2" > "$S/boot-text"; echo 0 > "$S/box-etwho-check-rc"
  BID="desk-$CASE-$3"
  cat > "$S/fwenv" <<EOF
FWGATE_DESK_TEST=1
FWGATE_CLI=$T/tools/claims-v3/fwgate/tests/fwcli-standin
FWGATE_ETWHO=$T/tools/claims-v3/fwgate/tests/etwho-standin
FWGATE_LOCKDIR=$LD
FWGATE_LEDGER_DIR=$R/aifoundry1/.local/state/fwgate
FWGATE_HOSTNAME=aifoundry1
FWGATE_BOOT_EPOCH=$3
FWGATE_BOOT_ID=$BID
FWGATE_STANDIN_LOG=$CLI
FWGATE_STANDIN_LOCKS=$LD/etsoc-shire0.lock:$LD/etsoc-shire1.lock
FWGATE_STANDIN_OUT=${4:-$S/answer-equal.txt}
FWGATE_STANDIN_ETWHO_LOG=$EW
FWGATE_STANDIN_ETWHO_RC=0
ET_DEVICES=1
EOF
  RB_OUT=$O RB_DESKTEST=1 E215_DESK_BUDGET_S=60 bash "$T/$E/rb/s02_window_e215.sh" B "$TODAY" 23:58 23:59 > "$S/$CASE-window.txt" 2>&1 || echo "window: rc $?"
}
setenv() { sed -i "s#^$1=.*#$1=$2#" "$S/fwenv"; grep -q "^$1=" "$S/fwenv" || echo "$1=$2" >> "$S/fwenv"; }
look() {  # look <log tag>: A2's step 4 in the case's RB_OUT (the both-cards wait 25 s here, 400 s on the card day); prints its exit
  RB_OUT=$O RB_DESKTEST=1 E215_DESK_BUDGET_S=60 E215A2_DESK_FLIM=25 bash "$T/$A/rb/s05_look_e215_a2.sh" B > "$S/$1.txt" 2>&1; echo $?
}
prelaunch() {  # the desk's and the box's inputs step 9 needs besides the look (today's build and dry pass, today's never-run report, a stand-in session)
  echo rgm > "$O/e215-built-B.txt"
  echo "$(date '+%F %T %Z') NEVER-RUN-E215 arm B: (desk-test stand-in)" > "$O/e215-neverrun-B.txt"
  mkdir -p "$R/aifoundry1/nekko/build/q141k/jobs" "$R/aifoundry1/nekko/$E"
  echo 0 > "$R/aifoundry1/nekko/build/q141k/jobs/a1-dry-e215.rc"
  echo "RGM-BUILT rc=0" > "$R/aifoundry1/nekko/build/q141k/jobs/a1-build-e215.out"
  printf '#!/bin/bash\n# A STAND-IN for session_e215.sh (A2'"'"'s desk test): no device; it only leaves a marker and ends\necho "STAND-IN SESSION started T0=${E215_T0:-} arm=${E215_ARM:-}" >> "$HOME/launched.txt"\n' > "$R/aifoundry1/nekko/$E/session_e215.sh"
}
forcelook() { echo "$(date '+%F %T %Z') A2-LOOK-B: EQUAL fwgate-aifoundry1-c1-20000101-000000.json (desk test: FORCED, so that the launch reaches the box and the guard decides)" > "$O/e215-a2-look-B.txt"; }
launch() {  # launch <log tag>: A2's step 9; prints its exit
  RB_OUT=$O RB_DESKTEST=1 E215_DESK_BUDGET_S=60 bash "$T/$A/rb/s11_session_e215_a2.sh" B > "$S/$1.txt" 2>&1; echo $?
}
started() { [ -s "$R/aifoundry1/launched.txt" ] && echo started || echo not-started; }
clin() { cnt "$CLI"; }
rec() { ls "$R/aifoundry1/nekko/build/e215/fwgate-B-$TODAY"/fwgate-aifoundry1-c1-*.json 2>/dev/null | head -n 1; }
recf() { /usr/bin/python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); print(r.get(sys.argv[2]))' "$1" "$2" 2>/dev/null; }
attlog() { local f="$R/aifoundry1/nekko/build/e215/a2-fwgate-attempts-aifoundry1-c1.jsonl"; [ -f "$f" ] && /usr/bin/python3 -c 'import json,sys; print(" ".join(json.loads(l)["event"] + ("=" + json.loads(l)["verdict"] if json.loads(l)["event"] == "END" else "") for l in open(sys.argv[1]) if l.strip()))' "$f" || echo none; }
evf() {  # evf <ledger|attempts> [<folder>]: the events in step 4's evidence file (event:verdict, a line each), 'empty', or 'none' (fix-a2e213)
  local d=${2:-$O/e215-a2-evidence-B} f
  case "$1" in ledger) f="$d/fwgate-ledger-aifoundry1-c1-this-boot.jsonl" ;; *) f="$d/a2-fwgate-attempts-aifoundry1-c1-this-boot.jsonl" ;; esac
  [ -f "$f" ] || { echo none; return; }
  /usr/bin/python3 -c 'import json,sys; L=[json.loads(x) for x in open(sys.argv[1]) if x.strip()]; print(" ".join(e["event"] + ":" + str(e.get("verdict")) for e in L) or "empty")' "$f" 2>/dev/null || echo unreadable
}
evsum() { if [ -f "$O/e215-a2-evidence-B.sha256" ]; then ( cd "$O/e215-a2-evidence-B" && sha256sum -c "$O/e215-a2-evidence-B.sha256" 2>&1 | grep -c ': OK$' ); else echo 0; fi; }

step "NE: NEEDS-READ, then EQUAL (the box booted after E82's read)"
newcase NE "$AFTER_TEXT" "$AFTER"
r=$(look NE)
RF=$(rec); NEO=$O; NER=$R; cp "$S/fwenv" "$S/fwenv.ne"
cl=$(/usr/bin/python3 -c 'import json,sys; L=[json.loads(x) for x in open(sys.argv[1]) if x.strip()]; e=L[0] if L else {}; print(len(L), " ".join(e.get("argv", [])), e.get("stdin"), ",".join(f"{k}={v}" for k, v in sorted(e.get("locks", {}).items())))' "$CLI" 2>/dev/null)
ok "$r|$cl|$(recf "$RF" verdict)|$(recf "$RF" ET_DEVICES)|$(recf "$RF" locks)|$(cnt "$EW")|$(attlog)|$(has '^[0-9-]+ [0-9:]+ [A-Z]+ A2-LOOK-B: EQUAL fwgate-aifoundry1-c1-' "$O/e215-a2-look-B.txt")|$(has 'SCRUB-CHECK CLEAN: 3 files, 1 held' "$S/NE.txt")" \
   "0|1 -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 1 -u 5000 /dev/null etsoc-shire0.lock=held,etsoc-shire1.lock=held|EQUAL|None|['etsoc-shire0.lock', 'etsoc-shire1.lock']|1|ATTEMPT END=EQUAL|1|1" \
   "$(line '^\[s05_look_a2_e215\] ' "$S/NE.txt" 300)"
[ "$r" = 0 ] || tail -n 40 "$S/NE.txt"
step "NE-EV: step 4's evidence of the one call (fix-a2e213): this boot's ledger and attempt-log lines in RB_OUT, read only"
ok "$(evf ledger)|$(evf attempts)|$(evsum)|$(has "A2-EVIDENCE-B: evidence: fwgate's ledger aifoundry1-c1\.jsonl: 2 line\(s\) of this boot \(SENT 1, END 1: EQUAL\); the kit's attempt log a2-fwgate-attempts-aifoundry1-c1\.jsonl: 2 line\(s\) of this boot \(ATTEMPT 1, END 1: EQUAL\): one call on this boot, ended EQUAL" "$O/runbook.log")|$(has '; evidence: .*one call on this boot, ended EQUAL \(RB_OUT/e215-a2-evidence-B/\)$' "$O/e215-a2-look-B.txt")" \
   "SENT:SENT END:EQUAL|ATTEMPT:None END:EQUAL|2|1|1" "$(line 'A2-EVIDENCE-B: ' "$O/runbook.log" 300)"
step "NC: step 4 again on the same boot the same day: CONTINUITY by this boot's EQUAL of today, no second read"
r=$(look NC)
ok "$r|$(clin)|$(has 'A2-LOOK: CONTINUITY: aifoundry1 card 1 booted .* the firmware read of ' "$S/NC.txt")|$(attlog)" "0|1|1|ATTEMPT END=EQUAL" "$(line 'A2-LOOK: ' "$S/NC.txt")"
step "NC-EV: the evidence captured again after CONTINUITY: the same one call"
ok "$(evf ledger)|$(evf attempts)|$(evsum)|$(grep -c 'A2-EVIDENCE-B: evidence: .*one call on this boot, ended EQUAL' "$O/runbook.log")" "SENT:SENT END:EQUAL|ATTEMPT:None END:EQUAL|2|2" \
   "$(grep 'A2-EVIDENCE-B: ' "$O/runbook.log" | tail -n 1 | cut -c1-200)"
step "NL: step 9 after NE: the guard reads this boot's EQUAL read and the launch goes on"
prelaunch
r=$(launch NL)
ok "$r|$(started)|$(has '^identity: aifoundry1 card 1 booted .*, before the firmware read of .*: ok$' "$S/NL.txt")|$(has 'A2-GUARD: ' "$S/NL.txt")|$(has '^\[s11_session_a2_e215\] e215 arm B launched' "$S/NL.txt")" "0|started|1|1|1" "$(line '^identity: ' "$S/NL.txt")"
[ "$r" = 0 ] || tail -n 30 "$S/NL.txt"
step "EVX: the helper's evidence alone (read only) on a copy of NE's ledger and attempt log (fix-a2e213)"
X="$S/evx"; mkdir -p "$X/tree/build/e215" "$X/ledger" "$X/locks"
( cd "$T" && rsync -a -R tools/claims-v3/fwgate/fwgate.py tools/claims-v3/fwgate/records "$A/fwgate_e215a2.py" "$X/tree/" )
cp "$NER/aifoundry1/.local/state/fwgate/aifoundry1-c1.jsonl" "$X/ledger/aifoundry1-c1.jsonl"
cp "$NER/aifoundry1/nekko/build/e215/a2-fwgate-attempts-aifoundry1-c1.jsonl" "$X/tree/build/e215/"
evx() {  # evx [<box>]: the helper's evidence in X's tree, NE's boot, X's ledger; its output in X/out.txt; prints "rc <exit>"
  ( cd "$X/tree" && env FWGATE_DESK_TEST=1 FWGATE_CLI="$T/tools/claims-v3/fwgate/tests/fwcli-standin" FWGATE_ETWHO="$T/tools/claims-v3/fwgate/tests/etwho-standin" \
      FWGATE_LOCKDIR="$X/locks" FWGATE_LEDGER_DIR="$X/ledger" FWGATE_HOSTNAME=aifoundry1 FWGATE_BOOT_EPOCH="$AFTER" FWGATE_BOOT_ID="desk-NE-$AFTER" \
      /usr/bin/python3 -I -B "$A/fwgate_e215a2.py" evidence --box "${1:-aifoundry1}" --card 1 --dir "build/e215/fwgate-B-$TODAY" > "$X/out.txt" 2>&1; echo "rc $?" )
}
xs() { cat "$X/ledger/aifoundry1-c1.jsonl" "$X/tree/build/e215/a2-fwgate-attempts-aifoundry1-c1.jsonl" | sha256sum | cut -c1-16; }
u0=$(xs); a=$(evx); u1=$(xs)
xa="$a $(grep -c '^A2-LEDGER ' "$X/out.txt") $(grep -c '^A2-ATTEMPT ' "$X/out.txt") $(has 'one call on this boot, ended EQUAL$' "$X/out.txt") $( [ "$u0" = "$u1" ] && echo unchanged || echo written)"
/usr/bin/python3 - "$X/ledger/aifoundry1-c1.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
e = dict(json.loads(open(p).readline())); e["boot_id"] = "desk-another-boot"; e["boot_epoch"] = 1790000000
open(p, "a").write(json.dumps(e, sort_keys=True) + "\n")
PY
b=$(evx); xb="$b $(grep -c '^A2-LEDGER ' "$X/out.txt") $(has 'one call on this boot, ended EQUAL$' "$X/out.txt")"
echo 'not a ledger line' >> "$X/ledger/aifoundry1-c1.jsonl"
c=$(evx); xc="$c $(has '1 line\(s\) of another form \(aifoundry1-c1\.jsonl:4\).*NOT one EQUAL call on this boot: read the lines$' "$X/out.txt")"
cp "$NER/aifoundry1/.local/state/fwgate/aifoundry1-c1.jsonl" "$X/ledger/aifoundry1-c1.jsonl"; head -n 1 "$X/ledger/aifoundry1-c1.jsonl" >> "$X/ledger/aifoundry1-c1.jsonl"
d=$(evx); xd="$d $(has '\(SENT 2, END 1: EQUAL\).*NOT one EQUAL call on this boot' "$X/out.txt")"
e=$(evx aifoundry2); xe="$e $(has '^A2-EVIDENCE: NOT READ: --box aifoundry2 is not this host' "$X/out.txt") $(grep -cE '^A2-(LEDGER|ATTEMPT) ' "$X/out.txt")"
ok "$xa|$xb|$xc|$xd|$xe" "rc 0 2 2 1 unchanged|rc 0 2 1|rc 0 1|rc 0 1|rc 16 1 0" "$(grep -m1 '^A2-EVIDENCE: ' "$X/out.txt" | cut -c1-160)"

step "CT: a boot BEFORE E82's read: CONTINUITY, no read; step 9 launches"
newcase CT "$BEFORE_TEXT" "$BEFORE"
r=$(look CT); prelaunch; r9=$(launch CT9)
ok "$r|$(clin)|$( [ -d "$R/aifoundry1/nekko/build/e215/fwgate-B-$TODAY" ] && echo dir || echo nodir)|$(has 'A2-LOOK-B: CONTINUITY' "$O/e215-a2-look-B.txt")|$r9|$(started)|$(has "^identity: aifoundry1 card 1 booted .*, before E82's firmware read of .*: ok$" "$S/CT9.txt")" \
   "0|0|nodir|1|0|started|1" "$(line 'A2-LOOK: ' "$S/CT.txt"); $(line '^identity: ' "$S/CT9.txt")"
step "CT-EV: the evidence on a continuity day: no line of this boot in either file"
ok "$(evf ledger)|$(evf attempts)|$(evsum)|$(has 'A2-EVIDENCE-B: evidence: .*: 0 line\(s\) of this boot .*: 0 line\(s\) of this boot .*: no call on this boot' "$O/runbook.log")" "empty|empty|2|1" \
   "$(line 'A2-EVIDENCE-B: ' "$O/runbook.log" 240)"

step "EV: the evidence call fails on the box (a stand-in box python3 refusing the 'evidence' subcommand alone): never a gate (fix-a2e213)"
newcase EV "$AFTER_TEXT" "$AFTER"
cp "$BB/python3" "$S/python3.bak"
printf '#!/bin/sh\ncase " $* " in *" evidence "*) echo "desk test: the evidence call fails here"; exit 1 ;; esac\nexec /usr/bin/python3 "$@"\n' > "$BB/python3"
r=$(look EV)
cp "$S/python3.bak" "$BB/python3"
prelaunch; r9=$(launch EV9)
ok "$r|$(clin)|$( [ -e "$O/e215-a2-evidence-B" ] && echo made || echo none)|$(has 'A2-EVIDENCE-B: evidence NOT CAPTURED by this call \(exit 1: no A2-EVIDENCE line\)' "$O/runbook.log")|$(has 'A2-LOOK-B: EQUAL fwgate-aifoundry1-c1-[0-9]{8}-[0-9]{6}\.json; .*; evidence NOT CAPTURED by this call' "$O/e215-a2-look-B.txt")|$r9|$(started)" \
   "0|1|none|1|1|0|started" "$(line 'A2-EVIDENCE-B: ' "$O/runbook.log" 240)"

stopcase() {  # stopcase <tag> <want step-4 exit> <want CLI calls>: step 4, step 4 again, then step 9 with a forced look file: IDENTITY-STOP
  local tag=$1 r r2 r9
  r=$(look "$tag"); local c1; c1=$(clin)
  r2=$(look "$tag-2"); local c2; c2=$(clin)
  prelaunch; forcelook; r9=$(launch "$tag-9")
  ok "$r|$c1|$r2|$c2|$r9|$(started)|$(has '^\[s11_session_a2_e215\] STOP: IDENTITY-STOP' "$S/$tag-9.txt")" "$2|$3|16|$3|16|not-started|1" \
     "step 4: $(line '\] STOP: ' "$S/$tag.txt" 230); again: $(line '\] STOP: ' "$S/$tag-2.txt" 160); step 9: $(line '\] STOP: ' "$S/$tag-9.txt" 200)"
}
step "DF: DIFFERENT (card 0's PMIC in the answer)"
newcase DF "$AFTER_TEXT" "$AFTER" "$S/answer-different.txt"
stopcase DF 16 1
ok "$(recf "$(rec)" verdict)|$(attlog)" "DIFFERENT|ATTEMPT END=DIFFERENT" "the record and the attempt log"
step "UR: UNREADABLE (no success line)"
newcase UR "$AFTER_TEXT" "$AFTER" "$S/answer-unreadable.txt"
stopcase UR 16 1
ok "$(recf "$(rec)" verdict)|$(attlog)" "UNREADABLE|ATTEMPT END=UNREADABLE" "the record and the attempt log"
step "CS: a cut-off SENT in fwgate's ledger (this boot, no END)"
newcase CS "$AFTER_TEXT" "$AFTER"
mkdir -p "$R/aifoundry1/.local/state/fwgate"
printf '{"at": 1795000000.0, "at_text": "2026-11-18 06:00:00 PST", "boot": "2026-11-17 16:46:32 PST", "boot_epoch": %s, "boot_id": "%s", "box": "aifoundry1", "card": 1, "desk_test": true, "event": "SENT", "record": "%s/fwgate-aifoundry1-c1-20261118-060000.json", "schema": "fwgate-ledger/1", "verdict": "SENT"}\n' \
  "$AFTER" "$BID" "$R/aifoundry1/nekko/build/e215/fwgate-B-$TODAY" > "$R/aifoundry1/.local/state/fwgate/aifoundry1-c1.jsonl"
stopcase CS 16 0
ok "$(has 'STOPPED: a firmware read of aifoundry1 card 1 on this boot' "$S/CS.txt")|$(attlog)" "1|none" "fwgate's look read the cut-off SENT; no attempt made"
step "BL: a BUSY LOCK (card 0's lock held by another process during the read)"
newcase BL "$AFTER_TEXT" "$AFTER"
exec 9<>"$LD/etsoc-shire0.lock"; flock -n 9 || echo "the test could not hold the lock"
r=$(look BL); c1=$(clin); a1=$(attlog)
exec 9>&-
r2=$(look BL-2); c2=$(clin); prelaunch; forcelook; r9=$(launch BL-9)
ok "$r|$c1|$a1|$r2|$c2|$(has 'an attempt of this boot did not end EQUAL|a read attempt of this boot did not end EQUAL' "$S/BL-2.txt")|$r9|$(started)" "16|0|ATTEMPT END=NOT-SENT-17|16|0|1|16|not-started" \
   "step 4: $(line '\] STOP: ' "$S/BL.txt" 200); again, the lock free: $(line '\] STOP: ' "$S/BL-2.txt" 160)"
step "BW: a BUSY et-who (et-who --check rc 1)"
newcase BW "$AFTER_TEXT" "$AFTER"; setenv FWGATE_STANDIN_ETWHO_RC 1
stopcase BW 16 0
ok "$(has 'HELD: the card is held' "$S/BW.txt")|$(attlog)" "1|ATTEMPT END=NOT-SENT-17" "fwgate's read: HELD, nothing sent"
step "ML: a MISSING LOCK FILE (card 0's)"
newcase ML "$AFTER_TEXT" "$AFTER"; rm -f "${LD:?}/etsoc-shire0.lock"
stopcase ML 16 0
ok "$(has 'etsoc-shire0.lock is missing' "$S/ML.txt")|$( [ -e "$LD/etsoc-shire0.lock" ] && echo made || echo not-made)|$(attlog)" "1|not-made|ATTEMPT END=NOT-SENT-17" "fwgate never makes a lock file"
step "NG: the guard with NO EQUAL OF THIS BOOT (no read made; a forced look file)"
newcase NG "$AFTER_TEXT" "$AFTER"; prelaunch; forcelook
( cd "$T" && rsync -a -R tools/claims-v3/fwgate/fwgate.py tools/claims-v3/fwgate/records "$A/fwgate_e215a2.py" "$R/aifoundry1/nekko/" )   # A2's box files there, as step 4 syncs them
r9=$(launch NG)
ok "$r9|$(started)|$(has 'IDENTITY-STOP: aifoundry1 card 1 booted .*not before E82' "$S/NG.txt")|$(clin)" "16|not-started|1|0" "$(line '\] STOP: ' "$S/NG.txt" 220)"
step "SB: A STALE EQUAL OF AN EARLIER BOOT (NE's read, then the box booted again)"
O=$NEO; R=$NER; echo "$R" > "$S/boxroot"; CLI="$S/cli-NE.jsonl"
rm -f "${R:?}/aifoundry1/launched.txt"
cp "$S/fwenv.ne" "$S/fwenv"
setenv FWGATE_BOOT_EPOCH 1795003200; setenv FWGATE_BOOT_ID desk-SB-reboot; echo "2026-11-18 04:00:00" > "$S/boot-text"
r9=$(launch SB)
ok "$r9|$(started)|$(has 'IDENTITY-STOP: aifoundry1 card 1 booted .*not before E82' "$S/SB.txt")|$(has 'not on this boot, not used' "$S/SB.txt")" "16|not-started|1|1" "$(line '\] STOP: ' "$S/SB.txt" 220)"
step "SD: A STALE EQUAL OF AN EARLIER DAY on the same boot (fwgate's clock a day on)"
cp "$S/fwenv.ne" "$S/fwenv"; echo "$AFTER_TEXT" > "$S/boot-text"; rm -f "${R:?}/aifoundry1/launched.txt"
setenv FWGATE_NOW_EPOCH "$(( $(date +%s) + 86400 ))"
r9=$(launch SD)
ok "$r9|$(started)|$(has 'not written today \(Pacific\), not used' "$S/SD.txt")" "16|not-started|1" "$(line '\] STOP: ' "$S/SD.txt" 220)"
step "RS: THE REST RULE before the read (a session of ours ended 10 minutes ago), then rested (50 minutes)"
newcase RS "$AFTER_TEXT" "$AFTER"
L="$R/aifoundry1/nekko/build/e199/T1794000000/session.log"; mkdir -p "$(dirname "$L")"
{ echo "$(date -d '-15 min' '+%F %T %Z') session start"; echo "$(date -d '-10 min' '+%F %T %Z') session end"; } > "$L"; touch -d '-10 min' "$L"
r=$(look RS); c1=$(clin); a1=$(attlog)
{ echo "$(date -d '-55 min' '+%F %T %Z') session start"; echo "$(date -d '-50 min' '+%F %T %Z') session end"; } > "$L"; touch -d '-50 min' "$L"
r2=$(look RS-2)
ok "$r|$c1|$a1|$(has 'REFUSED: 10 minutes since' "$S/RS.txt")|$r2|$(clin)|$(attlog)" "10|0|none|1|0|1|ATTEMPT END=EQUAL" "$(line '\] STOP: ' "$S/RS.txt" 200); rested: $(line 'A2-READ: ' "$S/RS-2.txt" 120)"
step "BH: both cards held before the read (the box's et-who --check reads held for the whole wait): 17, nothing read, no attempt"
newcase BH "$AFTER_TEXT" "$AFTER"; echo 1 > "$S/box-etwho-check-rc"
t0=$(date +%s); r=$(look BH); dt_=$(( $(date +%s) - t0 ))
echo 0 > "$S/box-etwho-check-rc"
ok "$r|$(clin)|$(attlog)|$(has 'A2-HELD: et-who --check has not read free' "$S/BH.txt")|$( [ -f "$O/hold-a2-aifoundry1.since" ] && echo since || echo none)|$( [ "$dt_" -ge 25 ] && echo waited || echo short)" \
   "17|0|none|1|since|waited" "$(line 'A2-HELD: ' "$S/BH.txt" 200) ($dt_ s; the desk test's wait 25 s)"
r2=$(look BH-2)
ok "$r2|$(clin)|$(attlog)|$( [ -f "$O/hold-a2-aifoundry1.since" ] && echo since || echo none)" "0|1|ATTEMPT END=EQUAL|none" "freed: $(line 'A2-READ: ' "$S/BH-2.txt" 160)"
step "PB: fwgate.py changed on the box after step 4: the launch guard's pins stop it"
newcase PB "$AFTER_TEXT" "$AFTER"
r=$(look PB); prelaunch; echo "# changed on the box" >> "$R/aifoundry1/nekko/tools/claims-v3/fwgate/fwgate.py"
r9=$(launch PB)
ok "$r|$r9|$(started)|$(has "IDENTITY-STOP: A2's box files are not at their pinned sha256" "$S/PB.txt")" "0|16|not-started|1" "$(line '\] STOP: ' "$S/PB.txt" 220)"
step "PD: A2's helper changed (uncommitted) in the lab clone: step 4 stops before any call reaches the box"
newcase PD "$AFTER_TEXT" "$AFTER"
cp "$T/$A/fwgate_e215a2.py" "$S/helper.bak"; echo "# an uncommitted change" >> "$T/$A/fwgate_e215a2.py"
m0=$(cnt "$S/calls.log"); r=$(look PD); m1=$(cnt "$S/calls.log")
cp "$S/helper.bak" "$T/$A/fwgate_e215a2.py"; $G checkout -q -- "$A/fwgate_e215a2.py"
ok "$r|$((m1 - m0))|$(clin)|$(git -C "$T" status --porcelain | grep -c .)" "16|0|0|0" "$(line '\] STOP: ' "$S/PD.txt" 200)"
step "AA: arm A is refused by A2's three steps"
newcase AA "$AFTER_TEXT" "$AFTER"
m0=$(cnt "$S/calls.log")
a=$(RB_OUT=$O RB_DESKTEST=1 bash "$T/$A/rb/s05_look_e215_a2.sh" A > "$S/AA1.txt" 2>&1; echo $?)
b=$(RB_OUT=$O RB_DESKTEST=1 bash "$T/$A/rb/s11_session_e215_a2.sh" A > "$S/AA2.txt" 2>&1; echo $?)
c=$(RB_OUT=$O RB_DESKTEST=1 bash "$T/$A/rb/s23_data_e215_a2.sh" A > "$S/AA3.txt" 2>&1; echo $?)
m1=$(cnt "$S/calls.log")
ok "$a $b $c $((m1 - m0)) $(has "arm B's alone" "$S/AA1.txt")" "10 10 10 0 1" "$(line 'STOP' "$S/AA1.txt" 160)"

step "DT: step 12's addition (data_e215a2.py) on a stand-in data directory"
DT=$S/dt; mkdir -p "$DT"
mkdata() {  # mkdata <dir>: a stand-in directory with SHA256SUMS in collect_e215.py's form
  mkdir -p "$1/session"; echo '{"stand-in": true}' > "$1/data-e215.json"; echo "stand-in" > "$1/reduce-e215.txt"; echo "a session file" > "$1/session/session.log"
  ( cd "$1" && find . -type f ! -name SHA256SUMS | sed 's#^\./##' | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$1.sums" && mv "$1.sums" "$1/SHA256SUMS"
}
dt() { RB_DESKTEST=1 /usr/bin/python3 -I -B "$T/$A/data_e215a2.py" add "$@"; }
mkdata "$DT/a"; s0=$(sha256sum "$DT/a/SHA256SUMS" | cut -d' ' -f1)
ra=$(dt "$DT/a" "$NEO/e215-a2-fwgate-B" "$NEO/e215-a2-fwgate-B.sha256" "$NEO/box-home-B-a2.txt" "$NEO/box-login-aifoundry1.txt" "$NEO/e215-a2-look-B.txt" > "$S/DTa.txt" 2>&1; echo $?)
sc=$(cd "$DT/a" && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$'); nf=$(find "$DT/a" -type f ! -name SHA256SUMS | wc -l | tr -d ' ')
RJ=$(ls "$DT/a/fwgate"/fwgate-aifoundry1-c1-*.json 2>/dev/null | head -n 1)
rawok=$(/usr/bin/python3 -c 'import json,sys,hashlib,os; r=json.load(open(sys.argv[1])); d=os.path.dirname(sys.argv[1]); print(all(hashlib.sha256(open(os.path.join(d, r["raw"][k]["file"]),"rb").read()).hexdigest()==r["raw"][k]["sha256"] for k in ("stdout","stderr")))' "$RJ" 2>/dev/null)
ok "$ra|$sc|$nf|$(recf "$RJ" ledger)|$rawok|$(has '^A2-DATA ADDED fwgate/: 3 files' "$S/DTa.txt")" "0|$nf|$nf|$(printf '%s/.local/state/fwgate/aifoundry1-c1.jsonl' '~')|True|1" "$(line '^A2-DATA' "$S/DTa.txt" 260)"
mkdata "$DT/b"; s0=$(sha256sum "$DT/b/SHA256SUMS" | cut -d' ' -f1)
rb_=$(dt "$DT/b" "$S/out-CT/e215-a2-fwgate-B" "$S/out-CT/e215-a2-fwgate-B.sha256" "$S/out-CT/box-home-B-a2.txt" "$S/out-CT/box-login-aifoundry1.txt" "$S/out-CT/e215-a2-look-B.txt" > "$S/DTb.txt" 2>&1; echo $?)
ok "$rb_|$( [ -e "$DT/b/fwgate" ] && echo added || echo none)|$( [ "$(sha256sum "$DT/b/SHA256SUMS" | cut -d' ' -f1)" = "$s0" ] && echo same || echo changed)|$(has '^A2-DATA CONTINUITY' "$S/DTb.txt")" "0|none|same|1" "$(line '^A2-DATA' "$S/DTb.txt" 200)"
mkdata "$DT/c"; s0=$(sha256sum "$DT/c/SHA256SUMS" | cut -d' ' -f1); cp -a "$NEO/e215-a2-fwgate-B" "$DT/copy-c"; printf ' ' >> "$(ls "$DT/copy-c"/*.stderr | head -n 1)"
rc_=$(dt "$DT/c" "$DT/copy-c" "$NEO/e215-a2-fwgate-B.sha256" "$NEO/box-home-B-a2.txt" "$NEO/box-login-aifoundry1.txt" "$NEO/e215-a2-look-B.txt" > "$S/DTc.txt" 2>&1; echo $?)
ok "$rc_|$( [ -e "$DT/c/fwgate" ] && echo added || echo none)|$( [ "$(sha256sum "$DT/c/SHA256SUMS" | cut -d' ' -f1)" = "$s0" ] && echo same || echo changed)|$(has 'not the box.s folder any more' "$S/DTc.txt")" "3|none|same|1" "$(line '^A2-DATA' "$S/DTc.txt" 200)"
mkdata "$DT/d"; s0=$(sha256sum "$DT/d/SHA256SUMS" | cut -d' ' -f1); cp -a "$NEO/e215-a2-fwgate-B" "$DT/copy-d"; echo "seen at $(printf '/%s/%s/x' home someone-else)" > "$DT/copy-d/note.txt"   # another login's home path, built here
cp "$NEO/e215-a2-fwgate-B.sha256" "$DT/list-d"; ( cd "$DT/copy-d" && sha256sum note.txt ) >> "$DT/list-d"
rd=$(dt "$DT/d" "$DT/copy-d" "$DT/list-d" "$NEO/box-home-B-a2.txt" "$NEO/box-login-aifoundry1.txt" "$NEO/e215-a2-look-B.txt" > "$S/DTd.txt" 2>&1; echo $?)
ok "$rd|$( [ -e "$DT/d/fwgate" ] && echo added || echo none)|$( [ "$(sha256sum "$DT/d/SHA256SUMS" | cut -d' ' -f1)" = "$s0" ] && echo same || echo changed)|$(has 'THE SCRUB left' "$S/DTd.txt")" "3|none|same|1" "$(line '^A2-DATA' "$S/DTd.txt" 200)"
re_=$(/usr/bin/python3 -I -B "$T/$A/data_e215a2.py" add docs/reports/data/2026-11-18-e215-blind-matmul-aifoundry3 "$NEO/e215-a2-fwgate-B" "$NEO/e215-a2-fwgate-B.sha256" "$NEO/box-home-B-a2.txt" "$NEO/box-login-aifoundry1.txt" "$NEO/e215-a2-look-B.txt" > "$S/DTe.txt" 2>&1; echo $?)
ok "$re_|$(has "is not E215 arm B's data directory" "$S/DTe.txt")" "3|1" "$(line '^A2-DATA' "$S/DTe.txt" 200)"
step "DT f-h: step 12's addition with step 4's evidence of the one call (fix-a2e213): added after the scrub, or left out and said, never a refusal"
EVN=fwgate-ledger-aifoundry1-c1-this-boot.jsonl; EVA=a2-fwgate-attempts-aifoundry1-c1-this-boot.jsonl
mkdata "$DT/f"
rf=$(dt "$DT/f" "$NEO/e215-a2-fwgate-B" "$NEO/e215-a2-fwgate-B.sha256" "$NEO/box-home-B-a2.txt" "$NEO/box-login-aifoundry1.txt" "$NEO/e215-a2-look-B.txt" "$NEO/e215-a2-evidence-B" > "$S/DTf.txt" 2>&1; echo $?)
scf=$(cd "$DT/f" && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$'); nff=$(find "$DT/f" -type f ! -name SHA256SUMS | wc -l | tr -d ' ')
recm=$(/usr/bin/python3 -c 'import json,sys; L=[json.loads(x) for x in open(sys.argv[1]) if x.strip()]; print(len(L) == 2 and all(e["record"].startswith("~" + "/") for e in L))' "$DT/f/fwgate/$EVN" 2>/dev/null)
ok "$rf|$scf|$nff|$(evf ledger "$DT/f/fwgate")|$(evf attempts "$DT/f/fwgate")|$(cat "$DT/f/fwgate/$EVN" "$DT/f/fwgate/$EVA" 2>/dev/null | grep -c "$(printf '/%s/' home)")|$recm|$(has "^A2-DATA ADDED fwgate/: 3 files .*the evidence of the one call: fwgate/$EVN \(2 line\(s\)\) and fwgate/$EVA \(2 line\(s\)\), this boot's, through the kit's scrub; SHA256SUMS made again: 8 entries \(3 the kit's and 5 A2's\)" "$S/DTf.txt")" \
   "0|8|8|SENT:SENT END:EQUAL|ATTEMPT:None END:EQUAL|0|True|1" "$(line '^A2-DATA' "$S/DTf.txt" 300)"
mkdata "$DT/g"; cp -a "$NEO/e215-a2-evidence-B" "$DT/ev-g"; cp "$NEO/e215-a2-evidence-B.sha256" "$DT/ev-g.sha256"; printf ' ' >> "$DT/ev-g/$EVN"
rg=$(dt "$DT/g" "$NEO/e215-a2-fwgate-B" "$NEO/e215-a2-fwgate-B.sha256" "$NEO/box-home-B-a2.txt" "$NEO/box-login-aifoundry1.txt" "$NEO/e215-a2-look-B.txt" "$DT/ev-g" > "$S/DTg.txt" 2>&1; echo $?)
ok "$rg|$(find "$DT/g/fwgate" -type f 2>/dev/null | wc -l | tr -d ' ')|$(cd "$DT/g" && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$')|$(has "the evidence of the one call: changed since step 4 or not whole \(differs $EVN\) \(left out\)" "$S/DTg.txt")" \
   "0|3|6|1" "$(line '^A2-DATA' "$S/DTg.txt" 300)"
mkdata "$DT/h"; cp -a "$NEO/e215-a2-evidence-B" "$DT/ev-h"; echo "{\"seen\": \"$(printf '/%s/%s/x' home someone-else)\"}" >> "$DT/ev-h/$EVA"   # another login's home path, built here
( cd "$DT/ev-h" && sha256sum "$EVN" "$EVA" ) > "$DT/ev-h.sha256"
rh=$(dt "$DT/h" "$NEO/e215-a2-fwgate-B" "$NEO/e215-a2-fwgate-B.sha256" "$NEO/box-home-B-a2.txt" "$NEO/box-login-aifoundry1.txt" "$NEO/e215-a2-look-B.txt" "$DT/ev-h" > "$S/DTh.txt" 2>&1; echo $?)
ok "$rh|$(find "$DT/h/fwgate" -type f 2>/dev/null | wc -l | tr -d ' ')|$(cd "$DT/h" && sha256sum -c SHA256SUMS 2>&1 | grep -c ': OK$')|$(has "the evidence of the one call: left out \(THE SCRUB left a home path, the login or another login's holder line in fwgate/$EVA\)" "$S/DTh.txt")" \
   "0|3|6|1" "$(line '^A2-DATA' "$S/DTh.txt" 300)"

step "DRY: A2's dry listing (arm B as amended)"
mkdir -p "$S/listing"
( cd "$T" && bash "$A/rb/list_steps_e215_a2.sh" "$S/listing" > "$S/DRY.txt" 2>&1 )
ok "$(has '^dry listing \(A2, arm B\): 15 steps listed, 0 exited non-zero, 0 box calls$' "$S/DRY.txt")" 1 "$(tail -n 1 "$S/DRY.txt")"

step "Z: no process of this test left running"
sleep 1
left=$(ps -eo pid=,args= | grep -E 'session_e215\.sh|fwcli-standin|fwgate\.py|rb_run\.py' | grep -v grep | grep -c .)
ok "$left" 0 "processes left: $left"
echo
echo "the stand-ins' calls: $(grep -c '^ssh ' "$S/calls.log") ssh, $(grep -c '^rsync ' "$S/calls.log") rsync (all to the stand-in aifoundry1)"
echo "SELFTEST-A2-E215 $npass of $ncase $( [ "$fail" = 0 ] && echo PASS || echo FAIL)"
[ "$fail" = 0 ]
}
main
