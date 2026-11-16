#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): THE SESSION'S WRAPPER on aifoundry3. Step 9
# (rb/s11_a3_session_e196.sh) starts it detached (setsid nohup) after k6's guard, THE REST RULE, today's dry pass and today's build; step 8
# (rb/s10_a3_dry_e196.sh) runs it with --dry. It runs THE LAB PORT of the proposal's reference session (run_session_e196.sh, which runs
# run_block_e196.py, the proposal's stopwatch.py and the lab's stops_e196.py; KIT.md section 1 says why a port), driven with the box's own
# tools, and adds only what E196.md section 17.2 asks of the kit, each through the registered stop file (OUT/STOP), never by editing,
# killing or re-ordering:
#   - before anything opens a card node (exit 2, "no device opened"): the host's name is aifoundry3 (hostname and Python's); USER is the
#     login; the registration's list at 467ede78... and the six registered files the session reads at their pins; the kit's list at the sha256 the
#     runbook passes and the kit's session files at their pins; the shared files at theirs; both hosts present and the ones today's build
#     recorded (build/BUILD-E196.txt in E196's root, written today, both kernels' .text 8798e43c...); the preflight GO; ONE CARD'S NODES
#     ONLY (exactly /dev/et0_ops and /dev/et0_mgmt, by name); the window's last end;
#   - THE FIRST CARD COMMAND, stamped as it starts (E193 kit's reading): the free check (et-who --check exit 0, no other user's device
#     process, a probe of the existing card lock, read-only, never created); the cap (60 card-minutes) and the window count from it;
#   - THE CUT ORDER (E196.md section 6): M = the minutes from the first card command to the earlier of the window's last end and the cap;
#     M >= 43: every arm, the passes that fit (passes 0-6 asked; the deadline cuts: six expected at M >= 53, five at 43-53); 40 <= M < 43:
#     DROP_ARMS=F.Ae,Z.b50,I.H.mFFFF; M < 40: no session ("no device opened");
#   - THE DEADLINE (E196.md section 10): DEADLINE = the first card command + 58 minutes, or the window's last end - 2 minutes if earlier;
#     no block starts that cannot end before it (run_session's own rule); THE END-STOP: STOPS_END_EPOCH = the first card command + the cap
#     - 60 s (or the last end - 60 s, if earlier): stops_e196.py writes STOP then, so the closing read fits inside the cap;
#   - the kits' session log (build/e196/T<T0>/session.log: "session start", "session end (T0 <T0>)"; every rest rule of ours reads it),
#     how the session ended ("GATE-STOP:" when no train or pass block ran: no data; "session stopped: ...; the blocks done stand" after a
#     registered stop; "session ended without a registered stop" for a crash), MANIFEST.sha256 last, session.rc after it.
# The box layout: E196's root R = <tree>/build/claims-v3/aifoundry3/e196 holds the synced files at their repository paths and both builds
# (R/build/sparsity-lab, the lab's unchanged workloads/sparsity; R/build/x14, the request's proposal/src); the session writes
# build/e196/T<T0>/ (the port's OUT is its run/ directory). The box's tools: the sampler build/ettelem/ettelem through E128's guard
# (R/tools/claims-v3/e128/ettelem_guard.sh, synced: it refuses --reset-ms and every word but config and sample); et-who; flock; timeout.
#   E196_T0=<epoch> E196_DEADLINE_EPOCH=<epoch> E196_KITLIST_SHA256=<sha256> bash <R>/tools/claims-v3/e196/session_e196.sh
#   E196_T0=<epoch> E196_KITLIST_SHA256=<sha256> bash <R>/tools/claims-v3/e196/session_e196.sh --dry       (nothing opened)
# Desk-test variables, read ONLY with E196_DESKTEST=1 (the card day never sets it; the session start line names it when set): E196_CAP_S
# (a shorter cap). Set without E196_DESKTEST=1 it is refused before anything.
# Exit codes: 0 ended (every block asked, or the deadline); 1 a registered stop after data (a live stop, a holder between blocks, the end-
# stop, a stop by hand); 2 a refusal before anything (no device opened); 3 the card not free (no device opened) or a gate stop (no train
# and no pass block ran: no data); 4 ended without a registered stop (a crash: a dated note decides); 16 the dry listing did not check.
# SPDX-License-Identifier: Apache-2.0
set -u
R=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)
TREE=$(cd "$R/../../../.." && pwd -P)
cd "$TREE" || exit 2
RR=${R#"$TREE"/}
DRY=; [ "${1:-}" = --dry ] && DRY=1
T0=${E196_T0:-}
case "$T0" in ''|*[!0-9]*) echo "E196_T0 must be the launch's epoch seconds"; exit 2 ;; esac
OUTD=build/e196/T$T0; [ -n "$DRY" ] && OUTD=$OUTD-dry
[ -e "$OUTD" ] && { echo "$OUTD exists: one session a T0"; exit 2; }
mkdir -p "$OUTD/run" || exit 2
LOG=$OUTD/session.log
say() { echo "$(date '+%Y-%m-%d %H:%M:%S %Z') ${DRY:+DRY }$*" | tee -a "$LOG"; }
KIT=$RR/tools/claims-v3/e196
H=$RR/build/x14/host/x14_host
LAB_H=$RR/build/sparsity-lab/host/sparsity_host
ETTELEM=$RR/tools/claims-v3/e128/ettelem_guard.sh
LAB_TILES=$RR/tools/claims-v3/kinds/tiles/fp32
REG_LIST=$KIT/SHA256SUMS-e196-registration
REG_LIST_SHA=467ede7827f5ed33df6c883c9641caccb1e10ed78f88fbadc322a15a90137ce5
LOCK=/run/lock/etsoc-shire0.lock
PASSES=7; CAP_S=3600; GAP=30
CUT_ARMS=F.Ae,Z.b50,I.H.mFFFF
REGF='  tools/claims-v3/e196/(proposal/src/(make_x14\.py|arms\.json|stopwatch\.py)|desk/(order-e196-aifoundry3\.txt|order-e196-aifoundry3-cut\.txt|commands-e196\.txt))$'
KITF='  tools/claims-v3/e196/(session_e196\.sh|run_session_e196\.sh|run_block_e196\.py|stops_e196\.py|e196_lines\.py|preflight_e196\.sh|drycheck_e196\.py)$'
DESK=
if [ "${E196_DESKTEST:-}" = 1 ]; then
  DESK=" DESKTEST"
  CAP_S=${E196_CAP_S:-$CAP_S}
