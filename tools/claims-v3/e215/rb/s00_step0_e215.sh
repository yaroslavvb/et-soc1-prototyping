#!/usr/bin/env bash
# E215 (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum), the card lane's STEP 0 checks that the kit can make (this file is s00): ONE
# CALL, READ ONLY, at the desk, in the shared lab clone at its HEAD (nothing written there: git with optional locks off). The card lane runs it
# inside its desk span (THE ONE-LAB RULE: `bash W/onelab.sh desk <lane>` first), after its booking and before step H; the readiness lane's go lines
# may wrap it with the land record's anchor lines (OUT/q224-anchor-lines-e215.txt), which this script does not read. Its lines:
#   S0  GitHub main by ls-remote (git reads take the round's environment-only HTTPS rewrite, which the caller sets: never a config file), and
#       the lab clone's HEAD (REPORTED: step 2 pulls);
#   F1  THE ARM'S FREEZE LINE ON GITHUB MAIN: arm A, MM1-v3.1's land 2c971828 (committed 23:09:13 PST Wed 18 Nov 2026: its frozen forecasts); arm
#       B, THE REGISTRATION COMMIT (found by its content: the commit that added tools/claims-v3/e215/E215.md, its tools/claims-v3/e215 subtree
#       e89e512f...), whose push froze arm B's forecasts, arm A's MM1-v2 column and every 'v3.1 with T7' forecast (E215.md section 0; E213's
#       answer 4 form: the arm's freeze line a booking condition); and, for
#       both arms, the kit commit (the commit that added tools/claims-v3/e215/KIT.md) after it. Each must be an ancestor of GitHub main: read in the
#       lab clone when GitHub main's commit is there; otherwise GitHub main is fetched into a TEMPORARY bare repository that borrows the lab
#       clone's objects read-only (git's alternates), never into the lab clone, and read there;
#   S1  THE SEALED-FORECAST CHECK (E215.md section 0; the orchestrator's answer 2): every sealed sha256 on a non-comment line ("E215 <sha256> ...")
#       of the round's record (the file E215_SEALED names: W/out/orch/sealed-e215.txt) is registered in tools/claims-v3/sealed-e215/
#       e215-freeze-lines.md at the lab clone's HEAD (the sha256 appears in that file there); "0 of 0" when the record is absent or lists none.
#       A sha256 the record lists and the note does not register: NOT AS STATED (do not go on: tell the orchestrator; the note lands first).
#       A LATER SEAL (E213's lesson; E215.md section 0) goes in a NEW note (tools/claims-v3/sealed-e215/e215-freeze-lines-2.md) and its record
#       line is a COMMENT (a '#' line), which this check never reads: a second non-comment sha256 that the first note does not hold is refused;
#   S2  (REPORTED) the commits on tools/claims-v3/sealed-e215 in any ref;
#   D0  NO E215 DATUM OF THIS ARM in any ref (a commit on a docs/reports/data FOLDER named *e215*-<aifoundry3 | aifoundry1-c1>: git's glob
#       magic, so a file whose name merely holds 'e215', as one of E175's design tiles does, is not one), the other arm's REPORTED;
#   G1  the lab clone's status 0 lines (git status --porcelain --untracked-files=all).
# Prints every line, then "STEP0-E215 arm <arm>: <n> of <n> as stated" and exits 0; any line not as stated: "STEP0-E215 arm <arm>: NOT AS STATED:
# <k> of <n> ..." and exit 1 (then: no box step that day, CARD-LANE-BRIEF row E, with undesk). Exit 2: a usage error.
#   E215_SEALED=<W>/out/orch/sealed-e215.txt bash tools/claims-v3/e215/rb/s00_step0_e215.sh A|B
# E215_S0_LAB=<dir> reads a stand-in clone and E215_S0_MAIN=<sha> a stand-in GitHub main (the runbook's desk test only, with RB_DESKTEST=1).
# SPDX-License-Identifier: Apache-2.0
set -u
ARM=${1:-}
case "$ARM" in A) SUF=aifoundry3 ;; B) SUF=aifoundry1-c1 ;; *) echo "usage: E215_SEALED=<record> s00_step0_e215.sh A|B"; exit 2 ;; esac
[ -n "${E215_SEALED:-}" ] || { echo "usage: E215_SEALED (the round's sealed-forecast record, W/out/orch/sealed-e215.txt) is not set"; exit 2; }
LAB=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E215_S0_LAB:-}" ] && LAB=$E215_S0_LAB
export GIT_OPTIONAL_LOCKS=0
G() { git -C "$LAB" "$@"; }
E=tools/claims-v3/e215
REG_SUB=e89e512f4b528c7429d454af0c372549ef233957
A_FREEZE=2c971828c29ebb62b4ecc156024c7a5debd7404e
NOK=0; NBAD=0
line() {  # line <id> <ok 0|1> <words>
  if [ "$2" = 1 ]; then NOK=$((NOK + 1)); echo "$1 as stated: $3"; else NBAD=$((NBAD + 1)); echo "$1 NOT AS STATED: $3"; fi
}
H=$(G rev-parse HEAD 2>/dev/null)
URL=$(G remote get-url origin 2>/dev/null)
if [ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E215_S0_MAIN:-}" ]; then M=$E215_S0_MAIN
else M=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main 2>/dev/null | awk '{print $1}' | head -n 1); fi
echo "S0 (REPORTED) GitHub main ${M:-NOT READ}; the lab clone's HEAD ${H:-none}$([ -n "$M" ] && [ "$M" = "$H" ] && echo ' (= GitHub main)')"
REG=$(G log --diff-filter=A --format=%H -- "$E/E215.md" 2>/dev/null | tail -n 1)
KIT=$(G log --diff-filter=A --format=%H -- "$E/KIT.md" 2>/dev/null | tail -n 1)
sub=""; [ -n "$REG" ] && sub=$(G rev-parse "$REG:$E" 2>/dev/null)
TMPR=""
anc() {  # anc <commit>: 0 if it is an ancestor of GitHub main M (in the lab clone, or in a temporary bare repo borrowing its objects)
  [ -n "$M" ] && [ -n "$1" ] || return 1
  if G cat-file -e "$M^{commit}" 2>/dev/null; then G merge-base --is-ancestor "$1" "$M"; return $?; fi
  if [ -z "$TMPR" ]; then
    TMPR=$(mktemp -d "${TMPDIR:-/tmp}/e215-s0-XXXXXX") || return 1
    git init -q --bare "$TMPR" && echo "$(cd "$LAB" && git rev-parse --path-format=absolute --git-common-dir)/objects" > "$TMPR/objects/info/alternates" &&
      timeout 300 git -C "$TMPR" fetch -q "$URL" "refs/heads/main:refs/heads/main" 2>/dev/null || { echo "      (the temporary fetch of GitHub main failed)"; return 1; }
  fi
  git -C "$TMPR" merge-base --is-ancestor "$1" "$M"
}
if [ "$ARM" = A ]; then
  if anc "$A_FREEZE"; then line F1 1 "arm A's freeze line, MM1-v3.1's land ${A_FREEZE:0:12} (its frozen forecasts), is an ancestor of GitHub main ${M:0:12}"
  else line F1 0 "arm A's freeze line ${A_FREEZE:0:12} is not shown to be an ancestor of GitHub main ${M:-(not read)}"; fi
