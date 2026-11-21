#!/usr/bin/env bash
# E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3
# card 0 at 03:11-03:56 PST that day), the card lane's STEP 0 checks that the kit can make (this file is s00): ONE CALL, READ ONLY, at the desk,
# in the shared lab clone at its HEAD (nothing written there: git with optional locks off). E218's step 0 (tools/claims-v3/e218/rb/s00_step0_e218.sh,
# kit 5582edfc, run as stated by E218's card lane at 03:04 PST Fri 20 Nov 2026), itself E215 arm A's, for E222's one arm and its freeze lines.
# The card lane runs it inside its desk span (THE ONE-LAB RULE: `bash W/onelab.sh desk <lane>` first), after its booking and before step H; the
# readiness lane's go lines may wrap it with the land record's anchor lines, which this script does not read. Its lines:
#   S0  GitHub main by ls-remote (git reads take the round's environment-only HTTPS rewrite, which the caller sets: never a config file), and
#       the lab clone's HEAD (REPORTED: step 2 pulls);
#   F0  THE POSTED FREEZE LINE (E222.md section 0): the round's record of the post (the file E222_FROZEN_POSTS names: W/out/orch/q236-frozen-posts.txt)
#       holds the line naming FROZEN.txt 172ed079... and the three forecast files (forecast-e222.json c4630d19..., forecast-e222.csv 223f943e...,
#       (the record's post lines begin with the post's own id, '#1.30.1.2.1.1.1 <time>: ...', and are read; its comments are '#' and a blank)
#       forecast-e222.txt f2d8047f...), posted at 13:51:12 PST Fri 20 Nov 2026 before any E220 or E222 datum; each of the three files at the lab
#       clone's HEAD has that sha256; and, when E222_FROZEN names the registration lane's FROZEN.txt, its bytes have FROZEN.txt's sha256;
#   F1  MM1-v3.2's land 4e386f75 (committed 19:50:04 PST Thu 19 Nov 2026: the baseline model's code and constants every E222 forecast reads in
#       place) an ancestor of GitHub main;
#   F1C THE THREE CANDIDATES' LANDS (land-cands, 07:49 PST Fri 20 Nov 2026: posimb badf08fa, gemmlnc-af4 911651ee, l3s 2a509f5a; each frozen and
#       posted before any E220 datum: W/out/orch/q234-frozen-posts.txt) ancestors of GitHub main;
#   F1R THE REGISTRATION COMMIT ON GITHUB MAIN (found by its content: the commit that added tools/claims-v3/e222/E222.md, its tools/claims-v3/e222
#       subtree f8e6ec56...), whose push is E222's second freeze line - every forecast, the points, the rules, the plan and the scorer (E222.md
#       section 0: "its push by the land lane is E222's second freeze line"; reg-e222's land notes: it must precede E222's first card command);
#   F2  the kit commit (the commit that added tools/claims-v3/e222/KIT.md) after it. Each must be an ancestor of GitHub main: read in the lab
#       clone when GitHub main's commit is there; otherwise GitHub main is fetched into a TEMPORARY bare repository that borrows the lab clone's
#       objects read-only (git's alternates), never into the lab clone, and read there;
#   S1  THE SEALED-FORECAST CHECK (E222.md section 0): every sealed sha256 on a non-comment line ("E222 <sha256> ...") of the round's record (the
#       file E222_SEALED names: W/out/orch/sealed-e222.txt) is registered in tools/claims-v3/sealed-e222/e222-freeze-lines.md at the lab clone's
#       HEAD (the sha256 appears in that file there); "0 of 0" when the record is absent or lists none. A sha256 the record lists and the note does
#       not register: NOT AS STATED (do not go on: tell the orchestrator; the note lands first). A LATER SEAL (E213's lesson; E222.md section 0)
#       goes in a NEW note (tools/claims-v3/sealed-e222/e222-freeze-lines-2.md) and its record line is a COMMENT (a '#' line), which this check
#       never reads: a second non-comment sha256 that the first note does not hold is refused;
#   S2  (REPORTED) the commits on tools/claims-v3/sealed-e222 in any ref;
#   D0  NO E222 DATUM in any ref (a commit on a docs/reports/data FOLDER named *e222*-aifoundry3: git's glob magic, so a file whose name merely
#       holds 'e222' is not one);
#   G1  the lab clone's status 0 lines (git status --porcelain --untracked-files=all).
# Prints every line, then "STEP0-E222 arm A: <n> of <n> as stated" (8 of 8) and exits 0; any line not as stated: "STEP0-E222 arm A: NOT AS STATED:
# <k> of <n> ..." and exit 1 (then: no box step that day, CARD-LANE-BRIEF row E, with undesk). Exit 2: a usage error.
#   E222_SEALED=<W>/out/orch/sealed-e222.txt E222_FROZEN_POSTS=<W>/out/orch/q236-frozen-posts.txt [E222_FROZEN=<W>/out/reg-e222/FROZEN.txt] \
#     bash tools/claims-v3/e222/rb/s00_step0_e222.sh A
# E222_S0_LAB=<dir> reads a stand-in clone and E222_S0_MAIN=<sha> a stand-in GitHub main (the runbook's desk test only, with RB_DESKTEST=1).
# SPDX-License-Identifier: Apache-2.0
set -u
ARM=${1:-}
case "$ARM" in A) SUF=aifoundry3 ;; *) echo "usage: E222_SEALED=<record> E222_FROZEN_POSTS=<record> s00_step0_e222.sh A"; exit 2 ;; esac
[ -n "${E222_SEALED:-}" ] || { echo "usage: E222_SEALED (the round's sealed-forecast record, W/out/orch/sealed-e222.txt) is not set"; exit 2; }
[ -n "${E222_FROZEN_POSTS:-}" ] || { echo "usage: E222_FROZEN_POSTS (the round's record of the freeze post, W/out/orch/q236-frozen-posts.txt) is not set"; exit 2; }
LAB=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
[ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E222_S0_LAB:-}" ] && LAB=$E222_S0_LAB
export GIT_OPTIONAL_LOCKS=0
G() { git -C "$LAB" "$@"; }
E=tools/claims-v3/e222
REG_SUB=f8e6ec568dc796a02231aa02f955d3c941db78e0
FREEZE=4e386f7519a236fb0bf8c43d26f8303be57e09a2
CANDS="badf08fa024c5823a912c30a03d944bbeddc371c 911651eefb6c29babc589a00853671ad5052e36e 2a509f5adc18d42091487e90de949e4c43387f8d"
FROZEN_SHA=172ed079a4a5640a381c984dd7adc1bb1a63cbb024373c0a1f8f9c0c40d9369f
FJ=c4630d19554ab0daacd9eacd83f74fb1d8bd0df851bcbd1cfc02d3ac715314a8
FC=223f943e32c01544063de6b1dc925712e0701ba43f4c99f97ff622e8c5b835cb
FT=f2d8047f1e1136924939250da1207cecd4a48a047a07ec678ce30417913ec910
NOK=0; NBAD=0
line() {  # line <id> <ok 0|1> <words>
  if [ "$2" = 1 ]; then NOK=$((NOK + 1)); echo "$1 as stated: $3"; else NBAD=$((NBAD + 1)); echo "$1 NOT AS STATED: $3"; fi
}
H=$(G rev-parse HEAD 2>/dev/null)
URL=$(G remote get-url origin 2>/dev/null)
if [ "${RB_DESKTEST:-}" = 1 ] && [ -n "${E222_S0_MAIN:-}" ]; then M=$E222_S0_MAIN
else M=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main 2>/dev/null | awk '{print $1}' | head -n 1); fi
echo "S0 (REPORTED) GitHub main ${M:-NOT READ}; the lab clone's HEAD ${H:-none}$([ -n "$M" ] && [ "$M" = "$H" ] && echo ' (= GitHub main)')"
# F0: the posted freeze line, and the three forecast files at HEAD at its sha256s
f0=""
if [ ! -f "$E222_FROZEN_POSTS" ]; then f0="the record $E222_FROZEN_POSTS is absent"
else
  pl=$(grep -v -E '^[[:space:]]*#([[:space:]]|$)' "$E222_FROZEN_POSTS" | grep -F "FROZEN.txt $FROZEN_SHA" | head -n 1)   # a comment: '#' and a blank
  if [ -z "$pl" ]; then f0="no post line names FROZEN.txt $FROZEN_SHA"
  else
    for spec in "forecast-e222.json:$FJ" "forecast-e222.csv:$FC" "forecast-e222.txt:$FT"; do
      fn=${spec%%:*}; want=${spec#*:}
      printf '%s' "$pl" | grep -qF "$fn $want" || f0="$f0; the post line does not name $fn $want"
      got=$(G show "HEAD:$E/$fn" 2>/dev/null | sha256sum | awk '{print $1}')
      [ "$got" = "$want" ] || f0="$f0; $fn at HEAD is ${got:0:12}, posted ${want:0:12}"
    done
  fi
  if [ -n "${E222_FROZEN:-}" ]; then
    fz=$(sha256sum "$E222_FROZEN" 2>/dev/null | awk '{print $1}')
    [ "$fz" = "$FROZEN_SHA" ] || f0="$f0; FROZEN.txt ($E222_FROZEN) is ${fz:-unreadable}, posted ${FROZEN_SHA:0:12}"
  fi
fi
f0=${f0#; }
if [ -z "$f0" ]; then line F0 1 "the posted freeze line (#1.30.1.2.1.1.1, 13:51:12 PST Fri 20 Nov 2026): FROZEN.txt ${FROZEN_SHA:0:12}$([ -n "${E222_FROZEN:-}" ] && echo ' (its bytes read)'), and forecast-e222.json ${FJ:0:12}, .csv ${FC:0:12}, .txt ${FT:0:12} equal at HEAD"
else line F0 0 "the posted freeze line: $f0"; fi
REG=$(G log --diff-filter=A --format=%H -- "$E/E222.md" 2>/dev/null | tail -n 1)
KIT=$(G log --diff-filter=A --format=%H -- "$E/KIT.md" 2>/dev/null | tail -n 1)
sub=""; [ -n "$REG" ] && sub=$(G rev-parse "$REG:$E" 2>/dev/null)
TMPR=""
anc() {  # anc <commit>: 0 if it is an ancestor of GitHub main M (in the lab clone, or in a temporary bare repo borrowing its objects)
  [ -n "$M" ] && [ -n "$1" ] || return 1
  if G cat-file -e "$M^{commit}" 2>/dev/null; then G merge-base --is-ancestor "$1" "$M"; return $?; fi
  if [ -z "$TMPR" ]; then
    TMPR=$(mktemp -d "${TMPDIR:-/tmp}/e222-s0-XXXXXX") || return 1
    git init -q --bare "$TMPR" && echo "$(cd "$LAB" && git rev-parse --path-format=absolute --git-common-dir)/objects" > "$TMPR/objects/info/alternates" &&
      timeout 300 git -C "$TMPR" fetch -q "$URL" "refs/heads/main:refs/heads/main" 2>/dev/null || { echo "      (the temporary fetch of GitHub main failed)"; return 1; }
  fi
  git -C "$TMPR" merge-base --is-ancestor "$1" "$M"
}
if anc "$FREEZE"; then line F1 1 "MM1-v3.2's land ${FREEZE:0:12} (the baseline model's code and constants the forecasts read in place) is an ancestor of GitHub main ${M:0:12}"
else line F1 0 "MM1-v3.2's land ${FREEZE:0:12} is not shown to be an ancestor of GitHub main ${M:-(not read)}"; fi
cb=""; for c in $CANDS; do anc "$c" || cb="$cb ${c:0:12}"; done
if [ -z "$cb" ]; then line F1C 1 "the three MM1-v3.3 candidates' lands (posimb badf08fa, gemmlnc-af4 911651ee, l3s 2a509f5a; frozen and posted before any E220 datum) are ancestors of GitHub main ${M:0:12}"
else line F1C 0 "the candidates' lands$cb are not shown to be ancestors of GitHub main ${M:-(not read)}"; fi
if [ -z "$REG" ]; then line F1R 0 "no registration commit in the lab clone (no commit added $E/E222.md): E222's forecasts, points, rules, plan and scorer are not frozen on GitHub main"
elif [ "$sub" != "$REG_SUB" ]; then line F1R 0 "the registration commit ${REG:0:12} holds subtree ${sub:-none}, not ${REG_SUB:0:12}"
elif anc "$REG"; then line F1R 1 "the registration commit ${REG:0:12} (subtree ${REG_SUB:0:8}; its push froze every forecast, the points, the rules, the plan and the scorer) is an ancestor of GitHub main ${M:0:12}"
else line F1R 0 "the registration commit ${REG:0:12} is not shown to be an ancestor of GitHub main ${M:-(not read)}"; fi
if [ -z "$KIT" ]; then line F2 0 "no kit commit in the lab clone (no commit added $E/KIT.md)"
elif anc "$KIT"; then line F2 1 "the kit commit ${KIT:0:12} is an ancestor of GitHub main ${M:0:12}"
else line F2 0 "the kit commit ${KIT:0:12} is not shown to be an ancestor of GitHub main ${M:-(not read)}"; fi
[ -n "$TMPR" ] && rm -rf -- "${TMPR:?}"
nrec=0; nreg=0; miss=""
if [ -f "$E222_SEALED" ]; then
  note=$(G show "HEAD:tools/claims-v3/sealed-e222/e222-freeze-lines.md" 2>/dev/null)
  while read -r w sha _; do
    [ "$w" = E222 ] || continue
    nrec=$((nrec + 1))
    if [ -n "$note" ] && printf '%s' "$note" | grep -q "$sha"; then nreg=$((nreg + 1)); else miss="$miss ${sha:0:12}"; fi
  done < <(grep -v '^[[:space:]]*#' "$E222_SEALED" | grep -E '^E222 [0-9a-f]{64}( |$)')
  bad=$(grep -v '^[[:space:]]*#' "$E222_SEALED" | grep -v '^[[:space:]]*$' | grep -cvE '^E222 [0-9a-f]{64}( |$)')
  [ "$bad" -eq 0 ] || miss="$miss (and $bad unreadable non-comment line(s))"
fi
if [ -z "$miss" ]; then line S1 1 "sealed $nreg of $nrec: every sealed sha256 the round's record lists is registered in tools/claims-v3/sealed-e222/e222-freeze-lines.md at HEAD$([ -f "$E222_SEALED" ] || echo ' (the record is absent: none posted)')"
else line S1 0 "sealed $nreg of $nrec: the record lists$miss, which the note at HEAD does not register: do not go on (tell the orchestrator; the note lands first)"; fi
echo "S2 (REPORTED) commits on tools/claims-v3/sealed-e222 in any ref: $(G log --all --oneline -- tools/claims-v3/sealed-e222 2>/dev/null | grep -c .)"
nd=$(G log --all --oneline -- ":(glob)docs/reports/data/*e222*-$SUF/**" 2>/dev/null | grep -c .)
if [ "$nd" -eq 0 ]; then line D0 1 "no E222 datum (no commit on a docs/reports/data folder named *e222*-$SUF in any ref)"
else line D0 0 "$nd commit(s) on a docs/reports/data folder named *e222*-$SUF in some ref: E222 has data already"; fi
st=$(G status --porcelain --untracked-files=all 2>/dev/null | grep -c .)
if [ "$st" -eq 0 ]; then line G1 1 "the lab clone's status: 0 lines"; else line G1 0 "the lab clone's status: $st line(s)"; fi
if [ "$NBAD" -eq 0 ]; then echo "STEP0-E222 arm $ARM: $NOK of $NOK as stated (HEAD ${H:0:12}, GitHub main ${M:0:12})"; exit 0; fi
echo "STEP0-E222 arm $ARM: NOT AS STATED: $NBAD of $((NOK + NBAD)) (the NOT AS STATED lines above): no box step today (row E, with undesk)"
exit 1
