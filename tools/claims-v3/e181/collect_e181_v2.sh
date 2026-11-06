#!/usr/bin/env bash
# E181 (M11's session 2): the collector v2, tools/claims-v3/e181/collect_e181.sh (33cdccf6, which stays as committed) with TWO changes, each
# marked v2 (the E181 kit verifier's fault 2, Fri 6 Nov 2026; the kit's README.md.dated-note-1.md):
#   1. a pass directory is copied only when it is on the box: one bounded read (ssh, timeout 60) asks whether build/claims-v3/aifoundry3/<pass dir>/
#      exists, and an absent one is named ("absent on the box: <pass dir>") instead of failing its rsync (rc 23). After an A6-1 stop, or a failed
#      smoke or smoke gate, the box holds no e181/ directory at all, so v1 stopped step 22 with 14 on "rsync e181 rc=23" and never read the gates.
#      A presence read that fails prints "rsync <pass dir> rc=<n>" (the copy was not made), which step 22 reads as a failed copy;
#   2. the files the session writes into build/e181/ are kept in logs/ only if the session's own last block in logs/session.log records
#      writing them: smoke-gate.json ("smoke gate rc="), config-session-start.json and config-session-end.json (with their .err and .time:
#      "config config-session-start.json:", "config config-session-end.json:"), dmcmd-preflight.txt ("dmcmd_audit preflight rc="). Any other
#      copy of them is from step 10's V3_DRY session (which writes the same names) or from an earlier try: it is moved to
#      logs/not-this-session/ and named in logs/not-this-session/README.txt. After an A6-1 stop, v1 collected the dry session's
#      smoke-gate.json as if it were the real session's.
# Everything else is v1's: the box is read only; the rsyncs are bounded (300 / 120 s); ccheck/ is emptied first; Q139(k)'s check of C runs on
# every C log (ccheck.py check, --jobs 2); a pass whose C log is absent or empty is named; it never runs the scorer and refuses to start if a
# scored file is already there. Step 22 v2 (rb/s22_collect_e181_v2.sh) runs it, then the gates, then the score (score_e181_v2.sh).
#   bash tools/claims-v3/e181/collect_e181_v2.sh docs/reports/data/<YYYY-MM-DD>-e181-m11-session2-aifoundry3
# Run it from step 22 v2, never alone.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?usage: collect_e181_v2.sh <data dir>}
PY=${PY:-/usr/bin/python3}
mkdir -p "$D/aifoundry3" "$D/logs" "$D/ccheck"
find "$D/ccheck" -mindepth 1 -maxdepth 1 -type f -delete
for f in scored-m11.json scored-m11.md scored-m11-lines.jsonl scored-m11-lines.jsonl.staging; do
  [ -e "$D/$f" ] && { echo "refusing: $D/$f exists before the gates (remove the data directory first)"; exit 3; }
done
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
for x in e181-smoke e181; do
  ans=$(timeout 60 $SSH aifoundry3 "test -d aifoundry/build/claims-v3/aifoundry3/$x && echo PRESENT || echo ABSENT" < /dev/null 2>&1); prc=$?   # v2 change 1
  case "$prc:$ans" in
    0:PRESENT) timeout 300 rsync -a -e "$SSH" --exclude 'telemetry.jsonl.raw' --exclude 'tiles/' aifoundry3:aifoundry/build/claims-v3/aifoundry3/$x/ "$D/aifoundry3/$x/" || echo "rsync $x rc=$?" ;;
    0:ABSENT) echo "absent on the box: build/claims-v3/aifoundry3/$x/ (no such pass directory: nothing to copy; step 22 reads the session's gates)" ;;
    *) echo "rsync $x rc=${prc} (the presence read did not answer PRESENT or ABSENT: ${ans:0:200}; nothing copied)" ;;
  esac
done
timeout 120 rsync -a -e "$SSH" aifoundry3:aifoundry/build/e181/ "$D/logs/" || echo "rsync logs rc=$?"
# v2 change 2: keep a session-written file only if the session's own last block records writing it
L=$D/logs/session.log
if [ -f "$L" ]; then
  blk=$(awk '/ session start/ {b = ""} {b = b $0 "\n"} END {printf "%s", b}' "$L")
  moved=0
  for spec in "smoke-gate.json|smoke gate rc=" "config-session-start.json|config config-session-start.json:" \
              "config-session-end.json|config config-session-end.json:" "dmcmd-preflight.txt|dmcmd_audit preflight rc="; do
    f=${spec%%|*}; key=${spec#*|}
    [ -e "$D/logs/$f" ] || continue
    printf '%s' "$blk" | grep -qF -- "$key" && continue
    mkdir -p "$D/logs/not-this-session"
    for g in "$D/logs/$f" "$D/logs/$f.err" "$D/logs/$f.time"; do [ -e "$g" ] && mv "$g" "$D/logs/not-this-session/"; done
    echo "$f (and its .err, .time): the session's last block in logs/session.log has no '$key' line, so this copy is step 10's V3_DRY session's or an earlier try's: moved to logs/not-this-session/" >> "$D/logs/not-this-session/README.txt"
    echo "not this session's: logs/$f -> logs/not-this-session/ (no '$key' in the session's last block)"
    moved=$((moved + 1))
  done
  echo "session-written files kept by the session's last block; $moved set aside"
else
  echo "no logs/session.log collected: the real session never wrote one (step 22 reads the gates)"
fi
logs=()
for d in "$D"/aifoundry3/e181-smoke/p18101 "$D"/aifoundry3/e181/p18120; do
  if [ ! -s "$d/c-log.jsonl" ]; then echo "c-log $(basename "$d"): absent or empty (step 22's launch gate reads whether this pass must carry one)"; continue; fi
  cp "$d/c-log.jsonl" "$D/ccheck/c-log-$(basename "$d").jsonl"
  logs+=("$D/ccheck/c-log-$(basename "$d").jsonl")
done
if [ ${#logs[@]} -gt 0 ]; then
  nice -n 10 "$PY" tools/claims-v3/ccheck/ccheck.py check "${logs[@]}" --out "$D/ccheck/ccheck-all.json" --jobs 2 > "$D/ccheck/ccheck.txt" 2>&1
  echo "ccheck rc=$? ($(tail -1 "$D/ccheck/ccheck.txt" | head -c 400))"
  gzip -f "${logs[@]}"
fi
echo "collected (no score: step 22 scores after its gates)"
du -sh "$D"
