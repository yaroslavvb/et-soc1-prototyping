#!/bin/bash
# blind-v3-e212s3 step 3: once the re-run's data commit is on GitHub main (work/main-with-data.txt, written by s02_wait.sh), read the
# committed data and score exactly as declared (DECLARED-blind-s3.md 23d9cdd6..., .json f6603956...; scorer s03_score.py 45803a24...).
#   a. git archive of the S3 data folder from main's commit into work/data-s3/ (LAB only read); its SHA256SUMS checked inside the folder;
#   b. the order check (s02_order.py) -> work/order-s3.json and the label (BLIND or REPORTED);
#   c. the frozen scorer, unchanged (its sha256 checked first), in slot.sh, single-threaded, waiting while the 1-minute load is above 6;
#   d. every file hashed, with the time, in logs/progress.txt.
set -u
W=<W>
L=$W/out/blind-v3-e212s3
LAB=<LAB>
V3=$L/work/lab-b149/tools/matmul/mm1/v3
SCORER_SHA=45803a24eb73e20816467aaa672bb742909f14d1d6f5e18ec294f95b638112c6
DECL_MD_SHA=23d9cdd6ce8b94f4aea5ff198a9039e934f11256a43f25514bc9c7303e3d8792
DECL_JS_SHA=f6603956e9cd3ea97cf0c3cb6fe4c6c0002f9abea1c94aec7c471d22d629f42a
DECLARED='2026-11-18 14:10:50'
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:
ts() { TZ=America/Los_Angeles date '+%F %T %Z'; }
prog() { echo "$(ts) $*" >> "$L/logs/progress.txt"; }
M=$(cat "$L/work/main-with-data.txt")
echo "== s03 run $(ts); main with data $M"
[ "$(sha256sum "$L/scripts/s03_score.py" | cut -d' ' -f1)" = "$SCORER_SHA" ] || { echo "STOP: the scorer differs from the declared one"; exit 4; }
[ "$(sha256sum "$L/DECLARED-blind-s3.md" | cut -d' ' -f1)" = "$DECL_MD_SHA" ] || { echo "STOP: DECLARED-blind-s3.md differs"; exit 4; }
[ "$(sha256sum "$L/DECLARED-blind-s3.json" | cut -d' ' -f1)" = "$DECL_JS_SHA" ] || { echo "STOP: DECLARED-blind-s3.json differs"; exit 4; }
echo "OK   scorer and declaration unchanged since step 1"
DIRS=$(git -C "$LAB" ls-tree -d --name-only "$M" docs/reports/data/ | grep -E 'e212.*a2c0-S3')
echo "   data folder(s) on main: $DIRS"
[ "$(echo "$DIRS" | grep -c .)" = 1 ] || { echo "STOP: want exactly one S3 data folder on main"; exit 4; }
D=$DIRS
[ -e "$L/work/data-s3" ] && { echo "STOP: work/data-s3 exists (no overwrite)"; exit 4; }
mkdir -p "$L/work/data-s3"
git -C "$LAB" archive --format=tar "$M" "$D" | tar -x -C "$L/work/data-s3"
echo "   archive rc ${PIPESTATUS[0]} $(ts)"
F=$L/work/data-s3/$D
( cd "$F" && for s in SHA256SUMS*; do echo "   $s sha256 $(sha256sum "$s" | cut -d' ' -f1): $(sha256sum -c "$s" 2>/dev/null | grep -c ': OK$') OK, $(sha256sum -c "$s" 2>/dev/null | grep -vc ': OK$') not OK"; done )
DATA=$(ls "$F"/data-e212-*S3*.json 2>/dev/null)
[ "$(echo "$DATA" | grep -c .)" = 1 ] || { echo "STOP: want exactly one data-e212-*S3*.json, found: $DATA"; exit 4; }
echo "   data file $(basename "$DATA") sha256 $(sha256sum "$DATA" | cut -d' ' -f1) $(wc -c < "$DATA") bytes"
prog "step 3a: data commit on main $M; folder $D archived to work/data-s3; data file $(basename "$DATA") sha256 $(sha256sum "$DATA" | cut -d' ' -f1); folder SHA256SUMS sha256 $(sha256sum "$F/SHA256SUMS" | cut -d' ' -f1) rc 0"
echo "-- the order check"
/usr/bin/python3 -I -B "$L/scripts/s02_order.py" --folder "$F" --lab "$LAB" --main "$M" --declared "$DECLARED" --out "$L/work/order-s3.json"
LABEL=$(/usr/bin/python3 -I -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["label"])' "$L/work/order-s3.json")
echo "   label: $LABEL"
prog "step 3b: order check work/order-s3.json sha256 $(sha256sum "$L/work/order-s3.json" | cut -d' ' -f1): label $LABEL rc 0"
case "$LABEL" in BLIND|REPORTED) ;; *) echo "STOP: label undecided"; exit 5;; esac
echo "-- the score"
end=$(( $(date +%s) + 480 ))
while :; do
  l1=$(cut -d' ' -f1 /proc/loadavg)
  if awk -v l="$l1" 'BEGIN{exit !(l <= 6.0)}'; then break; fi
  [ "$(date +%s)" -ge "$end" ] && { echo "load still $l1 at $(ts): not scored this call"; exit 3; }
  sleep 20
done
echo "   load $l1 at $(ts)"
mkdir -p "$L/work/score-s3"
bash "$W/slot.sh" env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  /usr/bin/python3 -I -B "$L/scripts/s03_score.py" --v3 "$V3" --data "$DATA" --session a2c0-S3 --label "$LABEL" --out "$L/work/score-s3"
rc=$?
echo "   scorer rc $rc at $(ts)"
for f in "$L"/work/score-s3/*; do echo "   $(sha256sum "$f" | cut -d' ' -f1) $(basename "$f")"; done
prog "step 3c: scored ($LABEL) by s03_score.py $SCORER_SHA: $(for f in "$L"/work/score-s3/*; do printf '%s %s; ' "$(basename "$f")" "$(sha256sum "$f" | cut -c1-16)"; done)rc $rc"
exit $rc
