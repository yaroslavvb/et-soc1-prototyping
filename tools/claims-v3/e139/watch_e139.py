#!/usr/bin/env python3
"""E139's board-power stop (registered; E132 had none, its verification's fault 3). Opens no device and sends no command: it reads the
telemetry file the pass's own sampler writes. Every second it follows the newest build/claims-v3/<host>/e139/p<pass>/telemetry.jsonl;
at a sample with board_w >= the stop (default 65 W) it writes that pass's STOP file (runitems.py ends the pass, exit 8) and
build/e139-STOP (queue_e139.sh starts no further pass), and logs the sample. It exits when build/e139/session-end.time exists or
after --max-s seconds.

    python3 tools/claims-v3/e139/watch_e139.py --root build/claims-v3/$(hostname)/e139 --stop-w 65 --max-s 3000 >> build/e139/watch.log
"""
import argparse, glob, json, os, time

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True); ap.add_argument("--stop-w", type=float, default=65.0)
ap.add_argument("--max-s", type=float, default=3000.0); ap.add_argument("--end-flag", default="build/e139/session-end.time")
a = ap.parse_args()
t_end = time.time() + a.max_s; pos = {}; peak = {}
def say(m): print(time.strftime("%T"), m, flush=True)
say("watch: board stop %.1f W on %s" % (a.stop_w, a.root))
while time.time() < t_end and not os.path.exists(a.end_flag):
    for f in sorted(glob.glob(os.path.join(a.root, "p139*", "telemetry.jsonl")), key=os.path.getmtime)[-2:]:
        try:
            with open(f) as fh:
                fh.seek(pos.get(f, 0)); data = fh.read(); 
        except OSError:
            continue
        cut = data.rfind("\n")
        if cut < 0: continue
        pos[f] = pos.get(f, 0) + cut + 1
        for line in data[:cut].splitlines():
            try: w = float(json.loads(line)["board_w"])
            except (ValueError, KeyError, TypeError): continue
            peak[f] = max(peak.get(f, 0.0), w)
            if w >= a.stop_w:
                d = os.path.dirname(f)
                for s in (os.path.join(d, "STOP"), "build/e139-STOP"):
                    open(s, "a").write("board %.2f W >= %.1f W at %s\n" % (w, a.stop_w, time.strftime("%T")))
                say("STOP: %s board %.2f W >= %.1f W" % (os.path.basename(d), w, a.stop_w))
    time.sleep(1.0)
for f, w in peak.items(): say("peak board %s %.2f W" % (os.path.basename(os.path.dirname(f)), w))
say("watch: end")
