#!/bin/bash
# E175 (Q143(g)): the collector, bounded. E173's collect_e173_bounded.sh (lab 5a2a9ba0) with E175's names, written before any E175 data; E173's
# is E165's collect_e165_bounded.sh (its A2-7 and A2-8) with three changes:
#   0. the code-path check is the harness (check_e175.py --desk: every kit, chain, scorer and pool file the desk's tree holds at its registered
#      sha256), else nothing is collected (exit 6);
#   4. Q139(k)'s check of C runs for EVERY session directory that holds a C log, and then THE C-LOG LIST (cclist_q142kg.py; the Q142 critic's fault
#      3): every session the registration requires to carry one (smoke, stoptest-board, every BURST session s1-s6 the queue started that ran a work
#      launch) must hold a C log, else nothing is scored (exit 8): E165's loop skipped a session with no C log;
#   6. the registered scorer is score_e175.py on the predictor's python (numpy), with every check of C; its own refusals stop the collection: exit 5
#      (a listed session with no check given) is this collector's exit 8, any other non-zero its exit 7.
# Run it on the Intel, from the top of the lab tree, AFTER the queue on aifoundry2 has ended (status.json "ended"), with the lab approvals in place:
#
#   bash tools/claims-v3/e175/collect_e175_bounded.sh <a new, empty scratch dir> <the data dir, docs/reports/data/<date>-e175-governed-aifoundry2>
#
# Read-only on aifoundry2: no device opened, no lock taken, nothing written there (the remote rsync and hashing at nice 19). Exit codes: 0 collected
# and scored; 2 refused (a dir); 3 a remote call failed or ran past its bound; 4 no session; 5 the probe met a login link or no answer; 6 the code
# path differs; 7 the scorer failed; 8 a required C log or its check is missing. SPDX-License-Identifier: Apache-2.0
set -u
RAW=${1:?usage: collect_e175_bounded.sh <new empty scratch dir> <data dir>}
D=${2:?usage: collect_e175_bounded.sh <new empty scratch dir> <data dir>}
[ -d "$RAW" ] && [ -n "$(ls -A "$RAW" 2>/dev/null)" ] && { echo "refused: $RAW is not empty"; exit 2; }
[ -e "$D/aifoundry2" ] && { echo "refused: $D/aifoundry2 exists"; exit 2; }
TO=$(command -v timeout || command -v gtimeout) || { echo "refused: no timeout(1) here (coreutils)"; exit 2; }
PY=${PY:-/usr/bin/python3}
CALL_S=${E175_REMOTE_TIMEOUT_S:-600}
PROBE_S=15
BOX=aifoundry2
TREE=claude/et-soc1-prototyping
SSHO="-o BatchMode=yes -o ConnectTimeout=10"
SSH="ssh $SSHO"
R() { "$TO" -k 10 "$CALL_S" "$@"; }

# 0. the code-path check, before anything is collected
PC=$("$PY" -B tools/claims-v3/e175/check_e175.py --desk 2>&1); rc=$?
echo "$PC" | tail -1
[ $rc -eq 0 ] || { echo "$PC"; echo "refused: the desk's tree is not the registered bytes (check_e175.py --desk rc $rc): nothing collected"; exit 6; }

# 1. the probe: one ssh, hard-killed after 15 s
PR=$("$TO" -k 2 "$PROBE_S" ssh $SSHO "$BOX" true 2>&1 < /dev/null); rc=$?
if printf '%s' "$PR" | grep -qE 'https?://login\.[A-Za-z0-9.-]+/'; then
  echo "stopped: $BOX asks for a login check (the lab approval lapsed): nothing collected; the queue's data stays on the box. Collect again after it."
  exit 5
fi
[ $rc -eq 0 ] || { echo "stopped: the probe of $BOX did not answer in ${PROBE_S} s (rc $rc): nothing collected; collect again later"; exit 5; }
echo "probe: $BOX answered at $(date '+%H:%M:%S %Z')"

mkdir -p "$RAW/logs" "$RAW/cc" || exit 2

# 2. the queue's records, its stdout and the slot file, each call bounded
R rsync -a --rsync-path="nice -n 19 rsync" -e "$SSH" "$BOX:$TREE/build/e175/runs/" "$RAW/runs/" || { echo "stopped: rsync of the runs failed or ran past ${CALL_S} s"; exit 3; }
R rsync -a --rsync-path="nice -n 19 rsync" -e "$SSH" "$BOX:$TREE/build/e175/queue.out" "$BOX:claude/work/q143-a2-e175-slot.txt" "$RAW/logs/" \
  || { echo "stopped: rsync of queue.out and the slot file failed or ran past ${CALL_S} s"; exit 3; }

