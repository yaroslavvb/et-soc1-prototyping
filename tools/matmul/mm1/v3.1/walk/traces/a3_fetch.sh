#!/bin/bash
# v31-trace (Q217): copy one traced run's kept files (summary.json.gz, out.json, err.log, RUN.txt, sandbox-check.txt) from aifoundry3 to
# traces/runs/<name>/ on the desk, ONLY while no lane books aifoundry3 and no claim file stands (book.sh show read just before).
#   bash a3_fetch.sh <name>
set -u
W=<W>
L=$W/out/v31-trace
name=$1
case "$name" in t[0-9]*-*) ;; *) echo "bad run name"; exit 2 ;; esac
bk=$(bash "$W/book.sh" show 2>&1)
if printf '%s\n' "$bk" | grep -qi 'aifoundry3'; then echo "BOOKED: nothing fetched"; exit 9; fi
[ -e "$W/out/orch/claim-aifoundry3.txt" ] && { echo "CLAIMED: nothing fetched"; exit 9; }
mkdir -p "$L/traces/runs/$name"
for f in summary.json.gz out.json RUN.txt sandbox-check.txt; do
  scp -o BatchMode=yes -o ConnectTimeout=10 -q "aifoundry3:claude/work/q217-v31-trace/runs/$name/$f" "$L/traces/runs/$name/$f" || echo "no $f"
done
# the host's stderr: its size, line count and first and last 40 lines (the runtime's per-poll INFO lines make it large)
ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry3 bash -s -- "$name" > "$L/traces/runs/$name/err.excerpt.txt" <<'RS'
f="$HOME/claude/work/q217-v31-trace/runs/$1/err.log"
echo "err.log: $(stat -c %s "$f") bytes, $(wc -l < "$f") lines; poll lines: $(grep -c 'Device memory read at\|Processing request' "$f")"
head -40 "$f" | sed "s#$HOME#~#g" | cut -c1-300; echo ...; tail -40 "$f" | sed "s#$HOME#~#g" | cut -c1-300
RS
ls -la "$L/traces/runs/$name"
sha256sum "$L/traces/runs/$name/summary.json.gz"
