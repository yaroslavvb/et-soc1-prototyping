#!/usr/bin/env bash
# E202's simulator checks: the mnistmlp kernel file in sys_emu at small batches, every run's labels, checksums and
# (debug) logits checked bit for bit by the host against the numpy model's expected files, and each run counted by the
# lab's counter (tools/counter/run_counted.sh: the instruction log streamed into count_kernel.py; nothing of the log is
# kept). No device: every host command carries --sysemu. Run it on a box with the ET install, at nice (run_counted
# runs the host at nice 19), one run at a time, and under the lab's simulator rule (a short run, minutes each).
#
#   bash sysemu_check.sh --build BUILD --data MNISTDIR --files FILESDIR --counter TOOLS_COUNTER --out NEWDIR [--runs LIST]
#     BUILD    a build of this folder (BUILD/host/mnistmlp_host, BUILD/kernel/mnistmlp.elf)
#     MNISTDIR the decompressed MNIST files (model/fetch_mnist.sh)
#     FILESDIR mnist-int8-trained.mlpw, mnist-int8-random.mlpw, expect-{trained,random}-train.mlpe and
#              logits-{trained,random}-train.mlpl (model/mnist_model.py), with the pins file PINS-SHA256SUMS
#     LIST     comma-separated, default S0a,S0b,S0c,S0r,S1,S2,S3,S3x,S1b (below)
#   sys_emu's five checkers (memory coherence, L1 and L2 scratchpad, FLB, TensorStore) are on by default in every
#   host-run simulation (SysEmuOptions: memcheck, l1ScpCheck, l2ScpCheck, flbCheck, tstoreCheck = true), so every run
#   below has them; S0a and S3 also pass their flags explicitly.
#   Runs (the network and the kernel file as on a card; only the batch is small):
#     S0a  dram staging, shire 0, 2 minions, 2 groups (1 round), trained weights, debug logits, the checkers' flags
#          given explicitly; counted (every hart of shire 0)
#     S0b  as S0a without debug logits and without the explicit flags (the default checkers still run): the counts of
#          the production path, one round
#     S0c  as S0b with 4 groups (2 rounds): S0c - S0b is one group per minion, exactly where the code allows
#     S0r  as S0a with the random weights (labels and logits against the model's random configuration)
#     S1   scp staging, 32 shires x 1 minion, 32 groups, trained, debug logits: the resident copy, the chip barrier and
#          every chunk copied from another shire's scratchpad; counted on shire 0 only
#     S2   dram staging, shire 0 with all 32 minions, 32 groups (1 round), trained: a card's shire-round (P = 32);
#          counted on minions 0, 27 and 31 (each copies 1, 1 or 0 tiles of a 28-tile chunk), the others run unlogged
#     S3   the padding path: as S0a with 3 groups (2 rounds): in round 2 minion 1 takes a padding group (input group 0,
#          its slot's discard line and discard logits); its work counts equal S0c's (counts_scale.py checks them)
#     S3x  the debug-logits gate's negative control: as S3 with the random configuration's logits file, so that only the
#          logits can disagree: wanted core_status PASS, logits_status FAIL, status FAIL (host exit 1)
#     S1b  scp staging, 32 shires x 2 minions, 63 groups (1 round a shire), trained, debug logits: the resident copy
#          split between 2 minions (tile mod P), every chunk copy split between 2 minions from another shire's
#          scratchpad, the chip barrier at P = 2, and one padding group (shire 31's minion 1); counted on shire 0 only
# Prints one line per run (host status, core and logits status, counter rc) and SYSEMU-CHECK PASS when every run read
# as wanted (PASS; for S3x the logits-only failure above).
# SPDX-License-Identifier: Apache-2.0
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
build="" data="" files="" counter="" out="" runs="S0a,S0b,S0c,S0r,S1,S2,S3,S3x,S1b" tmo=1500
while [ $# -gt 0 ]; do
  case "$1" in
    --build) build=$2; shift 2 ;;
    --data) data=$2; shift 2 ;;
    --files) files=$2; shift 2 ;;
    --counter) counter=$2; shift 2 ;;
    --out) out=$2; shift 2 ;;
    --runs) runs=$2; shift 2 ;;
    --timeout) tmo=$2; shift 2 ;;
    *) echo "sysemu_check: unknown option $1" >&2; exit 2 ;;
  esac
