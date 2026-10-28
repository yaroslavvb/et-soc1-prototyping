#!/usr/bin/env bash
# Q129 — re-reduce every aifoundry3 experiment at the card's MEASURED idle leakage slope (E71, 0.3803 W/°C over
# 58–62 °C) and rebuild Q128's data block from the result. Labelled sensitivities: nothing published is replaced.
#
#   bash docs/reports/data/2026-10-27-q129-leak-sensitivity/refit.sh [<repo root>] [<out dir>]
#
# Each reduction is ALSO run at its own published auto k, which must reproduce the committed file exactly; that
# reproduction is the integrity check, and all five passed (see README.md § Reproduction).
#
# Two interpreters are needed: reduce_hl.py wants numpy, and report_e70.py / report_e67.py / chain.py /
# build_data.py use nested same-quote f-strings (Python ≥ 3.12). PY_NP and PY312 may name the same binary.
set -u
ROOT=${1:-$PWD}
OUT=${2:-$ROOT/build/q129-leak-sensitivity}
PY_NP=${PY_NP:-python3}          # any python3 with numpy
PY312=${PY312:-python3}          # python >= 3.12 with numpy
D=$ROOT/docs/reports/data
E60=$D/2026-10-20-bitflip-ladder
E65=$D/2026-10-26-e65-bit-prices-hart-ladder
E67=$D/2026-10-27-e67-a-side-bit-prices
E70=$D/2026-10-27-e70-saturation-ladder
RED=$ROOT/tools/claims-v3/hl/reduce_hl.py
K=0.3803
mkdir -p "$OUT"

# ── 1. the four reductions, each at its own auto k (reproduction) and at the measured slope ──────────────
# E60: aifoundry3's eight passes only — aifoundry1's and aifoundry2's rows keep their own slopes.
for k in 0.2026495726495783 $K; do
  "$PY_NP" "$RED" "$E60"/aifoundry3/hl/p[1-8] --gen "$E60" --pred "$E60/predictions.json" --leak "$k" \
    --out "$OUT/e60-a3-k$k.json" --csv "$OUT/e60-a3-k$k.csv" > "$OUT/e60-a3-k$k.txt" 2>&1
done
# E65 blocks A+B (block C de-leaks with IDLE brackets and is unaffected; block D is E71's).
for k in 0.18237745098038693 $K; do
  "$PY_NP" "$RED" "$E65"/aifoundry3/hl/p65[1-7] --gen "$E65" --pred "$E60/predictions.json" --leak "$k" \
    --out "$OUT/e65ab-k$k.json" --csv "$OUT/e65ab-k$k.csv" > "$OUT/e65ab-k$k.txt" 2>&1
done
# E67 (registered set of passes).
for k in 0.17545454545454092 $K; do
  "$PY_NP" "$RED" "$E67"/aifoundry3/hl/p75[0-9] "$E67"/aifoundry3/hl/p77[0-9] \
    --gen "$E67" --pred "$E60/predictions.json" --leak "$k" \
    --out "$OUT/e67-k$k.json" --csv "$OUT/e67-k$k.csv" > "$OUT/e67-k$k.txt" 2>&1
done
# E70 (its --gen manifest is build/hl-gen5's, committed as the data directory's manifest.json).
mkdir -p "$OUT/gen70"; cp "$E70/manifest.json" "$OUT/gen70/manifest.json"
for k in 0.1975000000000174 $K; do
  "$PY_NP" "$RED" "$E70"/aifoundry3/hl/p79[0-6] --gen "$OUT/gen70" --pred "$E60/predictions.json" --leak "$k" \
    --out "$OUT/e70-k$k.json" --csv "$OUT/e70-k$k.csv" > "$OUT/e70-k$k.txt" 2>&1
done

# ── 2. closure.py needs the operand tiles; the committed data holds them per pass as <item>.b<pass>.bin ──
mkdir -p "$OUT/gen-tiles/tiles"; cp "$E67/manifest.json" "$OUT/gen-tiles/manifest.json"
"$PY312" - "$E67/aifoundry3/hl" "$OUT/gen-tiles/tiles" <<'EOF'
import os, sys
src, dst = sys.argv[1], sys.argv[2]
for p in sorted(os.listdir(src)):                 # the first pass that holds a file wins; gen.sha256 pins them
    td = os.path.join(src, p, "tiles")
    for f in sorted(os.listdir(td)) if os.path.isdir(td) else []:
        if f.endswith(".bin") and not os.path.exists(os.path.join(dst, f.split(".b")[0] + ".bin")):
            open(os.path.join(dst, f.split(".b")[0] + ".bin"), "wb").write(open(os.path.join(td, f), "rb").read())
print(len(os.listdir(dst)), "operand files")
EOF

