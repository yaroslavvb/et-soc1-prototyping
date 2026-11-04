# Q140(e) registration amendment RA1: after the freeze, before any E166 or E167 data (desk, Wed 4 Nov 2026)

*Written Wed 4 Nov 2026 (week 45), about 03:30-04:10 PST, on the Intel, desk only: no card, no device command, no ssh to a lab box, no
Discord, no Modal, no archive. It comes **after** the freeze commit `c9aaf179` (02:46:04 PST) and after the lane's verifier reported
(about 03:18 PST). It comes **before** any E166 or E167 claim, launch or data: neither session has run. So it touches no fit or score of
E166 or E167, because none exists. The post hoc figures it cites are on sessions already seen (E154, E161, E144, E97).*

*[`REGISTRATION.md`](REGISTRATION.md) and [`registration.json`](registration.json) stay as committed in `11174d20`. Every frozen number
in [`predictions-q140e.json`](predictions-q140e.json) stays as committed in `c9aaf179`, and no registered threshold changes. The numbers
below are printed by [`corrections_q140e.py`](corrections_q140e.py) into [`corrections.txt`](corrections.txt) and
[`corrections.json`](corrections.json). That script checks this lane's eight committed files against their sha256 at `c9aaf179` and
reproduces the frozen numbers it builds on (`C0`) before it prints anything else. The README's dated notes, C1-C10, say where each item
came from.*

## RA1.1 R2's disclosure, completed (README C4)

R2 says option (a) was chosen knowing Q140(l)'s post hoc C1, where option (b) reads E161's G1Q plateau closer (+0.22 against +0.51 °C at
the kernel duty). That disclosure is partial:
- the lane had read Q140(l)'s `corrections.txt` in full at 02:08 PST, before this registration;
- C1 there also gives E161 G1Q's **in-work level** under each option (Q140(l) `corrections.json` › `C1.E161_G1Q.level_high_by_w`):
  - (a): **0.08 W low**;
  - (b): **0.24 W high**;
  - M8: 0.91 W high.

That reading favoured (a). So the option was chosen after both readings, and both come from one hold. M9's fit never saw E161, but **E161's
G1Q is in sample for the choice of option**. C1 also gave the level's reference gap, 0.64-0.72 W (RA1.3).

## RA1.2 RK3-b is scored only in the 800 MHz regime (README C8)

Above a rest die of **49.97 °C** (at E161's rest-board law), the primary puts G1Q in the trip regime. There, R3 sets the predicted plateau to
the trip rule's 65.9 °C, which is not heat from the bits (Q139's final critic, fault 6). R4 said nothing about that case. From now on:
- **RK3-b is scored only when the primary puts G1Q in the 800 MHz regime at every die over the REST's ±0.5 °C.** The primary is run at
  E167's measured G1Q REST anchors (die and board) and the hold's own kernel duty.
- **Otherwise RK3-b reads "not scored: the trip regime"**, or "not scored: the trip edge inside the readout". Rank 3 is then not answered on
  this session pair, because R4 needs all three rules.
- **Not registered here:** a start gate. E167's own registration may add one before its claim: start G1Q only after a REST that reads
  49 °C or less in whole degrees. E161's REST read 47.0 °C.

G1Q's edge under the other arms (`corrections.json` › `C2`):
- 48.78 °C, Q139(e) as frozen. The README's "about 49.4" was wrong (README C2).
- 49.22 °C, amendment A2.
- 49.43 °C, RA1.3's arm.

## RA1.3 A reported arm: M9's level referred to M9's own T_ref (README C3)

This arm is reported beside the primary. It is never the primary and never a verdict.
- **The choice R2 made.** R2 puts M9's zeros-level shift on Q139(e)'s board, whose die law runs at 0.442 W/°C from its **56.0 °C**
  reference die. That is option (a) as Q140(l)'s C1 defines it.
