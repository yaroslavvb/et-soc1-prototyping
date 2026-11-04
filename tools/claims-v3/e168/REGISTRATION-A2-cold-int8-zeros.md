# Q140(q)'s registration, amendment A2, for E168: a cold int8 zeros hold at S2

*Dated Wed 4 Nov 2026 (week 45), about 09:25 PST. Written by Q141(o) on the Intel, desk only: no card claimed, no device command
sent, no ssh to a lab box.*

*It is written before any E168 data exists. By `git log`, nothing lies under `tools/claims-v3/e168/` and no E168 data directory
exists before this commit. No card has been claimed for E168.*

*It amends Q140(q)'s registration,
[`REGISTRATION.md`](../../../docs/reports/data/2026-11-04-q140q-gemm-g4-stride/REGISTRATION.md) (`49575094`, committed
02:26:25 PST):*
- *G4's predictions and E168's scorer were frozen in `e39d06da` (02:49:40 PST);*
- *amendment A1 and the scorer's 18-file sidecar followed in `1bfaa4e4` (04:03:20 PST).*

*Every file of those three commits keeps its bytes: `REGISTRATION.md`, `registration.json`, `REGISTRATION-A1.md`,
`predictions-e168.json`, `g4.json`, `g4_model.py`, `score_e168.py`, `frozen-sha256-e168.json` (9 files) and
`frozen-sha256-e168-scorer.txt` (18 files).*

**What it answers.**
- A1 item 5: *"A card lane that wants it tested adds an int8 zeros hold from a cold start by its own dated amendment, committed
  before its claim; the nominal cold prediction is already frozen in that table."* This is that amendment.
- Q140's final critic: `card_half[5]` (*"recommended: a dated amendment adding a cold int8 zeros hold at S2 ... the only test of
  G4's start dependence"*) and `desk_next` 5.
