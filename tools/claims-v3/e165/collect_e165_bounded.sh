#!/bin/bash
# E165 (Q141(g)), amendments A2-7 and A2-8: the collector, bounded. collect_e165.sh's steps, with five changes, written before any E165 data
# (4 below is a correction: collect_e165.sh's session list also takes the queue's s1.out file, and its scoring step would stop there):
#   0. the code-path check (A2-5): python3 -B tools/claims-v3/e165/check_path_e165.py must PASS, else nothing is collected or scored (exit 6);
#   1. one probe of the box first, hard-killed after 15 s (the round's Tailscale rule): a login.tailscale.com link, or no answer, stops the
#      collection at once (exit 5) with nothing written; the detached queue's data stays on the box, to collect when it answers;
#   2. every remote call (the two rsyncs, the box's hashing) under timeout(1), 600 s each (E165_REMOTE_TIMEOUT_S), the whole process group
#      killed 10 s after the TERM, so no ssh is left waiting on the desk;
#   3. after the registered scoring, the burst D in both forms (A2-4; report_d_e165.py, reported only), and the code-path check's output kept
#      in the data dir's logs;
#   4. the sessions scored are the run directories that hold a session.json (A2-8), not every name matching s[0-9]* (exit 4 if there is none),
#      and a failed scorer stops the collection with exit 7 (collect_e165.sh never reads the scorer's exit status).
# Run it on the Intel, from the top of the lab tree, AFTER the queue on aifoundry2 has ended (status.json "ended"), with the lab approvals in place:
#
#   bash tools/claims-v3/e165/collect_e165_bounded.sh <a new, empty scratch dir> <the data dir, docs/reports/data/<date>-e165-blind7-aifoundry2>
#
# Read-only on aifoundry2: no device opened, no lock taken, nothing written there, nothing re-run (the remote rsync and hashing at nice 19). Then
# the check of C and the registered scoring at the desk (nice 10, 2 jobs), as collect_e165.sh. SPDX-License-Identifier: Apache-2.0
set -u
RAW=${1:?usage: collect_e165_bounded.sh <new empty scratch dir> <data dir>}
D=${2:?usage: collect_e165_bounded.sh <new empty scratch dir> <data dir>}
[ -d "$RAW" ] && [ -n "$(ls -A "$RAW" 2>/dev/null)" ] && { echo "refused: $RAW is not empty"; exit 2; }
[ -e "$D/aifoundry2" ] && { echo "refused: $D/aifoundry2 exists"; exit 2; }
TO=$(command -v timeout || command -v gtimeout) || { echo "refused: no timeout(1) here (coreutils)"; exit 2; }
CALL_S=${E165_REMOTE_TIMEOUT_S:-600}
PROBE_S=15
BOX=aifoundry2
TREE=claude/et-soc1-prototyping
SSHO="-o BatchMode=yes -o ConnectTimeout=10"
SSH="ssh $SSHO"
R() { "$TO" -k 10 "$CALL_S" "$@"; }

# 0. the code-path check, before anything is collected
PC=$(python3 -B tools/claims-v3/e165/check_path_e165.py 2>&1); rc=$?
echo "$PC" | tail -1
[ $rc -eq 0 ] || { echo "$PC"; echo "refused: the score's code path is not the registered bytes (check_path_e165.py rc $rc): nothing collected"; exit 6; }

# 1. the probe: one ssh, hard-killed after 15 s
PR=$("$TO" -k 2 "$PROBE_S" ssh $SSHO "$BOX" true 2>&1 < /dev/null); rc=$?
if printf '%s' "$PR" | grep -q 'login.tailscale.com'; then
  echo "stopped: $BOX asks for a Tailscale check (the lab approval lapsed): $(printf '%s' "$PR" | grep -o 'https://login.tailscale.com[^ ]*' | head -1)"
  echo "nothing collected; the queue's data stays on the box. Collect again after the approval."
  exit 5
fi
[ $rc -eq 0 ] || { echo "stopped: the probe of $BOX did not answer in ${PROBE_S} s (rc $rc): nothing collected; collect again later"; exit 5; }
echo "probe: $BOX answered at $(date '+%H:%M:%S %Z')"

mkdir -p "$RAW/logs" "$RAW/cc" || exit 2

