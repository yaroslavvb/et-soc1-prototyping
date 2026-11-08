#!/usr/bin/env bash
# E185 (M11's session 3): the collector, E181's collect_e181_v2.sh (dc35a540, which stays as committed) with E185's names and these changes,
# each marked E185:
#   1. T0-named files: the session's own files come from build/e185/T<T0>/ on the box (T0 from build/e185/LAST_T0, which the real session
#      writes at its start; or E185_T0 when step 22 names it), copied into logs/; the dry session's T<T0>-dry/ directories are never copied;
#   2. an exact copy-back: the session's last act on the box is T<T0>/MANIFEST.sha256 (every file of the T0 directory and of both pass
#      directories, telemetry.jsonl.raw and tiles/ left out). After the copies, every manifest line is checked against the copied file
#      (missing or differing: "COPY-BACK DIFFERS", exit 4), and every copied file must be in the manifest ("COPY-BACK EXTRA", exit 4).
#      "COPY-BACK EXACT <n> files" when both hold. No manifest (a session that never ended): "COPY-BACK NO-MANIFEST", exit 4;
#   3. step 12's host windows are epoch-named on the box (build/e185/host/start-<epoch>.out, end-<epoch>.out): the newest start window
#      at or before T0 (within 30 minutes) and the oldest end window after the session's end (within 30 minutes) are copied as
#      logs/host-start.out and logs/host-end.out, each named in the output; none in range: "host window ... not found" (the score reads it as
#      not read);
#   4. kit v5's one copy of each C log (E181's data note 1, section 6): after the copy-back check, each pass's c-log.jsonl is moved into
#      ccheck/ and gzipped there, and Q139(k)'s check of C reads it; the pass directories keep no second copy.
# Everything else is E181's v2: the box is read only; a pass directory is copied only when a bounded read finds it on the box ("absent on
# the box" otherwise); the rsyncs are bounded (300 / 120 s); ccheck/ is emptied first; it never runs the scorer and refuses to start if a
# scored file is already there. Step 22 (rb/s22_collect_e185.sh) runs it, then the gates, then the score (score_e185.sh).
#   bash tools/claims-v3/e185/collect_e185.sh docs/reports/data/<YYYY-MM-DD>-e185-m11-session3-aifoundry3
# Run it from step 22, never alone.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
D=${1:?usage: collect_e185.sh <data dir>}
PY=${PY:-/usr/bin/python3}
mkdir -p "$D/aifoundry3" "$D/logs" "$D/ccheck"
find "$D/ccheck" -mindepth 1 -maxdepth 1 -type f -delete
for f in scored-m11.json scored-m11.md scored-m11-lines.jsonl scored-m11-lines.jsonl.staging; do
  [ -e "$D/$f" ] && { echo "refusing: $D/$f exists before the gates (remove the data directory first)"; exit 3; }
done
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
T0=${E185_T0:-}
if [ -z "$T0" ]; then
  T0=$(timeout 60 $SSH aifoundry3 "cat aifoundry/build/e185/LAST_T0 2>/dev/null || echo NONE" < /dev/null 2>&1 | tail -n 1)
fi
case "$T0" in ''|NONE|*[!0-9]*) echo "COPY-BACK NO-T0: no session T0 on the box (build/e185/LAST_T0: ${T0:0:80}): nothing collected"; exit 4 ;; esac
echo "T0 $T0 ($(date -d @"$T0" '+%F %T %Z' 2>/dev/null || date -r "$T0" '+%F %T %Z'))"
echo "$T0" > "$D/logs/T0"
for x in e185-smoke e185; do
  ans=$(timeout 60 $SSH aifoundry3 "test -d aifoundry/build/claims-v3/aifoundry3/$x && echo PRESENT || echo ABSENT" < /dev/null 2>&1); prc=$?
  case "$prc:$ans" in
    0:PRESENT) timeout 300 rsync -a -e "$SSH" --exclude 'telemetry.jsonl.raw' --exclude 'tiles/' --exclude '*.attempt-*' \
                 aifoundry3:aifoundry/build/claims-v3/aifoundry3/$x/ "$D/aifoundry3/$x/" || echo "rsync $x rc=$?" ;;
    0:ABSENT) echo "absent on the box: build/claims-v3/aifoundry3/$x/ (no such pass directory: nothing to copy; step 22 reads the session's gates)" ;;
    *) echo "rsync $x rc=${prc} (the presence read did not answer PRESENT or ABSENT: ${ans:0:200}; nothing copied)" ;;
  esac
done
timeout 120 rsync -a -e "$SSH" "aifoundry3:aifoundry/build/e185/T$T0/" "$D/logs/" || echo "rsync logs rc=$?"     # E185 change 1
# E185 change 2: the exact copy-back, against the session's own manifest
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
# E185 change 3: step 12's host windows, epoch-named on the box
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
# E185 change 4: one copy of each C log, in ccheck/
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
