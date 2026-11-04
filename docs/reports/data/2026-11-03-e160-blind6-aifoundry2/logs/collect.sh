# E160: how the data was collected and checked, Tue 3 Nov 2026, about 15:54-16:30 PST, on the Intel (the lane resumed after the session stopped at
# about 07:46 PST). Read-only on aifoundry2: no device opened, no lock taken, nothing written there, nothing re-run. <scratch> is the lane's scratch dir.
set -u
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
RAW=<scratch>/raw                      # a new, empty dir
D=docs/reports/data/2026-11-03-e160-blind6-aifoundry2

# 1. copy the queue's records (the remote rsync at nice 19, so it cannot disturb a card run that may have started)
rsync -a --rsync-path="nice -n 19 rsync" -e "$SSH" aifoundry2:claude/et-soc1-prototyping/build/e160/runs/ $RAW/runs/
rsync -a --rsync-path="nice -n 19 rsync" -e "$SSH" aifoundry2:claude/et-soc1-prototyping/build/e160/queue.out \
      aifoundry2:claude/work/q139-a2-e160-slot.txt $RAW/logs/
# 2. the sha256 and mtime of every file and binary the queue ran from, on the box, against the registration commit -> logs/box-files-sha256.txt

# 3. Q139(k)'s check of C at the desk, as registered, a fresh cache, nice 10, 6 jobs (about 5 minutes for s1's 2,596 launches)
for s in smoke stoptest-board s1; do        # stoptest-die stopped before any launch: no C log
  nice -n 10 python3 -I tools/claims-v3/ccheck/ccheck.py check $RAW/runs/$s/c-log.jsonl --out <scratch>/cc/ccheck-$s.json --jobs 6 \
      --cache <scratch>/ccache > <scratch>/cc/ccheck-$s.txt
done

# 4. the data dir: the runs as collected, with the sampler's lines, the launch records and the C logs gzipped (gzip -n) as E143's are
rsync -a $RAW/runs/ $D/aifoundry2/
find $D/aifoundry2 -path '*/tel/*.jsonl' -type f -exec gzip -n {} +
find $D/aifoundry2 \( -name launches.jsonl -o -name c-log.jsonl \) -type f -exec gzip -n {} +

# 5. the registered reduction (E160.md, "How to run it"), on the committed form; the same on the raw copy gave the same results.json but for
#    one file name's .gz in "peaks"
python3 tools/claims-v3/e160/reduce_e160.py $D/aifoundry2/s1 --ccheck <scratch>/cc/ccheck-s1.json --out $D/results.json > $D/reduce.txt
