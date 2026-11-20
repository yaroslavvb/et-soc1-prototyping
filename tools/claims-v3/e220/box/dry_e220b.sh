#!/usr/bin/env bash
# E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): the dry pass of E220's whole session with the doubles (E208's
# src/fake_card_mms.py and, for rgm211's host, E220's src/fake_card_e220b.py), every device call printed and kept in device-calls.txt, no
# device node opened, no card lock taken (a stand-in lock in the dry folder), time scaled. E209's src/dry_e209.sh form for E220's one
# session: the card a2c0 and the schedule src/sched/a2c0-E220.json, through src/run_e220b.py in its --dry mode (E208's runner, unchanged
# and imported, with E220's lines and family G); the refusals while the box lock is held, a card of this box is held or measured, or a
# CI job runs (E208's).
#   bash <root>/src/dry_e220b.sh [scale]    (default scale 0.02: E220's half-hour session in about two minutes)
# Writes dry/<T0>-a2c0-E220/ in the box root; prints the session's last lines, the count of device calls and DRY PASS when the session
# ran its whole schedule (every run started, every process rc 0 with its check exact or approx, the null runs with none), ran E220 arm B's
# 103 runs in the registered order with E220's point ids, gated every process (gates.jsonl: every gate OK, family G's 17 - s03 and the G
# block - on rgm211's host's double, every other on E208's host's), ran every host under its sized plain timeout (timeout 13 on xf04 alone,
# timeout 10 on every other: desk/timeouts-e220.json) and wrote its manifest. THE IDENTITY GATE READS THE BOX ROOT'S BUILT ELF (step 6 first).
# Exit 0 DRY PASS; 1 DRY FAIL; 3 refused.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
SCALE=${1:-0.02}
case "$SCALE" in ''|*[!0-9.]*) echo "usage: dry_e220b.sh [scale]"; exit 2 ;; esac
[ -f src/sched/a2c0-E220.json ] || { echo "no schedule src/sched/a2c0-E220.json"; exit 2; }
quiet_box() {
  local chk=9 devn cin
  if command -v et-who > /dev/null 2>&1; then timeout 20 et-who --check > /dev/null 2>&1; chk=$?; fi
  devn=$(ps -eo comm= | grep -Ec '(_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$)')
  cin=$(ps -eo comm= | grep -c '^Runner\.Worker$')
  if [ "$chk" -ne 0 ] || [ "$devn" -ne 0 ] || [ "$cin" -ne 0 ]; then
    echo "a card of this box is held or measured, or a CI job runs (et-who --check rc $chk: 0 free, 1 held, 2 failed, 9 no et-who; device processes $devn; CI jobs $cin)"
    return 1
  fi
  return 0
}
mkdir -p run
exec 9>>run/box.lock    # held (fd 9) until this script ends
if ! flock -n 9; then echo "DRY REFUSED: run/box.lock is held (a session, a build or a dry pass of this kit runs on this box)"; exit 3; fi
WHY=$(quiet_box) || { echo "DRY REFUSED: $WHY"; exit 3; }
T0=$(date +%s)
OUT=dry/$T0-a2c0-E220
mkdir -p "$OUT"
nice -n 10 /usr/bin/python3 -B src/run_e220b.py session --dry --scale "$SCALE" --card a2c0 --sched src/sched/a2c0-E220.json \
  --t0 "$T0" --out "$OUT" > "$OUT/runner.out" 2>&1 < /dev/null
RC=$?
tail -n 4 "$OUT/session.log"
/usr/bin/python3 -I -B - "$OUT" "$RC" <<'PY'
import json, os, sys
out, rc = sys.argv[1], int(sys.argv[2])
q = json.load(open(os.path.join(out, "queue.json")))
sched = json.load(open(os.path.join("src", "sched", "a2c0-E220.json")))
calls = open(os.path.join(out, "device-calls.txt")).read().splitlines()
ran = [x for x in q["queue"] if x.get("ran")]
bad = [x for x in q["queue"] if not x.get("ran") or (x.get("form") != "null" and (not x.get("rcs") or any(r != 0 for r in x["rcs"])
       or any(c not in ("exact", "approx") for c in x.get("checks") or [None])))]
order = [(x["i"], x["arm"]) for x in q["queue"]] == [(r["i"], r["arm"]) for r in sched["runs"]]
ids = sorted({r["arm"] for r in sched["runs"] if r["role"] == "arm"})
print(f"device calls {len(calls)} (config {sum(1 for c in calls if c.endswith(' config'))}, sampler "
      f"{sum(1 for c in calls if ' sample ' in c)}, host {sum(1 for c in calls if 'sparsity_host' in c)}); runs ran {len(ran)} of "
      f"{len(sched['runs'])} ({sum(1 for x in ran if x.get('form') == 'null')} null); the registered order {'kept' if order else 'NOT kept'}; "
      f"{len(ids)} point ids ({ids[0]}-{ids[-1]}); card-minutes (unscaled) {q.get('card_min')}; stop {q.get('stop')}")
gates = [json.loads(ln) for ln in open(os.path.join(out, "gates.jsonl"))] if os.path.exists(os.path.join(out, "gates.jsonl")) else []
g_calls = [c for c in calls if "build/e220brgm211/host/sparsity_host" in c]
g_runs = [r["arm"] for r in sched["runs"] if r.get("family") == "rgm136 gemmLnc"]
gate_ok = bool(gates) and all(g["ok"] for g in gates) and len(gates) == len(sched["smoke"]) + sum(1 for r in sched["runs"] if r["form"] != "null")
print(f"the identity gate: {sum(1 for g in gates if g['ok'])} of {len(gates)} processes GATE OK ({sum(1 for g in gates if g['family'] == 'rgm136 gemmLnc')} "
      f"'rgm136 gemmLnc', {sum(1 for g in gates if g['family'] == 'rgm136 gemmL')} 'rgm136 gemmL'); family G {len(g_runs)} runs, "
      f"{len(g_calls)} calls of rgm211's host (the last {len(g_runs)} host calls: "
      f"{'yes' if g_calls and calls[-len(g_runs) - 1:-1] == g_calls[-len(g_runs):] else 'NO'})")
hostcalls = [c.split() for c in calls if "sparsity_host" in c]
tos = [w[w.index("timeout") + 1] if "timeout" in w else None for w in hostcalls]
want_to = [str(r.get("timeout_s")) for r in sched["runs"] if r["form"] != "null"]
to_ok = tos[-len(want_to):] == want_to and all(x == "10" for x in tos[:-len(want_to)])
print(f"the sized plain timeout: {len(tos)} host calls, timeout 13 on {sum(1 for x in tos if x == '13')} (xf04's), every other "
      f"{sorted(set(x for x in tos if x != '13'))}: {'as the schedule sizes it' if to_ok else 'NOT as sized'}")
ok = rc == 0 and not bad and order and len(ran) == len(sched["runs"]) and os.path.exists(os.path.join(out, "MANIFEST.sha256")) \
    and gate_ok and len(g_calls) == len(g_runs) == 17 and to_ok
print(("DRY PASS " if ok else "DRY FAIL ") + f"a2c0 E220 (runner rc {rc}; {len(bad)} runs not clean)")
sys.exit(0 if ok else 1)
PY
