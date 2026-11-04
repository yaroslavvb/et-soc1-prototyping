#!/usr/bin/env bash
# E164 (Q141(b)'s fix pass, Wed 4 Nov 2026, before any E164 data; README.md.dated-note.md § 2): box step 7's collector. It runs
# collect_e164.sh, unchanged (ce10e301), with the same arguments, then two steps on the data directory it wrote:
#   1. scrub_etwho_e164.py on <out>/logs/: other people's logins and command lines out of the et-who readings and the others-present
#      lines (session_e164.sh appends et-who's output to session.log; collect_e164.sh copies every log), then --check, which must read OK;
#      it writes logs/et-who-summary.txt (every et-who reading, counted by card: whether card 0 was in use, no names);
#   2. rank1_e164.py on <out>/scored.json: E164-RANK1, card 1's half of rank 1 (amendment E164-A1, A1-3) -> rank1-e164.json.
# Desk compute, on the Intel, over a copy of the raw passes (box/pull_e164.sh), never on the card's host:
#
#   PY=/usr/bin/python3 PYS=<python 3.12 or later> E164_DATE=<the day> [E164_OWNER=<the box login of the session>] \
#     nice -n 10 bash tools/claims-v3/e164/collect_e164_a1.sh build/e164-raw [<E163's e163.json> [<its C-excluded tiles> [<E163's scored.json>]]]
#
# PY needs numpy (the reduction): /usr/bin/python3 (3.9.6, numpy 1.26.4) on the Intel. PYS runs score_e164.py and pair_rank4_e164.py,
# which need Python 3.12 or later (E157's scorer ran there: 3.12 changed float sum()): /usr/local/bin/python3.12 or the Intel's python3
# (3.13.11). E164_OWNER is needed only if the logs' own paths do not name the session's login once (/home/<login>/nekko/).
# Exit: collect_e164.sh's status if the scrub and its check pass; 7 if the scrub or its check fails (then nothing may be committed).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
export E164_DATE=${E164_DATE:-$(date +%F)}
OUT=$ROOT/build/e164-out/$E164_DATE-e164-blind7-card1
bash tools/claims-v3/e164/collect_e164.sh "$@"; rc=$?
echo "collect_e164.sh rc=$rc"
[ -d "$OUT/logs" ] || { echo "no $OUT/logs: nothing to scrub (the collector did not write the data directory)"; exit 7; }
OWN=(); [ -n "${E164_OWNER:-}" ] && OWN=(--owner "$E164_OWNER")
python3 -B tools/claims-v3/e164/scrub_etwho_e164.py "$OUT/logs" ${OWN[@]+"${OWN[@]}"} || { echo "scrub failed: commit nothing"; exit 7; }
python3 -B tools/claims-v3/e164/scrub_etwho_e164.py --check "$OUT/logs" ${OWN[@]+"${OWN[@]}"} || { echo "scrub check failed: commit nothing"; exit 7; }
cat "$OUT/logs/et-who-summary.txt"
if [ -s "$OUT/scored.json" ]; then
  python3 -B tools/claims-v3/e164/rank1_e164.py "$OUT/scored.json" --out "$OUT/rank1-e164.json"
else
  echo "no scored.json: E164-RANK1 not read"
fi
exit "$rc"
