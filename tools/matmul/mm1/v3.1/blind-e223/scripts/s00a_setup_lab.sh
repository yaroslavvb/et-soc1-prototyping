#!/bin/bash
# decl-e223 (Q239) step 0a: the lab's work copy (decl-e221's s00a in form). Desk; no device; no ssh; no E223 datum anywhere (none is read).
# - every frozen MM1 (tools/matmul/mm1: v0, v1, v2, v3 b1493082, v3.1 2c971828 with its counts and counts-e214, v3.2 4e386f75, the v3.2
#   terms, the three MM1-v3.3 candidates of Q234 as landed: posimb, gemmlnc-af4, l3s), E215's band code, the kinds, E136's rgm136 sources,
#   E214's src (MM1-v3.2's energy_v32 reads it at import), E213's points, and E221's, E222's and E224's registrations (THE FORM; E222's and
#   E224's desk callers compose the candidates), by git archive of GitHub main's commit (LAB HEAD = GitHub main, checked first; the archive
#   is a read of LAB under the lab-git lock) into work/lab/ (LAB itself is only read);
# - Q238's frozen 'MM1-v3.2 + posimb-mask' (OUT/mask-posimb, FROZEN.txt posted in W/out/orch/q238-frozen-posts.txt) by copy of its land
#   folder into work/lab/tools/matmul/mm1/v3.4-cands/posimb-mask/ (its own land path, absent at the commit), each file checked against
#   the sha256 its FROZEN.txt lists.
set -u
. <W>/out/decl-e223/scripts/env.sh
echo "start $(ts)"
REMOTE=$(timeout 60 git -C "$LAB" ls-remote origin refs/heads/main | cut -f1)
HEAD=$(git -C "$LAB" rev-parse HEAD)
echo "GitHub main $REMOTE ; LAB HEAD $HEAD"
if [ "$REMOTE" != "$HEAD" ]; then echo "LAB HEAD differs from GitHub main: stop"; exit 3; fi
echo "$HEAD" > "$L/work/lab-commit.txt"
mkdir -p "$L/work/lab"
if [ -d "$L/work/lab/tools" ]; then echo "work/lab/tools exists already: stop (no overwrite)"; exit 4; fi
flock -w 600 "$W/locks/lab-git.lock" nice -n 10 ionice -c 3 git -C "$LAB" archive --format=tar "$HEAD" \
  tools/matmul/mm1 tools/claims-v3/e215/rules_e215.py tools/claims-v3/e215/rules-e215.json tools/claims-v3/kinds \
  tools/claims-v3/e136 tools/claims-v3/e214 tools/claims-v3/e213/points-e213.csv tools/claims-v3/e221 tools/claims-v3/e222 tools/claims-v3/e224 \
  | tar -x -C "$L/work/lab"
echo "archive rc ${PIPESTATUS[0]} $(ts)"
for d in tools/matmul/mm1/v2 tools/matmul/mm1/v3 tools/matmul/mm1/v3.1 tools/matmul/mm1/v3.2 tools/matmul/mm1/v3.3-cands/posimb \
         tools/matmul/mm1/v3.3-cands/gemmlnc-af4 tools/matmul/mm1/v3.3-cands/l3s tools/claims-v3/e215/rules_e215.py tools/claims-v3/e221 \
         tools/claims-v3/e222 tools/claims-v3/e224; do
  git -C "$LAB" log -1 --format="last change %h %ci $d" "$HEAD" -- "$d"
done
chk() {  # $1 label, $2 dir, $3 sums file, $4 log name
  ( cd "$2" && echo "$1: $(sha256sum "$3")" && sha256sum -c "$3" > "$L/logs/$4" 2>&1; echo "$1: sha256sum -c rc $? ; OK $(grep -c ': OK$' "$L/logs/$4") ; not OK $(grep -vc ': OK$' "$L/logs/$4")" )
}
T=$L/work/lab/tools/matmul/mm1
chk "MM1-v2" "$T/v2" SHA256SUMS v2-sha256sum-c.txt
chk "MM1-v3" "$T/v3" SHA256SUMS v3-sha256sum-c.txt
chk "MM1-v3.1" "$T/v3.1" SHA256SUMS v31-sha256sum-c.txt
chk "MM1-v3.2 (4e386f75)" "$T/v3.2" SHA256SUMS v32-sha256sum-c.txt
for c in posimb gemmlnc-af4 l3s; do
  chk "Q234 $c" "$T/v3.3-cands/$c" SHA256SUMS "cand-$c-sha256sum-c.txt"
  chk "Q234 $c note 1" "$T/v3.3-cands/$c" SHA256SUMS-note1 "cand-$c-note1-sha256sum-c.txt"
