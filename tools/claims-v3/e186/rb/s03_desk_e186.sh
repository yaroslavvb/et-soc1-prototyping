#!/usr/bin/env bash
# E186 (Q158, the kit), KIT.md box step 2 (this file is s03): the desk check before any box step, on the Intel only. A port of E182's step 2
# v5 (tools/claims-v3/e182/rb/s03_desk_e182_v5.sh) in E185's v3 form (tools/claims-v3/e185/rb/s03_desk_e185_v3.sh: each list at its count
# AND its own committed bytes), each change marked E186:
#   - the window rule first: RB_OUT's window written today (Pacific) for E186 (e186_window), or refused (10) before any call;
#   - the pull runs under the lab-git lock (e186_pull: RB_GITLOCK required), never beside another lane's commit;
#   - HEAD descends from E186's registration (a41408d9), its merged list (80d53792) and its note M1 (3adb8bfe);
#   - E186's, M12's and the workload's paths clean, and E182's files that E186 calls;
#   - the history check (rb/check_history_e186.py tree, E185's day-2 check in E186's form, from verify-d2b's faults 2 and 3): no commit
#     since E186's registration changed anything but an addition on E186's paths, no added file shadows a module, nothing uncommitted;
#   - EVERY LIST E186 READS, each checked OK in full AND at its pinned count AND at its own committed sha256, with no override:
#       E186's registration 10; M12's four (read beside them: 37, 24, 1 and 9); E182's six whose files E186 calls or imports (32, 79, 50,
#       49, 89 and 19);
#     E186's kit list (SHA256SUMS-e186-kit) at its pinned count (it lists this file, so it cannot pin its own bytes here);
#   - october-forecast-model's note M1 (E186.md.dated-note-M1.md, 3adb8bfe): its list SHA256SUMS-e186-m1 read at its count (5) and its own
#     bytes and REPORTED, never a gate (the M1 arm is reported, never one of E186's rules); any later dated M-note list
#     (SHA256SUMS-e186-m2 and on) is read and reported the same way, never a gate;
#   - harness-e186.json rebuilt (CHECK PASS); E186's items, images, orders and trains (e186_common.py --verify); HARNESS OK 71 at the
#     desk; the train host's build inputs (E182's check_inputs_e182.py, NOTE1 FILES OK 10); the registration's plan and forecast lines
#     re-made (plan_e186.py --check, forecast_e186.py --check); the kit's desk tests' logs as committed; any E186 data in any ref reported.
#
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e186/rb/s03_desk_e186.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e186.sh"
rb_init s03_desk
e186_window
E=tools/claims-v3/e186
PINS="tools/claims-v3/e186/SHA256SUMS-e186-registration:10:04cc77c832595a6f9acaecf43c4ab6472f4f263515615e9a0efcc8701a8458b4
tools/claims-v3/m12/SHA256SUMS-m12:37:6d93edfd09bf7a5f816c494bb99745f752c9450d71d4504987808a36dfb70f7e
tools/claims-v3/m12/SHA256SUMS-m12-e186:24:1ecbcc772e52f8413820ff7822f16649fa85b81aefc91a71459e0f0eb1ea4aad
tools/claims-v3/m12/SHA256SUMS-m12-rules:1:938e2e1e750c64fd441453229f364b95530ea1869c02efaea968b5c4d7ed342e
tools/claims-v3/m12/SHA256SUMS-m12-note2:9:788b84bd445833cb39e4b0455776e9b023f1d6006de73871772ca59de5bdceea
tools/claims-v3/e182/SHA256SUMS-e182-registration:32:ff09c0d4407171909fe34be41a79804c49c407849c1e8a3111ad012ceb8a4dbe
tools/claims-v3/e182/SHA256SUMS-e182-kit:79:021a436e3cedb1d9f4e2849ee56e1cfa241448ba0420f2507b066b968929c2ca
tools/claims-v3/e182/SHA256SUMS-e182-note1:50:8a977cf28ea0a610f523b53024a37b8db3c90f2768861a647db3a778918f8e5c
tools/claims-v3/e182/SHA256SUMS-e182-note2:49:313a89d825421c3ce1e82bc071750a664744d8ef7fb9ffbe8ad328235611ef72
tools/claims-v3/e182/SHA256SUMS-e182-note3:89:c0c458eedbbb679a84107e87966a251becbf5faf8e23357b8618dc8cc393a456
tools/claims-v3/e182/SHA256SUMS-e182-note4:19:6870f1fee712a0c41394842b520b30924b47bb2f329fc06626a3eab36fcd878f"   # list:count:its own sha256
KITPIN=tools/claims-v3/e186/SHA256SUMS-e186-kit:74                   # the kit's own list, at its count
M1PIN=tools/claims-v3/e186/SHA256SUMS-e186-m1:5:06d278ddf41e5cd55cf210f1444a517312fc1a4a4a41a3bcffabd723dec426b3   # reported, never a gate
bad=""
e186_pull || bad="$bad pull"
for c in "$RB_E186_BASE registration" "$RB_E186_MERGED merged-list" "$RB_E186_M1 note-M1"; do
  set -- $c
  rb_local read local "HEAD descends from $1 (E186's $2)" git -C "$RB_REPO" merge-base --is-ancestor "$1" HEAD || bad="$bad ancestry-$2"
