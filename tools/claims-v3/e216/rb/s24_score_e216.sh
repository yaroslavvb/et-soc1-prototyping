#!/usr/bin/env bash
# E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum; E209's kit note 1's rb/s24_score_e209_n1.sh form): runbook step 13, THE
# REDUCTION AND THE FROZEN SCORER, AFTER THE DATA COMMIT. Its one manifest read of the committed session is `collect_e216.py --manifest-check`
# (every MANIFEST.sha256 line OK, but fwgate's read record, which passes only when it differs from the box's bytes by THE MASK's one ledger line
# alone: with the box's home written back, it reads its manifest line). Then E208's registered reducer (tools/claims-v3/e208/proposal/src/
# reduce_mms.py b9e32618... with its mms_common.py c3fc7883..., E216.md 7's measured side, run from the lab clone at its committed path) on the
# COMMITTED session folder, rb/post_e216.py labels before the scorer, score_e216.py (frozen) with step 6n's labels when they name a point
# (--labels), then rb/post_e216.py after (REPORTED: the points NO DATA named, by family, and the session's stop), then report_e216.py (fix-e216:
# E216-amendment-1.md A2 and A4, REPORTED: E1-E4 without family G, the head-to-heads by configuration). Outputs in RB_OUT/score/
# only; nothing is committed here (a later lane commits them).
#   RB_OUT=... bash tools/claims-v3/e216/rb/s24_score_e216.sh
# Exits: 0 scored (the scorer's words and the readings printed); 10 refused (no data commit of this day's directory in HEAD, the committed
# session not the copy-back's but for THE MASK, or a label naming nothing); 14 the reducer, the scorer or the readings failed (rc and output
# in RB_OUT/score/).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e216.sh"
rb_init s24_score
rb_need RB_OUT
[ -f "$RB_OUT/e216-datadir.txt" ] || rb_die 10 "no data directory in this RB_OUT (step 11)"
# shellcheck disable=SC1091
. "$RB_OUT/e216-datadir.txt"
cd "$RB_REPO" || rb_die 10 "cannot enter the lab clone"
C=$(git log --diff-filter=A --format=%H -- "$DD/SHA256SUMS" | tail -n 1)
[ -n "$C" ] || rb_die 10 "the data directory $DD is not committed in HEAD (step 12 first)"
[ -z "$(git status --porcelain -- "$DD")" ] || rb_die 10 "the data directory differs from its commit"
MC=$("$PY" -I -B "$E216_REL/collect_e216.py" --manifest-check "$DD/session" 2>&1); mrc=$?; echo "$MC"
[ "$mrc" -eq 0 ] || rb_die 10 "the committed session does not read its manifest OK, but for THE MASK (rc $mrc): $(echo "$MC" | tail -n 1)"
R8=tools/claims-v3/e208/proposal/src
[ "$(sha256sum $R8/reduce_mms.py | cut -c1-64)" = b9e32618020d28a590a615f97e5655c1ea458a6a757bf5658f2517a87fc3e0a5 ] || rb_die 10 "reduce_mms.py is not the registered one"
[ "$(sha256sum $R8/mms_common.py | cut -c1-64)" = c3fc7883544ad73c3e455f7e950b62b9b155fd2ed972cee5e3524d74a378569c ] || rb_die 10 "mms_common.py is not the registered one"
S="$RB_OUT/score"; mkdir -p "$S"
echo "the data commit ${C:0:12} ($(git log -1 --format=%cd --date=iso "$C")); HEAD $(git rev-parse --short HEAD)"
nice -n 10 timeout 900 "$PY" -I -B "$R8/reduce_mms.py" "$DD/session" --out "$S/data-e216.json" --txt "$S/reduce-e216.txt" > "$S/reduce.out" 2>&1
rc=$?; echo "reduce_mms.py rc $rc"
[ "$rc" -eq 0 ] || rb_die 14 "the reducer ended rc $rc (RB_OUT/score/reduce.out)"
LAB=()
if [ -f "$RB_OUT/ranbefore-e216.json" ]; then
  LW=$("$PY" -I -B "$E216_REL/rb/post_e216.py" labels "$RB_OUT/ranbefore-e216.json" 2>&1); lrc=$?
  echo "$LW"
  [ "$lrc" -eq 0 ] || rb_die 10 "the labels file: $(echo "$LW" | tail -n 1) (correct the dated note and RB_OUT/ranbefore-e216.json, never the scorer)"
fi
if [ -f "$RB_OUT/ranbefore-e216.json" ] && "$PY" -I -B -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1])).get("ran_before_points") else 1)' "$RB_OUT/ranbefore-e216.json"; then
  LAB=(--labels "$RB_OUT/ranbefore-e216.json")
  echo "the labels of step 6n are passed: $(grep -o '"ran_before_points": \[[^]]*\]' "$RB_OUT/ranbefore-e216.json")"
fi
OMP_NUM_THREADS=1 nice -n 10 timeout 1800 "$PY" -I -B "$E216_REL/score_e216.py" "$S/data-e216.json" --out "$S/scored-e216.json" "${LAB[@]}" > "$S/score.out" 2>&1
rc=$?; echo "score_e216.py rc $rc"
cat "$S/score.out"
[ "$rc" -eq 0 ] || rb_die 14 "the scorer ended rc $rc (RB_OUT/score/score.out)"
nice -n 10 timeout 900 "$PY" -I -B "$E216_REL/rb/post_e216.py" after "$S/data-e216.json" "$S/scored-e216.json" --out "$S/post-e216.json" > "$S/post.out" 2>&1
rc=$?; echo "post_e216.py after rc $rc"
cat "$S/post.out"
[ "$rc" -eq 0 ] || rb_die 14 "the readings beside the scorer ended rc $rc (RB_OUT/score/post.out)"
# fix-e216 (E216-amendment-1.md A2 and A4, REPORTED): T1-T3 and E1-E4 without family G and with G alone, and the head-to-heads by distinct
# configuration, from the frozen scorer's own output (the registered report_e216.py; it refuses, 4, unless the scorer is at its pin)
nice -n 10 timeout 900 "$PY" -I -B "$E216_REL/report_e216.py" "$S/scored-e216.json" --out "$S/reported-e216.json" > "$S/reported.out" 2>&1
rc=$?; echo "report_e216.py rc $rc (REPORTED: Amendment 1's A2 and A4)"
cat "$S/reported.out"
[ "$rc" -eq 0 ] || rb_die 14 "Amendment 1's REPORTED readings ended rc $rc (RB_OUT/score/reported.out); the scorer's outputs stand as written"
rb_ok "scored: RB_OUT/score/scored-e216.json, score.out, post-e216.json, post.out, reported-e216.json and reported.out (read their words: every rule, the head-to-heads, the pair rule, NO DATA named by family, Amendment 1's REPORTED readings; do not commit them here)"
