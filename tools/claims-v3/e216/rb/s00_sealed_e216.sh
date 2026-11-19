#!/usr/bin/env bash
# E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum): THE SEALED-FORECAST CHECK, S1 of step 0 and check 10 of step 2 (E216.md
# section 0; the E206 and E213 lessons). The orchestrator keeps the round's record W/out/orch/sealed-e216.txt (one line a posted seal: the
# 64-hex sha256, the post, its time); a seal posted BEFORE E216 books is registered first in the dated note
# tools/claims-v3/sealed-e216/e216-freeze-lines.md (E207's, E210's, E211's and E213's form), committed before the booking; a seal posted after
# one is registered goes in a NEW note (e216-freeze-lines-2.md, ...) with its record line written as a COMMENT ('# ...'). THIS CHECK: every
# 64-hex sha256 on a line of the record that is not a comment is registered in tools/claims-v3/sealed-e216/e216-freeze-lines.md at the lab
# clone's HEAD; a commented line is REPORTED (it must name a note e216-freeze-lines-<n>.md at HEAD holding its sha256, or it is only listed).
# No record, or one with no line that is not a comment: nothing to register ("sealed 0 of 0").
# fix-e216 (Q227, before any E216 datum; verify-e216's F7): a record that EXISTS but cannot be read (not a readable regular file, or its read
# fails) is refused (10), never read as "sealed 0 of 0"; and a 64-hex sha256 is read in either case (an upper-case seal is a seal: it is
# compared, lower-cased, with the notes case-insensitively).
#   RB_SEALED=<the round's record, may be unset or absent> bash tools/claims-v3/e216/rb/s00_sealed_e216.sh
# Prints "SEALED-E216: sealed <k> of <n> registered (...)" last. Exit 0 every non-comment sha256 registered; 10 one is not, or the record
# cannot be read (do not book).
# SPDX-License-Identifier: Apache-2.0
set -u
RB_E216_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
RB_REPO=$(cd "$RB_E216_DIR/../../../.." && pwd -P)
SN=$RB_REPO/tools/claims-v3/sealed-e216
NOTE=$SN/e216-freeze-lines.md
REC=${RB_SEALED:-}
if [ -z "$REC" ] || { [ ! -e "$REC" ] && [ ! -L "$REC" ]; }; then
  echo "SEALED-E216: sealed 0 of 0 registered (no record${REC:+ at $REC}; nothing posted)"
  exit 0
fi
if [ ! -f "$REC" ] || [ ! -r "$REC" ] || ! TXT=$(cat -- "$REC" 2>/dev/null); then
  echo "SEALED-E216: the record $REC exists but cannot be read: NOT CHECKED: do not book; tell the orchestrator"
  exit 10
fi
n=0; k=0; miss=""
for h in $(printf '%s\n' "$TXT" | grep -v '^[[:space:]]*#' | grep -oiE '\b[0-9a-f]{64}\b' | tr 'A-F' 'a-f' | sort -u); do
  n=$((n + 1))
  if [ -f "$NOTE" ] && grep -qi "$h" "$NOTE"; then k=$((k + 1)); else miss="$miss ${h:0:16}..."; fi
done
c=""
for h in $(printf '%s\n' "$TXT" | grep '^[[:space:]]*#' | grep -oiE '\b[0-9a-f]{64}\b' | tr 'A-F' 'a-f' | sort -u); do
  where=$(grep -li "$h" "$SN"/e216-freeze-lines-*.md 2>/dev/null | xargs -r -n1 basename | tr '\n' ' ')
  c="$c ${h:0:16}...(a comment line; ${where:-in no later note at HEAD: listed only})"
done
if [ -n "$miss" ]; then
  echo "SEALED-E216: sealed $k of $n registered: NOT REGISTERED at HEAD in tools/claims-v3/sealed-e216/e216-freeze-lines.md:$miss; comment lines:${c:- none}"
  exit 10
fi
echo "SEALED-E216: sealed $k of $n registered (tools/claims-v3/sealed-e216/e216-freeze-lines.md at HEAD); comment lines:${c:- none}"
exit 0
