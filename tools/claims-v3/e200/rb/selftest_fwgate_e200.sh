#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): the desk test of THE REBOOT GATE as E200's runbook calls it (E200.md
# 8): the lab's fwgate (tools/claims-v3/fwgate/fwgate.py, d5beec9b, run unchanged) in steps 4, 7 and 9, on the path the runbook test cannot
# take (rb/selftest_rb_e200.sh runs with /dev/et0_ops and /dev/et0_mgmt as regular files, where fwgate refuses its desk mode, so its box
# reads CONTINUITY from a stand-in record): NEEDS-READ, fwgate's one firmware read, its record in step 7's folder, step 9's guard over it,
# and the stops. fwgate runs in ITS OWN DESK MODE (FWGATE_DESK_TEST=1 with every stand-in it requires: its committed tests/fwcli-standin
# for the vendor CLI answering E72's committed answer or a changed one, tests/etwho-standin, a scratch lock folder and a scratch ledger
# folder, never the real ones), inside a bubblewrap of its own with no /dev/et* at all (run it inside W/nodev.sh), a private /run/lock with
# the card's lock file, a private PID namespace and the host name aifoundry2. The runbook's steps run as the card lane runs them, from the
# lab clone this test sits in (RB_REPO; nothing in it is written: RB_OUT, the box and the stand-ins are under the scratch), with a stand-in
# ssh serving a stand-in aifoundry2 box under the scratch (its tree ~/claude/et-soc1-prototyping, E200's root synced from the lab clone by
# harness_e200.py's list, today's build and dry-pass records as steps 6 and 8 leave them) and the kit's stand-in reader (fake_card_e200.py,
# the wrapper's desk-test pin E200_DESKTEST=1 / E200_READER_SHA256). No lab box is reached; nothing opens a device.
#   FW1  step 4, the look: fwgate's look (the desk) reads NEEDS-READ (the box booted after E72's record), FREE, exit 0
#   FW2  step 7: the rest, the stamp (FWGATE=read), fwgate's read (the stand-in answers E72's committed answer): EQUAL, its record in step
#        7's folder, ONE call to the stand-in CLI (exactly `-m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000`, the lock held), then the
#        config read: 0
#   FW3  step 7 again (after a 17, say): the read already made: never a second read on this boot (the CLI still called once), fwgate's guard
#        over the folder ok, the config read again: 0, the stamp kept
#   FW4  step 9: fwgate's guard --extra <step 7's folder>: "identity: ... ok", LAUNCHED with E200_FWGATE=read and E200_FIRSTDIR (the wrapper
#        then stops at its node count: this sandbox has no card node; the session log says so)
#   FW5  a DIFFERENT answer (PMIC 1.6.1), a new RB_OUT and ledger: step 7: 16, the record DIFFERENT, NO config read sent; FW6 then step 4:
#        16 (fwgate's ledger: STOPPED for this boot); FW7 step 9 over FW5's folder: IDENTITY-STOP, 16, nothing launched
#   FW8  the card held at fwgate's read (its et-who stand-in exit 1), a fresh ledger: step 7: 17, the CLI never called, no config read
#   bash tools/claims-v3/e200/rb/selftest_fwgate_e200.sh <scratch dir> > <log>      (prints SELFTEST-FWGATE-E200 <n> of <m> PASS or FAIL)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
if [ -z "${E200_FW_INNER:-}" ]; then
  for p in /dev/et*; do [ -e "$p" ] && { echo "REFUSED: $p exists here: run this test inside the no-device sandbox (W/nodev.sh)"; exit 2; }; done
  mkdir -p "$S" && S=$(cd "$S" && pwd)
  [ -z "$(ls -A "$S")" ] || { echo "give an empty scratch directory"; exit 2; }
  exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --unshare-pid --proc /proc --unshare-uts --hostname aifoundry2 \
    --die-with-parent --setenv E200_FW_INNER 1 -- /bin/bash "$SRC/tools/claims-v3/e200/rb/selftest_fwgate_e200.sh" "$S"
