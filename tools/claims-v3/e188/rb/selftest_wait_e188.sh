#!/usr/bin/env bash
# E188 (Q182, the kit's dated note 2, KIT.md.dated-note-2.md, Sun 15 Nov 2026, before any E188 datum): the desk test of step 10
# (rb/s20_wait_e188.sh, 726a6b64, UNCHANGED) on the REAL session script's name, with E183's and E190's two step-10 lessons. E183's step 10 v1
# looked for "session_e183\.sh", which its session v2 (session_e183_v2.sh) never matched: it read RUN-GONE while the session ran (Fri 13 Nov
# 2026). E190's step 10 v2 read every session that passed its identity gate as GATE-STOPPED, because one of its gate phrases is also in
# the pass line. No desk test of E188's kit had run step 10 (the runbook test's case L reads it once, on a session already ended at a gate).
# Here step 10 runs whole (rb_init, the probe, one bounded remote wait through k6's rb_run.py) against a stand-in aifoundry3: a FAKE ssh
# that runs the remote script with `bash -s` in a local directory laid out as the box's ~/aifoundry, and refuses any other host or command.
# The box's pgrep is the real one, so the test runs in a private PID namespace of its own (bubblewrap, re-executing itself; no /dev/et*,
# refused if one is visible), where the only processes are its own.
#   W0  the launch line of step 9 v2 (and v1) starts `bash tools/claims-v3/e188/session_e188.sh` from the tree's top: the name step 10's
#       pattern `session_$RUN\.sh` (RUN=e188) must see;
#   W1  THE REAL SESSION SCRIPT (session_e188.sh, a byte copy at its path on the stand-in box), launched with step 9 v2's own words from the
#       tree's top (`setsid nohup bash tools/claims-v3/e188/session_e188.sh`, its window's gates set), held at its harness check by a
#       stand-in python3 that waits to be released: the real pgrep lists exactly that process; step 10 reads RUN-RUNNING (17);
#   W2  released, the stand-in fails the harness check (exit 9, as check_e188.py fails), so the session writes "harness check failed: no
#       device opened", "session end" and its MANIFEST.sha256: step 10 reads RUN-ENDED, MANIFEST-WRITTEN and GATE-STOPPED (16);
#   W3  a second real session, held, then killed with SIGKILL (no session end): RUN-GONE (14);
#   W4  only other names running, each launched the same way (session_e1880.sh, session_e186.sh, queue_e188.sh, block_e188.sh), beside a
#       log with no session end: RUN-GONE (14): step 10 follows the session, which alone writes "session end" and the manifest;
#   W5  E190'S LESSON, a desk read of code: step 10's GATE-STOPPED pattern (read from its text) matches every stop line of session_e188.sh
#       (each stop_now message and the two gate lines) and no other line the session writes (its say lines); and no file the box session
#       runs (harness-e188.json's list) prints any of the pattern's three phrases but session_e188.sh's own stop lines;
#   W6  step 10's dry listing: the remote script with the pattern, exit 0, no call;
#   Z   no stand-in left in the namespace; no rsync or scp; the lock file untouched.
# The real session of W1-W3 stops at its harness check: no config read, no card lock, no device tool (the sandbox has no /dev/et*).
#   bash tools/claims-v3/e188/rb/selftest_wait_e188.sh <scratch dir outside the repository> > <log>
# Prints SELFTEST-WAIT-E188 PASS or FAIL (<n> of <m>). About a minute and a half (each running case waits one 15 s loop of the step).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
case "$S" in *session_e18*|*queue_e18*|*block_e18*) echo "the scratch directory's path must not name a session, a queue or a block"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible here: run this test only inside a no-device sandbox"; exit 2; }
if [ "${E188WT_INNER:-}" != 1 ]; then
  [ -x /usr/bin/bwrap ] || { echo "no /usr/bin/bwrap (bubblewrap)"; exit 2; }
  mkdir -p "$S" || exit 2
  SELF=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")
  E188WT_INNER=1 exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --unshare-pid --proc /proc --die-with-parent -- \
    /bin/bash "$SELF" "$S"