done
[ -n "$build" ] && [ -n "$data" ] && [ -n "$files" ] && [ -n "$counter" ] && [ -n "$out" ] || { sed -n 2,36p "$0"; exit 2; }
host=$build/host/mnistmlp_host
dis=$build/kernel/mnistmlp.dis
[ -x "$host" ] && [ -f "$build/kernel/mnistmlp.elf" ] || { echo "sysemu_check: no build at $build" >&2; exit 2; }
[ -f "$dis" ] || /opt/et/bin/riscv64-unknown-elf-objdump -d -w "$build/kernel/mnistmlp.elf" > "$dis"
mkdir -p "$out" || exit 1
CHECKERS="-mem_check -l1_scp_check -l2_scp_check -flb_check -tstore_check"
common=(--images "$data/train-images-idx3-ubyte" --split train --pins "$files/PINS-SHA256SUMS" --epoch 0xE2020001)
trained=(--weights "$files/mnist-int8-trained.mlpw" --expect "$files/expect-trained-train.mlpe")
random=(--weights "$files/mnist-int8-random.mlpw" --expect "$files/expect-random-train.mlpe")
all_pass=1
run() {  # run NAME WANTED LOGSEL HOSTARGS...   WANTED: PASS, or LOGITS-ONLY (core PASS, logits FAIL, status FAIL, exit 1)
  local name=$1 wanted=$2 logsel=$3; shift 3
  if [ -e "$out/$name" ]; then echo "RUN $name: $out/$name exists, skipped"; all_pass=0; return; fi
  local t0; t0=$(date +%s)
  bash "$counter/run_counted.sh" --no-prof --dis "$dis" --out "$out/$name" --log-sel "$logsel" --timeout "$tmo" -- \
    prlimit --as=4294967296 "$host" --sysemu --sim-args @SIM@ "$@" --out host-result.json > "$out/$name.run.txt" 2>&1
  local rc=$? st cs lg
  st=$(grep -o '"status":"[A-Z ]*"' "$out/$name/host-result.json" 2>/dev/null | tail -1)
  cs=$(grep -o '"core_status":"[A-Z ]*"' "$out/$name/host-result.json" 2>/dev/null | tail -1)
  lg=$(grep -o '"logits_status":"[A-Z ]*"' "$out/$name/host-result.json" 2>/dev/null | tail -1)
  echo "RUN $name: rc=$rc $st $cs $lg $(( $(date +%s) - t0 )) s (wanted $wanted)"
  case "$wanted" in
    PASS) case "$st" in *'"PASS"'*) ;; *) all_pass=0 ;; esac ;;
    LOGITS-ONLY)
      case "$rc|$st|$cs|$lg" in
        '1|"status":"FAIL"|"core_status":"PASS"|"logits_status":"FAIL"') ;;
        *) all_pass=0 ;;
      esac ;;
    *) all_pass=0 ;;
  esac
}
IFS=',' read -r -a want <<< "$runs"
for r in "${want[@]}"; do
  case "$r" in
    S0a) run S0a PASS '-ls 0,ffffffffffffffff' "${common[@]}" "${trained[@]}" --stage dram --shires 0x1 --per-shire 2 \
           --groups 2 --debug-logits --expect-logits "$files/logits-trained-train.mlpl" --sim-extra "$CHECKERS" ;;
    S0b) run S0b PASS '-ls 0,ffffffffffffffff' "${common[@]}" "${trained[@]}" --stage dram --shires 0x1 --per-shire 2 --groups 2 ;;
    S0c) run S0c PASS '-ls 0,ffffffffffffffff' "${common[@]}" "${trained[@]}" --stage dram --shires 0x1 --per-shire 2 --groups 4 ;;
    S0r) run S0r PASS '-ls 0,ffffffffffffffff' "${common[@]}" "${random[@]}" --stage dram --shires 0x1 --per-shire 2 \
           --groups 2 --debug-logits --expect-logits "$files/logits-random-train.mlpl" ;;
    S1)  run S1 PASS '-ls 0,ffffffffffffffff' "${common[@]}" "${trained[@]}" --stage scp --shires 0xffffffff --per-shire 1 \
           --groups 32 --debug-logits --expect-logits "$files/logits-trained-train.mlpl" ;;
    S2)  run S2 PASS '-ls 0,4040000000000001' "${common[@]}" "${trained[@]}" --stage dram --shires 0x1 --per-shire 32 --groups 32 ;;
    S3)  run S3 PASS '-ls 0,ffffffffffffffff' "${common[@]}" "${trained[@]}" --stage dram --shires 0x1 --per-shire 2 \
           --groups 3 --debug-logits --expect-logits "$files/logits-trained-train.mlpl" --sim-extra "$CHECKERS" ;;
    S3x) run S3x LOGITS-ONLY '-ls 0,ffffffffffffffff' "${common[@]}" "${trained[@]}" --stage dram --shires 0x1 --per-shire 2 \
           --groups 3 --debug-logits --expect-logits "$files/logits-random-train.mlpl" ;;
    S1b) run S1b PASS '-ls 0,ffffffffffffffff' "${common[@]}" "${trained[@]}" --stage scp --shires 0xffffffff --per-shire 2 \
           --groups 63 --debug-logits --expect-logits "$files/logits-trained-train.mlpl" ;;
    *) echo "sysemu_check: unknown run $r" >&2; all_pass=0 ;;
  esac
done
[ "$all_pass" = 1 ] && echo "SYSEMU-CHECK PASS" || echo "SYSEMU-CHECK FAIL"
[ "$all_pass" = 1 ]