done
echo "--- E222's and E224's registration sums"
( cd "$L/work/lab/tools/claims-v3/e222" && sha256sum SHA256SUMS-e222-registration SHA256SUMS-e222-kit && sha256sum -c SHA256SUMS-e222-registration > "$L/logs/e222-reg-sha256sum-c.txt" 2>&1; echo "e222 registration: rc $? ; OK $(grep -c ': OK$' "$L/logs/e222-reg-sha256sum-c.txt")" )
( cd "$L/work/lab/tools/claims-v3/e224" && ls SHA256SUMS* && for s in SHA256SUMS*; do sha256sum -c "$s" > "$L/logs/e224-$s-c.txt" 2>&1; echo "e224 $s: rc $? ; OK $(grep -c ': OK$' "$L/logs/e224-$s-c.txt")"; done )
echo "--- Q238's frozen mask candidates (W/out/orch/q238-frozen-posts.txt at $(ts)):"
cat "$W/out/orch/q238-frozen-posts.txt"
cp -a "$W/out/orch/q238-frozen-posts.txt" "$L/work/q238-frozen-posts-at-setup.txt"
PM=$W/out/mask-posimb
want=$(grep -o 'mask-posimb .*FROZEN.txt [0-9a-f]\{64\}' "$W/out/orch/q238-frozen-posts.txt" | grep -o '[0-9a-f]\{64\}$')
got=$(sha256sum "$PM/FROZEN.txt" | cut -c1-64)
echo "mask-posimb FROZEN.txt posted $want ; on disk $got"
if [ -n "$want" ] && [ "$want" = "$got" ]; then
  D=$L/work/lab/tools/matmul/mm1/v3.4-cands/posimb-mask
  [ -e "$D" ] && { echo "$D exists: stop"; exit 5; }
  mkdir -p "$L/work/lab/tools/matmul/mm1/v3.4-cands"
  cp -a "$PM/land/tools/matmul/mm1/v3.4-cands/posimb-mask" "$D"
  cp -a "$PM/FROZEN.txt" "$L/work/mask-posimb-FROZEN.txt"
  ( cd "$D" && grep -E '^[0-9a-f]{64}  ' "$L/work/mask-posimb-FROZEN.txt" > "$L/work/mask-posimb-frozen-lines.txt"; sha256sum -c "$L/work/mask-posimb-frozen-lines.txt" > "$L/logs/mask-posimb-frozen-c.txt" 2>&1; echo "mask-posimb files vs FROZEN.txt: rc $? ; OK $(grep -c ': OK$' "$L/logs/mask-posimb-frozen-c.txt") ; not OK $(grep -vc ': OK$' "$L/logs/mask-posimb-frozen-c.txt")" )
  ( cd "$D" && [ -f SHA256SUMS ] && sha256sum -c SHA256SUMS > "$L/logs/mask-posimb-sums-c.txt" 2>&1; echo "mask-posimb SHA256SUMS: rc $? ; OK $(grep -c ': OK$' "$L/logs/mask-posimb-sums-c.txt")" )
else
  echo "mask-posimb not posted or differs: not copied"
fi
for c in mask-mesh mask-ceiling; do
  if [ -e "$W/out/$c/FROZEN.txt" ]; then echo "$c: FROZEN.txt $(sha256sum "$W/out/$c/FROZEN.txt" | cut -c1-64) (posted? see the file above)"; else echo "$c: no FROZEN.txt at $(ts)"; fi
done
echo "end $(ts)"
