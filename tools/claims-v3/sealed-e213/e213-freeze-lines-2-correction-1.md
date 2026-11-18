# Correction 1 to `e213-freeze-lines-2.md`: arm A's label (a dated note)

*Written Wed 18 Nov 2026 (week 47), PST, at the desk on aifoundry2 by the round's orchestrator, after the note was committed
(`d8404ef2`, pushed 07:54:53 PST). Nothing here was measured, no card was touched, and no committed file is edited.*

**What it corrects.** The note's paragraph on arm A says that, for arm A, the model session's second seal (sha256
`d622ce167c421999ee646c9ec60a478e365b7fc4f2177504b6750efbde0327bd`) "is labelled post-data", because arm A's data commit `c69a12aa`
was on GitHub main when the note was written and committed. That label follows the round orchestrator's brief to the lane that
registered the seal: the brief tied arm A's label to the time of the registration. That was the orchestrator's error. E213.md
section 0 ties the label to the time the seal was **posted**: "One posted after an arm's first card command is REPORTED as sealed
during the session, or after its data commit as post-data."

**The times.**

| event | time (PST, Wed 18 Nov 2026) | source |
|---|---|---|
| arm A's card lane books aifoundry3 | 06:32:00 | arm A's card lane (the booking, G) |
| arm A's first card command | 06:37:09 | arm A's session record (T0) |
| the second seal is posted (#2.7.1.1.1.1.1.2) | 06:53:32 | the post |
| arm A's session ends | 07:19:59 | arm A's session record |
| arm A's data commit `c69a12aa` | committed 07:23:29, pushed by 07:23:33 | the commit |
| the note registering the seal, `d8404ef2` | pushed 07:54:53 | the commit |

**The corrected label.** For arm A, the second seal is **REPORTED as sealed during arm A's session, before its data commit**. It
is not post-data. It is not a freeze line of arm A either, as the note says, because it was posted after arm A booked. The post came
before arm A's data commit; only the registration came after it.

**What does not change.** For arm B the seal remains freeze line 2: it was posted before arm B's first card command and before any
arm B datum, and registered before arm B's rerun books. The sha256, the post's words and every other line of the note stand. The
seal stays sealed: no number of it is in the lab, and no lab rule scores it. The round's record of sealed E213 forecasts carries
this label in its comment line.