else
  if [ -z "$REG" ]; then line F1 0 "no registration commit in the lab clone (no commit added $E/E215.md): arm B's forecasts are not frozen on GitHub main"
  elif [ "$sub" != "$REG_SUB" ]; then line F1 0 "the registration commit ${REG:0:12} holds subtree ${sub:-none}, not ${REG_SUB:0:12}"
  elif anc "$REG"; then line F1 1 "arm B's freeze line, the registration commit ${REG:0:12} (subtree ${REG_SUB:0:8}; its push froze arm B's forecasts), is an ancestor of GitHub main ${M:0:12}"
  else line F1 0 "arm B's freeze line, the registration commit ${REG:0:12}, is not shown to be an ancestor of GitHub main ${M:-(not read)}"; fi
fi
if [ -z "$KIT" ]; then line F2 0 "no kit commit in the lab clone (no commit added $E/KIT.md)"
elif anc "$KIT"; then line F2 1 "the kit commit ${KIT:0:12} is an ancestor of GitHub main ${M:0:12}"
else line F2 0 "the kit commit ${KIT:0:12} is not shown to be an ancestor of GitHub main ${M:-(not read)}"; fi
[ -n "$TMPR" ] && rm -rf -- "${TMPR:?}"
nrec=0; nreg=0; miss=""
if [ -f "$E215_SEALED" ]; then
  note=$(G show "HEAD:tools/claims-v3/sealed-e215/e215-freeze-lines.md" 2>/dev/null)
  while read -r w sha _; do
    [ "$w" = E215 ] || continue
    nrec=$((nrec + 1))
    if [ -n "$note" ] && printf '%s' "$note" | grep -q "$sha"; then nreg=$((nreg + 1)); else miss="$miss ${sha:0:12}"; fi
  done < <(grep -v '^[[:space:]]*#' "$E215_SEALED" | grep -E '^E215 [0-9a-f]{64}( |$)')
  bad=$(grep -v '^[[:space:]]*#' "$E215_SEALED" | grep -v '^[[:space:]]*$' | grep -cvE '^E215 [0-9a-f]{64}( |$)')
  [ "$bad" -eq 0 ] || miss="$miss (and $bad unreadable non-comment line(s))"
