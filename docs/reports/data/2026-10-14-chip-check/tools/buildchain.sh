#!/bin/bash
# buildchain.sh REPO : run the chip diagram's and the memory levels' whole build chain in REPO, in the documented order
# (MIRROR.md's rows; the ladder README), to its fixed point, and print what changed. Stops at the first failing step.
set -euo pipefail
R=${1:?repo}
cd "$R"
step() { echo "== $*"; "$@" > /tmp/claude-1019/buildchain-step.log 2>&1 || { echo "FAILED: $*"; tail -30 /tmp/claude-1019/buildchain-step.log; exit 1; }; tail -2 /tmp/claude-1019/buildchain-step.log; }
LD=docs/reports/data/2026-10-01-ladder
CD=docs/reports/data/2026-09-27-chip-diagram
MD=docs/reports/data/2026-09-28-memory-levels
# the shared ladder
step python3 $LD/research/build_process.py
step python3 $LD/research/build_particles.py
step python3 $LD/research/build_studio45.py
step python3 $LD/research/build_circuits.py
step python3 $LD/build_ladder.py
step python3 $LD/build_ladder.py --check
# the memory levels' research files
for f in l1 l2 l3 dram scp; do step python3 $MD/research/build_facts_$f.py; done
# the chip diagram's live research builders
step python3 $CD/research/build_layout_facts.py
step python3 $CD/research/build_facts_v2.py
step python3 $CD/research/make_asks.py
# the fixed point: inside -> chip facts -> memory levels facts -> inside -> chip facts
for i in 1 2 3; do
  step python3 $CD/research/build_inside.py
  step python3 $CD/research/build_outside.py
  step python3 $MD/build_facts.py
  step python3 $CD/build_facts.py
done
step python3 $CD/research/make_circuitkit.py --check
# the pages
step python3 scripts/build-report.py chip-diagram $CD/facts.json docs/reports/2026-09-27-et-soc1-chip-diagram.html
step python3 scripts/build-report.py memory-levels $MD/facts.json docs/reports/2026-09-28-et-soc1-memory-levels.html
echo "== changed files"
git status --short
git diff --stat | tail -3
