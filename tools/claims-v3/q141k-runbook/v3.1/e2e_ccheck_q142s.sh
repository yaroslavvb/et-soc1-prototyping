#!/usr/bin/env bash
# Q142(s) v3.1: s22 e163 end to end with the REAL collector, reducer, C check and scorer, at the desk only. A sparse scratch clone of the
# lab at HEAD; a stand-in aifoundry3 rebuilt from E163's committed raw layout; a stand-in ssh (it answers the probe and refuses anything
# else) and rsync (host paths read from the stand-in box), first on PATH. Never touches the lab clone it is run from (collect_e163.sh
# removes build/e163-out), and never reaches a box.
#   1. the C check crashes: the clone holds no rtl-sim/fma_toggle_v2/ (ccheck.py's engine source). v3.1, v3 and v2's s22 e163 each run;
#   2. the clone gets rtl-sim/fma_toggle_v2/ and v3.1's s22 e163 runs again: its outputs are compared with the committed E163 directory.
#   bash tools/claims-v3/q141k-runbook/v3.1/e2e_ccheck_q142s.sh <a new, empty scratch dir> > tools/claims-v3/q141k-runbook/v3.1/logs/e2e-ccheck.txt
# Every path in what it prints is relative to the scratch dir (<S>) or the clone. Local compute: the reducer one process at a time,
# the C check collect_e163.sh's --jobs 2, about 3-4 minutes. SPDX-License-Identifier: Apache-2.0
set -u
S0=${1:?usage: e2e_ccheck_q142s.sh <a new, empty scratch dir>}
[ -d "$S0" ] && [ -n "$(ls -A "$S0" 2>/dev/null)" ] && { echo "refused: the scratch dir is not empty"; exit 2; }
mkdir -p "$S0" || exit 2
S=$(cd "$S0" && pwd -P)
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
scrub() { sed -e "s#$S#<S>#g" -e "s#$SRC#<lab clone>#g" -e "s#$HOME#<home>#g"; }
git clone --local --no-checkout --quiet "$SRC" "$S/lab" || exit 2
git -C "$S/lab" sparse-checkout set --no-cone /tools/ /docs/reports/data/2026-11-03-q139u-footing/ \
  /docs/reports/data/2026-11-04-q141t-s7-recount/ /docs/reports/data/2026-11-04-q140m-m9/ /docs/reports/data/2026-11-03-q139m-model/ \
  /docs/reports/data/2026-11-04-q140l-a2-session-terms/ || exit 2
