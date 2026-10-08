#!/usr/bin/env python3
"""extract.py: copy the live collector's 5-second records for this report out of aifoundry2's history files.

  python3 extract.py ~/live/history records.jsonl.gz

The window is Tue 6 Oct 2026 16:00 to Wed 7 Oct 2026 17:10 PDT: from just before the card came back on the PCIe bus
after the 6 October BIOS fan fix until after it fell off again. The history files are named by UTC date, so three
of them cover it. Records are written unchanged, one JSON object per line, gzipped."""
import gzip, json, os, sys, datetime as dt

src, out = sys.argv[1], sys.argv[2]
PDT = dt.timezone(dt.timedelta(hours=-7))
t0 = dt.datetime(2026, 10, 6, 16, 0, tzinfo=PDT).timestamp() * 1000
t1 = dt.datetime(2026, 10, 7, 17, 10, tzinfo=PDT).timestamp() * 1000
n = 0
with gzip.open(out, "wt", encoding="utf-8") as f:
    for name in ("2026-10-06.jsonl", "2026-10-07.jsonl", "2026-10-08.jsonl"):
        for line in open(os.path.join(src, name), encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if t0 <= r["t"] < t1:
                f.write(json.dumps(r, separators=(",", ":")) + "\n"); n += 1
print(f"{n} records written to {out}")
