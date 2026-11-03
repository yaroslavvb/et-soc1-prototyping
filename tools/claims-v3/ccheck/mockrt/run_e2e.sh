#!/usr/bin/env bash
# Q139(k): the C log end to end on a desk machine, no card: build the host as committed and as patched against the mock
# runtime (build_mock.sh), run the patched one on pool-5 tiles with a correct software kernel and with each injected
# kernel fault, check every C log with ccheck.py, and compare the two hosts' SPARSITY lines and DMA. No device access.
#
#   bash tools/claims-v3/ccheck/mockrt/run_e2e.sh <out-dir>
set -u
OUT=${1:?usage: run_e2e.sh <out-dir>}
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.."
R=$PWD
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
bash "$R/tools/claims-v3/ccheck/mockrt/build_mock.sh" "$OUT/mock" > "$OUT/build.log" 2>&1 || { tail -20 "$OUT/build.log"; exit 1; }
M=$OUT/mock
T=$R/tools/claims-v3/kinds/blind5/tiles
cd "$OUT"
rm -f ./*.jsonl ./*.out ./*.err ./*.check
export MOCK_ACCUM=$M/accum MOCK_SLEEP_MS=40
COMMON=(--pattern none --shires 0x3 --per-shire 8 --iters 40 --seconds 0.3 --seed 1 --kernel "$M/accum")
run() { # name type tile fault expect extra...
  local name=$1 ty=$2 tile=$3 f=$4 want=$5; shift 5
  MOCK_FAULT=$f "$M/sparsity_host_ccheck" --test fma --type "$ty" --values "file:$tile" "${COMMON[@]}" --c-log "$name.jsonl" "$@" \
    > "$name.out" 2> "$name.err"
  local hrc=$?
  python3 "$R/tools/claims-v3/ccheck/ccheck.py" check "$name.jsonl" --jobs 2 --cache "$OUT/cache" > "$name.check" 2>&1
  local crc=$?
  local got=PASS; [ $crc -eq 0 ] || got=FAIL
  # UNMODELLED (amendment A1): every launch refused, none failed
  tail -1 "$name.check" | grep -q '"PASS": 0, "ROUNDING": 0, "UNMODELLED": [1-9][0-9]*, "FAIL": 0' && got=UNMODELLED
  local ok=as-expected; [ "$got" = "$want" ] || ok=UNEXPECTED
  echo "$ok: $name (fault $f, $*) host rc=$hrc, ccheck $got (expected $want): $(tail -1 "$name.check")"
  echo "    $(tail -1 "$name.err")"
  grep -v '^PASS' "$name.check" | grep -v '^{' | head -1 | cut -c1-300 | sed 's/^/    first non-PASS: /'
}
run ok_fp16    fp16 "$T/fp16/fp16.real_pythia_qk.bin"      none    PASS --c-poison
run ok_fp32    fp32 "$T/fp32/fp32.wideexp48_dense.bin"     none    PASS --c-poison
run ok_int8    int8 "$T/int8/int8.real_pythia_w8a8_up.bin" none    PASS --c-poison
run ok_anchor  fp32 "$T/fp32/fp32.anchor_randn.bin"        none    PASS --c-poison
run ok_nopois  fp16 "$T/fp16/fp16.real_pythia_qk.bin"      none    PASS
run bitflip    fp16 "$T/fp16/fp16.real_pythia_qk.bin"      bitflip FAIL --c-poison
run nostore_p  fp32 "$T/fp32/fp32.wideexp48_dense.bin"     nostore FAIL --c-poison
run nostore_np fp32 "$T/fp32/fp32.wideexp48_dense.bin"     nostore FAIL
run stale_p    int8 "$T/int8/int8.real_pythia_w8a8_up.bin" stale   FAIL --c-poison
run stale2_p   int8 "$T/int8/int8.real_pythia_w8a8_up.bin" stale2  FAIL --c-poison
run stale2_np  int8 "$T/int8/int8.real_pythia_w8a8_up.bin" stale2  PASS
run wrongn     fp16 "$T/fp16/fp16.real_pythia_qk.bin"      wrongn  FAIL --c-poison
run swapab     int8 "$T/int8/int8.real_pythia_w8a8_up.bin" swapab  FAIL --c-poison
# added in the fix pass of Tue 3 Nov 2026: the mask and the stream are logged and refused (the mock kernel ignores both,
# so C is the unmasked reference: ccheck still says UNMODELLED), and a record cut short fails only its own launch
run masked     fp32 "$T/fp32/fp32.wideexp48_dense.bin"     none    UNMODELLED --c-poison --row-mask 0xfff0
run bstream    fp16 "$T/fp16/fp16.real_pythia_qk.bin"      none    UNMODELLED --c-poison --b-stream
MOCK_FAULT=none "$M/sparsity_host_ccheck" --test fma --type fp32 --values "file:$T/fp32/fp32.wideexp48_dense.bin" "${COMMON[@]}" \
  --c-log cut.jsonl --c-poison > cut1.out 2> cut1.err
python3 - cut.jsonl <<'EOF'
import sys
p = sys.argv[1]
L = open(p).read().splitlines()
open(p, "w").write("\n".join(L[:-1]) + "\n" + L[-1][:len(L[-1]) // 2])   # the last C record cut mid-hex, no newline
EOF
MOCK_FAULT=none "$M/sparsity_host_ccheck" --test fma --type int8 --values "file:$T/int8/int8.real_pythia_w8a8_up.bin" "${COMMON[@]}" \
  --c-log cut.jsonl --c-poison > cut2.out 2> cut2.err
python3 "$R/tools/claims-v3/ccheck/ccheck.py" check cut.jsonl --jobs 2 --cache "$OUT/cache" > cut.check 2>&1
echo "cut record: rc=$? (expected 1), $(($(grep -c SPARSITY cut1.out) + $(grep -c SPARSITY cut2.out))) launches in two processes: $(tail -1 cut.check)"
grep '^FAIL' cut.check | cut -c1-200 | sed 's/^/    /'
# through the runner wrapper, as a run_e78-style runner calls it (--sparsity sparsity_ccheck.sh, no ccheck flags of its own)
CCHECK_HOST=$M/sparsity_host_ccheck CCHECK_KERNEL=$M/accum CCHECK_LOG=$OUT/wrapper.jsonl MOCK_FAULT=none \
  "$R/tools/claims-v3/ccheck/sparsity_ccheck.sh" --test fma --type fp16 --pattern none --values "file:$T/fp16/fp16.exp_only.bin" \
  --shires 0x3 --per-shire 8 --iters 40 --seconds 0.3 --seed 1 > wrapper.out 2> wrapper.err
echo "wrapper: rc=$? $(grep -c SPARSITY wrapper.out) launches; $(tail -1 wrapper.err)"
python3 "$R/tools/claims-v3/ccheck/ccheck.py" check wrapper.jsonl --jobs 2 --cache "$OUT/cache" > wrapper.check 2>&1
echo "wrapper: ccheck rc=$? $(tail -1 wrapper.check)"
echo "wrapper: host record: $(grep -m1 '"kind":"host"' wrapper.jsonl | cut -c1-60)... kernel_from $(grep -m1 -o '"kernel_from":"[a-zA-Z_]*"' wrapper.jsonl)"
# a runner that passes its own --kernel (E143's runner on aifoundry2 does): the wrapper must not append a second one
CCHECK_HOST=$M/sparsity_host_ccheck CCHECK_LOG=$OUT/wrapper_rk.jsonl MOCK_FAULT=none \
  "$R/tools/claims-v3/ccheck/sparsity_ccheck.sh" --test fma --type fp16 --pattern none --values "file:$T/fp16/fp16.exp_only.bin" \
  --shires 0x3 --per-shire 8 --iters 40 --seconds 0.3 --seed 1 --kernel "$M/accum" > wrapper_rk.out 2> wrapper_rk.err
echo "wrapper, runner's own --kernel: rc=$? $(grep -c SPARSITY wrapper_rk.out) launches; $(grep -m1 -o '"kernel_from":"[a-zA-Z_]*"' wrapper_rk.jsonl); tiles record kernel $(grep -m1 -o '"kernel":"[^"]*"' wrapper_rk.jsonl | sed 's#.*/##')"
python3 "$R/tools/claims-v3/ccheck/ccheck.py" check wrapper_rk.jsonl --jobs 2 --cache "$OUT/cache" > wrapper_rk.check 2>&1
echo "wrapper, runner's own --kernel: ccheck rc=$? $(tail -1 wrapper_rk.check)"
# the runner's --kernel and a different CCHECK_KERNEL: refused before the host starts
CCHECK_HOST=$M/sparsity_host_ccheck CCHECK_KERNEL=$M/sparsity_host_orig CCHECK_LOG=$OUT/wrapper_x.jsonl MOCK_FAULT=none \
  "$R/tools/claims-v3/ccheck/sparsity_ccheck.sh" --test fma --type fp16 --values "file:$T/fp16/fp16.exp_only.bin" \
  --kernel "$M/accum" > wrapper_x.out 2> wrapper_x.err
