#!/usr/bin/env bash
# E188 (Q165, the kit), KIT.md box step 2 (this file is s03): the desk check before any box step, on the Intel only. A port of E186's step
# 2 v2 with its v1 inside it (tools/claims-v3/e186/rb/s03_desk_e186_v2.sh and s03_desk_e186.sh, run on 9 Nov 2026) in one file, with E183's
# step 2 v5's list rule (tools/claims-v3/e183/rb/s03_desk_e183_v5.sh: lists found by "SHA256SUMS" ANYWHERE in a file's name), each change
# marked E188:
#   - the window rule first: RB_OUT's window written today (Pacific) for E188 (e188_window), or refused (10) before any call;
#   - the pull runs under the lab-git lock (e188_pull: RB_GITLOCK required), never beside another lane's commit;
#   - HEAD descends from E188's registration (878b6f63);
#   - E188's, E186's, M12's, E182's called files' and the workload's paths clean;
#   - the history check (rb/check_history_e188.py tree): no commit since E188's registration changed anything but an addition on E188's
#     paths, no added file shadows a module, nothing uncommitted;
#   - EVERY LIST E188 READS, each OK in full AND at its pinned count AND at its own committed sha256, with no override: E188's
#     registration 20; M12's four (37, 24, 1, 9); E182's six (32, 79, 50, 49, 89, 19); E186's registration 10; E186's data 376 and its
#     note 1 6 (E188-GB1's and E188-GA23's references and the scorer's self-test); the scale route's six (209, 16, 9, 68, 10, 160); and THE
#     KIT'S OWN LIST (SHA256SUMS-e188-kit) at its count and its own bytes (this step is outside it: a file cannot hold the sha256 of a list
#     that holds its own; E188's anchor lines give this step's sha256 beside the list's);
#   - E188 change: every file with "SHA256SUMS" anywhere in its name under tools/claims-v3/e188 is found (find -name '*SHA256SUMS*'): each
#     one this step pins is read as above; one it does not know is REPORTED, never a gate (E183 v5's rule);
#   - harness-e188.json rebuilt (CHECK PASS); E188's items, images, orders and trains (e188_common.py --verify); HARNESS OK 72 at the desk;
#     the train host's build inputs (E182's check_inputs_e182.py, NOTE1 FILES OK 10); the registration's plan and forecast lines re-made
#     (plan_e188.py --check, forecast_e188.py check) and e188_stats.py's self-check; the kit's desk tests' logs as committed; any E188 data in
#     any ref reported;
#   - HEAD unchanged across all of it, else 16.
#
#   RB_GITLOCK=<the lab-git lock> bash tools/claims-v3/e188/rb/s03_desk_e188.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e188.sh"
rb_init s03_desk
e188_window
E=tools/claims-v3/e188
PINS="tools/claims-v3/e188/SHA256SUMS-e188-registration:20:b098561b055e9d85b87ea7e501105fda2f84234699a2b50b7ee8724fa0b9970e
tools/claims-v3/m12/SHA256SUMS-m12:37:6d93edfd09bf7a5f816c494bb99745f752c9450d71d4504987808a36dfb70f7e
tools/claims-v3/m12/SHA256SUMS-m12-e186:24:1ecbcc772e52f8413820ff7822f16649fa85b81aefc91a71459e0f0eb1ea4aad
tools/claims-v3/m12/SHA256SUMS-m12-rules:1:938e2e1e750c64fd441453229f364b95530ea1869c02efaea968b5c4d7ed342e
tools/claims-v3/m12/SHA256SUMS-m12-note2:9:788b84bd445833cb39e4b0455776e9b023f1d6006de73871772ca59de5bdceea
tools/claims-v3/e182/SHA256SUMS-e182-registration:32:ff09c0d4407171909fe34be41a79804c49c407849c1e8a3111ad012ceb8a4dbe
tools/claims-v3/e182/SHA256SUMS-e182-kit:79:021a436e3cedb1d9f4e2849ee56e1cfa241448ba0420f2507b066b968929c2ca
tools/claims-v3/e182/SHA256SUMS-e182-note1:50:8a977cf28ea0a610f523b53024a37b8db3c90f2768861a647db3a778918f8e5c
tools/claims-v3/e182/SHA256SUMS-e182-note2:49:313a89d825421c3ce1e82bc071750a664744d8ef7fb9ffbe8ad328235611ef72
tools/claims-v3/e182/SHA256SUMS-e182-note3:89:c0c458eedbbb679a84107e87966a251becbf5faf8e23357b8618dc8cc393a456
tools/claims-v3/e182/SHA256SUMS-e182-note4:19:6870f1fee712a0c41394842b520b30924b47bb2f329fc06626a3eab36fcd878f
tools/claims-v3/e186/SHA256SUMS-e186-registration:10:04cc77c832595a6f9acaecf43c4ab6472f4f263515615e9a0efcc8701a8458b4
docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3/SHA256SUMS:376:7eaf01e5aff31a000d7294a8c1f853574c2c29b25cc5a6ada0fb15304e6c4ad6
docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3/SHA256SUMS-note1:6:f430d8695609ed8fe1b577f4e6cbb866d83e1e94736b6df6307d95367d0fd2c1
tools/claims-v3/m10/POOL8-SHA256SUMS:209:9675e44e1343dd77871d33427efd84ffff43a858659446c3e17edf9dc7c8cd18
docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS:16:fa274e3673865d5681d83c2fc3deb38e76fde001fd6931cef332c6119df85013
docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS-a2:9:65942a7669016df1b1f46f5266bb95cb78bcef2083bc873d3832bd5887898b27
docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS:68:89463de27354f68fed9fab56ec7bb8b5d962ede274f2fb8b0662d86fc34ef597
docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS-a2:10:0187d28e5d9c2a3992fc152c343d1a38f9b2c87a157abef6e40d1def5dc24c65
docs/reports/data/2026-11-05-q142x-pool8-freeze/SHA256SUMS:160:26eb0b2511e6f4ed3e6e9cc0646f24106a06cfffd402b388ddb110a5e10ab8d2"   # list:count:its own sha256
KITPIN=tools/claims-v3/e188/SHA256SUMS-e188-kit:106:e9bb2836479f97ae686207571925836e4aa76575e2790cbb52dc25b984be1024   # the kit's own list, at its count and its own bytes
bad=""
e188_pull || bad="$bad pull"
rb_local read local "HEAD before the checks" git -C "$RB_REPO" rev-parse HEAD
h0=$(rb_val '^([0-9a-f]{40})$')
rb_local read local "HEAD descends from $RB_E188_BASE (E188's registration)" git -C "$RB_REPO" merge-base --is-ancestor "$RB_E188_BASE" HEAD || bad="$bad ancestry"
rb_local read local "E188's, E186's, M12's and the workload's paths and E182's called files clean" git -C "$RB_REPO" status --short tools/claims-v3/e188 \
  tools/claims-v3/e186 tools/claims-v3/m12 workloads/sparsity tools/claims-v3/e182/patch_host_e182.py tools/claims-v3/e182/check_inputs_e182.py \
  tools/claims-v3/e182/harness-e182.json tools/claims-v3/e182/harness-e182-note1.json tools/claims-v3/e182/build_host_e182_v2.sh \
  tools/claims-v3/e182/e182_stats.py tools/claims-v3/e182/power_e182.py tools/claims-v3/e182/plan_e182.py tools/claims-v3/e182/reduce_e182.py
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad status"
rb_local read local "the history check: no change but an addition since $RB_E188_BASE on E188's paths, no shadowing addition, nothing uncommitted (check_history_e188.py)" \
  /usr/bin/python3 -I -B $E/rb/check_history_e188.py tree --anchor "$RB_E188_BASE"
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || bad="$bad history"
# every list at its count and its own bytes (no override); M12's and the beside-form data lists name their files beside them
paths=""; for spec in $PINS $KITPIN; do paths="$paths ${spec%%:*}"; done
rb_local read local "the own sha256 of the lists E188 reads (pinned)" shasum -a 256 $paths
own=$RB_CAP
for spec in $PINS $KITPIN; do
  l=${spec%%:*}; rest=${spec#*:}; pin=${rest%%:*}; hpin=${rest#*:}
  case "$l" in
    tools/claims-v3/m12/*|docs/reports/data/2026-11-09-e186-*|docs/reports/data/2026-11-04-q142m-m10/*) RB_CWD="$RB_REPO/$(dirname "$l")"; arg=$(basename "$l") ;;
    *) RB_CWD="$RB_REPO"; arg=$l ;;
  esac
  RB_CWD=$RB_CWD rb_local read local "the list $(basename "$l") (pinned at $pin entries and its own sha256)" shasum -a 256 -c "$arg"
  if [ -z "${RB_DRY:-}" ]; then
    n=$(grep -c ': OK$' "$RB_CAP"); m=$(grep -c . "$RB_REPO/$l" 2>/dev/null); m=${m:-0}
    h=$(awk -v p="$l" '$2 == p {print $1}' "$own")
    why=""; [ "$h" = "$hpin" ] || why="; its own bytes differ from the pin"
    { [ "$RB_RC" -eq 0 ] && [ "$n" -eq "$m" ] && [ "$n" -eq "$pin" ] && [ -z "$why" ]; } || bad="$bad $(basename "$l")($n OK of $m; pinned $pin$why)"
  fi
done
unset RB_CWD
# E188: every list in E188's directory by "SHA256SUMS" anywhere in its name; the pinned are read above, any other reported, never a gate
rb_local read local "every file with SHA256SUMS anywhere in its name under $E" find "$E" -name '*SHA256SUMS*' -type f
unknown=""
if [ -z "${RB_DRY:-}" ]; then
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    case " $paths " in *" $f "*) ;; *) unknown="$unknown $f" ;; esac
  done < "$RB_CAP"
fi
for f in $unknown; do
  rb_local read local "a list step 2 does not pin: $(basename "$f") (REPORTED, never a gate)" shasum -a 256 -c "$f"
done
rb_local read local "harness-e188.json rebuilt" /usr/bin/python3 -B $E/make_harness_e188.py --check
rb_has '^CHECK PASS' || bad="$bad harness-rebuild"
rb_local read local "the items, their images, the kinds passes' orders and the trains (e188_common.py --verify)" /usr/bin/python3 -B $E/e188_common.py --verify
rb_has '"problems": \[\]' || bad="$bad items"
rb_local read local "the harness without binaries (check_e188.py --desk)" /usr/bin/python3 -B $E/check_e188.py --desk
rb_has '^HARNESS OK: 72 files' || bad="$bad harness"
rb_local read local "the train host's build inputs and E182 note 1's box files (check_inputs_e182.py, E182's, unchanged)" /usr/bin/python3 -B tools/claims-v3/e182/check_inputs_e182.py
rb_has '^NOTE1 FILES OK: 10 files' || bad="$bad build-inputs"
rb_local read local "the registration's plan re-made (plan_e188.py --check)" /usr/bin/python3 -B $E/plan_e188.py --root . --check
rb_has '^CHECK PASS' || bad="$bad plan"
rb_local read local "the registration's forecast lines re-made (forecast_e188.py check)" /usr/bin/python3 -B $E/forecast_e188.py --root . check
rb_has 'CHECK PASS' || bad="$bad forecast"
rb_local read local "the registration's statistics' self-check (e188_stats.py)" /usr/bin/python3 -B $E/e188_stats.py
rb_has '^e188_stats self-check PASS' || bad="$bad stats"
for spec in "logs/desktest-train-check-e188.txt ^DESKTEST-TRAIN-CHECK-E188.PASS" "logs/desktest-host-e188.txt ^DESKTEST-HOST-E188.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-score-e188.txt ^SELFTEST-SCORE-E188.[0-9]+.of.[0-9]+.PASS" "logs/selftest-arm-e188.txt ^SELFTEST-ARM-E188.[0-9]+.of.[0-9]+.PASS" \
            "logs/selftest-stops-e188t.txt ^SELFTEST-STOPS-E188T.[0-9]+.of.[0-9]+.PASS" "logs/dry-intel-e188.txt ^DRY-INTEL-E188.PASS" \
            "logs/selftest-rest-e188.txt ^SELFTEST-REST-E188.PASS" "logs/selftest-rb-e188.txt ^SELFTEST-RB-E188.[0-9]+.of.[0-9]+.PASS"; do
  set -- $spec
  rb_local read local "a desk test's log, as committed: $1" grep -cE "$2" "$E/$1"
  rb_has '^1$' || bad="$bad $(basename "$1" .txt)"
done
rb_local read local "HEAD after the checks" git -C "$RB_REPO" rev-parse HEAD
h1=$(rb_val '^([0-9a-f]{40})$')
[ -n "${RB_DRY:-}" ] || [ "$h0" = "$h1" ] || bad="$bad HEAD-moved"
[ -z "$bad" ] || rb_die $RB_E_GATE "the desk check failed:$bad"
rb_local read local "E188 data in any ref (want none before the session)" git -C "$RB_REPO" log --all --oneline -- 'docs/reports/data/*e188*'
nd=0; [ -z "${RB_DRY:-}" ] && nd=$(grep -c . "$RB_CAP")
echo "$(date '+%F %T %Z') step=$RB_STEP lists not pinned (reported):${unknown:- none}" >> "$RB_LOG"
rb_say "desk check: the window written today for E188; pulled under the lab-git lock, HEAD ${h1:0:12} descends from $RB_E188_BASE, the paths clean, no change but an addition since $RB_E188_BASE on E188's paths (HISTORY OK), the lists at their pinned counts and bytes (20; 37, 24, 1, 9; 32, 79, 50, 49, 89, 19; 10; 376, 6; 209, 16, 9, 68, 10, 160) and the kit's ($(echo "$KITPIN" | cut -d: -f2)), lists not pinned (reported):${unknown:- none}; harness-e188.json rebuilt, the items, images, orders and trains verified, HARNESS OK 72, NOTE1 FILES OK 10, the plan and forecast re-made, the statistics' self-check, the kit's desk tests' logs; commits naming E188 data: $nd"
