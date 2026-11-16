#!/usr/bin/env bash
# E197 (Q185, the kit), the box step "the dry pass" (this file is s10), for this RB_OUT's sitting: THE SITTING'S WRAPPER ITSELF with
# --dry on aifoundry3 (session_e197.sh, its dry path: its refusals run, nothing is opened, the reference session's own DRY mode lists
# every device call), into build/e197/T<T0>-dry (the rest rules skip it), each listing compared by the wrapper, byte for byte with the
# host and OUT written as the registration's and the clock stamps dropped, to the registration's (check_e197.py drycmp, LISTING SAME):
# sitting 1 BOTH PLANS (full, 429 device calls; short, 331), because step 7 chooses the plan later, at the first card command; sitting 2
# the ext plan (277). E193's step 8's form: k6's detached job a3-dry-e197-<sitting> (one at a time, never beside a session of ours),
# then `wait` (bounded; 17 while it runs), which writes RB_OUT/e197-<sitting>-dry-ok.txt when it ended rc 0 (step 7's wrapper requires
# it). Step 9 refuses a sitting whose dry pass did not end rc 0 today. It sends nothing to the card: run it before the rest has opened
# (the order 5, 6, 8, then 7 and 9).
#   bash tools/claims-v3/e197/rb/s10_a3_dry_e197.sh start      then      ... wait
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e197.sh"
rb_init s10_a3_dry
act=${1:-}
case "$act" in start|wait) ;; *) rb_die $RB_E_USAGE "usage: s10_a3_dry_e197.sh start | wait" ;; esac
e197_window
JOB=a3-dry-e197-$E197_SIT
[ -n "${RB_DRY:-}" ] || e197_built_today || rb_die $RB_E_USAGE "regfile was not built today (RB_OUT/e197-built.txt, step 6's wait): run step 6 first"
if [ "$act" = start ]; then
  rb_need_start
  hs=$(e197_harness_sha); [ -n "${RB_DRY:-}" ] && hs=${hs:-HARNESS-SHA256}
  [ -n "$hs" ] || rb_die $RB_E_USAGE "harness-e197.json's sha256 could not be read in the lab clone"
  rm -f "$RB_OUT/e197-$E197_SIT-dry-ok.txt"
  rb_probe aifoundry3
  body=$(rb_file body)
  { echo "SIT=$E197_SIT; HSHA=$hs; ROOT=$E197_ROOT"
    cat <<'EOF2'
K=$ROOT/tools/claims-v3/e197
PLANS="full short"; [ "$SIT" = 2 ] && PLANS=ext
T0=$(date +%s); ok=1; i=0
for P in $PLANS; do
  T=$((T0 + i)); i=$((i + 1))
  E197_T0=$T E197_SIT=$SIT E197_PLAN=$P E197_HARNESS_SHA256=$HSHA bash "$K/session_e197.sh" --dry < /dev/null
  rc=$?
  SD=build/e197/T$T-dry
  grep -E 'session start|checked:|DRY mode|GATE-STOP|session end' "$SD/session.log" 2>/dev/null | cut -c1-240
  echo "E197-DRY sitting $SIT plan $P rc=$rc $(head -n 1 "$SD/drycmp.txt" 2>/dev/null | cut -c1-120) manifest=$([ -s "$SD/MANIFEST.sha256" ] && echo written || echo absent)"
  [ "$rc" -eq 0 ] && grep -q '^LISTING SAME ' "$SD/drycmp.txt" 2>/dev/null && [ -s "$SD/MANIFEST.sha256" ] || ok=0
done
[ "$ok" -eq 1 ]
EOF2
  } > "$body"
  rb_job_start aifoundry3 "$JOB" "$body"
  rb_say "the dry pass $JOB started on aifoundry3: run this step's wait (bounded) until it ends"
  exit 0
fi
rb_probe aifoundry3
rb_job_wait aifoundry3 "$JOB"
rc=$?
[ -n "${RB_DRY:-}" ] && { rb_say "then, on rc 0: RB_OUT/e197-$E197_SIT-dry-ok.txt (step 7's wrapper requires it)"; exit 0; }
if [ "$rc" -eq 0 ]; then
  grep '^E197-DRY' "$RB_CAP" > "$RB_OUT/e197-$E197_SIT-dry-ok.txt"
  rb_say "the dry pass ended rc 0: $(grep '^E197-DRY' "$RB_CAP" | cut -c1-120 | tr '\n' ';')"
  exit 0
fi
exit "$rc"
