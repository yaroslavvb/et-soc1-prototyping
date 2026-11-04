# Dated note beside step81/README.md (Wed 4 Nov 2026, about 12:20 PST; Q141(t)'s fix pass)

*`step81/README.md`, `summary81.json` and `summary81.txt` (`9c7ae1f2`) stay as committed. One figure there is the upper middle value,
not the median. Nothing else in this step changes.*

- **What Results 2 says:** "e(27)/e(81) is 1.61-1.97, median 1.76".
- **The median is 1.754.** The ten ratios, sorted, are 1.605, 1.649, 1.690, 1.742, 1.744, 1.764, 1.818, 1.904, 1.905 and 1.970.
  Their median is the mean of the 5th and 6th, 1.754, so **1.75**.
- **Where 1.76 comes from:** it is the 6th value, the upper middle one. `run_recount_rule.py` takes `sorted(rats)[len(rats) // 2]`.
  `summary81.json`'s `e27_over_e81_median` (1.7636), `summary81.txt` and `9c7ae1f2`'s message carry the same 1.76.
- **What it changes:** nothing. Either way the ratio sits near the 1/√N law's 1.73.
- **For the records:** quote "median 1.75 (upper middle 1.76)". The lane's other corrections are in
  [`../README.md.dated-note.md`](../README.md.dated-note.md).