# 3. the sha256 of every kit file, pool tile and binary the queue ran from, on the box, against the desk's copy and the pins
cat > "$RAW/box_hash.sh" <<'EOS'
cd ~/claude/et-soc1-prototyping || exit 9
nice -n 19 sha256sum tools/claims-v3/e175/*.py tools/claims-v3/e175/*.json tools/claims-v3/e175/pool/tiles/*/*.bin tools/claims-v3/e173/p8gov.py tools/claims-v3/ccheck/*.sh \
  tools/claims-v3/ccheck/*.py tools/claims-v3/hpl/run_hpl.py tools/claims-v3/hpl/watcher_q142s.py build/ccheck/b/host/sparsity_host \
  build/sparsity_t2/kernel/sparsity.elf build/ettelem-hpl/ettelem
EOS
R $SSH "$BOX" 'bash -s' < "$RAW/box_hash.sh" > "$RAW/logs/box-files-sha256.txt" || { echo "stopped: the box's hashing failed or ran past ${CALL_S} s"; exit 3; }
"$PY" -B - "$RAW/logs/box-files-sha256.txt" <<'EOP' > "$RAW/logs/box-files-check.txt"
import hashlib, json, os, sys
H = json.load(open("tools/claims-v3/e175/harness-e175.json"))
pins = H["box_binaries_sha256"]
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

# 4. Q139(k)'s check of C at the desk (a fresh cache in the scratch dir), for every session that holds a C log; then the C-log list
for sd in "$RAW"/runs/*/; do
  s=$(basename "$sd")
  [ -f "$sd/c-log.jsonl" ] || continue
  CCHECK_CACHE="$RAW/ccache" nice -n 10 "$PY" -B tools/claims-v3/ccheck/ccheck.py check "$sd/c-log.jsonl" --out "$RAW/cc/ccheck-$s.json" \
    --jobs 2 > "$RAW/cc/ccheck-$s.txt" 2>&1
  echo "ccheck $s rc=$?"
done
"$PY" -B tools/claims-v3/q142kg-runbook/cclist_q142kg.py "$RAW/runs" "$RAW/cc" | tee "$RAW/logs/cclist.txt"
[ "${PIPESTATUS[0]}" -eq 0 ] || { echo "stopped: a session the registration requires to carry a C log has none (cclist above): nothing scored"; exit 8; }

# 4b. no other login enters the public repo: E111's scrub on the scratch copy (an end reason of E64's can hold one), as v3.1's s22 does for
#     aifoundry2's E168 and E169 copies, before anything reaches the data dir
"$PY" -B tools/claims-v3/e111/scrub_logins_e111.py "$RAW" > "$RAW/logs/scrub.txt" 2>&1 || { cat "$RAW/logs/scrub.txt"; echo "stopped: the login scrub failed: nothing reached $D"; exit 7; }

# 5. the data dir, as E165's collector lays it out
mkdir -p "$D/aifoundry2" "$D/logs"
rsync -a "$RAW/runs/" "$D/aifoundry2/"
cp "$RAW/logs/"* "$D/logs/"
cp "$RAW/cc/"ccheck-*.json "$D/" 2>/dev/null
find "$D/aifoundry2" -path '*/tel/*.jsonl' -type f -exec gzip -n {} +
find "$D/aifoundry2" \( -name launches.jsonl -o -name c-log.jsonl \) -type f -exec gzip -n {} +
printf '%s\n' "$PC" > "$D/logs/path-check.txt"

# 6. the registered scoring (score_e175.py): the sessions are the directories that hold a session.json (E165's A2-8), with every check of C
SESS=$(for s in "$D"/aifoundry2/s[0-9]*; do [ -f "$s/session.json" ] && printf '%s\n' "$s"; done)
[ -n "$SESS" ] || { echo "stopped: no session directory (with a session.json) under $D/aifoundry2: collected, not scored"; exit 4; }
CC=$(ls "$D"/ccheck-*.json 2>/dev/null)
nice -n 10 "$PY" -B tools/claims-v3/e175/score_e175.py $SESS --ccheck $CC --out "$D/results.json" > "$D/score.txt"; rc=$?
[ $rc -eq 5 ] && { cat "$D/score.txt"; echo "stopped: the scorer refused: a listed session has no check of C (exit 5): collected, not scored"; exit 8; }
[ $rc -eq 0 ] || { cat "$D/score.txt"; echo "stopped: the registered scorer failed (rc $rc): collected, not scored"; exit 7; }
ls "$D"/ccheck-s[0-9]*.json > /dev/null 2>&1 && gzip -n -k "$D"/ccheck-s[0-9]*.json
echo "collected into $D; scored: $(head -1 "$D/score.txt")"