# 2. the queue's records, its stdout and the slot file (collect_e165.sh step 1, each call bounded)
R rsync -a --rsync-path="nice -n 19 rsync" -e "$SSH" "$BOX:$TREE/build/e165/runs/" "$RAW/runs/" || { echo "stopped: rsync of the runs failed or ran past ${CALL_S} s"; exit 3; }
R rsync -a --rsync-path="nice -n 19 rsync" -e "$SSH" "$BOX:$TREE/build/e165/queue.out" "$BOX:claude/work/q141-a2-e165-slot.txt" "$RAW/logs/" \
  || { echo "stopped: rsync of queue.out and the slot file failed or ran past ${CALL_S} s"; exit 3; }

# 3. the sha256 of every kit file, pool tile and binary the queue ran from, on the box, against the desk's copy (collect_e165.sh step 2, bounded)
cat > "$RAW/box_hash.sh" <<'EOS'
cd ~/claude/et-soc1-prototyping || exit 9
nice -n 19 sha256sum tools/claims-v3/e165/*.py tools/claims-v3/e165/*.json tools/claims-v3/kinds/blind7/tiles/*/*.bin tools/claims-v3/ccheck/*.sh \
  tools/claims-v3/ccheck/*.py docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json build/ccheck/b/host/sparsity_host \
  build/sparsity_t2/kernel/sparsity.elf build/ettelem-hpl/ettelem
EOS
R $SSH "$BOX" 'bash -s' < "$RAW/box_hash.sh" > "$RAW/logs/box-files-sha256.txt" || { echo "stopped: the box's hashing failed or ran past ${CALL_S} s"; exit 3; }
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

# 4. Q139(k)'s check of C at the desk, as registered (a fresh cache in the scratch dir; collect_e165.sh step 3)
for s in smoke stoptest-board s1 s2 s3; do        # stoptest-die stops before any launch: no C log
  [ -f "$RAW/runs/$s/c-log.jsonl" ] || continue
  CCHECK_CACHE="$RAW/ccache" nice -n 10 python3 -B tools/claims-v3/ccheck/ccheck.py check "$RAW/runs/$s/c-log.jsonl" --out "$RAW/cc/ccheck-$s.json" \
    --jobs 2 > "$RAW/cc/ccheck-$s.txt"
done

# 5. the data dir, as collect_e165.sh step 4
mkdir -p "$D/aifoundry2" "$D/logs"
rsync -a "$RAW/runs/" "$D/aifoundry2/"
cp "$RAW/logs/"* "$D/logs/"
cp "$RAW/cc/"ccheck-*.json "$D/"
find "$D/aifoundry2" -path '*/tel/*.jsonl' -type f -exec gzip -n {} +
find "$D/aifoundry2" \( -name launches.jsonl -o -name c-log.jsonl \) -type f -exec gzip -n {} +
printf '%s\n' "$PC" > "$D/logs/path-check.txt"

# 6. the registered scoring (E165.md, "How to run it"; collect_e165.sh step 5), then the burst D in both forms (A2-4, reported only). The
#    sessions are the directories that hold a session.json (A2-8): collect_e165.sh's `ls -d s[0-9]*` also lists the queue's s1.out beside s1/,
#    on which the scorer stops (NotADirectoryError), so it would never have scored.
SESS=$(for s in "$D"/aifoundry2/s[0-9]*; do [ -f "$s/session.json" ] && printf '%s\n' "$s"; done)
[ -n "$SESS" ] || { echo "stopped: no session directory (with a session.json) under $D/aifoundry2: collected, not scored"; exit 4; }
CC=$(ls "$D"/ccheck-s[0-9]*.json 2>/dev/null)
nice -n 10 python3 -B tools/claims-v3/e165/score_e165.py $SESS --ccheck $CC --out "$D/results.json" > "$D/score.txt"; rc=$?
[ $rc -eq 0 ] || { echo "stopped: the registered scorer failed (rc $rc; its message is above): collected, not scored"; exit 7; }
nice -n 10 python3 -B tools/claims-v3/e165/report_d_e165.py $SESS --ccheck $CC --out "$D/d-both.json" > "$D/d-both.txt" \
  || echo "warning: the D report (A2-4, reported only) failed; the registered score stands"
ls "$D"/ccheck-s[0-9]*.json > /dev/null 2>&1 && gzip -n -k "$D"/ccheck-s[0-9]*.json
echo "collected into $D; scored: $(head -1 "$D/score.txt"); burst D in both forms: $(head -1 "$D/d-both.txt")"