done
rb_local read local "E186's, M12's and the workload's paths and E182's called files clean" git -C "$RB_REPO" status --short tools/claims-v3/e186 \
  tools/claims-v3/m12 workloads/sparsity tools/claims-v3/e182/patch_host_e182.py tools/claims-v3/e182/check_inputs_e182.py \
  tools/claims-v3/e182/harness-e182.json tools/claims-v3/e182/harness-e182-note1.json tools/claims-v3/e182/build_host_e182_v2.sh \
  tools/claims-v3/e182/e182_stats.py tools/claims-v3/e182/power_e182.py
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
# E186 (from verify-d2b's faults 2 and 3 on the day-2 kits): the history check. The kit's own list is pinned at its count only (it lists
# this file), so a kit file rewritten together with its line would pass it; no commit since E186's registration may change anything but
# an addition on E186's paths, no added file may shadow a module, and nothing may be uncommitted there (rb/check_history_e186.py)
rb_local read local "the history check: no change but an addition since $RB_E186_BASE on E186's paths, no shadowing addition, nothing uncommitted (check_history_e186.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e186.py tree --anchor "$RB_E186_BASE"
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
# every list at its count and its own bytes (no override); M12's lists name their files beside them, so each list is read in its directory
paths=""; for spec in $PINS; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the eleven lists E186 reads (pinned)" shasum -a 256 $paths
own=$RB_CAP
for spec in $PINS; do
  l=${spec%%:*}; rest=${spec#*:}; pin=${rest%%:*}; hpin=${rest#*:}
  RB_CWD="$RB_REPO/$(dirname "$l")"
  case "$l" in tools/claims-v3/m12/*) ;; *) RB_CWD="$RB_REPO" ;; esac
  arg=$l; [ "$RB_CWD" != "$RB_REPO" ] && arg=$(basename "$l")
  RB_CWD=$RB_CWD rb_local read local "the list $(basename "$l") (pinned at $pin entries and its own sha256)" shasum -a 256 -c "$arg"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$RB_REPO/$l" 2>/dev/null); m=${m:-0}
    h=$(awk -v p="$l" '$2 == p {print $1}' "$own")
    why=""; [ "$h" = "$hpin" ] || why="; its own bytes differ from the pin"
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ] && [ -z "$why" ]; } || bad="$bad $(basename "$l")($n OK of $m; pinned $pin$why)"
  fi
done
unset RB_CWD
l=${KITPIN%%:*}; pin=${KITPIN##*:}
rb_local read local "E186's kit list $(basename "$l") (pinned at $pin entries)" shasum -a 256 -c "$l"
if [ -z "${RB_DRY:-}" ]; then
  n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$RB_REPO/$l" 2>/dev/null); m=${m:-0}
  { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ]; } || bad="$bad $(basename "$l")($n OK of $m; pinned $pin)"
fi
rb_local read local "harness-e186.json rebuilt" /usr/bin/python3 -B $E/make_harness_e186.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local read local "the items, their images, the fallback's orders and the trains (e186_common.py --verify)" /usr/bin/python3 -B $E/e186_common.py --verify
rb_has '"problems": \[\]' || bad="$bad items"
rb_local read local "the harness without binaries (check_e186.py --desk)" /usr/bin/python3 -B $E/check_e186.py --desk
rb_has '^HARNESS OK: 71 files' || bad="$bad harness"
rb_local read local "the train host's build inputs and E182 note 1's box files (check_inputs_e182.py, E182's, unchanged)" /usr/bin/python3 -B tools/claims-v3/e182/check_inputs_e182.py
rb_has '^NOTE1 FILES OK: 10 files' || bad="$bad build-inputs"
rb_local read local "the registration's plan re-made (plan_e186.py --check)" /usr/bin/python3 -B $E/plan_e186.py --root . --check
rb_has '^CHECK PASS' || bad="$bad plan"
rb_local read local "the registration's forecast lines re-made (forecast_e186.py --check)" /usr/bin/python3 -B $E/forecast_e186.py --root . --check
rb_has '^CHECK PASS' || bad="$bad forecast"
for spec in "logs/desktest-host-e186.txt ^DESKTEST-HOST-E186.[0-9]+.of.[0-9]+.PASS" "logs/selftest-score-e186.txt ^SELFTEST-SCORE-E186.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-stops-e186t.txt ^SELFTEST-STOPS-E186T.[0-9]+.of.[0-9]+.PASS" "logs/dry-intel-e186.txt ^DRY-INTEL-E186.PASS" \
            "logs/selftest-rb-e186.txt ^SELFTEST-RB-E186.[0-9]+.of.[0-9]+.PASS" "logs/selftest-history-e186.txt ^SELFTEST-HISTORY-E186.[0-9]+.of.[0-9]+.PASS"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
# october-forecast-model's notes, REPORTED (never a gate): note M1's list at its count and its own bytes; any later M-note's list read
l=${M1PIN%%:*}; rest=${M1PIN#*:}; pin=${rest%%:*}; hpin=${rest#*:}
m1="absent (not read)"
if [ -f "$E/E186.md.dated-note-M1.md" ] || [ -n "${RB_DRY:-}" ]; then
  rb_local read local "october-forecast-model's note M1: its list $(basename "$l") ($pin entries and its own sha256; REPORTED, never a gate)" shasum -a 256 -c "$l"
  if [ -n "${RB_DRY:-}" ]; then
    m1="(its list read at $pin entries and its own bytes)"
  else
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$RB_REPO/$l" 2>/dev/null); m=${m:-0}
    h=$(shasum -a 256 "$RB_REPO/$l" 2>/dev/null | awk '{print $1}')
    if [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ] && [ "$h" = "$hpin" ]; then
      m1="present, its list $n of $pin at its pinned bytes (read beside, by its reader, after step 11's score)"
    else
      m1="present, but its list is off its pin ($n OK of $m; pinned $pin$([ "$h" = "$hpin" ] || echo '; its own bytes differ')): the M1 arm is not read on this day (a reported arm: no E186 rule depends on it; the data README records it)"
    fi
  fi
fi
later=""
for ml in "$RB_REPO"/$E/SHA256SUMS-e186-m[2-9]*; do
  [ -f "$ml" ] || continue
  rb_local read local "a later october-forecast-model note's list $(basename "$ml") (REPORTED, never a gate)" shasum -a 256 -c "$E/$(basename "$ml")"
  later="$later $(basename "$ml") rc $RB_RC ($(grep -c ': OK$' "$RB_CAP") OK);"
done
rb_local read local "E186 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e186*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
echo "$(date '+%F %T %Z') step=$RB_STEP october-forecast-model note M1 $m1;${later:- no later M-note}" >> "$RB_LOG"
rb_say "desk check: the window written today for E186; pulled under the lab-git lock, HEAD descends from $RB_E186_BASE, $RB_E186_MERGED and $RB_E186_M1, the paths clean, no change but an addition since $RB_E186_BASE on E186's paths (HISTORY OK), the eleven lists at their pinned counts and bytes (10; 37, 24, 1, 9; 32, 79, 50, 49, 89, 19) and the kit's at its count (${KITPIN##*:}), harness-e186.json rebuilt, the items, images, orders and trains verified, HARNESS OK 71, NOTE1 FILES OK 10, the plan and forecast re-made, the kit's desk tests' logs; october-forecast-model note M1 $m1;${later:- no later M-note}; commits naming E186 data: $nd"