echo "wrapper, runner's --kernel against another CCHECK_KERNEL: rc=$? (expected 2), $(grep -c SPARSITY wrapper_x.out) launches, log $( [ -e wrapper_x.jsonl ] && echo written || echo absent); $(tail -1 wrapper_x.err)"
# the host as committed, and the patched host without its flags, on the same tile: the DMA each makes
for v in orig ccheck; do
  MOCK_FAULT=none "$M/sparsity_host_$v" --test fma --type fp16 --values "file:$T/fp16/fp16.real_pythia_qk.bin" "${COMMON[@]}" \
    > "noflags_$v.out" 2> "noflags_$v.err"
  echo "host $v without --c-log: rc=$? $(grep -c SPARSITY "noflags_$v.out") launches; $(tail -1 "noflags_$v.err")"
done
python3 - "$OUT" <<'EOF'
import json, sys, os
d = sys.argv[1]
def recs(f):
    return [json.loads(l.split(" ", 1)[1]) for l in open(os.path.join(d, f)) if l.startswith("SPARSITY ")]
a, b, c = recs("noflags_orig.out"), recs("noflags_ccheck.out"), recs("ok_fp16.out")
same_keys = all(list(x) == list(y) for x, y in zip(a, c)) and all(list(x) == list(y) for x, y in zip(a, b))
timing = {"wall_s", "t_start_ms", "t_end_ms", "ghz"}
first = all(a[0][k] == c[0][k] for k in a[0] if k not in timing) and all(a[0][k] == b[0][k] for k in a[0] if k not in timing)
print("SPARSITY lines: the same keys in the same order on every launch (orig, patched without flags, patched with "
      "--c-log --c-poison): %s; the calibration launch (iters 40) equal on every field but its timing: %s" % (same_keys, first))
EOF
