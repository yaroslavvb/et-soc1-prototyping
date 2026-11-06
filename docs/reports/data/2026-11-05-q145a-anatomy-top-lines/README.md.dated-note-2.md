# Dated note 2 beside README.md, Fri 6 Nov 2026 (week 45), about 00:20 PST: two wordings of dated note 1 narrowed to its figures, and its time

*This note sits beside [`README.md`](README.md) and [`README.md.dated-note-1.md`](README.md.dated-note-1.md) (lab `877e7476`, Fri 6 Nov
2026 00:03:14 PST), which stay as committed. The fix pass found these on its own re-read, before any verifier. Post hoc; no number in
[`posthoc-note1-q145a.json`](posthoc-note1-q145a.json) or [`posthoc-note1-q145a.txt`](posthoc-note1-q145a.txt) changes, and nothing
is re-run.*

1. **Note 1, section 1.5, last sentence of its first paragraph after the table:** "on the published fit the random steps' gaps are
   2.8-3.4 times its rms (0.31 and 0.48 W)" holds for the **fp32** random steps only (E171 3.44, E78 3.06, E172 2.79, E82 2.81). The
   **fp16** random steps' gaps are **2.2-2.5** times it (E171 2.23, E78 2.52, E172 2.39, E82 2.26). These are the named gaps of
   `posthoc-note1-q145a.txt` F3 (published fit) over each card's published rms (0.3078 W on aifoundry3, 0.4780 W on card 1, F1's
   table).
2. **Note 1, section 4, second bullet:** "the random steps sit at the bottom of E82's interquartile range" should read: they sit **just
   below** it (fp32 random 1.0567 and fp16 random 1.0570, against its lower end 1.0584 after V²), with `anchor_pi` (1.0474) and
   `int8.full` (1.0392) further below, and all four inside E82's extremes across kinds (1.013-1.088 after V²). The agreement with E82's
   1.061 is otherwise as note 1 gives it.
3. **Note 1's title** gives its writing as "to Fri 6 Nov about 00:40 PST"; it was committed at 00:03:14 PST.

`SHA256SUMS-note2` lists this file.
