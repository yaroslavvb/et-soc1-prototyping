#!/usr/bin/env bash
# E218 (Q230, lane kit-e218, Thu 19 Nov 2026, before any E218 datum), the card lane's STEP 0 checks that the kit can make (this file is s00): ONE
# CALL, READ ONLY, at the desk, in the shared lab clone at its HEAD (nothing written there: git with optional locks off). E215 arm A's step 0
# (tools/claims-v3/e215/rb/s00_step0_e215.sh, landed in 8bde0182, run as stated by E215 arm A's card lane today) for E218's one arm and its two
# freeze lines. The card lane runs it inside its desk span (THE ONE-LAB RULE: `bash W/onelab.sh desk <lane>` first), after its booking and before
# step H; the readiness lane's go lines may wrap it with the land record's anchor lines, which this script does not read. Its lines:
#   S0  GitHub main by ls-remote (git reads take the round's environment-only HTTPS rewrite, which the caller sets: never a config file), and
#       the lab clone's HEAD (REPORTED: step 2 pulls);
#   F1  THE POINTS' AND FORECASTS' FREEZE LINE ON GITHUB MAIN: MM1-v3.2's land 4e386f75 (committed 19:50:04 PST Thu 19 Nov 2026, pushed 19:50:09:
#       E218's points and every declared model's forecasts, E218.md section 0);
#   F1R THE REGISTRATION COMMIT ON GITHUB MAIN (found by its content: the commit that added tools/claims-v3/e218/E218.md, its tools/claims-v3/e218
#       subtree deb6726f...), whose push froze the column it makes ('MM1-v3.2 without its gemmLnc term'), the rules and the scorer (E218.md
#       section 0: "it must precede E218's first card command");
#   F2  the kit commit (the commit that added tools/claims-v3/e218/KIT.md) after it. Each must be an ancestor of GitHub main: read in the lab
#       clone when GitHub main's commit is there; otherwise GitHub main is fetched into a TEMPORARY bare repository that borrows the lab clone's
#       objects read-only (git's alternates), never into the lab clone, and read there;
#   S1  THE SEALED-FORECAST CHECK (E218.md section 0; the orchestrator's answer 2 in e218-answers.txt): every sealed sha256 on a non-comment line
#       ("E218 <sha256> ...") of the round's record (the file E218_SEALED names: W/out/orch/sealed-e218.txt) is registered in
#       tools/claims-v3/sealed-e218/e218-freeze-lines.md at the lab clone's HEAD (the sha256 appears in that file there); "0 of 0" when the record
#       is absent or lists none. A sha256 the record lists and the note does not register: NOT AS STATED (do not go on: tell the orchestrator; the
#       note lands first). A LATER SEAL (E213's lesson; E218.md section 0) goes in a NEW note (tools/claims-v3/sealed-e218/e218-freeze-lines-2.md)
#       and its record line is a COMMENT (a '#' line), which this check never reads: a second non-comment sha256 that the first note does not hold
#       is refused;
#   S2  (REPORTED) the commits on tools/claims-v3/sealed-e218 in any ref;
#   D0  NO E218 DATUM in any ref (a commit on a docs/reports/data FOLDER named *e218*-aifoundry3: git's glob magic, so a file whose name merely
#       holds 'e218' is not one);
#   G1  the lab clone's status 0 lines (git status --porcelain --untracked-files=all).
# Prints every line, then "STEP0-E218 arm A: <n> of <n> as stated" and exits 0; any line not as stated: "STEP0-E218 arm A: NOT AS STATED:
# <k> of <n> ..." and exit 1 (then: no box step that day, CARD-LANE-BRIEF row E, with undesk). Exit 2: a usage error.
#   E218_SEALED=<W>/out/orch/sealed-e218.txt bash tools/claims-v3/e218/rb/s00_step0_e218.sh A
# E218_S0_LAB=<dir> reads a stand-in clone and E218_S0_MAIN=<sha> a stand-in GitHub main (the runbook's desk test only, with RB_DESKTEST=1).
# SPDX-License-Identifier: Apache-2.0
set -u
ARM=${1:-}
case "$ARM" in A) SUF=aifoundry3 ;; *) echo "usage: E218_SEALED=<record> s00_step0_e218.sh A"; exit 2 ;; esac
[ -n "${E218_SEALED:-}" ] || { echo "usage: E218_SEALED (the round's sealed-forecast record, W/out/orch/sealed-e218.txt) is not set"; exit 2; }
LAB=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E218_S0_LAB:-}" ] && LAB=$E218_S0_LAB
export GIT_OPTIONAL_LOCKS=0
G() { git -C "$LAB" "$@"; }
E=tools/claims-v3/e218
REG_SUB=deb6726f8823b6dd08a10d72ddd68837862c2a92
FREEZE=4e386f7519a236fb0bf8c43d26f8303be57e09a2
NOK=0; NBAD=0
line() {  # line <id> <ok 0|1> <words>
  if [ "$2" = 1 ]; then NOK=$((NOK + 1)); echo "$1 as stated: $3"; else NBAD=$((NBAD + 1)); echo "$1 NOT AS STATED: $3"; fi
}
H=$(G rev-parse HEAD 2>/dev/null)
URL=$(G remote get-url origin 2>/dev/null)
if [ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E218_S0_MAIN:-}" ]; then M=$E218_S0_MAIN
else M=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main 2>/dev/null | awk '{print $1}' | head -n 1); fi
echo "S0 (REPORTED) GitHub main ${M:-NOT READ}; the lab clone's HEAD ${H:-none}$([ -n "$M" ] && [ "$M" = "$H" ] && echo ' (= GitHub main)')"
REG=$(G log --diff-filter=A --format=%H -- "$E/E218.md" 2>/dev/null | tail -n 1)
KIT=$(G log --diff-filter=A --format=%H -- "$E/KIT.md" 2>/dev/null | tail -n 1)
sub=""; [ -n "$REG" ] && sub=$(G rev-parse "$REG:$E" 2>/dev/null)
TMPR=""
anc() {  # anc <commit>: 0 if it is an ancestor of GitHub main M (in the lab clone, or in a temporary bare repo borrowing its objects)
  [ -n "$M" ] && [ -n "$1" ] || return 1
  if G cat-file -e "$M^{commit}" 2>/dev/null; then G merge-base --is-ancestor "$1" "$M"; return $?; fi
  if [ -z "$TMPR" ]; then
    TMPR=$(mktemp -d "${TMPDIR:-/tmp}/e218-s0-XXXXXX") || return 1
    git init -q --bare "$TMPR" && echo "$(cd "$LAB" && git rev-parse --path-format=absolute --git-common-dir)/objects" > "$TMPR/objects/info/alternates" &&
      timeout 300 git -C "$TMPR" fetch -q "$URL" "refs/heads/main:refs/heads/main" 2>/dev/null || { echo "      (the temporary fetch of GitHub main failed)"; return 1; }
  fi
  git -C "$TMPR" merge-base --is-ancestor "$1" "$M"
}
if anc "$FREEZE"; then line F1 1 "the points' and forecasts' freeze line, MM1-v3.2's land ${FREEZE:0:12}, is an ancestor of GitHub main ${M:0:12}"
else line F1 0 "the freeze line ${FREEZE:0:12} (MM1-v3.2's land) is not shown to be an ancestor of GitHub main ${M:-(not read)}"; fi
if [ -z "$REG" ]; then line F1R 0 "no registration commit in the lab clone (no commit added $E/E218.md): the registration's column, rules and scorer are not frozen on GitHub main"
elif [ "$sub" != "$REG_SUB" ]; then line F1R 0 "the registration commit ${REG:0:12} holds subtree ${sub:-none}, not ${REG_SUB:0:12}"
elif anc "$REG"; then line F1R 1 "the registration commit ${REG:0:12} (subtree ${REG_SUB:0:8}; its push froze 'MM1-v3.2 without its gemmLnc term', the rules and the scorer) is an ancestor of GitHub main ${M:0:12}"
else line F1R 0 "the registration commit ${REG:0:12} is not shown to be an ancestor of GitHub main ${M:-(not read)}"; fi
if [ -z "$KIT" ]; then line F2 0 "no kit commit in the lab clone (no commit added $E/KIT.md)"
elif anc "$KIT"; then line F2 1 "the kit commit ${KIT:0:12} is an ancestor of GitHub main ${M:0:12}"
else line F2 0 "the kit commit ${KIT:0:12} is not shown to be an ancestor of GitHub main ${M:-(not read)}"; fi
[ -n "$TMPR" ] && rm -rf -- "${TMPR:?}"
nrec=0; nreg=0; miss=""
if [ -f "$E218_SEALED" ]; then
  note=$(G show "HEAD:tools/claims-v3/sealed-e218/e218-freeze-lines.md" 2>/dev/null)
  while read -r w sha _; do
    [ "$w" = E218 ] || continue
    nrec=$((nrec + 1))
    if [ -n "$note" ] && printf '%s' "$note" | grep -q "$sha"; then nreg=$((nreg + 1)); else miss="$miss ${sha:0:12}"; fi
  done < <(grep -v '^[[:space:]]*#' "$E218_SEALED" | grep -E '^E218 [0-9a-f]{64}( |$)')
  bad=$(grep -v '^[[:space:]]*#' "$E218_SEALED" | grep -v '^[[:space:]]*$' | grep -cvE '^E218 [0-9a-f]{64}( |$)')
  [ "$bad" -eq 0 ] || miss="$miss (and $bad unreadable non-comment line(s))"
