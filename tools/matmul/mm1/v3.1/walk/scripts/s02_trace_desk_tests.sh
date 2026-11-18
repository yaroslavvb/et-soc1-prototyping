#!/bin/bash
# Q217 v31-trace: desk tests of the trace summarizer (traces/trace_run.py summarize) and THE CHECK (traces/check_v31.py) on SYNTHETIC logs
# in sys_emu's line formats made from the walk (traces/make_fake_log.py). No simulator, no device. One slot job (THE CPU RULE).
#   bash s02_trace_desk_tests.sh            -> logs/s02_trace_desk_tests.log; prints 'TRACE DESK TESTS n of n PASS'
set -u
W=<W>
L=$W/out/v31-trace
read l1 l5 l15 rest < /proc/loadavg
awk -v l="$l1" 'BEGIN{exit !(l<=6.0)}' || { echo "LOAD $l1 ABOVE 6: not running"; exit 6; }
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
cat > "$L/work/s02_inner.sh" <<'EOF'
#!/bin/bash
set -u
L=<W>/out/v31-trace
T=$L/work/desk-traces
mkdir -p "$T"
P="/usr/bin/python3 -I -B"
pass=0; tot=0
diag="0 9 18 27 4 13 22 31"
harts_for() {   # $1 = shires (space separated), plus hart 1 of minions 0 and 31 of the first shire, plus hart 0 of minion 0 of shire 31
  local out="" s m first=""
  for s in $1; do [ -z "$first" ] && first=$s; for m in $diag; do out="$out,$((64 * s + 2 * m))"; done; done
  out="$out,$((64 * first + 1)),$((64 * first + 63)),$((64 * 31))"
  echo "${out#,}"
}
one() {   # name kernel shape mask shires perturb want(EXACT|DIFFERS) [expect_diff_positions]
  local name=$1 k=$2 shp=$3 mk=$4 shs=$5 pert=$6 want=$7 wantpos=${8:-}
  tot=$((tot + 1))
  $P "$L/traces/make_fake_log.py" --kernel "$k" --shape "$shp" --mask "$mk" --harts "$(harts_for "$shs")" --perturb "$pert" --out "$T/$name.log" > /dev/null || { echo "FAIL $name: fake log"; return; }
  $P "$L/traces/trace_run.py" summarize --log "$T/$name.log" --out "$T/$name.sum.json.gz" > /dev/null || { echo "FAIL $name: summarize"; return; }
  rm -f "${T:?}/${name:?}.log"   # the synthetic log is not kept (only its summary)
  $P "$L/traces/check_v31.py" --summary "$T/$name.sum.json.gz" --kernel "$k" --shape "$shp" --mask "$mk" --out "$T/$name.check.json" > "$T/$name.check.out"
  local v pos
  v=$($P -c "import json;print(json.load(open('$T/$name.check.json'))['verdict'])")
  pos=$($P -c "import json;print(json.load(open('$T/$name.check.json'))['diff_positions_total'])")
  if [ "$v" = "$want" ] && { [ -z "$wantpos" ] || [ "$pos" = "$wantpos" ]; }; then pass=$((pass + 1)); echo "PASS $name: $v (diff positions $pos)";
  else echo "FAIL $name: got $v (diff positions $pos), want $want ${wantpos:+($wantpos)}"; fi
}
one gemmL-2x2x1-0xf     rgm136.gemmL   2x2x1 0xf    "0 1 2 3"    none  EXACT 0
one gemmL-2x2x1-0x1111  rgm136.gemmL   2x2x1 0x1111 "0 4 8 12"   none  EXACT 0
one gemmLn-2x3x2-0xf    rgm211.gemmLn  2x3x2 0xf    "0 1 2 3"    none  EXACT 0
one gemmLn-2x3x2-0x1111 rgm211.gemmLn  2x3x2 0x1111 "0 4 8 12"   none  EXACT 0
one gemmLnc-2x2x1-0xf   rgm136.gemmLnc 2x2x1 0xf    "0 1 2 3"    none  EXACT 0
# the wrong kernel's walk must not pass: rgm211's trace read as rgm136's (differs at MB, NB >= 2)
tot=$((tot + 1))
$P "$L/traces/check_v31.py" --summary "$T/gemmLn-2x3x2-0xf.sum.json.gz" --kernel rgm136.gemmL --shape 2x3x2 --mask 0xf --out "$T/wrongwalk.check.json" > /dev/null
v=$($P -c "import json;print(json.load(open('$T/wrongwalk.check.json'))['verdict'])")
[ "$v" = DIFFERS ] && { pass=$((pass + 1)); echo "PASS wrong-walk: DIFFERS"; } || echo "FAIL wrong-walk: $v"
# perturbations on the first hart: a swap of two A addresses (2 positions), a B address (1 position), a store left out (shifts the rest)
one pert-swapA rgm136.gemmL 2x2x1 0xf "0 1 2 3" swapA DIFFERS 2
one pert-bumpB rgm136.gemmL 2x2x1 0xf "0 1 2 3" bumpB DIFFERS 1
one pert-dropS rgm136.gemmL 2x2x1 0xf "0 1 2 3" dropS DIFFERS
echo "TRACE DESK TESTS $pass of $tot PASS (python $(/usr/bin/python3 -c 'import sys;print(sys.version.split()[0])'))"
[ "$pass" = "$tot" ]
EOF
bash "$W/slot.sh" /bin/bash "$L/work/s02_inner.sh" > "$L/logs/s02_trace_desk_tests.log" 2>&1
rc=$?
cat "$L/logs/s02_trace_desk_tests.log"
echo "rc=$rc at $(date '+%H:%M:%S %Z')"
exit $rc