# ── 3. each experiment's own scoring code on top of the new reductions ───────────────────────────────────
for tag in pub k; do
  case $tag in
    pub) E67HL=$OUT/e67-k0.17545454545454092.json; E65HL=$E65/hl.json;              E70HL=$OUT/e70-k0.1975000000000174.json; E70CSV=$OUT/e70-k0.1975000000000174.csv;;
      k) E67HL=$OUT/e67-k$K.json;                  E65HL=$OUT/e65ab-k$K.json;       E70HL=$OUT/e70-k$K.json;                 E70CSV=$OUT/e70-k$K.csv;;
  esac
  "$PY312" "$ROOT/tools/claims-v3/ha/closure.py" --gen "$OUT/gen-tiles" --e67 "$E67HL" --e65 "$E65HL" \
    --out "$OUT/closure-$tag.json" > "$OUT/closure-$tag.txt" 2>&1
  "$PY312" "$ROOT/tools/claims-v3/ha/report_e67.py" --e67 "$E67HL" --e65 "$E65HL" --closure "$OUT/closure-$tag.json" \
    --out "$OUT/e67-results-$tag.md" --json "$OUT/e67-scored-$tag.json" > "$OUT/e67-report-$tag.txt" 2>&1
  # report_e70.py is given E67's COMMITTED closure.json in both runs, so only E70's own rungs move (see README).
  "$PY312" "$ROOT/tools/claims-v3/hs/report_e70.py" --hl "$E70HL" --pred "$E70/predictions-e70.json" \
    --leak "$E70/hl-leak0.2.json,$E70/hl-leak0.3.json,$E70/hl-leak0.4.json" --load "$E70/logs/e70-load.jsonl" \
    --runs "$E70CSV" --blocks "$E70/aifoundry3/hl" --closure "$E67/closure.json" \
    --out "$OUT/e70-report-$tag.md" --json "$OUT/e70-scored-$tag.json" > "$OUT/e70-report-$tag.txt" 2>&1
done

# ── 4. Q128's own chain.py and build_data.py over a SHADOW root: symlinks everywhere, four substituted files
SH=$OUT/shadow
rm -rf "${OUT:?}/shadow"; mkdir -p "$SH/docs/reports/data"
for p in "$ROOT"/*;              do b=$(basename "$p"); [ "$b" = docs ]    || ln -s "$p" "$SH/$b"; done
for p in "$ROOT"/docs/*;         do b=$(basename "$p"); [ "$b" = reports ] || ln -s "$p" "$SH/docs/$b"; done
for p in "$ROOT"/docs/reports/*; do b=$(basename "$p"); [ "$b" = data ]    || ln -s "$p" "$SH/docs/reports/$b"; done
for p in "$D"/*; do
  b=$(basename "$p")
  case $b in 2026-10-20-bitflip-ladder|2026-10-26-e65-bit-prices-hart-ladder|2026-10-27-e67-a-side-bit-prices) ;;
             *) ln -s "$p" "$SH/docs/reports/data/$b"; continue;; esac
  mkdir -p "$SH/docs/reports/data/$b"
  for q in "$p"/*; do c=$(basename "$q")
    case $c in hl.json|scored.json|closure.json) ;; *) ln -s "$q" "$SH/docs/reports/data/$b/$c";; esac; done
done
cp "$OUT/e65ab-k$K.json"    "$SH/docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json"
ln -s "$E65/scored.json"    "$SH/docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/scored.json" 2>/dev/null || true
cp "$OUT/e67-k$K.json"      "$SH/docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json"
cp "$OUT/e67-scored-k.json" "$SH/docs/reports/data/2026-10-27-e67-a-side-bit-prices/scored.json"
cp "$OUT/closure-k.json"    "$SH/docs/reports/data/2026-10-27-e67-a-side-bit-prices/closure.json"
# E60's hl.json holds three cards and only aifoundry3 is re-reduced, so splice that one card in.
"$PY312" - "$E60/hl.json" "$OUT/e60-a3-k$K.json" "$SH/docs/reports/data/2026-10-20-bitflip-ladder/hl.json" <<'EOF'
import json, sys
pub, new = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
assert list(new["cards"]) == ["aifoundry3"]
pub["cards"]["aifoundry3"], pub["gates"]["aifoundry3"] = new["cards"]["aifoundry3"], new["gates"]["aifoundry3"]
json.dump(pub, open(sys.argv[3], "w"))
EOF
mkdir -p "$OUT/chain-k"
"$PY312" "$D/2026-10-27-chain-closure/chain.py" "$SH" "$OUT/chain-k" > "$OUT/chain-k.txt" 2>&1
# build_data.py reads chain.json out of the data directory, so give it a root whose chain dir holds the new one
BD=$OUT/bd/docs/reports/data; rm -rf "${OUT:?}/bd"; mkdir -p "$BD/2026-10-27-chain-closure"
for p in "$SH"/*;              do b=$(basename "$p"); [ "$b" = docs ]    || ln -s "$(readlink -f "$p")" "$OUT/bd/$b"; done
for p in "$SH"/docs/*;         do b=$(basename "$p"); [ "$b" = reports ] || ln -s "$(readlink -f "$p")" "$OUT/bd/docs/$b"; done
for p in "$SH"/docs/reports/*; do b=$(basename "$p"); [ "$b" = data ]    || ln -s "$(readlink -f "$p")" "$OUT/bd/docs/reports/$b"; done
for p in "$SH"/docs/reports/data/*; do b=$(basename "$p")
  [ "$b" = 2026-10-27-chain-closure ] || ln -s "$(readlink -f "$p")" "$BD/$b"; done
for q in "$D"/2026-10-27-chain-closure/*; do c=$(basename "$q")
  [ "$c" = chain.json ] || ln -s "$q" "$BD/2026-10-27-chain-closure/$c"; done
cp "$OUT/chain-k/chain.json" "$BD/2026-10-27-chain-closure/chain.json"
"$PY312" "$D/2026-10-27-matmul-to-transistor/build_data.py" "$OUT/bd" "$OUT/q128-data-at-0.3803.json" \
  > "$OUT/bd.txt" 2>&1
echo "done: $OUT"
