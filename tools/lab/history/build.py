#!/usr/bin/env python3
"""build.py: the lab history page from the live collectors' records (tools/lab/live/live-collector.py writes
~/live/history/<UTC date>.jsonl on each machine, one record every 5 s).

  build.py <records dir> <out.html> [--dash data.json]

<records dir> holds one subdirectory per host (aifoundry1/, ...) with that host's .jsonl files (update.sh gathers them
with rsync). The page carries three views per host, each a fixed grid of buckets ending now:
  hour  5 s buckets (720)     day  1 min buckets (1440)     week  10 min buckets (1008)
Each bucket holds the means of CPU %, memory %, the host temperatures, and per card the mean die
temperature and the highest of the firmware's peak since the card started or its stats were last reset
(not a current hottest sensor; C30) and the mean board power; null where nothing was recorded (a machine down, a card held or off the bus).
--dash adds the dashboard's 30-minute card samples (data.json "history", 10-minute steps over 48 h) as dots, for the
time before the collectors kept records.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWS = {"hour": (5, 720), "day": (60, 1440), "week": (600, 1008)}
HOSTS = ["aifoundry1", "aifoundry2", "aifoundry3"]
TEMPS = ["cpu", "nvme", "nic"]


def load(dirpath, since_ms):
    recs = []
    try:
        names = sorted(os.listdir(dirpath))
    except OSError:
        return recs
    cut_day = time.strftime("%Y-%m-%d", time.gmtime(since_ms / 1000 - 86400))
    for fn in names:
        if not fn.endswith(".jsonl") or fn[:10] < cut_day:
            continue
        with open(os.path.join(dirpath, fn), errors="replace") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue  # a line cut short by a reboot
                if isinstance(r, dict) and r.get("t", 0) >= since_ms:
                    recs.append(r)
    recs.sort(key=lambda r: r["t"])
    return recs


def r1(x):
    return None if x is None else round(x, 1)


def bucketize(recs, end_ms, step_s, n):
    t0 = end_ms - n * step_s * 1000
    acc = [None] * n
    for r in recs:
        i = int((r["t"] - t0) // (step_s * 1000))
        if not 0 <= i < n:
            continue
        a = acc[i]
        if a is None:
            a = acc[i] = {"n": 0, "cpu": [], "mem": [], "t": {k: [] for k in TEMPS}, "cards": {}}
        a["n"] += 1
        a["cpu"].append(r.get("cpu"))
        a["mem"].append(r.get("mem"))
        for k in TEMPS:
            v = (r.get("temps") or {}).get(k)
            if v is not None:
                a["t"][k].append(v)
        for c in r.get("cards") or []:
            cc = a["cards"].setdefault(str(c.get("n")), {"die": [], "max": [], "w": [], "down": 0, "held": 0})
            if c.get("ok") is False:
                cc["down"] += 1
            if c.get("held"):
                cc["held"] += 1
            for k in ("die", "max", "w"):
                if c.get(k) is not None:
                    cc[k].append(c[k])

    def mean(xs):
        xs = [x for x in xs if x is not None]
        return r1(sum(xs) / len(xs)) if xs else None

    out = {"t0": t0, "step": step_s, "up": [], "cpu": [], "mem": [], "temps": {k: [] for k in TEMPS}, "cards": {}}
    cards = sorted({k for a in acc if a for k in a["cards"]})
    for k in cards:
        out["cards"][k] = {"die": [], "max": [], "w": [], "down": [], "held": []}
    for a in acc:
        out["up"].append(1 if a else 0)
        out["cpu"].append(mean(a["cpu"]) if a else None)
        out["mem"].append(mean(a["mem"]) if a else None)
        for k in TEMPS:
            out["temps"][k].append(mean(a["t"][k]) if a else None)
        for k in cards:
            cc = (a or {"cards": {}})["cards"].get(k)
            o = out["cards"][k]
            o["die"].append(mean(cc["die"]) if cc else None)
            o["max"].append(max(cc["max"]) if cc and cc["max"] else None)
            o["w"].append(mean(cc["w"]) if cc else None)
            o["down"].append(1 if cc and cc["down"] else 0)
            o["held"].append(1 if cc and cc["held"] else 0)
    return out


def dash_samples(path):
    """the dashboard's own card samples: {host: {card n: {"die": [[t_ms, °C], ...], "w": [[t_ms, W], ...]}}}"""
    try:
        d = json.load(open(path))
    except (OSError, ValueError):
        return {}
    h = d.get("history") or {}
    t0, step = h.get("t0_ms"), (h.get("step_min") or 10) * 60000
    out = {}
    for key, ser in (h.get("cards") or {}).items():
        host, _, c = key.partition("-c")
        if t0 is None:
            continue
        for k, name in (("die_c", "die"), ("board_w", "w")):
            pts = [[t0 + i * step, v] for i, v in enumerate(ser.get(k) or []) if v is not None]
            if pts:
                out.setdefault(host, {}).setdefault(c or "0", {})[name] = pts
    return out


def main(argv):
    dash, args, it = None, [], iter(argv)
    for a in it:
        if a == "--dash":
            dash = next(it, None)
        else:
            args.append(a)
    if len(args) != 2:
        sys.exit(__doc__)
    src, out = args
    now = int(time.time() * 1000)
    data = {"generated": now, "views": {k: {"step": v[0], "n": v[1]} for k, v in VIEWS.items()}, "hosts": {},
            "dash": dash_samples(dash) if dash else {}}
    for h in HOSTS:
        recs = load(os.path.join(src, h), now - 7 * 86400 * 1000)
        data["hosts"][h] = {"last": recs[-1]["t"] if recs else None, "first": recs[0]["t"] if recs else None,
                            **{k: bucketize(recs, now, *VIEWS[k]) for k in VIEWS}}
    tpl = open(os.path.join(HERE, "history.template.html")).read()
    page = tpl.replace("__DATA__", json.dumps(data, separators=(",", ":")).replace("</", "<\\/"))
    tmp = out + ".tmp"
    with open(tmp, "w") as f:
        f.write(page)
    os.replace(tmp, out)
    print(f"wrote {out} {len(page)} bytes")


if __name__ == "__main__":
    main(sys.argv[1:])