fi
nodev() { say "refused: $* (no device opened)"; finish_files 2; exit 2; }
notfree() { say "the card is not free: $* (no device opened)"; finish_files 3; exit 3; }
finish_files() {  # the manifest last, then session.rc
  ( cd "$OUTD" && find . -type f ! -name 'MANIFEST.sha256*' ! -name session.rc | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) > "$OUTD/MANIFEST.sha256.tmp"
  mv "$OUTD/MANIFEST.sha256.tmp" "$OUTD/MANIFEST.sha256"
  echo "$1" > "$OUTD/session.rc"
}
say "session start (T0 $T0 = $(date -d @"$T0" '+%H:%M:%S %Z' 2>/dev/null); E196, the lab port of the proposal's reference session, kit-e196$DESK${DRY:+; DRY})"
# ---- refusals before anything opens a card node (both paths) -----------------------------------------------------------------
if [ "${E196_DESKTEST:-}" != 1 ]; then
  for v in E196_CAP_S; do
    [ -z "${!v:-}" ] || nodev "$v is a desk-test variable, read only with E196_DESKTEST=1 (the card day never sets it)"
  done
fi
hn=$(hostname 2>/dev/null); pyhn=$(python3 -I -B -c 'import socket; print(socket.gethostname())' 2>/dev/null)
[ "$hn" = aifoundry3 ] && [ "$pyhn" = aifoundry3 ] || nodev "this host is '$hn' (Python reads '$pyhn'), not aifoundry3: E196 runs on aifoundry3 card 0 (its order is aifoundry3's)"
[ -n "${USER:-}" ] && [ "$USER" = "$(id -un)" ] || nodev "USER is not this login (E183 kit note 6's carried rule)"
[ "$(sha256sum "$REG_LIST" 2>/dev/null | cut -d' ' -f1)" = "$REG_LIST_SHA" ] || nodev "the registration's list is not at its sha256 ${REG_LIST_SHA:0:12}"
( cd "$R" && grep -E "$REGF" tools/claims-v3/e196/SHA256SUMS-e196-registration | sha256sum -c --quiet - ) > "$OUTD/pins-registration.txt" 2>&1 ||
  nodev "a registered session file is off its sha256 ($(head -c 200 "$OUTD/pins-registration.txt"))"
