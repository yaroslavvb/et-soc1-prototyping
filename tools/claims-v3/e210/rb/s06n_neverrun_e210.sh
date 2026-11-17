#!/usr/bin/env bash
# E210 (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; kit-e207's step 6n form), the step "the never-run search, repeated" (this
# file is s06n): E210.md section 4's "E210's card lane repeats this search before its data commit and says which". Two forms:
#   STEP 6n (`A`, the last step before step 7's config read, the day's first card command): E210's registered scanner and report, unchanged,
#     over the registered roots (desk/neverrun_card_e210.py says which and what it leaves out): at the desk the lab clone at HEAD, the round's
#     lane folders (E210_ROUND_OUT: the card lane sets it to the round's OUT) and HOME/claude/work; on aifoundry3 one bounded read (the wait
#     class, 600 s; reads only, nice 19 and idle IO, nothing written there): the registered tops that exist, E210's own folders and the model
#     session's left out by the scanner's own --exclude; `A --desk-only` leaves the box out and the words say "aifoundry3 NOT SEARCHED" (only
#     after three failed tries of the full form: CARD-LANE-BRIEF.md 2). RB_OUT/neverrun-<time>/ holds the scans and the report;
#     RB_OUT/e210-neverrun.txt its NEVER-RUN line, whose time step 7 reads (step 7 refuses, 10, unless this step ended rc 0 within the last 30
#     minutes) and which step 9 needs from today;
#   STEP 12n (`A --late`, after the copy-back and before step 12): the desk's three roots again (the lab at HEAD, the lane folders, the work
#     folder; no box call): RB_OUT/neverrun-late-<time>/ and RB_OUT/e210-neverrun-late.txt, written after the session's end, which step 12
#     needs (both reports go into the data directory).
# A pattern found run is REPORTED (the card lane's README says which; E210.md 4: it stays in E210), never a gate. The words give the verdict of
# E210.md amendment A1 item 1 first (fix-e210, before any datum: both conditions count a GEMM string only inside a host launch record;
# desk/neverrun_gens_e210.py classes every string, at the desk and in the same bounded read on aifoundry3), then its conditions apart,
# condition (ii) read anywhere, and the registered rule's verdict as first written (desk/neverrun_card_e210.py).
# Exits: 0 the search done (its words on the last line); 10 refused (no window, no E210_ROUND_OUT, --late before a copy-back); 14 a scan or the
# report failed (run it again); the k6 codes for the box call (11, 12, 13).
#   E210_ROUND_OUT=<the round's OUT> bash tools/claims-v3/e210/rb/s06n_neverrun_e210.sh A [--desk-only | --late]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e210.sh"
rb_init s06n_neverrun
e210_arm "${1:-}"
form=${2:-}
case "$form" in ""|--desk-only|--late) ;; *) rb_die $RB_E_USAGE "usage: s06n_neverrun_e210.sh A [--desk-only | --late]" ;; esac
e210_window
E=tools/claims-v3/e210
if [ -z "${RB_DRY:-}" ]; then
  [ -n "${E210_ROUND_OUT:-}" ] && [ -d "${E210_ROUND_OUT:-}" ] || rb_die $RB_E_USAGE "E210_ROUND_OUT does not name the round's lane folders (set it to the round's OUT)"
  case "$(cd "$E210_ROUND_OUT" && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "E210_ROUND_OUT is inside the lab repo: refused" ;; esac
  if [ "$form" = --late ]; then
    cb=$(ls -1t "$RB_OUT"/e210-copied-*.txt 2>/dev/null | head -n 1)
    [ -n "$cb" ] && [ "$(TZ=America/Los_Angeles date -r "$cb" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ] ||
      rb_die $RB_E_USAGE "the --late form follows today's copy-back (step 11's RB_OUT/e210-copied-*.txt): none today"
  fi
fi
tag=neverrun; [ "$form" = --late ] && tag=neverrun-late
N="$RB_OUT/$tag-$(date +%Y%m%dT%H%M%S)"
[ -n "${RB_DRY:-}" ] || mkdir -p "$N" || rb_die $RB_E_USAGE "cannot make $N"
export E210_ROUND_OUT
late=(); [ "$form" = --late ] && late=(--late)
rb_local desk local "the never-run search at the desk: E210's registered scanner (unchanged) over the lab at HEAD, the round's lane folders and HOME/claude/work, E210's own folders and the model session's left out" \
  /usr/bin/python3 -I -B $E/desk/neverrun_card_e210.py desk "$N" ${late[@]+"${late[@]}"}
[ -n "${RB_DRY:-}" ] || rb_has '^SCANNED-DESK ' || rb_die $RB_E_FAIL "the desk's scans did not end (rc $RB_RC; the lines above): run this step again"
a3args=(--a3-not-searched "the --desk-only form, after three failed tries of the full form (CARD-LANE-BRIEF.md 2)")
[ "$form" = --late ] && a3args=()
if [ -z "$form" ]; then
  rb_probe "$BOX"
  f=$(rb_file a3scan)
  { rb_prelude "$BOX"
    echo 'tops=""; for d in "$HOME/claude/work" "$HOME/claude/et-soc1-prototyping" "$HOME/aifoundry" "$HOME/e71" "$HOME"/q1[0-9][0-9]-* "$HOME/tmp"; do [ -d "$d" ] && tops="$tops $d"; done'
    echo 'ex=""; for d in "$HOME"/aifoundry/build/e210 "$HOME"/aifoundry/build/e210rgm "$HOME"/aifoundry/tools/claims-v3/e210 "$HOME"/claude/work/ee-*; do [ -d "$d" ] && ex="$ex --exclude=$d"; done'
    echo 'echo "A3HOME $HOME"'
    echo 'echo "A3SCAN-BEGIN"'
    echo 'nice -n 19 ionice -c 3 python3 -I -B - scan aifoundry3-ours $tops $ex 2>/dev/null <<'"'"'RB_NR_EOF'"'"''
    cat "$RB_REPO/$E/desk/neverrun_e210.py"
    echo 'RB_NR_EOF'
    echo 'rc=$?; echo; echo "A3SCAN-END rc $rc"'          # the scanner's JSON ends without a newline
    echo 'echo "A3GENS-BEGIN"'                              # E210.md A1 item 1 (fix-e210): the classes of non-host generators, the same tops
    echo 'nice -n 19 ionice -c 3 python3 -I -B - scan aifoundry3-ours $tops $ex 2>/dev/null <<'"'"'RB_NG_EOF'"'"''
    cat "$RB_REPO/$E/desk/neverrun_gens_e210.py"
    echo 'RB_NG_EOF'
    echo 'rc=$?; echo; echo "A3GENS-END rc $rc"'
  } > "$f"
  rb_remote wait "$BOX" "the never-run search on aifoundry3: E210's registered scanner (unchanged) and A1's scanner, both on stdin, over our folders there, reads only" "$f"
  if [ -z "${RB_DRY:-}" ]; then
    [ "$RB_RC" -eq 0 ] && rb_has '^A3SCAN-END rc 0$' || rb_die $RB_E_FAIL "aifoundry3's scan did not end rc 0 (rc $RB_RC): run this step again (after three failed tries: A --desk-only)"
    sed -n '/^A3SCAN-BEGIN$/,/^A3SCAN-END rc /p' "$RB_CAP" | sed '1d;$d' > "$N/scan-aifoundry3-ours.json"
    "$RB_PY" -I -B -c 'import json, sys; json.load(open(sys.argv[1]))' "$N/scan-aifoundry3-ours.json" 2> /dev/null ||
      rb_die $RB_E_FAIL "aifoundry3's scan output is not whole JSON: run this step again"
    rb_has '^A3GENS-END rc 0$' || rb_die $RB_E_FAIL "aifoundry3's A1 scan did not end rc 0: run this step again (after three failed tries: A --desk-only)"
    sed -n '/^A3GENS-BEGIN$/,/^A3GENS-END rc /p' "$RB_CAP" | sed '1d;$d' > "$N/gens-aifoundry3-ours.json"
    "$RB_PY" -I -B -c 'import json, sys; json.load(open(sys.argv[1]))' "$N/gens-aifoundry3-ours.json" 2> /dev/null ||
      rb_die $RB_E_FAIL "aifoundry3's A1 scan output is not whole JSON: run this step again"
    a3h=$(sed -n 's/^A3HOME //p' "$RB_CAP" | head -n 1)
    a3args=(--a3 "$N/scan-aifoundry3-ours.json" --a3-gens "$N/gens-aifoundry3-ours.json" --a3-home "$a3h")
  else
    a3args=(--a3 "$N/scan-aifoundry3-ours.json" --a3-gens "$N/gens-aifoundry3-ours.json")
  fi
fi
rb_local desk local "the report: E210's registered report (neverrun_e210.py report, unchanged), scrubbed, and the files naming any hit" \
  /usr/bin/python3 -I -B $E/desk/neverrun_card_e210.py report "$N" ${a3args[@]+"${a3args[@]}"} ${late[@]+"${late[@]}"}
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^NEVER-RUN ' || rb_die $RB_E_FAIL "the report gave no NEVER-RUN line (rc $RB_RC; the lines above): run this step again"
line=$(grep -m1 '^NEVER-RUN ' "$RB_CAP")
if [ "$form" = --late ]; then
  echo "$N" > "$RB_OUT/e210-neverrun-late-dir.txt"
  echo "$(date '+%F %T %Z') $line" > "$RB_OUT/e210-neverrun-late.txt"
else
  echo "$N" > "$RB_OUT/e210-neverrun-dir.txt"
  echo "$(date '+%F %T %Z') $line" > "$RB_OUT/e210-neverrun.txt"
fi
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM form=${form:-6n} $line" >> "$RB_LOG"
rb_say "the never-run search, repeated (${form:-6n}): $line (the report in $(basename "$N")/$([ "$form" = --late ] && echo '; step 12 copies it into the data directory' || echo '; step 7 follows within 30 minutes, else this step again'))"
exit 0