fi
if [ -z "$miss" ]; then line S1 1 "sealed $nreg of $nrec: every sealed sha256 the round's record lists is registered in tools/claims-v3/sealed-e215/e215-freeze-lines.md at HEAD$([ -f "$E215_SEALED" ] || echo ' (the record is absent: none posted)')"
else line S1 0 "sealed $nreg of $nrec: the record lists$miss, which the note at HEAD does not register: do not go on (tell the orchestrator; the note lands first)"; fi
echo "S2 (REPORTED) commits on tools/claims-v3/sealed-e215 in any ref: $(G log --all --oneline -- tools/claims-v3/sealed-e215 2>/dev/null | grep -c .)"
nd=$(G log --all --oneline -- ":(glob)docs/reports/data/*e215*-$SUF/**" 2>/dev/null | grep -c .)
no=$(G log --all --oneline -- ':(glob)docs/reports/data/*e215*/**' 2>/dev/null | grep -c .)
if [ "$nd" -eq 0 ]; then line D0 1 "no E215 datum of arm $ARM (no commit on a docs/reports/data folder named *e215*-$SUF in any ref; the other arm's, REPORTED: $((no - nd)))"
else line D0 0 "$nd commit(s) on a docs/reports/data folder named *e215*-$SUF in some ref: arm $ARM has data already"; fi
st=$(G status --porcelain --untracked-files=all 2>/dev/null | grep -c .)
if [ "$st" -eq 0 ]; then line G1 1 "the lab clone's status: 0 lines"; else line G1 0 "the lab clone's status: $st line(s)"; fi
if [ "$NBAD" -eq 0 ]; then echo "STEP0-E215 arm $ARM: $NOK of $NOK as stated (HEAD ${H:0:12}, GitHub main ${M:0:12})"; exit 0; fi
echo "STEP0-E215 arm $ARM: NOT AS STATED: $NBAD of $((NOK + NBAD)) (the NOT AS STATED lines above): no box step today (row E, with undesk)"
exit 1
