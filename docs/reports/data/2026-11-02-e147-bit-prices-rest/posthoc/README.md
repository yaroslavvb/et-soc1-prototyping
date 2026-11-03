# E147 post hoc: M7 at E147's items (added after verification, Mon 2 Nov 2026)

*Post hoc, labelled, unregistered, no verdict.* E147's registration (`c41c3905`) named M6 and M5. M7 (Q138(m), frozen at `3a210f2b`,
19:21:05 PST, before that registration) was scored here after E147's data, by
[`../posthoc_m7_e147.py`](../posthoc_m7_e147.py), with nothing refitted or tuned. The correction is C2 of the data README's
[§ Corrections after verification](../README.md#corrections-after-verification-mon-2-nov-2026).

- `predict_blind5/predictions-aifoundry3.json` and `.md`: the output of Q138(m)'s frozen
  [`predict_blind5.py`](../../2026-11-02-q138m-model/predict_blind5.py) on E147's 73 committed tiles, on aifoundry3: each tile's D
  by M7, M6 and M5, with the sha256 of every model file, the pool manifest and the bench counts it read. Its title calls them frozen
  predictions because the models are frozen; they were computed after the data.
- `m7-e147.json` and `m7-e147.txt`: the steps (D(item) − D(own zero)) by M7, M6 and M5 against the measured steps over E147's
  registered lists, the exponent's measured / model, per-flip errors, M7's contrasts, and a check that M6's and M5's steps from
  this run equal E147's registered frozen steps (to 0.0001 W).

M7 reads the 68 new items to 0.202 W rms (bias −0.092): the mantissa to 0.160 W, the exponent to 0.278 W, where the card pays 0.84
of M7's watts.