[ "$(grep -cE "$REGF" "$REG_LIST")" = 6 ] || nodev "the registration's list does not name the six session files"
KL=$KIT/SHA256SUMS-e196-kit
[ -n "${E196_KITLIST_SHA256:-}" ] && [ "$(sha256sum "$KL" 2>/dev/null | cut -d' ' -f1)" = "$E196_KITLIST_SHA256" ] ||
  nodev "the kit's list is not at the sha256 the runbook passed (E196_KITLIST_SHA256)"
( cd "$R" && grep -E "$KITF" tools/claims-v3/e196/SHA256SUMS-e196-kit | sha256sum -c --quiet - ) > "$OUTD/pins-kit.txt" 2>&1 ||
  nodev "a kit session file is off its sha256 ($(head -c 200 "$OUTD/pins-kit.txt"))"
[ "$(grep -cE "$KITF" "$KL")" = 7 ] || nodev "the kit's list does not name the seven kit session files"
( cd "$R" && sha256sum -c --quiet tools/claims-v3/e196/SHA256SUMS-e196-shared ) > "$OUTD/pins-shared.txt" 2>&1 ||
  nodev "a shared file is off its sha256 ($(head -c 200 "$OUTD/pins-shared.txt"))"
for f in "$H" "$LAB_H" "$ETTELEM" build/ettelem/ettelem; do [ -x "$f" ] || nodev "no executable $f"; done
BREC=$RR/build/BUILD-E196.txt
[ -f "$BREC" ] && [ "$(TZ=America/Los_Angeles date -r "$BREC" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
  nodev "no build record written today ($BREC: step 6)"
for pair in "x14_host_sha256:$H" "lab_host_sha256:$LAB_H"; do
  k=${pair%%:*}; f=${pair#*:}
  [ "$(sha256sum "$f" | cut -d' ' -f1)" = "$(sed -n "s/^$k \([0-9a-f]\{64\}\)\$/\1/p" "$BREC")" ] || nodev "$f is not the binary today's build recorded ($k)"
done
grep -q '^E196-BUILT rc=0' "$BREC" && [ "$(grep -c '^kernel_text_sha256_.* 8798e43c4869a124690bc652d574d5ab78d686faa70293cbcff658d24c30a399$' "$BREC")" = 2 ] ||
  nodev "today's build record does not read E196-BUILT with both kernels' .text at 8798e43c... (E196.md section 11: no session)"
bash "$KIT/preflight_e196.sh" > "$OUTD/dmcmd-preflight.txt" 2>&1; prc=$?
[ "$prc" -eq 0 ] && grep -q '^E196-PREFLIGHT: GO' "$OUTD/dmcmd-preflight.txt" || nodev "the device-command audit is not GO (rc $prc)"
ops=""; for d in /dev/et*_ops; do [ -e "$d" ] && ops="$ops $d"; done
mgs=""; for d in /dev/et*_mgmt; do [ -e "$d" ] && mgs="$mgs $d"; done
[ "$ops" = " /dev/et0_ops" ] && [ "$mgs" = " /dev/et0_mgmt" ] ||
  nodev "the card nodes here are '${ops# }' and '${mgs# }', not exactly /dev/et0_ops and /dev/et0_mgmt: one card only, counted before anything opens a node"
sed -n 's/^\(x14_host_sha256\|lab_host_sha256\|kernel_elf_sha256_[a-z0-9]*\|kernel_text_sha256_[a-z0-9]*\) /\1 /p' "$BREC" > "$OUTD/hashes.txt"
echo "sampler build/ettelem/ettelem $(sha256sum build/ettelem/ettelem | cut -d' ' -f1)" >> "$OUTD/hashes.txt"
say "checked: host aifoundry3; USER the login; the registration's list ${REG_LIST_SHA:0:12} and its six session files; the kit's list and its seven session files; the shared files; both hosts today's build ($(grep -c . "$OUTD/hashes.txt") hashes in hashes.txt; both .text 8798e43c...); the sampler and E128's guard; dmcmd_audit GO; one card's nodes (/dev/et0_ops, /dev/et0_mgmt)"
export H LAB_H HEATER="$LAB_H" ETTELEM SAMPLER=ettelem GAP TARGET=58 PREHEAT=59 LOCK LAB_TILES TRAINS="T1 T2"
unset ET_DEVICES V3_DEVICE SAMPLER_S SESSION_MIN GEN DROP_ARMS
# ---- the dry path: the port's DRY mode, every device call listed, nothing opened ------------------------------------------------
if [ -n "$DRY" ]; then
  say "would run, the first card command: the free check (et-who --check; other users' device processes; a probe of $LOCK, read-only, never created)"
  say "would run: the cut order from M (the first card command to the earlier of the window's last end and the cap, $CAP_S s); DEADLINE = the first card command + $((CAP_S - 120)) s or the last end - 120 s; the end-stop at the cap - 60 s"
  rc=0
  DRY=1 DEADLINE=$(( $(date +%s) + CAP_S - 120 )) bash "$KIT/run_session_e196.sh" "$OUTD/run" 6 > "$OUTD/run_session.out" 2>&1 || rc=$?
  DRY=1 DROP_ARMS=$CUT_ARMS DEADLINE=$(( $(date +%s) + CAP_S - 120 )) bash "$KIT/run_session_e196.sh" "$OUTD/run-cut" 6 > "$OUTD/run_session-cut.out" 2>&1 || rc=$?
  python3 -I -B "$KIT/drycheck_e196.py" "$OUTD/run_session.out" "$OUTD/run_session-cut.out" "$KIT/desk" > "$OUTD/drycheck.txt" 2>&1; dc=$?
  say "the port's DRY mode: rc $rc; $(tail -n 1 "$OUTD/drycheck.txt")"
  say "session end (T0 $T0)"
  r=$rc; [ "$dc" -ne 0 ] && r=16
  finish_files "$r"; exit "$r"
fi
# ---- the real path -----------------------------------------------------------------------------------------------------------
LAST_END=${E196_DEADLINE_EPOCH:-}
case "$LAST_END" in ''|*[!0-9]*) nodev "no E196_DEADLINE_EPOCH (the window's last end)" ;; esac
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner.Worker$'
FIRST=$(date +%s); echo "$FIRST" > "$OUTD/first-card-command.txt"     # stamped as the first card command starts
o=$(timeout 30 et-who --check 2>&1); wrc=$?
printf '%s\n' "$o" | grep -cE '^(/dev/et|lock:)' > "$OUTD/etwho-start-holders.txt"
[ "$wrc" -eq 0 ] || notfree "et-who --check exit $wrc ($(printf '%s' "$o" | grep -cE '^(/dev/et|lock:)') holder lines)"
p=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 != me && $3 ~ re {n++} END {print n+0}')
[ "$p" -eq 0 ] || notfree "$p device process(es) of another user"
[ -e "$LOCK" ] || nodev "no card lock file $LOCK (the host makes it at boot; never created here)"
exec 9< "$LOCK"; flock -n -E 75 9; lrc=$?; flock -u 9 2>/dev/null; exec 9<&-
[ "$lrc" -eq 0 ] || notfree "the card lock is held (probe exit $lrc)"
CAPEND=$((FIRST + CAP_S)); EARLY=$CAPEND; [ "$LAST_END" -lt "$EARLY" ] && EARLY=$LAST_END
M=$(( (EARLY - FIRST) / 60 ))
if [ "$M" -lt 40 ]; then
  nodev "the cut order: M = $M minutes from the first card command to the earlier of the window's last end and the cap: M < 40, no session (E196.md section 6)"
elif [ "$M" -lt 43 ]; then
  export DROP_ARMS=$CUT_ARMS; plan="40 <= M < 43: DROP_ARMS=$CUT_ARMS (left out of every pass), the trains stay, the passes that fit"
elif [ "$M" -lt 53 ]; then
  unset DROP_ARMS; plan="43 <= M < 53: every arm, the passes that fit (five expected)"
else
  unset DROP_ARMS; plan="M >= 53: every arm, passes 0-5 and pass 6 if it fits"
fi
DEADLINE=$((FIRST + CAP_S - 120)); [ $((LAST_END - 120)) -lt "$DEADLINE" ] && DEADLINE=$((LAST_END - 120))
STOPS_END_EPOCH=$((FIRST + CAP_S - 60)); [ $((LAST_END - 60)) -lt "$STOPS_END_EPOCH" ] && STOPS_END_EPOCH=$((LAST_END - 60))
export DEADLINE STOPS_END_EPOCH
say "the first card command at $(date -d @"$FIRST" '+%H:%M:%S %Z'); the cap at $(date -d @"$CAPEND" '+%H:%M:%S %Z') ($CAP_S s); the window's last end $(date -d @"$LAST_END" '+%H:%M:%S %Z')"
say "the cut order: M = $M minutes: $plan; DEADLINE $(date -d @"$DEADLINE" '+%H:%M:%S %Z'); the end-stop $(date -d @"$STOPS_END_EPOCH" '+%H:%M:%S %Z')"
bash "$KIT/run_session_e196.sh" "$OUTD/run" "$PASSES" > "$OUTD/run_session.out" 2>&1 < /dev/null &
RS=$!
stopw() {  # stopw <why>: the registered stop file, written once (the first writer's reason stands)
  [ -e "$OUTD/run/STOP" ] || printf '{"by": "session_e196", "why": "%s", "t_ms": %s}\n' "$1" "$(date +%s%3N)" > "$OUTD/run/STOP"
}
trap 'stopw "a signal to the wrapper: the run in flight finishes"; say "signal: STOP written; waiting for the session to end"' TERM INT HUP
say "running: run_session_e196.sh (pid $RS)"
while kill -0 "$RS" 2>/dev/null; do sleep 1; done
wait "$RS"; rc=$?
if [ ! -e "$OUTD/run/SESSION_DONE" ]; then   # E192 kit's fix: the port exited before its EXIT trap (its refusals, its free check, the gate)
  printf '{"by": "session_e196", "why": "run_session_e196.sh exited (rc %s) before its own end marker", "t_ms": %s}\n' "$rc" "$(date +%s%3N)" > "$OUTD/run/SESSION_DONE"
  say "run_session_e196.sh exited (rc $rc) before its own end marker: the wrapper wrote run/SESSION_DONE"
fi
trap - TERM INT HUP
END=$(date +%s)
counts=$(python3 -I -B -c 'import json,sys,os
d=sys.argv[1]
def jl(f):
    out=[]
    p=os.path.join(d,f)
    if os.path.exists(p):
        for l in open(p):
            try: out.append(json.loads(l))
            except ValueError: pass
    return out
m=jl("marks.jsonl"); r=jl("runs.jsonl"); t=jl("train.jsonl")
passes=sorted({x["pass"] for x in m if x.get("kind")=="idle" and x.get("label")=="after" and 0<=x.get("pass",-1)<100})
trains=sorted({x["pass"] for x in m if x.get("kind")=="idle" and x.get("label")=="after" and x.get("pass",-1)>100})
data=sum(1 for x in r+t if x.get("pass",-1)>=0)
unread=sum(1 for x in m if x.get("kind")=="host_lines" and x.get("written") is False)
print(len(passes), len(trains), data, unread, len(r), len(t))' "$OUTD/run" 2>/dev/null)
read -r npass ntrain ndata nunread nruns ntrl <<< "${counts:-0 0 0 0 0 0}"
st=""; [ -e "$OUTD/run/STOP" ] && st=$(head -c 300 "$OUTD/run/STOP")
say "run_session_e196.sh rc $rc; the last lines of its log: $(tail -n 2 "$OUTD/run/session.log" 2>/dev/null | tr '\n' ' ' | cut -c1-300)"
[ -n "$st" ] && say "STOP: $st"
[ "${nunread:-0}" -gt 0 ] && say "unreadable host outputs: $nunread process(es) wrote no record (marks.jsonl, kind host_lines)"
if [ "$rc" -eq 0 ] && [ "${ndata:-0}" -gt 0 ]; then
  out=0
elif [ "${ndata:-0}" -eq 0 ]; then
  out=3
  if [ ! -e "$OUTD/run/config-start.json" ] && { [ "$rc" -eq 2 ] || [ "$rc" -eq 3 ]; }; then
    say "GATE-STOP: run_session_e196.sh rc $rc at its own refusals or free check, before its configuration read (no device opened)"
  else
    say "GATE-STOP: run_session_e196.sh rc $rc before any train or pass block (no data; E196.md section 11)${st:+; $st}"
  fi
elif [ -n "$st" ] || [ "$rc" -eq 3 ] || [ "$rc" -eq 5 ] || [ "$rc" -eq 75 ]; then
  out=1; say "session stopped: run_session_e196.sh rc $rc${st:+; stop: $st}; the blocks done stand (reduced as they stand)"
else
  out=4; say "session ended without a registered stop: run_session_e196.sh rc $rc, no stop recorded (a crash: report it, kill nothing; a dated note decides whether its blocks are reduced)"
fi
say "trains complete: $ntrain of 2; passes complete: $npass of $PASSES asked (pass 6 only if it fit); launch records $nruns pass, $ntrl train; card time $((END - FIRST)) s from the first card command (cap $CAP_S s)"
say "session end (T0 $T0)"
finish_files "$out"
exit "$out"