fi
for v in RB_DRY RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
date --version 2> /dev/null | head -n 1 | grep -q 'GNU coreutils' || { echo "this test needs GNU date as date (the session's own forms)"; exit 2; }
S=$(cd "$S" && pwd)
ME=$(id -un)
main() {
rm -rf "${S:?}/box" "${S:?}/bin" "${S:?}/held" "${S:?}/out" "${S:?}/pids"
BOX=$S/box/aifoundry3; BT=$BOX/aifoundry; BIN=$S/bin; HB=$S/held
mkdir -p "$BT/build/q141k" "$BT/build/e188" "$BT/tools/claims-v3/e188" "$BIN" "$HB" "$S/out" "$S/pids"
cp -p "$SRC/tools/claims-v3/e188/session_e188.sh" "$BT/tools/claims-v3/e188/session_e188.sh"
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
[ "\$host" = aifoundry3 ] || { echo "STAND-IN SSH: refusing host \$host" >&2; exit 97; }
[ "\$cmd" = true ] && exit 0
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: refusing the command \$cmd" >&2; exit 97; }
cd "$BOX" && HOME="$BOX" exec bash -s
EOF
for n in rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/calls.log" "$n" > "$BIN/$n"; done
# the held session's python3 (first on that session's PATH only): its first call is the harness check, which waits here until released
cat > "$HB/python3" <<EOF
#!/bin/bash
echo "\$\$" > "$S/pids/held-python3-\$\$.pid"; : > "$S/held.flag"
while [ ! -e "$S/release" ]; do sleep 0.2; done
echo "harness check: the desk-test stand-in held it, then failed it (exit 9, as check_e188.py does on a changed file)"
exit 9
EOF
chmod +x "$BIN"/* "$HB/python3"
standin() {  # standin <name>: a small script at tools/claims-v3/e188/<name> that records its pid and waits to be stopped
  printf '#!/bin/bash\necho $$ > "%s/pids/%s.pid"\nwhile :; do sleep 1; done\n' "$S" "$1" > "$BT/tools/claims-v3/e188/$1"
}
for n in session_e1880.sh session_e186.sh queue_e188.sh block_e188.sh; do standin "$n"; done
launch() {  # launch <name> [<T0>]: as step 9 v2 launches (its words, from the tree's top), the held python3 first on PATH
  ( cd "$BT" && E188_T0=${2:-0} E188_PLAN=FULL E188_TRAINS=yes E188_LATEST_START="$(date -d '+1 hour' '+%F %T')" E188_DEADLINE="$(date -d '+2 hour' '+%F %T')" \
      PATH="$HB:$PATH" setsid -f nohup bash "tools/claims-v3/e188/$1" > build/e188/session.out 2>&1 < /dev/null )
}
stopall() { local f p; for f in "$S"/pids/*.pid; do [ -e "$f" ] || continue; p=$(cat "$f"); kill "$p" 2> /dev/null; rm -f "$f"; done; sleep 1.5; }
fresh_t0() { local t; t=$(date +%s); while [ "$(date +%s)" -eq "$t" ]; do sleep 0.1; done; date +%s; }
held() { local k; for k in $(seq 1 50); do [ -e "$S/held.flag" ] && return 0; sleep 0.2; done; return 1; }
export PATH="$BIN:$PATH" RB_OUT="$S/out" RB_LOCK="$S/lock.txt" RB_WAIT_LOOP_S=3
: > "$S/calls.log"; : > "$RB_LOCK"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
R=$SRC/tools/claims-v3/e188/rb
wait10() { bash "$R/s20_wait_e188.sh" > "$S/w.out" 2>&1; local r=$?; grep -E '^(RUN-|GATE-|MANIFEST-)|STOP|still runs|has ended' "$S/w.out" | cut -c1-170; return "$r"; }
seen() { echo "visible in this namespace: $(pgrep -c -f '(session|queue|block)_e18') process(es) by the names; by step 10's pattern 'session_e188\.sh': $(pgrep -a -f 'session_e188\.sh' | sed 's/^[0-9]* //' | tr '\n' ';')"; }
newrun() { T0=$1; echo "$T0" > "$BT/build/q141k/e188.T0"; echo "$T0" > "$RB_OUT/e188-T0.txt"; }

step "W0. step 9's launch line (v2, and v1) starts bash tools/claims-v3/e188/session_e188.sh from the tree's top"
l2=$(grep -c 'setsid nohup bash tools/claims-v3/e188/session_e188.sh > build/e188/session.out 2>&1 < /dev/null &$' "$R/s11_a3_session_e188_v2.sh")
l1=$(grep -c 'setsid nohup bash tools/claims-v3/e188/session_e188.sh > build/e188/session.out 2>&1 < /dev/null &$' "$R/s11_a3_session_e188.sh")
pt=$(grep -c 'pgrep -u "$(id -u)" -f "session_$RUN\\.sh"' "$R/s20_wait_e188.sh"); rn=$(grep -c '^run=e188; box=aifoundry3$' "$R/s20_wait_e188.sh")
grep -o 'setsid nohup bash tools/claims-v3/e188/session_e188.sh' "$R/s11_a3_session_e188_v2.sh"; grep -o 'pgrep -u "$(id -u)" -f "session_$RUN\\.sh"' "$R/s20_wait_e188.sh"
ok "$l2.$l1.$pt.$rn" "1.1.1.1" "W0 the launch line starts session_e188.sh by that name; step 10's pattern is session_\$RUN\\.sh with RUN=e188"

step "W1. the REAL session_e188.sh, launched with step 9 v2's words, held at its harness check"
newrun "$(fresh_t0)"; rm -f "$S/held.flag" "$S/release"
launch session_e188.sh "$T0"; held; echo "held at its harness check: $([ -e "$S/held.flag" ] && echo yes || echo NO)"; seen
np=$(pgrep -f 'session_e188\.sh' | grep -c .); cmdl=$(pgrep -a -f 'session_e188\.sh' | sed 's/^[0-9]* //' | head -n 1)
sed 's/^[0-9-]* [0-9:]* [A-Z]* //' "$BT/build/e188/T$T0/session.log" | cut -c1-150
wait10; rc=$?
ok "$rc.$np.$([ "$cmdl" = 'bash tools/claims-v3/e188/session_e188.sh' ] && echo 1 || echo 0).$(grep -c "^RUN-RUNNING e188" "$S/w.out")" "17.1.1.1" "W1 the real pgrep lists exactly 'bash tools/claims-v3/e188/session_e188.sh'; step 10 reads RUN-RUNNING (17)"

step "W2. released: the session stops at its harness check, writes its session end and its manifest"
: > "$S/release"
for k in $(seq 1 50); do [ -s "$BT/build/e188/T$T0/MANIFEST.sha256" ] && break; sleep 0.2; done
sleep 1
grep -E 'harness check failed|session end' "$BT/build/e188/T$T0/session.log" | sed 's/^[0-9-]* [0-9:]* [A-Z]* //'
wait10; rc=$?
ok "$rc.$(grep -c '^RUN-ENDED e188' "$S/w.out").$(grep -c '^MANIFEST-WRITTEN' "$S/w.out").$(grep -c '^GATE-STOPPED e188' "$S/w.out").$(pgrep -f 'session_e188\.sh' | grep -c .)" "16.1.1.1.0" \
  "W2 step 10 reads RUN-ENDED, MANIFEST-WRITTEN and GATE-STOPPED (16) for a session that stopped at a gate; no session process left"

step "W3. a second real session, held, then killed with SIGKILL before its session end"
newrun "$(fresh_t0)"; rm -f "$S/held.flag" "$S/release"; stopall
launch session_e188.sh "$T0"; held; seen
pk=$(pgrep -f 'session_e188\.sh' | head -n 1); kill -KILL "$pk" 2> /dev/null; sleep 0.5; : > "$S/release"; sleep 0.5; stopall
echo "after SIGKILL: $(pgrep -f 'session_e188\.sh' | grep -c .) process(es) by the pattern; session end in its log: $(grep -c 'session end' "$BT/build/e188/T$T0/session.log")"
wait10; rc=$?
ok "$rc.$(grep -c '^RUN-GONE e188' "$S/w.out")" "14.1" "W3 step 10 reads RUN-GONE (14): no session process and no session end"

step "W4. only other names running, launched the same way, beside a log with no session end"
newrun "$(fresh_t0)"; mkdir -p "$BT/build/e188/T$T0"
echo "$(date '+%F %T %Z') session start (budget anchor T0 x; plan FULL; trains yes; its files in build/e188/T$T0)" > "$BT/build/e188/T$T0/session.log"
for n in session_e1880.sh session_e186.sh queue_e188.sh block_e188.sh; do launch "$n"; done
sleep 1; seen
wait10; rc=$?; stopall
ok "$rc.$(grep -c '^RUN-GONE e188' "$S/w.out")" "14.1" "W4 step 10 reads RUN-GONE (14) with session_e1880.sh, session_e186.sh, queue_e188.sh and block_e188.sh running: it follows the session alone"

step "W5. E190's lesson (a desk read of code): step 10's GATE-STOPPED pattern against every line the session writes, and the session's files"
/usr/bin/python3 -I -B - "$SRC" > "$S/w5.out" 2>&1 <<'PYEOF'
import json, os, re, sys
src = sys.argv[1]
E = os.path.join(src, "tools/claims-v3/e188")
wait = open(os.path.join(E, "rb/s20_wait_e188.sh")).read()
pat = re.search(r"if grep -qE '([^']+)' \"\$L\" 2>/dev/null; then echo \"GATE-STOPPED \$RUN\"", wait).group(1)
rx = re.compile(pat)
sess = open(os.path.join(E, "session_e188.sh")).read()
def dq(rest):  # a double-quoted shell word's text, up to its closing quote (quotes inside $( ... ) do not close it)
    i, depth = 0, 0
    while i < len(rest):
        if rest.startswith("$(", i):
            depth += 1; i += 2; continue
        c = rest[i]
        if c == "\\":
            i += 2; continue
        if c == ")" and depth:
            depth -= 1
        elif c == '"' and not depth:
            return rest[:i]
        i += 1
    return rest
def calls(word):  # each call's message (the first word after the command name)
    out = []
    for ln in sess.splitlines():
        if ln.lstrip().startswith("#"):
            continue
        for m in re.finditer(r'(?<![a-z_])' + word + r' "', ln):
            out.append(dq(ln[m.end():]))
    return out
stops = calls("stop_now")
says = [s for s in calls("say") if s != "$1"]
gate_says = [s for s in says if s.startswith(("stop-path test failed", "smoke gate failed"))]
pass_says = [s for s in says if s not in gate_says]
bad_stop = [s for s in stops + gate_says if not rx.search(s)]
bad_pass = [s for s in pass_says if rx.search(s)]
print(f"step 10's GATE-STOPPED pattern: {pat}")
print(f"session_e188.sh: {len(stops)} stop_now messages and {len(gate_says)} gate lines, every one matched: {not bad_stop}; "
      f"{len(pass_says)} other say lines, none matched: {not bad_pass}")
for s in bad_stop + bad_pass:
    print(f"  MISREAD: {s[:120]}")
h = json.load(open(os.path.join(E, "harness-e188.json")))
files = sorted({f for k, v in h.items() if k.endswith("_sha256") and k != "box_binaries_sha256" and isinstance(v, dict) for f in v})
phr = pat.split("|")
hits, read = {}, 0
for f in files:
    p = os.path.join(src, f)
    if not os.path.isfile(p) or f.endswith(".bin"):
        continue
    try:
        text = open(p, encoding="utf-8").read()
    except UnicodeDecodeError:
        continue
    read += 1
    for i, ln in enumerate(text.splitlines(), 1):
        if ln.lstrip().startswith("#"):
            continue
        if any(x in ln for x in phr):
            hits.setdefault(f, []).append(i)
others = {f: v for f, v in hits.items() if not f.endswith("e188/session_e188.sh")}
print(f"the text files harness-e188.json names: {read} read (of {len(files)}); lines outside comments holding a phrase of the pattern: "
      + ("; ".join(f"{f} {len(v)}" for f, v in sorted(hits.items())) or "none") + f"; in any file but session_e188.sh: {len(others)}")
good = not bad_stop and not bad_pass and not others and len(stops) >= 9 and len(gate_says) == 2 and read >= 30
print("W5-RESULT", "OK" if good else "BAD")
PYEOF
cat "$S/w5.out"
ok "$(grep -c '^W5-RESULT OK$' "$S/w5.out")" 1 "W5 the GATE-STOPPED pattern reads every stop line of session_e188.sh and none of its other lines; no other file the session runs prints any of its phrases"

step "W6. step 10's dry listing"
n0=$(grep -c . "$S/calls.log")
RB_DRY=1 bash "$R/s20_wait_e188.sh" > "$S/w6.out" 2>&1; rc=$?
grep -F 'pgrep -u "$(id -u)" -f "session_$RUN\.sh"' "$S/w6.out" | sed 's/^ *| *//' | cut -c1-140
ok "$rc.$(grep -cF 'pgrep -u "$(id -u)" -f "session_$RUN\.sh"' "$S/w6.out").$(grep -c '^    | RUN=e188; LIM=' "$S/w6.out").$(( $(grep -c . "$S/calls.log") - n0 ))" "0.1.1.0" "W6 the listing shows the pattern with RUN=e188 and makes no call"

step "Z. no stand-in left in this namespace; no rsync or scp; the lock file untouched"
stopall
left=$(pgrep -c -f '(session|queue|block)_e18'); nl=$(grep -c . "$RB_LOCK"); nn=$(grep -c -E '^(rsync|scp) ' "$S/calls.log")
echo "processes by those names left: $left; lock file lines: $nl; rsync or scp calls: $nn; ssh calls: $(grep -c '^ssh ' "$S/calls.log")"
ok "$left.$nl.$nn" "0.0.0" "Z"
echo
echo "SELFTEST-WAIT-E188 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase): step 10 reads the real session_e188.sh running (17), gone (14) and stopped at a gate (16); its gate pattern reads no passing line"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g; s#$HOME#<home>#g; s#\\b$ME\\b#<login>#g"
exit "${PIPESTATUS[0]}"
