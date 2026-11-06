#!/usr/bin/env bash
# E180 (Q146(g); the kit's dated note 2, KIT.md.dated-note-2.md sections 1-3), v3: the desk collection of a session copied back from the box
# (step 22 v3 runs it), on the Intel. collect_e180_v2.sh (v2, which stays as committed) with three changes:
#   1. the build record: build_record_e180.py brings the box's BUILD-E180.json (the kernel's and the host's sha256; its toolchain listing's
#      owner and group withheld) and the box's kernel listing (step 6 v2's objdump) from <raw>/build-record/ into logs/ (build-e180.json,
#      e180-kernel-dis.txt), so A1-7's evidence and the kernel's sha256 are in the data (the kit verifier's fault 3);
#   2. A1-7 is read at the desk: check_elf_e180_v2.py walks that listing into logs/elfcheck-e180-v2.txt (A1-7's words; the case's own zeroing
#      block, so 261 and 262 read in either layout: the verifier's faults 1 and 2). The box's own line, logs/elfcheck-e180.txt (v1's walk at
#      step 6 v2), comes back with the session's logs as before and is kept beside; a FAIL there is a reading, never a stop here;
#   3. the reduction is reduce_e180_v3.py (one unreadable pass is set aside with its reason; the rest are reduced: fault 4) and the scorer
#      score_e180_v3.py (v2's, with A1-7 read from the desk walk, the per-kind marks and A1-5's band test named: faults 5 and 6).
# Everything else is v2's, line for line. It reads no card and commits nothing.
#
#   E180_DATE=<YYYY-MM-DD> [PY=/usr/bin/python3] bash tools/claims-v3/e180/collect_e180_v3.sh <raw copy: build/e180-raw>
#   -> build/e180-out/<day>-e180-vector-add-aifoundry3/{raw/, logs/ (with build-e180.json, e180-kernel-dis.txt, elfcheck-e180.txt,
#      elfcheck-e180-v2.txt), reduced-e180-v3.json, scored-e180.json, scored-e180.md}
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
RAW=${1:?usage: collect_e180_v3.sh <raw copy>}
DAY=${E180_DATE:?E180_DATE - the card day, YYYY-MM-DD}
PY=${PY:-python3}
OUT=build/e180-out/$DAY-e180-vector-add-aifoundry3
mkdir -p "$OUT/raw" "$OUT/logs"
for d in e180 e180-smoke e180-stoptest; do
  [ -d "$RAW/$d" ] && rsync -a --exclude '*.raw' "$RAW/$d" "$OUT/raw/"
done
[ -d "$RAW/logs" ] && rsync -a "$RAW/logs/" "$OUT/logs/"
"$PY" -B tools/claims-v3/e180/build_record_e180.py --raw "$RAW/build-record" --out "$OUT/logs" || { echo "build_record_e180 failed"; exit 1; }
"$PY" -B tools/claims-v3/e180/check_elf_e180_v2.py "$OUT/logs/e180-kernel-dis.txt" --also-160 > "$OUT/logs/elfcheck-e180-v2.txt" 2>&1
e=$?
{ [ "$e" -le 1 ] && tail -n 1 "$OUT/logs/elfcheck-e180-v2.txt" | grep -q '^ELFCHECK-E180-V2: '; } ||
  { echo "check_elf_e180_v2 failed (rc $e, no count line): $(tail -n 1 "$OUT/logs/elfcheck-e180-v2.txt")"; exit 1; }
echo "check_elf_e180_v2 rc=$e: $(tail -n 1 "$OUT/logs/elfcheck-e180-v2.txt")"
grep -E '^(PASS|FAIL|UNREAD) ' "$OUT/logs/elfcheck-e180-v2.txt" | cut -c1-200
"$PY" -B tools/claims-v3/e180/reduce_e180_v3.py --data "$OUT/raw/e180" --out "$OUT/reduced-e180-v3.json" --root . || { echo "reduce_e180_v3 failed"; exit 1; }
"$PY" -B tools/claims-v3/e180/score_e180_v3.py --reduced "$OUT/reduced-e180-v3.json" --out "$OUT/scored-e180" \
  --elfcheck-v2 "$OUT/logs/elfcheck-e180-v2.txt" --elfcheck-box "$OUT/logs/elfcheck-e180.txt" || { echo "score_e180_v3 failed"; exit 1; }
[ -s "$OUT/scored-e180.md" ] && echo "scored-e180.md written: $OUT"
