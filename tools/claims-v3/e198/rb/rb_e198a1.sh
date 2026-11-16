# E198 dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum): the part every A1 runbook step sources. It sources
# rb_e198.sh (kit-e198, Q191, unchanged: k6's common library, the window rule, the lab-git lock, the box, the sittings) and changes only:
#   - e198_harness_sha reads harness-e198-a1.json (the A1 session's harness; the launch passes its sha256);
#   - E198_A1_DOC, the amendment's file: step 2 (A1) finds A1's commit by its content (the commit that added it);
#   - the A1 jobs' names: the build a1-build-e198a1, the dry pass a1-dry-e198a1-<A|B>. The kit's v1 steps 6, 8 and 9 read only their own
#     names (a1-build-e198, a1-dry-e198-<A|B>), so a v1 sitting cannot launch on A1's build or dry pass (step 9 v1 refuses: not built today);
#   - E198_SESSION_RE, the A1 session's real script name for pgrep (step 10 and 11): session_e198a1\.sh; step 11 refuses beside either
#     session's name (E198_ANY_SESSION_RE).
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e198.sh"
E198_A1_DOC=tools/claims-v3/e198/E198.md.dated-amendment-A1.md
E198_A1_BUILD_JOB=a1-build-e198a1
E198_SESSION_RE='session_e198a1\.sh'
E198_ANY_SESSION_RE='session_e198(a1)?\.sh'

e198_harness_sha() {  # the committed harness-e198-a1.json's sha256 in the lab clone (step 2 (A1) pins it by A1's list)
  sha256sum "$RB_REPO/tools/claims-v3/e198/harness-e198-a1.json" 2>/dev/null | cut -d' ' -f1
}