git -C "$S/lab" checkout --quiet main || exit 2
# v3.1 as it stands in the clone this runs from (the test is of these files, before or after their commit)
rm -rf "${S:?}/lab/tools/claims-v3/q141k-runbook/v3.1"
cp -R "$SRC/tools/claims-v3/q141k-runbook/v3.1" "$S/lab/tools/claims-v3/q141k-runbook/" || exit 2
rm -rf "${S:?}/lab/tools/claims-v3/q141k-runbook/v3.1/logs"
echo "# Q142(s) v3.1 end-to-end test of s22 e163, $(date '+%a %d %b %Y %H:%M:%S %Z'): the scratch clone at $(git -C "$S/lab" log -1 --format='%h %ad' --date=format-local:'%F %T')"
echo "# v3.1 under test: s22_collect.sh $(shasum -a 256 "$S/lab/tools/claims-v3/q141k-runbook/v3.1/s22_collect.sh" | cut -c1-12), ccdone_q142s.py $(shasum -a 256 "$S/lab/tools/claims-v3/q141k-runbook/v3.1/ccdone_q142s.py" | cut -c1-12), nopath_q142s.py $(shasum -a 256 "$S/lab/tools/claims-v3/q141k-runbook/v3.1/nopath_q142s.py" | cut -c1-12), rb_common.sh $(shasum -a 256 "$S/lab/tools/claims-v3/q141k-runbook/v3.1/rb_common.sh" | cut -c1-12) (sha256, first 12)"
D=$SRC/docs/reports/data/2026-11-04-e163-blind7-aifoundry3
B=$S/box/aifoundry3/aifoundry/build
mkdir -p "$B/claims-v3/aifoundry3" "$B/e163"
cp -R "$D/aifoundry3/e163" "$D/aifoundry3/e163-smoke" "$D/aifoundry3/e163-stoptest" "$B/claims-v3/aifoundry3/" || exit 2
cp -R "$D/aifoundry3/logs/." "$B/e163/" || exit 2
find "$S/box" -name '*.gz' -exec gunzip -f {} +
echo "the stand-in box: $(find "$B/claims-v3/aifoundry3" -maxdepth 2 -type d -name 'p163*' | wc -l | tr -d ' ') pass directories from E163's committed raw layout"
mkdir -p "$S/bin"
cat > "$S/bin/ssh" <<'EOS'
#!/bin/bash
echo "$(date '+%T') ssh $*" >> "$E2E_LOG"
h=""; r=()
while [ $# -gt 0 ]; do case "$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "$h" ]; then h=$1; shift; else r+=("$1"); shift; fi ;; esac; done
[ "${r[*]:-}" = true ] && exit 0
echo "stand-in ssh: refused $h ${r[*]:-}" >&2; exit 255
EOS
cat > "$S/bin/rsync" <<'EOS'
#!/bin/bash
echo "$(date '+%T') rsync $*" >> "$E2E_LOG"
a=()
while [ $# -gt 0 ]; do
  case "$1" in -e) shift 2 ;; --rsync-path=*) shift ;; aifoundry[0-9]:*) h=${1%%:*}; p=${1#*:}; a+=("$E2E_BOX/$h/$p"); shift ;; *) a+=("$1"); shift ;; esac
done
exec /usr/bin/rsync "${a[@]}"
EOS
chmod +x "$S/bin/ssh" "$S/bin/rsync"
export E2E_LOG=$S/calls.txt E2E_BOX=$S/box PATH="$S/bin:$PATH" RB_LOCK=$S/lock.txt
: > "$RB_LOCK"
[ "$(command -v ssh)" = "$S/bin/ssh" ] && [ "$(command -v rsync)" = "$S/bin/rsync" ] || { echo "refused: the stand-ins are not first on PATH"; exit 2; }
win() {  # a sample window for the desk (s02_window.sh refuses a past one); s22 reads only its day
  mkdir -p "$1"
  printf '%s\n' "RB_DAY=2026-11-04" "RB_LAST_START='2026-11-04 18:15 PST'" "RB_LAST_END='2026-11-04 19:00 PST'" \
    "RB_LAST_START_EPOCH=1793844900" "RB_LAST_END_EPOCH=1793847600" "RB_LAST_START_HM=18:15" "RB_LAST_END_HM=19:00" \
    "RB_E164_DEADLINE='2026-11-04 18:50 PST'" "RB_PLAN=full" "RB_GO_EPOCH=1793832000" > "$1/window.env"
}
OUT=build/e163-out/2026-11-04-e163-blind7-aifoundry3
cd "$S/lab" || exit 2
echo; echo "== 1. the C check crashes (no rtl-sim/fma_toggle_v2/ in the clone)"
for v in v3.1 v3 v2; do
  win "$S/rbout-1-$v"
  t=$(date +%s)
  RB_OUT=$S/rbout-1-$v bash tools/claims-v3/q141k-runbook/$v/s22_collect.sh e163 > "$S/s22-1-$v.txt" 2>&1; rc=$?
  echo "-- $v: s22_collect.sh e163 exit $rc in $(( $(date +%s) - t )) s"
  grep -E '^ccheck rc=|^CCHECK-|^ccdone:|^nopath:|STOP:|collected and scored' "$S/s22-1-$v.txt" | scrub | cut -c1-260 | sed 's/^/   /'
  cp "$OUT/scored.json" "$S/scored-1-$v.json" 2>/dev/null
done
cat > "$S/flips.py" <<'PY2'
import json, sys
crash = json.load(open(sys.argv[1]))["verdicts"]
good = json.load(open(sys.argv[2]))["verdicts"]
ns = [k for k in good if crash.get(k) == "NOT SCORED" and good[k] != "NOT SCORED"]
fl = [f"{k} {good[k]} -> {crash.get(k)}" for k in good if crash.get(k) not in (good[k], "NOT SCORED")]
extra = [f"{k} {crash[k]}" for k in crash if k not in good]
print(f"   what the scorer wrote over the crashed check, against the committed scored.json's {len(good)} registered verdicts:")
print(f"     NOT SCORED: {len(ns)} of {len(good)}: {', '.join(ns)}")
print(f"     changed otherwise: {len(fl)}: {'; '.join(fl)}")
print(f"     added, not registered: {'; '.join(extra) or 'none'}")
PY2
/usr/bin/python3 -I "$S/flips.py" "$S/scored-1-v2.json" "$D/scored.json"
cmp -s "$S/scored-1-v2.json" "$S/scored-1-v3.1.json" && cmp -s "$S/scored-1-v2.json" "$S/scored-1-v3.json" &&
  echo "   (the same scored.json under all three versions: the collector wrote it; v2 reported it as collected and scored)"
echo; echo "== 2. the clone gets rtl-sim/fma_toggle_v2/: v3.1's s22 e163 again"
git sparse-checkout add /rtl-sim/fma_toggle_v2/ || exit 2
win "$S/rbout-2"
t=$(date +%s)
RB_OUT=$S/rbout-2 bash tools/claims-v3/q141k-runbook/v3.1/s22_collect.sh e163 > "$S/s22-2.txt" 2>&1; rc=$?
echo "-- v3.1: s22_collect.sh e163 exit $rc in $(( $(date +%s) - t )) s"
grep -E '^ccheck rc=|^CCHECK-|^ccdone:|^nopath:|STOP:|collected and scored' "$S/s22-2.txt" | scrub | cut -c1-260 | sed 's/^/   /'
cat > "$S/cmp.py" <<'PY'
import json, os, sys
out, com = sys.argv[1], sys.argv[2]
a, b = "build/e163-raw/e163/", "docs/reports/data/2026-11-04-e163-blind7-aifoundry3/aifoundry3/e163/"
names = sorted(f for f in os.listdir(out) if os.path.isfile(os.path.join(out, f)))
same, differ, missing = [], [], []
for f in names:
    c = os.path.join(com, f)
    if not os.path.exists(c):
        missing.append(f)
        continue
    x = open(os.path.join(out, f), "rb").read().replace(a.encode(), b.encode())
    (same if x == open(c, "rb").read() else differ).append(f)
print(f"   top-level files written: {len(names)}; byte-identical to the committed directory once the pass prefix is normalised: "
      f"{len(same)}; differ: {len(differ)} {differ}; not in the committed directory: {len(missing)} {missing}")
v1, v2 = json.load(open(os.path.join(out, "scored.json")))["verdicts"], json.load(open(os.path.join(com, "scored.json")))["verdicts"]
print(f"   verdicts: {len(v1)}, identical to the committed scored.json's: {v1 == v2}")
dirs = json.load(open(os.path.join(out, "e163.json"))).get("dirs")
print(f"   e163.json dirs: {dirs}")
PY
/usr/bin/python3 -I "$S/cmp.py" "$OUT" "$D" | scrub
echo; echo "== the stand-ins' calls (none reached a box)"
scrub < "$E2E_LOG" | cut -c1-160 | sed 's/^/   /'
echo "   lock file lines: $(wc -l < "$RB_LOCK" | tr -d ' ')"
find "$SRC/tools/claims-v3/q141k-runbook" -name __pycache__ -type d -prune -exec rm -rf {} +
