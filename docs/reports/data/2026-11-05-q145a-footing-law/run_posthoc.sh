#!/bin/bash
# Q145(a), the footing law's post hoc study (FOOTING-LAW.md FL7 and "Why"), from the lab clone's top, with a python that has numpy:
#   bash docs/reports/data/2026-11-05-q145a-footing-law/run_posthoc.sh <a scratch directory outside the repository>
# It reads committed files only and writes only to the scratch directory; each step takes seconds to a few minutes.
set -u
OUT=${1:?usage: run_posthoc.sh <scratch dir>}
mkdir -p "$OUT/fl7"
PY=${PY:-/usr/bin/python3}
D=docs/reports/data/2026-11-05-q145a-footing-law
D1=docs/reports/data/2026-11-05-e171-blind8-aifoundry3
D2=docs/reports/data/2026-11-05-e172-blind8-card1
# 1. the re-derivations: the dedicated idle cycles, the in-run and rest slopes with the sensor test, the run profile, the laws, the estimator
$PY -B $D/rederive_idle.py . "$OUT/idle.json"
$PY -B $D/footing_inrun.py . "$OUT/inrun.json"
$PY -B $D/profile_inrun.py . "$OUT/profile.json"
$PY -B $D/law_rule.py . "$OUT/idle.json" "$OUT/profile.json" "$OUT/law.json"
$PY -B $D/sim_attenuation.py "$OUT/sim.json"
# 2. FL7: the two sessions at the law's k_s (tools/claims-v3/footing-law/k-e17x.json), by their registered reducers and scorer
K1=$($PY -B -c 'import json;print(json.load(open("tools/claims-v3/footing-law/k-e171.json"))["k_w_per_c"])')
K2=$($PY -B -c 'import json;print(json.load(open("tools/claims-v3/footing-law/k-e172.json"))["k_w_per_c"])')
gzip -dc $D2/ccheck/ccheck-session.json.gz > "$OUT/fl7/e172-ccheck-session.json"
$PY -B tools/claims-v3/e171/reduce_e171.py $(ls -d $D1/aifoundry3/e171/p1711[0-9]) --leak "$K1" --no-refit --drop-dips \
  --out "$OUT/fl7/e171-law.json" --csv "$OUT/fl7/runs-e171-law.csv" --txt "$OUT/fl7/reduce-e171-law.txt" > "$OUT/fl7/reduce-e171-law.log" 2>&1
$PY -B tools/claims-v3/e172/reduce_e172.py $(ls -d $D2/aifoundry1-c1/e172/p1721[0-9]) --leak "$K2" --no-refit \
  --out "$OUT/fl7/e172-law.json" --csv "$OUT/fl7/runs-e172-law.csv" --txt "$OUT/fl7/reduce-e172-law.txt" > "$OUT/fl7/reduce-e172-law.log" 2>&1
for arm in law control own; do
  case $arm in law) R1="$OUT/fl7/e171-law.json"; R2="$OUT/fl7/e172-law.json" ;;
               control) R1=$D1/e171.json; R2=$D2/e172.json ;;
               own) R1=$D1/e171-auto-nodips.json; R2=$D2/e172-auto.json ;; esac
  $PY -B tools/claims-v3/p8-600/score_p8_600.py score --run E171 --reduction "$R1" --raw $D1/aifoundry3 --ccheck $D1/ccheck/ccheck-all.json \
    --json "$OUT/fl7/scored-e171-$arm.json" --md "$OUT/fl7/results-e171-$arm.md"
  $PY -B tools/claims-v3/p8-600/score_p8_600.py score --run E172 --reduction "$R2" --raw $D2/aifoundry1-c1 --ccheck "$OUT/fl7/e172-ccheck-session.json" \
    --json "$OUT/fl7/scored-e172-$arm.json" --md "$OUT/fl7/results-e172-$arm.md"
done
$PY -B tools/claims-v3/p8-600/score_p8_600.py ka-pooled "$OUT/fl7/scored-e171-law.json" "$OUT/fl7/scored-e172-law.json" --json "$OUT/fl7/ka-pooled-law.json"
$PY -B tools/claims-v3/p8-600/score_p8_600.py ka-pooled "$OUT/fl7/scored-e171-control.json" "$OUT/fl7/scored-e172-control.json" --json "$OUT/fl7/ka-pooled-control.json"
# 3. the first-order one-footing companions (f = 1 - c1 dk; c1 from law.json > s_vs_k, dk from the frozen and the law's k)
F() { $PY -B -c "import json;L=json.load(open('$OUT/law.json'));print(1-L['s_vs_k']['$1']['fit_c1']*($2-$3))"; }
$PY -B $D/companion_fl7.py "$OUT/fl7/scored-e171-law.json" "$(F E171 "$K1" 0.20563713796102187)" E171 > "$OUT/fl7/companion-e171.json"
$PY -B $D/companion_fl7.py "$OUT/fl7/scored-e172-law.json" "$(F E172 "$K2" 0.3134106532552718)" E172 > "$OUT/fl7/companion-e172.json"
$PY -B $D/companion_fl7.py "$OUT/fl7/scored-e171-own.json" "$(F E171 0.2850400903444 0.20563713796102187)" E171own > "$OUT/fl7/companion-e171-own.json"
$PY -B $D/companion_fl7.py "$OUT/fl7/scored-e172-own.json" "$(F E172 0.4030303030303078 0.3134106532552718)" E172own > "$OUT/fl7/companion-e172-own.json"
$PY -B - "$OUT" <<'PY'
import json, sys
o = sys.argv[1] + "/fl7/"
rows = json.load(open(o + "companion-e171.json"))["ka_rows"] + json.load(open(o + "companion-e172.json"))["ka_rows"]
sp = sum(x["e_primary"] ** 2 for x in rows); s0 = sum(x["e_a_priori"] ** 2 for x in rows); ins = all(x["inside_power"] for x in rows)
json.dump({"verdict": "PASS" if (sp < s0 and ins) else "FAIL", "n": len(rows), "sum_e_primary_sq": sp, "sum_e_a_priori_sq": s0, "all_inside": ins},
          open(o + "companion-ka-pooled.json", "w"), indent=1)
PY
echo "done: $OUT"
