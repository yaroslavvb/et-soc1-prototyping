#!/usr/bin/env bash
# E185 (M11's session 3): the collector v2, the kit's dated note 1 (KIT.md.dated-note-1.md). It is collect_e185.sh (460c352f, which stays
# as committed) with two changes, each marked v2, for the kit verifier's major fault 1 and its nit (b) (Sat 7 Nov 2026):
#   1. the two pass directories are copied BY NAME, build/claims-v3/aifoundry3/e185-smoke/p18501/ and e185/p18520/, the two that
#      session_e185.sh's manifest covers, and nothing else of e185-smoke/ or e185/. v1 copied all of e185-smoke/, so after a later try
#      (s11 --later-try moves the first smoke aside as p18501.try1) the exact copy-back read COPY-BACK EXTRA on p18501.try1 and step 22
#      stopped with 16 on every collection. An earlier try's directories (p18501.try1, a block's p185xx.attempt-<epoch>) stay on the box,
#      read-only; one bounded read names each of them ("left on the box (not this session's manifest): ...");
#   2. a data directory that holds any file is refused before any box call ("refusing: ...", exit 3). v1 refused only a scored file, so a
#      second collection into a directory a first one had filled read COPY-BACK EXTRA on logs/host-start.out and logs/host-end.out (the
#      collector's own copies, made after its check). The exact copy-back needs an empty data directory: remove it, then collect again.
# Everything else is v1's, line for line: T0 from build/e185/LAST_T0 (or E185_T0 when step 22 names it); the session's own T0 directory
# copied as logs/; the exact copy-back against T<T0>/MANIFEST.sha256 ("COPY-BACK EXACT", else DIFFERS, EXTRA, NO-MANIFEST or NO-T0, exit 4);
# the host windows picked by T0; one copy of each C log, moved into ccheck/; the box read only; every rsync bounded (300 / 120 / 60 s); a
# pass directory copied only when a bounded read finds it ("absent on the box" otherwise); it never runs the scorer.
#   bash tools/claims-v3/e185/collect_e185_v2.sh docs/reports/data/<YYYY-MM-DD>-e185-m11-session3-aifoundry3
# Run it from step 22 v2 (rb/s22_collect_e185_v2.sh), never alone.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?usage: collect_e185_v2.sh <data dir>}
PY=${PY:-/usr/bin/python3}
if [ -d "$D" ] && [ -n "$(find "$D" -type f -print 2>/dev/null | head -n 1)" ]; then                          # v2 change 2
  echo "refusing: $D holds files already (an earlier collection, or another source): the exact copy-back needs an empty data directory; remove $D, then collect again"
  exit 3
fi
mkdir -p "$D/aifoundry3/e185-smoke" "$D/aifoundry3/e185" "$D/logs" "$D/ccheck"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
T0=${E185_T0:-}
if [ -z "$T0" ]; then
  T0=$(timeout 60 $SSH aifoundry3 "cat aifoundry/build/e185/LAST_T0 2>/dev/null || echo NONE" < /dev/null 2>&1 | tail -n 1)
