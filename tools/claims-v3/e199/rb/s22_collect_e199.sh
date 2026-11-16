#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum; E192's file, a6fe5c20, unchanged beside it, ported to aifoundry1 card 1), the box step "the collection" (this file is s22): the exact copy-back,
# then the data directory at the desk. E183's step 11 v3's form (rb/s22_collect_e183_v3.sh, kit note 5) with E199's files:
#   0. (E192's step 0, E183's desk-path gate's inputs, is NOT used here: E183's gate refuses on a desk whose home holds an entry named as
#      the box's tree, and aifoundry2's home holds 'nekko', aifoundry1's tree; E191's step 11 form is used instead: k6's desk-path gate,
#      rb_nopath (nopath_q142s.py), on the copy and on the data directory, as E191's collections of Sun 15 Nov 2026 ran it);
#   1. the T0 step 9 recorded (RB_OUT/e199-T0.txt) names the session: only its own files are taken. One bounded read on the box: which
#      sources exist (the session's directory build/e199/T<T0>/, its launch output, E199's build record, check_elf, arm table, the box's
#      preflight and the build attempts; the cmake logs stay on the box) and the box's manifest of every file under them, by sha256;
#   2. the copy back (rsync -a -R, bounded) into RB_OUT/e199-raw/tree, at the box tree's paths;
#   3. THE EXACT COPY-BACK (collect_e199.py copycheck): the box's manifest against the copy, file by file (every file listed is there at
#      its sha256, nothing else is), and the session's own MANIFEST.sha256 holds: else 16, nothing collected; then THE DESK-PATH GATE on
#      the copy itself (k6's rb_nopath, before our login is masked: a desk path is caught in the box's own bytes);
#   4. the data directory (collect_e199.py assemble): RB_OUT/e199-out/<day>-e199-intbits-aifoundry1-c1/ (run/, session/, build/,
#      box-manifest.txt, facts-e199.json, SHA256SUMS), OUR OWN BOX LOGIN MASKED (the look recorded it, RB_OUT/box-login-aifoundry1.txt);
#   5. the holder-line check (collect_e199.py scrubcheck: the reference session's "held:" and "another user's device process:" lines and
#      /home paths of another name), the desk-path gate again on the data directory (k6's rb_nopath), the login scrub (E178's scrub_tree_e178.py --check, unchanged), and no E199 datum in any ref yet.
# The data directory is docs/reports/data/<day>-e199-intbits-aifoundry1-c1/ in the data commit (the card lane's, after the public-text scan,
# through the lab's commit script, new files only, with the README in KIT.md section 9's form).
#   bash tools/claims-v3/e199/rb/s22_collect_e199.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e199.sh"
rb_init s22_collect
rb_window
DAY=$RB_DAY
T0=$(cat "$RB_OUT/e199-T0.txt" 2>/dev/null)
[ -n "$T0" ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_USAGE "no T0 recorded by step 9 ($RB_OUT/e199-T0.txt): collect only a session this runbook launched"
T0=${T0:-T0}
RAW=$RB_OUT/e199-raw; OUTP=$RB_OUT/e199-out; OUT=$OUTP/$DAY-e199-intbits-aifoundry1-c1
own=$(cat "$RB_OUT/box-login-aifoundry1.txt" 2>/dev/null)
[ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
[ -n "$own" ] || rb_die $RB_E_USAGE "no box login recorded by s05_look_k6.sh (RB_OUT/box-login-aifoundry1.txt): run the look first"
if [ -z "${RB_DRY:-}" ]; then
  [ -e "$RAW" ] && rb_die $RB_E_USAGE "$RAW already exists: move it aside first (a copy-back is exact only into an empty directory)"
  [ -e "$OUT" ] && rb_die $RB_E_USAGE "$OUT already exists: move it aside first"
  mkdir -p "$RAW/tree" "$OUTP"
fi
SRCS="build/e199/T$T0 build/e199/launch-T$T0.out $E199_R/build/intbits/BUILD-E199.txt $E199_R/build/intbits/check_elf.txt $E199_R/build/intbits/arm-table.jsonl $E199_R/build/intbits/preflight.txt $E199_R/build-attempts.txt"
# (the cmake logs stay on the box: they carry the box's absolute paths and nothing the data needs; BUILD-E199.txt carries the hashes)
rb_probe aifoundry1
f=$(rb_file have)
{ rb_prelude aifoundry1
  echo "SRCS='$SRCS'; DAY='$DAY'; ER='$E199_R'"
  cat <<'EOF2'
for s in $SRCS; do
  if [ -e "$s" ]; then echo "HAVE $s"; else echo "ABSENT $s"; fi
done
for s in $SRCS; do
  [ -e "$s" ] || continue
  find "$s" -type f | LC_ALL=C sort | while read -r p; do echo "SUM $(sha256sum "$p" | cut -d' ' -f1) $p"; done
done
EOF2
} > "$f"
rb_remote read aifoundry1 "which of E199's sources exist on the box, and the box's manifest of every file under them (sha256)" "$f"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read of E199's sources on aifoundry1 exited $RB_RC"
G=()
if [ -z "${RB_DRY:-}" ]; then
  rb_has "^HAVE build/e199/T$T0\$" || rb_die $RB_E_FAIL "aifoundry1 holds no session directory for T0 $T0: was the session launched by step 9?"
  grep '^SUM ' "$RB_CAP" > "$RAW/box-manifest.txt"
  grep '^ABSENT ' "$RB_CAP" > "$RAW/absent-on-box.txt"
  while read -r _ s; do G+=("aifoundry1:nekko/./$s"); done < <(grep '^HAVE ' "$RB_CAP")
else
  G=("aifoundry1:nekko/./build/e199/T<T0>" "aifoundry1:nekko/./<the build record and logs>")
fi
rb_local copy aifoundry1 "copy back E199's session and build record (those the box holds), at the box tree's paths" rsync -a -R -e "$RB_RSH" "${G[@]}" "$RAW/tree/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
rb_local read local "the exact copy-back: the box's manifest against the copy, and the session's own manifest (collect_e199.py copycheck)" \
  "$RB_PY" -I -B tools/claims-v3/e199/collect_e199.py copycheck "$RAW/box-manifest.txt" "$RAW/tree" "$T0"
rb_has '^COPY EXACT: ' || rb_die $RB_E_GATE "the copy back is not exact (the lines above): collect nothing; move $RAW aside and run this step again"
rb_nopath "$RAW/tree"                                            # k6's desk-path gate (E191's step 11 form) on the box's own bytes, before the login is masked
rb_local desk local "the data directory (collect_e199.py assemble; our own box login masked)" \
  "$RB_PY" -I -B tools/claims-v3/e199/collect_e199.py assemble "$RAW/tree" "$T0" "$DAY" "$OUTP" --owner "$own"
rb_has '^ASSEMBLED ' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "the data directory was not assembled: read the output above"
rb_local read local "the holder lines and /home paths (collect_e199.py scrubcheck)" "$RB_PY" -I -B tools/claims-v3/e199/collect_e199.py scrubcheck "$OUT" --owner "$own"
rb_has '^SCRUB-CHECK OK' || rb_die $RB_E_GATE "a line names another account (the lines above): rewrite it by hand (E178's form, <another-user>), name it in the data README, then collect again"
rb_nopath "$OUT"
rb_local read local "another account's login or uid in any directory of the output (scrub_tree_e178.py --check, E178's, unchanged)" \
  /usr/bin/python3 -B tools/claims-v3/e178/scrub_tree_e178.py --check "$OUT" --owner "$own"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another account's login or uid is left in the output (the lines above): scrub it before any commit"
rb_local read local "no E199 datum in any ref yet (check_history_e199.py nodatum)" "$RB_PY" -I -B tools/claims-v3/e199/rb/check_history_e199.py nodatum
rb_has '^NO-DATUM OK' || rb_die $RB_E_GATE "an E199 datum is already in a ref: commit nothing; read why"
rb_say "E199 COLLECTED: $OUT (the data directory is docs/reports/data/$DAY-e199-intbits-aifoundry1-c1/), T0 $T0, the copy exact; $(grep -m1 '^ASSEMBLED' "$RB_CAP" 2>/dev/null | cut -c1-160); before the data commit, the public-text scan over its files and message"
exit 0
