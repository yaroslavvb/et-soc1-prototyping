#!/bin/bash
# E165 (Q141(g)): the collector, E160's (docs/reports/data/2026-11-03-e160-blind6-aifoundry2/logs/collect.sh) as a script. Run it on the Intel, from
# the top of the lab tree, AFTER the queue on aifoundry2 has ended (status.json "ended"), with the lab approvals in place:
#
#   bash tools/claims-v3/e165/collect_e165.sh <a new, empty scratch dir> <the data dir, docs/reports/data/<date>-e165-blind7-aifoundry2>
#
# Read-only on aifoundry2: no device opened, no lock taken, nothing written there, nothing re-run (the remote rsync and hashing at nice 19, so they
# cannot disturb a card run that may have started). Then the check of C and the registered scoring at the desk (nice 10, 2 jobs).
set -u
RAW=${1:?usage: collect_e165.sh <new empty scratch dir> <data dir>}
D=${2:?usage: collect_e165.sh <new empty scratch dir> <data dir>}
[ -d "$RAW" ] && [ -n "$(ls -A "$RAW" 2>/dev/null)" ] && { echo "refused: $RAW is not empty"; exit 2; }
[ -e "$D/aifoundry2" ] && { echo "refused: $D/aifoundry2 exists"; exit 2; }
mkdir -p "$RAW/logs" "$RAW/cc" || exit 2
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
BOX=aifoundry2
TREE=claude/et-soc1-prototyping

# 1. the queue's records, its stdout and the slot file
rsync -a --rsync-path="nice -n 19 rsync" -e "$SSH" "$BOX:$TREE/build/e165/runs/" "$RAW/runs/" || exit 3
rsync -a --rsync-path="nice -n 19 rsync" -e "$SSH" "$BOX:$TREE/build/e165/queue.out" "$BOX:claude/work/q141-a2-e165-slot.txt" "$RAW/logs/" || exit 3

# 2. the sha256 of every kit file, pool tile and binary the queue ran from, on the box, against the desk's copy at the kit's commit
cat > "$RAW/box_hash.sh" <<'EOS'
cd ~/claude/et-soc1-prototyping || exit 9
nice -n 19 sha256sum tools/claims-v3/e165/*.py tools/claims-v3/e165/*.json tools/claims-v3/kinds/blind7/tiles/*/*.bin tools/claims-v3/ccheck/*.sh \
  tools/claims-v3/ccheck/*.py docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json build/ccheck/b/host/sparsity_host \
  build/sparsity_t2/kernel/sparsity.elf build/ettelem-hpl/ettelem
EOS
$SSH "$BOX" 'bash -s' < "$RAW/box_hash.sh" > "$RAW/logs/box-files-sha256.txt" || exit 3
python3 -B - "$RAW/logs/box-files-sha256.txt" <<'EOP' > "$RAW/logs/box-files-check.txt"
import hashlib, os, sys
pins = {"build/ccheck/b/host/sparsity_host": "eae32a152b8f0861bd2922c500eac217c931c9b464d3274a6bcf346cc986bfd2",
        "build/sparsity_t2/kernel/sparsity.elf": "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24",
        "build/ettelem-hpl/ettelem": "77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5"}
bad = 0
for ln in open(sys.argv[1]):
    h, p = ln.split(None, 1)
    p = p.strip()
    want = pins.get(p) or (hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None)
    if h != want:
        bad += 1
        print("DIFFERS", p, h, want)
print("box files:", "all as the desk's tree and the pins" if not bad else f"{bad} differ")
EOP
cat "$RAW/logs/box-files-check.txt"

# 3. Q139(k)'s check of C at the desk, as registered (a fresh cache in the scratch dir)
for s in smoke stoptest-board s1 s2 s3; do        # stoptest-die stops before any launch: no C log
  [ -f "$RAW/runs/$s/c-log.jsonl" ] || continue
  CCHECK_CACHE="$RAW/ccache" nice -n 10 python3 -B tools/claims-v3/ccheck/ccheck.py check "$RAW/runs/$s/c-log.jsonl" --out "$RAW/cc/ccheck-$s.json" \
    --jobs 2 > "$RAW/cc/ccheck-$s.txt"
done

# 4. the data dir: the runs as collected, the sampler's lines, the launch records and the C logs gzipped (gzip -n) as E160's are
mkdir -p "$D/aifoundry2" "$D/logs"
rsync -a "$RAW/runs/" "$D/aifoundry2/"
cp "$RAW/logs/"* "$D/logs/"
cp "$RAW/cc/"ccheck-*.json "$D/"
find "$D/aifoundry2" -path '*/tel/*.jsonl' -type f -exec gzip -n {} +
find "$D/aifoundry2" \( -name launches.jsonl -o -name c-log.jsonl \) -type f -exec gzip -n {} +

# 5. the registered scoring (E165.md, "How to run it"), on the committed form, every BURST session the queue ran
SESS=$(ls -d "$D"/aifoundry2/s[0-9]* 2>/dev/null)
CC=$(ls "$D"/ccheck-s[0-9]*.json 2>/dev/null)
nice -n 10 python3 -B tools/claims-v3/e165/score_e165.py $SESS --ccheck $CC --out "$D/results.json" > "$D/score.txt"
gzip -n -k "$D"/ccheck-s[0-9]*.json
echo "collected into $D; scored: $(head -1 "$D/score.txt")"
