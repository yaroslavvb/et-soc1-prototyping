#!/usr/bin/env bash
# E224 ARM B (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum; E216's kit's rb/s24_score_e216.sh form, landed in 59f5288b; E209's
# kit note 1's): runbook step 13, THE REDUCTION AND THE FROZEN SCORER, AFTER THE DATA COMMIT. Its one manifest read of the committed session is
# `collect_e224b.py --manifest-check` (every MANIFEST.sha256 line OK, but fwgate's read record, which passes only when it differs from the box's
# bytes by THE MASK's one ledger line alone). Then E208's registered reducer (tools/claims-v3/e208/proposal/src/reduce_mms.py b9e32618... with its
# mms_common.py c3fc7883..., E224.md 7's measured side for arm B, run from the lab clone at its committed path) on the COMMITTED session folder;
# step 6n's labels checked (desk/neverrun_card_e224.py check-labels ... --arm B); score_e224.py (frozen) with `--b` (arm B's measured side) and
# the labels when they name a point (--labels); then rb/post_e224b.py after (REPORTED: arm B's points with no route-c reading named, by family,
# and the session's stop). Outputs in RB_OUT/score/ only: scores-e224.json and .txt for arm B alone (arm A's rules and the pooled rules read NO
# DATA in this file: the scores lane scores the pooled rules once both arms are committed); nothing is committed here (a later lane commits them).
#   RB_OUT=... bash tools/claims-v3/e224/rb/s24_score_e224b.sh
# Exits: 0 scored (the scorer's words and the readings printed); 10 refused (no data commit of this day's directory in HEAD, the committed
# session not the copy-back's but for THE MASK, or a label naming nothing); 14 the reducer, the scorer or the readings failed (rc and output
# in RB_OUT/score/).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e224b.sh"
rb_init s24_score
rb_need RB_OUT
[ -f "$RB_OUT/e224b-datadir.txt" ] || rb_die 10 "no data directory in this RB_OUT (step 11)"
# shellcheck disable=SC1091
. "$RB_OUT/e224b-datadir.txt"
cd "$RB_REPO" || rb_die 10 "cannot enter the lab clone"
C=$(git log --diff-filter=A --format=%H -- "$DD/SHA256SUMS" | tail -n 1)
[ -n "$C" ] || rb_die 10 "the data directory $DD is not committed in HEAD (step 12 first)"
[ -z "$(git status --porcelain -- "$DD")" ] || rb_die 10 "the data directory differs from its commit"
MC=$("$PY" -I -B "$E224B_REL/collect_e224b.py" --manifest-check "$DD/session" 2>&1); mrc=$?; echo "$MC"
[ "$mrc" -eq 0 ] || rb_die 10 "the committed session does not read its manifest OK, but for THE MASK (rc $mrc): $(echo "$MC" | tail -n 1)"
R8=tools/claims-v3/e208/proposal/src
[ "$(sha256sum $R8/reduce_mms.py | cut -c1-64)" = b9e32618020d28a590a615f97e5655c1ea458a6a757bf5658f2517a87fc3e0a5 ] || rb_die 10 "reduce_mms.py is not the registered one"
[ "$(sha256sum $R8/mms_common.py | cut -c1-64)" = c3fc7883544ad73c3e455f7e950b62b9b155fd2ed972cee5e3524d74a378569c ] || rb_die 10 "mms_common.py is not the registered one"
S="$RB_OUT/score"; mkdir -p "$S"
echo "the data commit ${C:0:12} ($(git log -1 --format=%cd --date=iso "$C")); HEAD $(git rev-parse --short HEAD)"
nice -n 10 timeout 900 "$PY" -I -B "$R8/reduce_mms.py" "$DD/session" --out "$S/data-e224b.json" --txt "$S/reduce-e224b.txt" > "$S/reduce.out" 2>&1
rc=$?; echo "reduce_mms.py rc $rc"
[ "$rc" -eq 0 ] || rb_die 14 "the reducer ended rc $rc (RB_OUT/score/reduce.out)"
LAB=()
if [ -f "$RB_OUT/ranbefore-e224b.json" ]; then
  LW=$("$PY" -I -B "$E224B_REL/desk/neverrun_card_e224.py" check-labels "$RB_OUT/ranbefore-e224b.json" --arm B 2>&1); lrc=$?
  echo "$LW"
  [ "$lrc" -eq 0 ] || rb_die 10 "the labels file: $(echo "$LW" | tail -n 1) (correct the dated note and RB_OUT/ranbefore-e224b.json, never the scorer)"
  if "$PY" -I -B -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1]))["ran_before_points"]["B"] else 1)' "$RB_OUT/ranbefore-e224b.json"; then
    LAB=(--labels "$RB_OUT/ranbefore-e224b.json")
    echo "the labels of step 6n are passed: $(tr -d '\n ' < "$RB_OUT/ranbefore-e224b.json")"
  fi
fi
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 nice -n 10 timeout 1800 "$PY" -I -B "$E224B_REL/score_e224.py" --lab "$RB_REPO" --b "$S/data-e224b.json" "${LAB[@]}" --out "$S" > "$S/score.out" 2>&1
rc=$?; echo "score_e224.py rc $rc"
cat "$S/score.out"
[ "$rc" -eq 0 ] && [ -s "$S/scores-e224.json" ] || rb_die 14 "the scorer ended rc $rc (RB_OUT/score/score.out)"
nice -n 10 timeout 900 "$PY" -I -B "$E224B_REL/rb/post_e224b.py" after "$S/data-e224b.json" "$S/scores-e224.json" --out "$S/post-e224b.json" > "$S/post.out" 2>&1
rc=$?; echo "post_e224b.py after rc $rc"
cat "$S/post.out"
[ "$rc" -eq 0 ] || rb_die 14 "the readings beside the scorer ended rc $rc (RB_OUT/score/post.out)"
rb_ok "scored: RB_OUT/score/scores-e224.json and .txt, score.out, post-e224b.json and post.out (read their words: THE PICK as the lab holds it, arm B's R0, T1-T3, E1-E4, H1-H12, the REPORTED readings, NO DATA named by family; do not commit them here)"