fi
case "$T0" in ''|NONE|*[!0-9]*) echo "COPY-BACK NO-T0: no session T0 on the box (build/e185/LAST_T0: ${T0:0:80}): nothing collected"; exit 4 ;; esac
echo "T0 $T0 ($(date -d @"$T0" '+%F %T %Z' 2>/dev/null || date -r "$T0" '+%F %T %Z'))"
echo "$T0" > "$D/logs/T0"
# v2 change 1: one bounded read names the two pass directories (PRESENT or ABSENT) and every other entry beside them
RCMD='cd aifoundry/build/claims-v3/aifoundry3 2>/dev/null || { echo "PASS e185-smoke/p18501 ABSENT"; echo "PASS e185/p18520 ABSENT"; echo READ-DONE; exit 0; }
for p in e185-smoke/p18501 e185/p18520; do if [ -d "$p" ]; then echo "PASS $p PRESENT"; else echo "PASS $p ABSENT"; fi; done
for x in e185-smoke e185; do [ -d "$x" ] || continue; for e in "$x"/*; do [ -e "$e" ] || continue
  case "$e" in e185-smoke/p18501|e185/p18520) ;; *) echo "OTHER $e" ;; esac; done; done
echo READ-DONE'
ans=$(timeout 60 $SSH aifoundry3 'bash -s' <<< "$RCMD" 2>&1); prc=$?       # bash on the box, whatever its login shell
for p in e185-smoke/p18501 e185/p18520; do
  st=$(printf '%s\n' "$ans" | awk -v p="$p" '$1 == "PASS" && $2 == p && NF == 3 {print $3; exit}')
  case "$prc:$st" in
    0:PRESENT) timeout 300 rsync -a -e "$SSH" --exclude 'telemetry.jsonl.raw' --exclude 'tiles/' \
                 "aifoundry3:aifoundry/build/claims-v3/aifoundry3/$p/" "$D/aifoundry3/$p/" || echo "rsync $p rc=$?" ;;
    0:ABSENT) echo "absent on the box: build/claims-v3/aifoundry3/$p/ (no such pass directory: nothing to copy; step 22 reads the session's gates)" ;;
    *) echo "rsync $p rc=${prc} (the presence read did not answer PRESENT or ABSENT: ${ans:0:200}; nothing copied)" ;;
  esac
done
printf '%s\n' "$ans" | grep -q '^READ-DONE$' || echo "rsync presence rc=${prc} (the presence read did not finish: ${ans:0:200})"
left=$(printf '%s\n' "$ans" | sed -n 's#^OTHER ##p' | tr '\n' ' ')
[ -n "$left" ] && echo "left on the box (not this session's manifest; an earlier try's, not copied): ${left% }"
timeout 120 rsync -a -e "$SSH" "aifoundry3:aifoundry/build/e185/T$T0/" "$D/logs/" || echo "rsync logs rc=$?"
# the exact copy-back, against the session's own manifest (v1's, unchanged)
"$PY" -B - "$D" "$T0" <<'PY'
import hashlib, os, sys
D, T0 = sys.argv[1], sys.argv[2]
man = os.path.join(D, "logs", "MANIFEST.sha256")
if not os.path.exists(man):
    print("COPY-BACK NO-MANIFEST: the session's MANIFEST.sha256 is not there (a session that never ended, or nothing copied)")
    sys.exit(4)
def local(p):
    pre = f"build/e185/T{T0}/"
    if p.startswith(pre):
        return os.path.join(D, "logs", p[len(pre):])
    for x in ("e185-smoke", "e185"):
        pre = f"build/claims-v3/aifoundry3/{x}/"
        if p.startswith(pre):
            return os.path.join(D, "aifoundry3", x, p[len(pre):])
    return None
want, bad = {}, []
for line in open(man):
    parts = line.rstrip("\n").split("  ", 1)
    if len(parts) != 2:
        continue
    h, p = parts
    q = local(p)
    if q is None:
        bad.append(f"outside the session's directories: {p}")
        continue
    want[os.path.normpath(q)] = h
    if not os.path.exists(q):
        bad.append(f"missing: {p}")
    elif hashlib.sha256(open(q, "rb").read()).hexdigest() != h:
        bad.append(f"differs: {p}")
have = set()
for root in (os.path.join(D, "logs"), os.path.join(D, "aifoundry3", "e185-smoke"), os.path.join(D, "aifoundry3", "e185")):
    for dp, dn, fn in os.walk(root):
        for f in fn:
            q = os.path.normpath(os.path.join(dp, f))
            if q in (os.path.normpath(man), os.path.normpath(os.path.join(D, "logs", "T0"))):
                continue
            have.add(q)
extra = sorted(have - set(want))
if bad:
    print("COPY-BACK DIFFERS: " + "; ".join(bad[:20]))
    sys.exit(4)
if extra:
    print("COPY-BACK EXTRA: files the session's manifest does not list: " + "; ".join(os.path.relpath(x, D) for x in extra[:20]))
    sys.exit(4)
print(f"COPY-BACK EXACT {len(want)} files (every manifest line read back, and nothing else)")
PY
cb=$?
[ "$cb" -eq 0 ] || { echo "collect stops: the copy-back is not exact (rc $cb)"; exit 4; }
# step 12's host windows, epoch-named on the box (v1's, unchanged)
END_EPOCH=$(date -r "$D/logs/MANIFEST.sha256" +%s 2>/dev/null || stat -f %m "$D/logs/MANIFEST.sha256")
ls_out=$(timeout 60 $SSH aifoundry3 "ls aifoundry/build/e185/host/ 2>/dev/null" < /dev/null 2>&1)
pick() {  # pick <start|end>
  local best="" e
  for f in $ls_out; do
    case "$f" in "$1"-[0-9]*.out) e=${f#"$1"-}; e=${e%.out} ;; *) continue ;; esac
    if [ "$1" = start ]; then
      [ "$e" -le "$T0" ] && [ $((T0 - e)) -le 1800 ] && { [ -z "$best" ] || [ "$e" -gt "${best#*:}" ]; } && best="$f:$e"
    else
      [ "$e" -ge "$((END_EPOCH - 120))" ] && [ $((e - END_EPOCH)) -le 1800 ] && { [ -z "$best" ] || [ "$e" -lt "${best#*:}" ]; } && best="$f:$e"
    fi
  done
  echo "${best%%:*}"
}
for w in start end; do
  f=$(pick $w)
  if [ -n "$f" ]; then
    timeout 60 rsync -a -e "$SSH" "aifoundry3:aifoundry/build/e185/host/$f" "$D/logs/host-$w.out" && echo "host window $w: $f -> logs/host-$w.out" || echo "rsync host $w rc=$?"
  else
    echo "host window $w: not found within 30 minutes of the session (the score reads it as not read)"
  fi
done
# one copy of each C log, in ccheck/ (v1's, unchanged)
logs=()
for d in "$D"/aifoundry3/e185-smoke/p18501 "$D"/aifoundry3/e185/p18520; do
  if [ ! -s "$d/c-log.jsonl" ]; then echo "c-log $(basename "$d"): absent or empty (step 22's launch gate reads whether this pass must carry one)"; continue; fi
  mv "$d/c-log.jsonl" "$D/ccheck/c-log-$(basename "$d").jsonl"
  logs+=("$D/ccheck/c-log-$(basename "$d").jsonl")
done
if [ ${#logs[@]} -gt 0 ]; then
  nice -n 10 "$PY" tools/claims-v3/ccheck/ccheck.py check "${logs[@]}" --out "$D/ccheck/ccheck-all.json" --jobs 2 > "$D/ccheck/ccheck.txt" 2>&1
  echo "ccheck rc=$? ($(tail -1 "$D/ccheck/ccheck.txt" | head -c 400))"
  gzip -f "${logs[@]}"
fi
echo "collected (no score: step 22 scores after its gates)"
du -sh "$D"
