#!/usr/bin/env bash
# collect.sh : copy the OH blocks (E53) from the lab hosts into raw/<card>/oh/ and their queue logs into logs/, then
# reduce them. Read-only on the hosts (rsync from ~/nekko/build/claims-v3); nothing here touches a card.
# Run it only after both queue logs say "queue ends" (or a block failed and the session stopped).
#   bash docs/reports/data/2026-09-28-overheating/collect.sh
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../../../.." && pwd)
for pair in aifoundry3:aifoundry3 aifoundry1:aifoundry1-c1; do
  host=${pair%%:*}; card=${pair##*:}
  mkdir -p "$here/raw/$card/oh" "$here/logs"
  # blocks (a failed attempt the queue set aside keeps its .attempt-<t> suffix); never who/et-who/ps files
  rsync -a --exclude who.txt --exclude et-who.txt --exclude ps.txt "$host:nekko/build/claims-v3/$card/oh/" "$here/raw/$card/oh/"
  rsync -a "$host:nekko/build/claims-v3/queue-oh-$card.log" "$host:nekko/build/claims-v3/oh-smoke-$card.log" "$here/logs/" 2>/dev/null || true
done
left=$(find "$here/raw" \( -name who.txt -o -name et-who.txt -o -name ps.txt -o -name '*.raw' -o -name '.state-*' \) | head -5)
[ -z "$left" ] || { echo "collect.sh: remove before committing: $left" >&2; exit 1; }
python3 "$root/tools/claims-v3/oh/reduce.py" --all --data "$here/raw" --out "$here/reductions"
du -sh "$here/raw"