- **The other reference.** M9's own fit refers its level to its T_ref, **54.38 °C**. Referred there, through the same 0.442 W/°C law, the
  in-work board is **0.715 W higher** at every clock (0.640 W at k_T's slope).
- **At E161's anchors** (`corrections.json` › `C3.at_E161_anchor`, `C2`):
  - G1Q's plateau: **62.30 → 62.95 °C** (+0.65 °C, two-thirds of RK3-b's 1.0 °C);
  - G2Q's trip clock: **685.6 → 677.5 MHz**;
  - G1Q's trip edge: 49.97 → 49.43 °C.
  - By rest die 44-48 °C, the arm reads G1Q 0.65 °C warmer and G2Q's trip clock 5.6-8.1 MHz lower (`C3.by_rest_die`).
- **Post hoc on E161, in sample for the choice of option** (`C3.posthoc_E161`, `C3.E161_G1Q_in_work_level_high_by_W`):
  - G1Q's in-work board: 0.64 W high, against the primary's 0.08 W low;
  - G1Q's plateau error: −0.01 °C, against +0.64 °C;
  - G2Q's clock error: +4.1 MHz, against −4.0 MHz.
  - The close plateau is a cancellation. A level 0.64 W high offsets two other errors: the chain reading low given the watts, and the idle
    counting of time outside the kernel launches (README C5).
- **How E167's scorer computes it:** `predict_q140e.a2_hold`, with the in-work level of `corrections_q140e._levels(item, "M9a_ref54")`.

## RA1.4 R5 governs K_O's window when K_OL ends early; the start gate is not registered (README C7)

R5 governs as registered. When K_OL's room rule ends the hold early, "its K_O window still scored", with D2's b: the end of the last process
that ends at or before 600 s after the first process's start. That b exists at every room in the table: K_OL ends at 566.5 s at 53.5 °C
(`predictions-q140e.json` › `E166.room_rules.K_OL_above_53C`). So K_O is scored on [b − 300 s, b).
- The README's "K_O is not scored" was wrong and is withdrawn.
- The README's "E166 is worth starting only with R0's room at or under 53.0 °C" is advice, not a registered gate.
- E166's own registration may add that gate, and an exclusion for an incomplete K_O window, before its claim.

## RA1.5 The slow-stage reading: its null, stated; one reported slope added (README C10)

**The SEEN threshold (G_A ≥ +0.15 °C) stays as registered.** Its false-positive rate is estimated now from committed aifoundry3 holds.
- **The statistic:** arm A's late error slope, read as a G_A-equivalent (the slope over the 900 s between the registered windows' centres).
- **The pools and their rates** (post hoc; `corrections.json` › `C10.null`):

  | pool | the spread (rms about zero) | SEEN's false-positive rate |
  |---|---|---|
  | E144's two holds and E154's three int8 holds (out of sample for the chain) | 0.135 °C | **13%** |
  | the same, plus E154's two fp32 large rises (K_S, K_O) | 0.39 °C | **35%** |
  | E97's two 30-minute holds (in sample for the chain), G_A at the registered geometry +0.12 and −0.38 °C | 0.28 °C | **30%** |

- **On those pools, a threshold with a 5% false-positive rate would sit at +0.22 to +0.65 °C.**
- **Reported beside the registered verdict, never a verdict:**
  - G_A against those spreads;
  - arm A's least-squares slope over 300-600 s of K_OL. It is one statistic read on four things:

    | where | slope (°C per 10 min) |
    |---|---|
    | E154's own K_O | +0.42 |
    | the extra-stage scenarios | 0.58-0.69 |
    | the gain scenario | 0.10 |
    | the chain as frozen | 0 |

## RA1.6 D6's time (README C1)

D6, the gain scenario, is reported only. It was added to `predict_q140e.py` at **02:36:43 PST**:
- after the three extra-stage scenarios' G_A had been printed (02:31:53);
- before the freeze commit `c9aaf179` (02:46:04).

The README said about 03:00 PST. D6 changes no threshold.
