# E209 data, dated note 15, erratum 1: three figures in note 15's prose were rounded one unit high in their last digit

*Tue 17 Nov 2026 (week 47), PST. Written at about 14:05 PST by round Q212's lane `fix-e209d`, after note 15's commit `b067742b` (13:56:32
PST). This is a new file: note 15 is not edited. Note 15's printout (`posthoc-note15-e209.txt`) and its JSON (`posthoc-note15-e209.json`)
carry the right values. Only three figures in its prose were rounded twice: first to the printout's five or four decimals, then again by hand.*

| where in `README.md.dated-note-15.md` | it reads | it should read | the JSON's value |
|---|---|---|---|
| section 3, row H2: the registered bootstrap interval of the mean d | [+0.0063, +0.0451] | [+0.0063, **+0.0450**] | 0.0450485 |
| section 3, row H5: the other test's bootstrap mean d | +0.1098 | **+0.1097** | 0.1097461 |
| section 4 (a): e30, measured / MM1-v2 | 1.016 | **1.015** | 1.0154582 |

**No verdict, cell, count or reading changes.** This lane read note 15's figures back against its JSON (section 3's table and section 4's
readings, by script). The read-back found these three differences and no others.
