#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): runbook step 13, THE REDUCTION AND THE FROZEN SCORER, AFTER THE DATA
# COMMIT (E209.md section 7): E208's registered reducer, unchanged (tools/claims-v3/e208/proposal/src/reduce_mms.py b9e32618... with its
# mms_common.py c3fc7883..., run from the lab clone at its committed path), on the COMMITTED session folder (checked first against
# the copy-back's manifest), then score_e209.py, frozen, on its output, with step 6n's labels when they name a point (--labels). Outputs in
# RB_OUT/score/ only; nothing is committed here (a later lane commits them, byte for byte, with their printed lines).
# fix-e209 (Q202c, before any E209 datum; E209.md amendment A1, verify-e209's findings 3, 5 and 6): before the scorer, rb/post_e209.py
# labels refuses (10) a labels file with an entry that names no point or time case of points-e209.json (the frozen scorer would echo it as
# applied and go on scoring the point); after it, rb/post_e209.py after writes RB_OUT/score/post-e209.json and post.out, REPORTED only:
# the points left out of every rule unnamed (NO DATA: no kept run; kept runs but no time reading; a time reading but no energy reading),
# reading (f)'s day offset against E208's 27 anchor runs on this card, and H4n on H4's line.
#   RB_OUT=... bash tools/claims-v3/e209/rb/s24_score_e209.sh
# Exits: 0 scored (the scorer's words and the readings printed); 10 refused (no data commit of this day's directory in HEAD, the committed
# session not the copy-back's, or a label naming nothing); 14 the reducer, the scorer or the readings failed (rc and output in RB_OUT/score/).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e209.sh"
rb_init s24_score
rb_need RB_OUT
[ -f "$RB_OUT/e209-datadir.txt" ] || rb_die 10 "no data directory in this RB_OUT (step 11)"
# shellcheck disable=SC1091
. "$RB_OUT/e209-datadir.txt"
cd "$RB_REPO" || rb_die 10 "cannot enter the lab clone"
C=$(git log --diff-filter=A --format=%H -- "$DD/SHA256SUMS" | tail -n 1)
[ -n "$C" ] || rb_die 10 "the data directory $DD is not committed in HEAD (step 12 first)"
[ -z "$(git status --porcelain -- "$DD")" ] || rb_die 10 "the data directory differs from its commit"
( cd "$DD/session" && sha256sum -c --quiet MANIFEST.sha256 ) || rb_die 10 "the committed session does not read its manifest OK"
R8=tools/claims-v3/e208/proposal/src
[ "$(sha256sum $R8/reduce_mms.py | cut -c1-64)" = b9e32618020d28a590a615f97e5655c1ea458a6a757bf5658f2517a87fc3e0a5 ] || rb_die 10 "reduce_mms.py is not the registered one"
[ "$(sha256sum $R8/mms_common.py | cut -c1-64)" = c3fc7883544ad73c3e455f7e950b62b9b155fd2ed972cee5e3524d74a378569c ] || rb_die 10 "mms_common.py is not the registered one"
S="$RB_OUT/score"; mkdir -p "$S"
echo "the data commit ${C:0:12} ($(git log -1 --format=%cd --date=iso "$C")); HEAD $(git rev-parse --short HEAD)"
nice -n 10 timeout 900 "$PY" -I -B "$R8/reduce_mms.py" "$DD/session" --out "$S/data-e209.json" --txt "$S/reduce-e209.txt" > "$S/reduce.out" 2>&1
rc=$?; echo "reduce_mms.py rc $rc"
[ "$rc" -eq 0 ] || rb_die 14 "the reducer ended rc $rc (RB_OUT/score/reduce.out)"
LAB=()
if [ -f "$RB_OUT/ranbefore-e209.json" ]; then
  LW=$("$PY" -I -B "$E209_REL/rb/post_e209.py" labels "$RB_OUT/ranbefore-e209.json" 2>&1); lrc=$?
  echo "$LW"
  [ "$lrc" -eq 0 ] || rb_die 10 "the labels file: $(echo "$LW" | tail -n 1) (correct the dated note and RB_OUT/ranbefore-e209.json, never the scorer)"
fi
if [ -f "$RB_OUT/ranbefore-e209.json" ] && "$PY" -I -B -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1])).get("ran_before_points") or json.load(open(sys.argv[1])).get("ran_before_cases") else 1)' "$RB_OUT/ranbefore-e209.json"; then
  LAB=(--labels "$RB_OUT/ranbefore-e209.json")
  echo "the labels of step 6n are passed: $(grep -o '"ran_before_points": \[[^]]*\]' "$RB_OUT/ranbefore-e209.json")"
fi
OMP_NUM_THREADS=1 nice -n 10 timeout 1800 "$PY" -I -B "$E209_REL/score_e209.py" "$S/data-e209.json" --out "$S/scored-e209.json" "${LAB[@]}" > "$S/score.out" 2>&1
rc=$?; echo "score_e209.py rc $rc"
cat "$S/score.out"
[ "$rc" -eq 0 ] || rb_die 14 "the scorer ended rc $rc (RB_OUT/score/score.out)"
nice -n 10 timeout 900 "$PY" -I -B "$E209_REL/rb/post_e209.py" after "$S/data-e209.json" "$S/scored-e209.json" --out "$S/post-e209.json" > "$S/post.out" 2>&1
rc=$?; echo "post_e209.py after rc $rc"
cat "$S/post.out"
[ "$rc" -eq 0 ] || rb_die 14 "the readings beside the scorer ended rc $rc (RB_OUT/score/post.out)"
rb_ok "scored: RB_OUT/score/scored-e209.json, score.out, post-e209.json and post.out (read their words: NO DATA named, the day offset, H4n beside H4; do not commit them here)"
