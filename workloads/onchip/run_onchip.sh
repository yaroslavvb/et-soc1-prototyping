#!/usr/bin/env bash
# Does shire-to-shire communication beat main memory?
#
#   workloads/onchip/run_onchip.sh <out-dir>
#
# One JSON line per configuration in <out-dir>/sweep.jsonl. Every launch holds the card for a few
# milliseconds. The three media run the same kernel over the same volume with the same barriers; the only
# thing that changes is where a stage's output goes:
#   dram  write it to DRAM and read it back next stage   (the standard approach)
#   scp   keep it in this shire's own L2 scratchpad      (on-chip, no data crosses a shire)
#   hop   write it where the next shire will read it     (on-chip, every stage crosses a shire)
set -u
out=${1:?out dir}
mkdir -p "$out"; cd "$(dirname "${BASH_SOURCE[0]}")/../.."
export LD_LIBRARY_PATH=/opt/et/lib
H=build/onchip/host/onchip_host
run() {  # group medium stage-bytes stages work shires [hop-distance]
  timeout 40 $H --test relay --medium "$2" --stage-bytes "$3" --stages "$4" --work "$5" --shires "$6" \
      --hop-distance "${7:-1}" 2>/dev/null |
    grep ONCHIP | sed "s/^ONCHIP {/{\"group\":\"$1\",\"host\":\"$(hostname)\",/" >> "$out/sweep.jsonl"
}
: > "$out/sweep.jsonl"

# Does a cross-shire write land where the next shire reads it, at all?
for m in 0 1; do
  timeout 30 $H --test probe --method $m --shift 1 2>/dev/null | grep ONCHIP |
    sed "s/^ONCHIP {/{\"group\":\"probe\",\"host\":\"$(hostname)\",/" >> "$out/sweep.jsonl"
done

# The headline: same work, same barriers, three media.
for med in dram scp hop; do run headline $med 1M 8 1 0xffffffff; done

# Arithmetic intensity: where does the advantage run out?
for w in 1 2 4 8 16 32 64 128 256; do
  for med in dram scp hop; do run intensity $med 1M 8 "$w" 0xffffffff; done
done

# Working-set size: below the 32 MB L3 the DRAM route is not really going to DRAM.
for b in 64K 128K 256K 512K 1M; do
  for med in dram scp hop; do run size $med "$b" 8 1 0xffffffff; done
done

# Stages: the per-stage barrier is a fixed cost, and in `hop` the data travels one more shire each time.
for k in 1 2 4 8 16 32; do
  for med in dram scp hop; do run stages $med 1M "$k" 1 0xffffffff; done
done

# How many shires have to take part.
for m in 0x3 0xf 0xff 0xffff 0xffffffff; do
  for med in dram scp hop; do run shires $med 1M 8 1 "$m"; done
done

# How far round the ring a slab is handed: does the mesh distance cost anything?
for d in 1 2 4 8 16; do run distance hop 1M 8 1 0xffffffff "$d"; done

# Past the scratchpad's reach, DRAM only: is 48 GB/s really the floor?
for b in 2M 4M 8M; do run bigsize dram "$b" 8 1 0xffffffff; done
echo "wrote $(wc -l < "$out/sweep.jsonl") configurations to $out/sweep.jsonl"