fi
E=tools/claims-v3/e200
R=$SRC/$E/rb
BOXH=$S/box/aifoundry2; TREE=$BOXH/claude/et-soc1-prototyping; BIN=$S/bin; BB=$S/boxbin; ST=$S/box-state
mkdir -p "$TREE/build" "$BIN" "$BB" "$ST" "$S/fwlocks"
: > /run/lock/etsoc-shire0.lock; : > "$S/fwlocks/etsoc-shire0.lock"
npass=0; ncase=0; fail=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-300; }
echo "E200 fwgate desk test, $(date '+%F %T %Z'), $(/usr/bin/python3 --version 2>&1); inside its sandbox: host $(hostname), /dev/et*: $(ls /dev/et* 2>/dev/null | wc -l) entries"
# ---- the stand-ins: ssh and rsync to the stand-in box, its tools
REAL_RSYNC=$(command -v rsync); REAL_PGREP=$(command -v pgrep)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry2) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: only 'true' and 'bash -s', not '\$cmd'" >&2; exit 97; }
cd "$BOXH" || exit 1
exec /usr/bin/env HOME="$BOXH" PATH="$BB:/usr/bin:/bin" E200_STANDIN_DIR="$ST" USER=$(id -un) LOGNAME=$(id -un) bash -s
EOF
for n in rsync scp sudo; do printf '#!/bin/sh\necho "STAND-IN: %s refused" >&2\nexit 97\n' "$n" > "$BIN/$n"; done
FAKE=$SRC/$E/fake_card_e200.py
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s etwho "$@"\n' "$FAKE" > "$BB/et-who"
printf '#!/bin/sh\necho aifoundry2\n' > "$BB/hostname"
cat > "$BB/pgrep" <<EOF
#!/bin/bash
out=""
for q in \$("$REAL_PGREP" "\$@"); do c=\$(readlink "/proc/\$q/cwd" 2>/dev/null) || continue; case "\$c/" in "$BOXH"/*) out="\$out\$q
" ;; esac; done
[ -n "\$out" ] || exit 1
printf '%s' "\$out"
EOF
cat > "$BB/ps" <<EOF_PS
#!/bin/bash
[ "\$*" = "-eo uid=,pid=,comm=" ] || [ "\$*" = "-eo uid=,comm=" ] || exec /usr/bin/ps "\$@"
/usr/bin/ps -eo uid=,pid=,comm= | while read -r u p c; do d=\$(readlink "/proc/\$p/cwd" 2>/dev/null) || continue; case "\$d/" in "$BOXH"/*) if [ "\$*" = "-eo uid=,comm=" ]; then echo "\$u \$c"; else echo "\$u \$p \$c"; fi ;; esac; done
EOF_PS
chmod +x "$BIN"/* "$BB"/*
# ---- the stand-in box tree: E200's root synced from the lab clone (harness_e200.py's list), the stand-in reader, today's records
RT=$TREE/build/claims-v3/aifoundry2/e200
( cd "$SRC" && /usr/bin/python3 -I -B $E/harness_e200.py --list ) | while IFS= read -r p; do mkdir -p "$RT/$(dirname "$p")"; cp -p "$SRC/$p" "$RT/$p"; done
mkdir -p "$TREE/build/ettelem-hpl" "$RT/build/regfile/host" "$TREE/build/q141k/jobs"
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s sampler "$@"\n' "$FAKE" > "$TREE/build/ettelem-hpl/ettelem"; chmod +x "$TREE/build/ettelem-hpl/ettelem"
printf '#!/bin/bash\nexec /usr/bin/python3 -I -B %s host "$@"\n' "$FAKE" > "$RT/build/regfile/host/regfile_host"; chmod +x "$RT/build/regfile/host/regfile_host"
{ echo "REGFILE-BUILT $(date '+%F %T %Z')"; echo "kernel x"; echo "text x"; echo "host $(sha256sum "$RT/build/regfile/host/regfile_host" | cut -d' ' -f1)"; } > "$RT/build/regfile-built.txt"
echo "REGFILE-BUILT rc=0" > "$TREE/build/q141k/jobs/a2-build-e200.out"
for j in a2-dry-e200-1 a2-build-e200; do echo 0 > "$TREE/build/q141k/jobs/$j.rc"; done
echo '{}' > "$ST/scenario.json"
export E200_DESKTEST=1 E200_READER_SHA256=$(sha256sum "$TREE/build/ettelem-hpl/ettelem" | cut -d' ' -f1)
# ---- fwgate's desk mode: its own stand-ins (committed with it), a scratch lock folder and ledger, this boot after E72's record
export FWGATE_DESK_TEST=1 FWGATE_CLI="$SRC/tools/claims-v3/fwgate/tests/fwcli-standin" FWGATE_ETWHO="$SRC/tools/claims-v3/fwgate/tests/etwho-standin"
export FWGATE_LOCKDIR="$S/fwlocks" FWGATE_LEDGER_DIR="$S/ledger-1" FWGATE_HOSTNAME=aifoundry2 FWGATE_BOOT_EPOCH=$(( $(date +%s) - 3600 ))
export FWGATE_STANDIN_LOG="$S/cli.log" FWGATE_STANDIN_LOCKS="$S/fwlocks/etsoc-shire0.lock" FWGATE_STANDIN_ETWHO_LOG="$S/fw-etwho.log"
/usr/bin/python3 -I -B - "$SRC" "$S/answer-e72.txt" "$S/answer-diff.txt" <<'PY'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("fwgate", sys.argv[1] + "/tools/claims-v3/fwgate/fwgate.py")
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
t = F.section_text(sys.argv[1] + "/docs/reports/data/2026-10-27-e72-600mhz/gov.jsonl", jsonl_line=2, pointer="queries.firmware.out")
open(sys.argv[2], "w").write(t)
d = t.replace("PMIC Firmware versions: Major: 1 Minor: 5 Revision: 0", "PMIC Firmware versions: Major: 1 Minor: 6 Revision: 1")
assert d != t
open(sys.argv[3], "w").write(d)
PY
export FWGATE_STANDIN_OUT="$S/answer-e72.txt"
export PATH="$BIN:$PATH" RB_LOCK="$S/lock.txt" RB_QUIET="$S/quiet-flag"
: > "$S/lock.txt"; : > "$S/cli.log"
bash "$R/quiet_e200.sh" raise e200-fw-desktest > /dev/null
TODAY=$(TZ=America/Los_Angeles date +%F)
win() { mkdir -p "$1"; RB_OUT="$1" bash "$R/s02_window_e200.sh" 1 "$TODAY" 21:59 23:59 > /dev/null 2>&1
        printf 'REGFILE-BUILT rc=0\n' > "$1/e200-built.txt"; echo "E200-DRY sitting 1 plan full rc=0 LISTING SAME" > "$1/e200-1-dry-ok.txt"; }
cfgcalls() { local n; n=$(grep -c '"mode": "config"' "$ST/calls/sampler.log" 2>/dev/null); echo "${n:-0}"; }
clicalls() { local n; n=$(grep -c . "$S/cli.log" 2>/dev/null); echo "${n:-0}"; }

step "FW1. step 4: fwgate's look reads NEEDS-READ at the desk (no device); the box FREE"
win "$S/out-1"
RB_OUT="$S/out-1" bash "$R/s05_look_e200.sh" > "$S/fw1.txt" 2>&1; f1=$?
grep -E 'NEEDS-READ|FREE|STOP' "$S/fw1.txt" | cut -c1-220
ok "$f1.$(has '^NEEDS-READ: aifoundry2 card 0' "$S/out-1/e200-fwgate-look.txt").$(has 'FREE' "$S/fw1.txt").$(clicalls)" "0.1.1.0" "FW1 the look: NEEDS-READ, FREE, nothing sent"

step "FW2. step 7: the stamp, fwgate's read EQUAL into step 7's folder (one CLI call, the lock held), then the config read"
c0=$(cfgcalls)
RB_OUT="$S/out-1" bash "$R/s09_reads_e200.sh" 1 > "$S/fw2.txt" 2>&1; f2=$?
grep -E 'sitting 1:|EQUAL|STOP|aifoundry2 card 0:' "$S/fw2.txt" | cut -c1-240
F1=$(sed -n 's/^FIRST=//p' "$S/out-1/e200-1-first.txt" 2>/dev/null)
FD=$TREE/build/e200/first-s1-$F1
rec=$(ls "$FD"/fwgate-aifoundry2-c0-*.json 2>/dev/null | head -n 1)
v=$([ -n "$rec" ] && /usr/bin/python3 -I -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["verdict"])' "$rec")
argv=$(/usr/bin/python3 -I -B -c 'import json,sys; e=[json.loads(l) for l in open(sys.argv[1]) if l.strip()]; print(len(e), " ".join(e[0]["argv"]) if e else "", e[0]["locks"].get("etsoc-shire0.lock") if e else "")' "$S/cli.log")
ok "$f2.$(has 'FWGATE=read' "$S/out-1/e200-1-first.txt").$v.$argv.$(($(cfgcalls) - c0)).$([ -s "$FD/config.out" ] && echo 1 || echo 0)" \
  "0.1.EQUAL.1 -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000 held.1.1" "FW2 the read EQUAL, its record in step 7's folder, one CLI call exactly as fwgate writes it with the card's lock held, one config read kept there"

step "FW3. step 7 again: no second read on this boot; fwgate's guard over the folder; the config read again"
RB_OUT="$S/out-1" bash "$R/s09_reads_e200.sh" 1 > "$S/fw3.txt" 2>&1; f3=$?
F1b=$(sed -n 's/^FIRST=//p' "$S/out-1/e200-1-first.txt")
ok "$f3.$(has 'never a second read on this boot' "$S/fw3.txt").$(clicalls).$([ "$F1" = "$F1b" ] && echo kept || echo moved)" "0.1.1.kept" "FW3 again: the read not repeated (one CLI call in all), the stamp kept"

step "FW4. step 9: fwgate's guard over step 7's folder reads the identity ok; launched (the wrapper then meets this sandbox's missing card nodes)"
RB_OUT="$S/out-1" bash "$R/s11_session_e200.sh" 1 > "$S/fw4.txt" 2>&1; f4=$?
grep -E 'identity:|LAUNCHED|STOP' "$S/fw4.txt" | cut -c1-240
T0=$(cat "$S/out-1/e200-1-T0.txt" 2>/dev/null)
k=0; while [ "$k" -lt 30 ] && ! grep -q 'session end' "$TREE/build/e200/T$T0/session.log" 2>/dev/null; do sleep 1; k=$((k + 1)); done
sl=$TREE/build/e200/T$T0/session.log
ok "$f4.$(has 'identity: aifoundry2 card 0 booted .*: ok' "$S/fw4.txt").$(has 'LAUNCHED e200-1' "$S/fw4.txt").$(has 'GATE-STOP: refused: the card nodes here are' "$sl").$(clicalls)" \
  "0.1.1.1.1" "FW4 step 9 past fwgate's guard (identity ok over the read's record), launched; the wrapper stops at the node count in this node-less sandbox"

step "FW5-FW7. a DIFFERENT answer: step 7 stops (16) with no config read; then the look and step 9 stop for this boot"
export FWGATE_LEDGER_DIR="$S/ledger-2" FWGATE_STANDIN_OUT="$S/answer-diff.txt"
win "$S/out-2"
RB_OUT="$S/out-2" bash "$R/s05_look_e200.sh" > /dev/null 2>&1
c0=$(cfgcalls); n0=$(clicalls)
RB_OUT="$S/out-2" bash "$R/s09_reads_e200.sh" 1 > "$S/fw5.txt" 2>&1; f5=$?
stopline "$S/fw5.txt"
F2=$(sed -n 's/^FIRST=//p' "$S/out-2/e200-1-first.txt" 2>/dev/null)
rec2=$(ls "$TREE/build/e200/first-s1-$F2"/fwgate-aifoundry2-c0-*.json 2>/dev/null | head -n 1)
v2=$([ -n "$rec2" ] && /usr/bin/python3 -I -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["verdict"])' "$rec2")
RB_OUT="$S/out-2" bash "$R/s05_look_e200.sh" > "$S/fw6.txt" 2>&1; f6=$?
stopline "$S/fw6.txt"
RB_OUT="$S/out-2" bash "$R/s11_session_e200.sh" 1 > "$S/fw7.txt" 2>&1; f7=$?
stopline "$S/fw7.txt"
ok "$f5.$v2.$(($(clicalls) - n0)).$(($(cfgcalls) - c0)).$(has 'did not read EQUAL' "$S/fw5.txt").$f6.$(has 'STOPPED' "$S/fw6.txt").$f7.$(has 'IDENTITY-STOP' "$S/fw7.txt").$(has 'LAUNCHED' "$S/fw7.txt")" \
  "16.DIFFERENT.1.0.1.16.1.16.1.0" "FW5 the read DIFFERENT: 16, no config read sent; FW6 the look then: 16 (STOPPED for this boot); FW7 step 9: IDENTITY-STOP, 16, nothing launched"

step "FW8. the card held at fwgate's read (a fresh ledger): step 7 17, nothing sent"
export FWGATE_LEDGER_DIR="$S/ledger-3" FWGATE_STANDIN_OUT="$S/answer-e72.txt" FWGATE_STANDIN_ETWHO_RC=1
sleep 1.2; win "$S/out-3"
c0=$(cfgcalls); n0=$(clicalls)
RB_OUT="$S/out-3" bash "$R/s09_reads_e200.sh" 1 > "$S/fw8.txt" 2>&1; f8=$?
stopline "$S/fw8.txt"
unset FWGATE_STANDIN_ETWHO_RC
ok "$f8.$(($(clicalls) - n0)).$(($(cfgcalls) - c0)).$(has 'nothing sent' "$S/fw8.txt")" "17.0.0.1" "FW8 the card held at the read: 17 (call again), the CLI never called, no config read"

step "Z. nothing left on the stand-in box"
left=$("$REAL_PGREP" -u "$(id -u)" -f 'session_e200\.sh|run_trains\.py|fake_card_e200\.py' | while read -r q; do c=$(readlink "/proc/$q/cwd" 2>/dev/null); case "$c/" in "$BOXH"/*) echo "$q" ;; esac; done | grep -c .)
ok "$left" "0" "Z no session or stand-in of this test left running"
echo; echo "SELFTEST-FWGATE-E200 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
[ "$fail" -eq 0 ]
