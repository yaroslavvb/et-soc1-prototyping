#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum), the box step "the collection" (this file is s22): the exact copy-back,
# then the data directory at the desk. E192's step 11's form (rb/s22_collect_e192.sh) with E195's files:
#   0. the desk-path gate's inputs first, before any copy (E183's nopath_desk_ready, rb/nopath_desk_e183.sh sourced UNCHANGED: HOME is
#      this account's home, else 10; no entry of the desk's home named as the box's tree, else 16);
#   1. the T0 step 9 recorded (RB_OUT/e195-T0.txt) names the session: only its own files are taken. One bounded read on the box: which
#      sources exist (the session's directory build/e195/T<T0>/, its launch output, its data folder in E195's root
#      build/claims-v3/aifoundry3/e195/build/claims-v3/aifoundry3/x09-T<T0>/, E195's build record, check_elf, loops, arm table, generator
#      check, the build attempts and their logs; the cmake logs stay on the box), and the box's manifest of every file under them by sha256
#      (a stuck sampler's telemetry.jsonl.raw, still being written, is left out of both, as the session's own manifest leaves it out);
#   2. the copy back (rsync -a -R, bounded) into RB_OUT/e195-raw/tree, at the box tree's paths;
#   3. THE EXACT COPY-BACK (collect_e195.py copycheck): the box's manifest against the copy, file by file (every file listed is there at
#      its sha256, nothing else is), and the session's own MANIFEST.sha256 holds: else 16, nothing collected; then THE DESK-PATH GATE on
#      the copy itself (nopath_desk, before our login is masked: a desk path is caught in the box's own bytes);
#   4. the data directory (collect_e195.py assemble): RB_OUT/e195-out/<day>-e195-x09-dramtoggle-aifoundry3/ (session/, passes/, build/,
#      launch.out, box-manifest.txt, facts-e195.json, SHA256SUMS) or, for a session that ended at a gate, its gate stop's record
#      RB_OUT/e195-out/gate-stops/<day>-e195-x09-dramtoggle-T<T0>-aifoundry3/ (committed under docs/reports/gate-stops/, never a datum);
#      OUR OWN BOX LOGIN MASKED (the look recorded it, RB_OUT/box-login-aifoundry3.txt);
#   5. the holder-line check (collect_e195.py scrubcheck), the desk-path gate again on the output (E183's kit note 5's nopath_desk, for a
#      desk whose home has the box's shape), the login scrub (E178's scrub_tree_e178.py --check, unchanged), and no E195 datum in any ref.
# The data directory is docs/reports/data/<day>-e195-x09-dramtoggle-aifoundry3/ in the data commit (the card lane's, after the public-text
# scan, through the lab's commit script, new files only, with the README in DATA-README-FORM-e195.md's form).
#   bash tools/claims-v3/e195/rb/s22_collect_e195.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e195.sh"
. "$(dirname "${BASH_SOURCE[0]}")/../../e183/rb/nopath_desk_e183.sh"     # E183's kit note 5, unchanged (E183_BOX is set by rb_e195.sh)
rb_init s22_collect
rb_window
nopath_desk_ready
DAY=$RB_DAY
T0=$(cat "$RB_OUT/e195-T0.txt" 2>/dev/null)
[ -n "$T0" ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_USAGE "no T0 recorded by step 9 ($RB_OUT/e195-T0.txt): collect only a session this runbook launched"
T0=${T0:-T0}
RAW=$RB_OUT/e195-raw; OUTP=$RB_OUT/e195-out
own=$(cat "$RB_OUT/box-login-aifoundry3.txt" 2>/dev/null)
[ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
[ -n "$own" ] || rb_die $RB_E_USAGE "no box login recorded by s05_look_k6.sh (RB_OUT/box-login-aifoundry3.txt): run the look first"
if [ -z "${RB_DRY:-}" ]; then
  [ -e "$RAW" ] && rb_die $RB_E_USAGE "$RAW already exists: move it aside first (a copy-back is exact only into an empty directory)"
  [ -e "$OUTP" ] && rb_die $RB_E_USAGE "$OUTP already exists: move it aside first"
  mkdir -p "$RAW/tree" "$OUTP"
fi
R=$E195_R
SRCS="build/e195/T$T0 build/e195/launch-T$T0.out $R/build/claims-v3/aifoundry3/x09-T$T0 $R/build/x09mem-built.txt $R/build/x09mem/check_elf.txt $R/build/x09mem/loops.txt $R/build/x09mem/arm-table.json $R/build/x09mem/arm-table.txt $R/build/x09mem/make-check.txt $R/build-attempts.txt $R/build-logs"
# (the cmake logs stay on the box: they carry the box's absolute paths and nothing the data needs; x09mem-built.txt carries the hashes)
rb_probe aifoundry3
f=$(rb_file have)
{ rb_prelude aifoundry3
  echo "SRCS='$SRCS'"
  cat <<'EOF2'
if [ "$(ours_live)" -gt 0 ]; then echo "REFUSED: a card session of ours still runs on $BOX: collect after it has ended (step 10)"; exit 3; fi
for s in $SRCS; do
  if [ -e "$s" ]; then echo "HAVE $s"; else echo "ABSENT $s"; fi
done
for s in $SRCS; do
  [ -e "$s" ] || continue
  find "$s" -type f ! -name telemetry.jsonl.raw | LC_ALL=C sort | while read -r p; do echo "SUM $(sha256sum "$p" | cut -d' ' -f1) $p"; done
done
EOF2
} > "$f"
rb_remote read aifoundry3 "which of E195's sources exist on the box, and the box's manifest of every file under them (sha256)" "$f"
rb_refused
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the read of E195's sources on aifoundry3 exited $RB_RC"
G=()
if [ -z "${RB_DRY:-}" ]; then
  rb_has "^HAVE build/e195/T$T0\$" || rb_die $RB_E_FAIL "aifoundry3 holds no session directory for T0 $T0: was the session launched by step 9?"
  grep '^SUM ' "$RB_CAP" > "$RAW/box-manifest.txt"
  grep '^ABSENT ' "$RB_CAP" > "$RAW/absent-on-box.txt"
  while read -r _ s; do G+=("aifoundry3:aifoundry/./$s"); done < <(grep '^HAVE ' "$RB_CAP")
else
  G=("aifoundry3:aifoundry/./build/e195/T<T0>" "aifoundry3:aifoundry/./<the data folder, the build record and logs>")
fi
rb_local copy aifoundry3 "copy back E195's session, its data folder and the build record (those the box holds), at the box tree's paths" \
  rsync -a -R --exclude telemetry.jsonl.raw -e "$RB_RSH" "${G[@]}" "$RAW/tree/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
rb_local read local "the exact copy-back: the box's manifest against the copy, and the session's own manifest (collect_e195.py copycheck)" \
  "$RB_PY" -I -B tools/claims-v3/e195/collect_e195.py copycheck "$RAW/box-manifest.txt" "$RAW/tree" "$T0"
rb_has '^COPY EXACT: ' || rb_die $RB_E_GATE "the copy back is not exact (the lines above): collect nothing; move $RAW aside and run this step again"
nopath_desk "$RAW/tree"                                          # the desk-path gate on the box's own bytes, before the login is masked
rb_local desk local "the data directory, or a gate stop's record (collect_e195.py assemble; our own box login masked)" \
  "$RB_PY" -I -B tools/claims-v3/e195/collect_e195.py assemble "$RAW/tree" "$T0" "$DAY" "$OUTP" --owner "$own"
rb_has '^ASSEMBLED ' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "the data directory was not assembled: read the output above"
asm=$(grep -m1 '^ASSEMBLED' "$RB_CAP" 2>/dev/null | cut -c1-200)
OUT=$OUTP/$DAY-e195-x09-dramtoggle-aifoundry3
rb_has '^ASSEMBLED gate-stops/' && OUT=$OUTP/gate-stops/$DAY-e195-x09-dramtoggle-T$T0-aifoundry3
rb_local read local "the holder lines and /home paths (collect_e195.py scrubcheck)" "$RB_PY" -I -B tools/claims-v3/e195/collect_e195.py scrubcheck "$OUT" --owner "$own"
rb_has '^SCRUB-CHECK OK' || rb_die $RB_E_GATE "a line names another account (the lines above): rewrite it by hand (E178's form, <another-user>), name it in the data README, then collect again"
nopath_desk "$OUT"
rb_local read local "another account's login or uid in any directory of the output (scrub_tree_e178.py --check, E178's, unchanged)" \
  /usr/bin/python3 -B tools/claims-v3/e178/scrub_tree_e178.py --check "$OUT" --owner "$own"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another account's login or uid is left in the output (the lines above): scrub it before any commit"
rb_local read local "no E195 datum in any ref yet (check_history_e195.py nodatum)" "$RB_PY" -I -B tools/claims-v3/e195/rb/check_history_e195.py nodatum
rb_has '^NO-DATUM OK' || rb_die $RB_E_GATE "an E195 datum is already in a ref: commit nothing; read why"
where="docs/reports/data/$DAY-e195-x09-dramtoggle-aifoundry3/"
case "$OUT" in */gate-stops/*) where="docs/reports/gate-stops/$DAY-e195-x09-dramtoggle-T$T0-aifoundry3/ (a gate stop's record: never a datum, never reduced)" ;; esac
rb_say "E195 COLLECTED: $OUT (it is $where), T0 $T0, the copy exact; ${asm:-}; before the commit, the public-text scan over its files and message"
exit 0
