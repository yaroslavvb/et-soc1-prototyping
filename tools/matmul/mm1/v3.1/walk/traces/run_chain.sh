#!/bin/bash
# v31-trace (Q217): run the named traced runs of plan.json ONE AFTER ANOTHER on aifoundry3, each through a3_send.sh (which reads book.sh show,
# the claim file and queue_state.py aifoundry3 e213a just before its ssh and refuses otherwise), then fetch it (a3_fetch.sh, the same booking
# check) and remove its host stderr log there by its literal path (an excerpt is kept on the desk). Stops at the first refusal or failure.
#   bash run_chain.sh <run name> [<run name> ...]
set -u
W=<W>
L=$W/out/v31-trace
T=$L/traces
for name in "$@"; do
  args=$(/usr/bin/python3 -I -B - "$T/plan.json" "$name" <<'PY'
import json, sys
p = json.load(open(sys.argv[1]))
r = [x for x in p["runs"] if x["name"] == sys.argv[2]]
if not r:
    sys.exit(2)
r = r[0]
print(" ".join([r["name"], r["kernel"], r["arm"], r["mask"]] + r["log_sel"]))
PY
)
  [ -n "$args" ] || { echo "CHAIN: no run $name in plan.json"; exit 2; }
  echo "CHAIN $(date '+%T %Z'): $name"
  # shellcheck disable=SC2086
  bash "$T/a3_send.sh" script "$T/r_trace.sh" $args > "$L/logs/$name.out" 2>&1
  rc=$?
  tail -6 "$L/logs/$name.out" | cut -c1-400
  [ "$rc" = 0 ] || { echo "CHAIN STOPPED at $name: rc $rc"; exit "$rc"; }
  bash "$T/a3_fetch.sh" "$name" > "$L/logs/$name.fetch" 2>&1 || { echo "CHAIN: fetch of $name failed"; exit 3; }
  rmf="$L/work/r_rm_errlog_$name.sh"
  printf '#!/bin/bash\n# v31-trace: remove run %s host stderr log on aifoundry3 by its literal path (excerpt kept on the desk)\nrm -f ~/claude/work/q217-v31-trace/runs/%s/err.log\ndu -sh ~/claude/work/q217-v31-trace/runs/%s\n' "$name" "$name" "$name" > "$rmf"
  bash "$T/a3_send.sh" script "$rmf" > "$L/logs/$name.rm" 2>&1
  echo "CHAIN $(date '+%T %Z'): $name done and fetched ($(tail -2 "$L/logs/$name.rm" | head -1))"
done
echo "CHAIN DONE $(date '+%T %Z')"