- Q139's final critic, rank 5 (G4).
- The kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 1 ("Where
  a large GEMM falls") and item 6 (the power model).

## 1. The added hold

One hold, the tenth and last, after the nine of A6's frozen order, in a block of its own:

| hold | values | start | P0 600 / 700 / 800 | predicted peak | **G4, frozen** (MHz, W, window die) | G3 as frozen |
|---|---|---|---|---|---|---|
| `S2-int8-zeros-cold` | `gemmL3x3x2:tiles:tools/claims-v3/kinds/tiles/int8/zeros.bin` | cold: rest until the die mean reads 46 °C or less, at most 360 s | 27.668 / 31.077 / 37.126 W | 45.64 W | **800, 37.660, 53.662** from 46.0 °C | 800, 37.909, 53.840 |
| `S2-int8-zeros-warm55` (hold 7, unchanged) | the same | warm55 | the same | 45.64 W | 800, 36.326, 55.960 from 54.98 °C | 800, 37.268, 56.421 |

- **The hold.** It runs as A6's other holds do: 12 processes of `--seconds 8` (budget 9.5, tail 6 s), about 106 s, with the last
  40 s read. It uses the same shape, format and values string as hold 7.
- **Its prediction was frozen before this amendment.** It is `predictions-e168.json`
  `cells.S2-int8-zeros-warm55.both_nominal_starts.cold` (`e39d06da`): G4 run from the chain at rest at 46.0 °C, the same model
  as the registered primary.
- **This amendment computes nothing.** [`make_amendment_a2.py`](make_amendment_a2.py) checks the frozen file's sha256
  (`430f4afa…`). It copies the `g4` block and that cell into [`predictions-e168-a2.json`](predictions-e168-a2.json) (sha256
  `2afb290f…`) under two labels:
  - `S2-int8-zeros-warm55`: the frozen cell, every field unchanged;
  - `S2-int8-zeros-cold`: the same levels, values string, peak and `both_nominal_starts`, with its G4 and G3 numbers taken from
    `both_nominal_starts.cold`.

  [`amendment-a2.txt`](amendment-a2.txt) prints it.
- **Admission.** Its estimate is the frozen peak rule's 45.64 W (P0(800) + 8.51 W, A8), under 82 W, so it runs as designed.
  E105's 82 W lock applies to it as to the nine.
- **Card time.** It adds about 8 card-minutes: the rest, typically 3-4.5 min and at most 6, then the hold's 141 s plan.
  Q140(q)'s budget for the nine was about 45 card-minutes with a cap of 55 (`predictions-e168.json` `design.budget`). With A2
  the cap is **63 card-minutes in all**, the smoke and the stop-path tests included.
- **Nothing of the nine changes.** It runs last, after hold 9 (S2 int8 sparse50, warm). The nine keep A6's order, A6's starts,
  A8's stops and A7's rules. If time, the cap or a stop leaves the tenth out, it is reported as not run, and A7 is untouched.

## 2. The bounds A6 left open

A6 says *"cold: the card at rest, die about 46 °C (wait for it, bounded)"* and *"warm55: after the preceding hold, idle until
the die reads 55 °C"* (`predictions-e168.json` `design.hold.starts`). It gives no bound and names no reading. Both are fixed
here, before any data:

| start | the gate (run_hpl.py's `cool` start, as E159's 57 °C gate) | bound | then |
|---|---|---|---|
| cold (holds 1, 3, 5 and A2's 10) | the die mean (the minion shires' mean, the gate's own reading) at or below **46 °C** | at most **360 s** | the hold starts, the gate's reading and wait recorded |
| warm55 (holds 2, 4, 6, 7, 8, 9) | the die mean at or below **55 °C** | at most **300 s** (E159's) | the same |

**Why 360 s.**
- **Q138(t)'s frozen aifoundry2 chain.** After a warm fp32 random hold (die about 65.5 °C at its end), it brings the die within
  1 °C of the rest in about 207 s and within 0.5 °C in about 272 s. After the sparse50 hold (about 59.9 °C), it takes about 178 s
  and 242 s. This is a planning aid, run on the frozen code; its output is in the kit's `logs/rest-chain.txt`.
- **E161's measured rest on this card.** After its 13-minute G1Q hold, the die read 50 °C at 120 s and 47 °C, that evening's
  floor, from about 274 s on. (E161's data dir, `history/`, the box's own 5 s rows.)
- **When the floor is above 46 °C.** That evening's floor would never reach 46 °C. The gate then waits the full 360 s and the
  hold starts at about 47 °C. G4 is scored from each hold's measured start, so that start is used, not 46.0 °C.

## 3. How the added hold is scored

- **It is not in A7.**
  - A7's verdicts cover the nine frozen holds alone. They come from `score_e168.py score`, with `predictions-e168.json` as frozen.
  - That file does not name `S2-int8-zeros-cold`, so the frozen scorer leaves the hold out by itself: `score_e168.build` scores
    only the labels its predictions file names.
  - The kit's reduction also passes the frozen scorer the nine holds only.
- **The primary path, reported.**
  - The tenth hold is scored by the same frozen code from its own measured start:
    `score_e168.score(<session>, ppath=predictions-e168-a2.json)`.
  - Only its rows are read. Its verdict lines, computed over two rows, are not.
  - Its measured − G4 per quantity is printed against A7's lines (15 MHz, 2 W, 1 °C). It is not counted.
  - The warm hold's row from that call must equal its row in the nine-hold call. The kit checks this.
- **The reported test of G4's start dependence.**
  - **What G4 predicts.** G4's in-run leakage is an effective constant, 0.2 W/°C above each run's start die (`g4.json`). So G4
    predicts the cold hold's window board higher than the warm one's, though its die is cooler: **+1.334 W** at the nominal
    starts (37.660 − 36.326 W), with the window die **2.298 °C lower** (53.662 against 55.960 °C).
  - **What was seen before.** Q140(q)'s check (ii) found that signature unphysical where it could be seen. E159's three fp32
    zeros holds, starting at 51.6-57.4 °C, spread **0.057 W** in the window, where G4 spreads them **0.442 W** and G3 as frozen
    0.097 W (`checks-g4.json` › `ii_E159_zeros_spread`).
  - **Why E168 needs this hold.** E168's frozen int8 holds all start warm, so E168 as designed cannot test the start dependence
    (A1 item 5; the data README's C8). A2 tests it on one shape, one format and one values string, in one session.
  - **Measured:** ΔW = the window board of `S2-int8-zeros-cold` − that of `S2-int8-zeros-warm55`. Each is `score_e168.build`'s
    window mean, the in-kernel samples of the last 40 s.
  - **Predicted:**
    - ΔW_G4: the same difference of score_e168's G4 predictions, each from that hold's measured start;
    - G4's frozen nominal +1.334 W beside it;
    - G3 as frozen the same way (nominal +0.641 W);
    - E136's law, whose board does not depend on the start (ΔW 0).
  - **The reading, registered now.** With h = ΔW_G4 / 2:

    | ΔW measured | reading |
    |---|---|
    | at or above +h | **G4's start dependence SUPPORTED** |
    | between −h and +h | **NO START DEPENDENCE**, E159's reading |
    | at or below −h | **OPPOSITE SIGN**: the window board falls with the start, the direction a leakage law in the absolute die gives (the cold hold's window die is predicted 2.3 °C lower; at A2's grid of 0.44-0.50 W/°C that law would read about −1.0 to −1.15 W) |

    If ΔW_G4 is 0.2 W or less (the two starts too close), the test has no power and is labelled so, with no reading.
  - **Reported beside it:** ΔW − ΔW_G4, ΔW − ΔW_G3, the window die difference against G4's, and both measured starts.
  - **What drops out of the difference.** T_Z's fallback shift and T_G's dip do not enter it. The format is the same, and int8
    zeros, at about 37 W, sit under T_G's 56 W gate.
  - **The noise.** E159's three zeros holds spread 0.057 W. With h about 0.67 W at the nominal starts, the three readings lie
    about ten times that spread apart.
- **The day's zeros offset, if E165 ran first.** E165 is the day's first run on aifoundry2 and reads kinds zeros anchors. If it
  ran that day, the reduction passes its zeros-anchor reads to `score_e168.score`'s `--anchors` arm (`G4_own_anchors`, A6's
  second arm), for the nine and for the tenth. The arm is reported and labelled *E165's session, not E168's*. The fallback stays
  the primary, as A6 says.

## 4. What this does to predicting power and heat

- **The term tested** is G4's in-run leakage law: an effective constant (0.2 W/°C) from each run's start die. The tenth hold
  sets it against one law in the absolute die (A2's T_D, rejected by A4's held-out loss) and against no start dependence.
- **Why it matters.** Every G4 prediction of a sustained GEMM's board carries that law. If the reading is NO START DEPENDENCE or
  OPPOSITE SIGN, G4's fp32 cold holds owe part of their predicted level to an unphysical term. They are predicted +4.86 W over
  their warm twins at the nominal starts on S1 (57.952 against 53.097 W). Part of that is the start-referenced term, and part is
  the slow stages' heat. The next model would then need a start-free law, which A4 has not found.
- **It is blind.** The frozen cold prediction and this reading rule exist before any E168 data.
- **No frozen prediction changes**, and neither does any frozen rule, constant or verdict.