fi
if [ -z "$miss" ]; then line S1 1 "sealed $nreg of $nrec: every sealed sha256 the round's record lists is registered in tools/claims-v3/sealed-e218/e218-freeze-lines.md at HEAD$([ -f "$E218_SEALED" ] || echo ' (the record is absent: none posted)')"
else line S1 0 "sealed $nreg of $nrec: the record lists$miss, which the note at HEAD does not register: do not go on (tell the orchestrator; the note lands first)"; fi
echo "S2 (REPORTED) commits on tools/claims-v3/sealed-e218 in any ref: $(G log --all --oneline -- tools/claims-v3/sealed-e218 2>/dev/null | grep -c .)"
nd=$(G log --all --oneline -- ":(glob)docs/reports/data/*e218*-$SUF/**" 2>/dev/null | grep -c .)
if [ "$nd" -eq 0 ]; then line D0 1 "no E218 datum (no commit on a docs/reports/data folder named *e218*-$SUF in any ref)"
else line D0 0 "$nd commit(s) on a docs/reports/data folder named *e218*-$SUF in some ref: E218 has data already"; fi
st=$(G status --porcelain --untracked-files=all 2>/dev/null | grep -c .)
if [ "$st" -eq 0 ]; then line G1 1 "the lab clone's status: 0 lines"; else line G1 0 "the lab clone's status: $st line(s)"; fi
if [ "$NBAD" -eq 0 ]; then echo "STEP0-E218 arm $ARM: $NOK of $NOK as stated (HEAD ${H:0:12}, GitHub main ${M:0:12})"; exit 0; fi
echo "STEP0-E218 arm $ARM: NOT AS STATED: $NBAD of $((NOK + NBAD)) (the NOT AS STATED lines above): no box step today (row E, with undesk)"
exit 1
