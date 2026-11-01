# Q130: the chip has one zero test, and it is 32 bits wide

*Dated 1 Nov 2026: the rule read here is tested on silicon by [E93](../2026-11-01-e93-zero-gate-silicon/README.md), at power resolution on one card: `-0` and denormal words leave the lane on, and int8's eight-byte B rule, its pairing and its A word read as the RTL says.*

*Desk pass, Sat 31 Oct 2026 (week 44). No card, no simulation: this is a correction, settled from the public RTL,
the two public document sets and this repo's own earlier measurements. It exists because a documentary pass earlier
today got the sign of the zero-price prediction backwards and a review caught it; the corrected mechanism is written
down here because E78, E79 and E80 all price zeros, and all three need it right.*

## Result

**There is exactly one zero test in the tensor datapath, and it compares a whole 32-bit operand word against zero.**

- It is taken **once, when the tensor operand register is written**, not per element and not in the multiplier:
  `external/core-et/rtl/shire/minion/vpu/vpu_ctrl.v:1230`,
  `f3_zero_data_a = {VPU_LANE_NUM{(f3_tena_regfile_wdata_l == VPU_DATA_S_SZ'b0)}}`, with
  `VPU_DATA_S_SZ = 32` (`external/core-et/rtl/inc/minion_defines.vh:191`) and `VPU_LANE_NUM = 8` (line 189).
- One flag per lane is latched per register entry (`vpu_ctrl.v:737-755`), muxed into `ex_tensor_zero_mask`
  (`:817`), and that single mask drives **both** the float unit — `ex_fma_gate_mask` -> `ex_txfma_valid`
  (`:837-839`) — **and both integer units** — `ex_tensor_zero_mask_ext` -> `ex_tima_valid` (`:827-830`), two per
  lane (`VPU_NUM_TIMA = 2`, `external/core-et/rtl/inc/vpu_defines.vh:210`).
- The B side for the integer units is an **AND** of the two TIMA B words (`:808-818`), so a B-side gate needs both
  of a lane's B words zero.
- The gate is in the **vector control**, and it is described there as such: "In order to save power, the VPU control
  implements some logic to conditionally compute the operations based on the values of the A/B matrices. This is
  done to gate the functional units when we know the result of the FMA multiplication is going to be zero because
  any/some of the input operands are zeros" — *Minion VPU Specification* §2.3.6.1, in the public `core-et` docs
  (`openhwfoundation/core-et`, Erbium branch, `docs/Minion VPU Specification.pdf`).

**The format therefore only sets how many numbers ride in one gated word** — one fp32, two fp16, four int8 — and the
price of a zero falls as the format narrows:

| format | numbers per 32-bit word | what a zero must do to gate | scattered zeros at density p gate |
|---|---|---|---|
| fp32 | 1 | be the element | ~p of words |
| fp16 | 2 (packed pair) | its partner half must be zero too | ~p² of words |
| int8 | 4 (byte group) | all four bytes of the A word, or all eight bytes of the two B words a lane alternates between (columns *l* and *l* + 8) | ~p⁴ of A words, **~p⁸ of B pairs** (corrected below) |

**A zero is worth most in fp32, less in fp16 and least in int8** — and in the narrow formats *grouping* buys power
where density does not. A zeroed column, a zeroed pair, a zeroed 4-byte group pay; the same number of zeros
scattered does not.

*Corrected Sun 1 Nov 2026 (week 44), Q132(o). This table's int8 row read "all four bytes of the word must be zero, ~p⁴ of
words". p⁴ is int8's word-zero rate. The rule is `A_zero | (tenB_zero[raddr] & tenB_zero[raddr|1])` (`vpu_ctrl.v:1229-1234`):
a B-side decision needs two words, eight bytes, so ~p⁸ of B pairs, and an A word gates a micro-op on its own four bytes,
so ~p⁴ of A words. With both operands sparse a lane gates at p⁴ + p⁸ − p¹², 6.6% at p = ½, the 6.7 ± 1.5% of `kinds.json`.
Both rules were read at power resolution on one card by [E93](../2026-11-01-e93-zero-gate-silicon/README.md) (R6a–c, R7).*

## What this corrects

1. **"fp16 throws away a valid product."** It does not, and this repo already measured that: E39 found 546 cycles
   per 16x16x16 op at any sparsity on three cards and the **correct sum** from a packed pair holding one zero half.
   See `docs/reports/2026-09-18-et-soc1-sparsity.html` §1 (the Hook / PRM / RTL / Measured table, the fp16
   zero-skip row, and the "two answers that are easy to miss" list), `docs/findings/15-earlier-findings.md`,
   `docs/et-soc1-notes.md`, and `docs/findings/01-resources.md` R1, which already lists the fp16 skip rule as a
   known documentation bug. The literal guard
   `if (a1 != 0 && a2 != 0 && b1 != 0 && b2 != 0)` is written in the *ET Programmer's Reference Manual* §9.4
   (public: `aifoundry-org/et-man`), and it is wrong about the hardware. **A document does not overturn a
   measurement.**
2. **"int8 never checks for zeros at all."** True of the PRM pseudo-code, false of the hardware: the RTL above
   gates the integer units from the same mask. int8 zeros are worth *least*, not nothing — which is a different
   prediction and a different blog sentence.
3. **The sign of the zero-price prediction.** Any prediction that has fp16 benefiting from a zero *more* than fp32
   (because "all four halves must be nonzero") is backwards. The word-wide rule makes fp16 benefit *less*.
4. **Why fp16 can draw more power than fp32** — the one claim that survives intact, with a corrected premise. Two
   multiply-adds ride one micro-operation through one shared TXFMA, so a busy lane does twice the arithmetic per
   cycle; and because the gate tests the packed word, it fires less often than fp32's effectively per-element test.
   Both effects push power per cycle up while energy per unit of work falls.

## What it changes for the card runs

- **E79** (fp16/int8 single-bit price lists): the design is unaffected — every operand element is nonzero, which is
  ungated under either candidate rule, so no measurement is invalidated. Two text corrections are owed in
  `tools/claims-v3/hlp/`: `README.md` and `make_hlp.py` justify the all-nonzero operand set partly by the PRM's
  four-operand guard. The right justification is the word-wide rule (an operand *word* of zero gates the lane),
  which is the stronger reason anyway. A dated amendment, written before the data it touches, from the lane that
  owns those files.
- **A one-ladder discriminating test, cheap.** Walk a single zero through the packed positions of an fp16 word and
  then zero the whole word. Under the word-wide rule the single-half rungs are flat and only the full word pays;
  under the PRM's literal rule every position pays. The same ladder in int8 over one, two, three and four zero
  bytes measures the group size directly.
- **The micro-operation counters** (retired fp32 tensor u-ops, retired fp16 tensor u-ops, started int8 u-ops) read
  on zeros against random per format measure the gate's granularity without inferring it from power.
- **Do not re-run the fp16 numerical-loss check.** E39 answered it; the prediction of a wrong answer is false.

## Status

Desk correction, no new measurement. Everything above is checkable in this clone: the RTL paths are in
`external/core-et` (`openhwfoundation/core-et`, Apache-2.0) and the two document sets are public
(`aifoundry-org/et-man` for the PRM, `openhwfoundation/core-et` docs for the VPU specification). Nothing here rests
on a private source.
