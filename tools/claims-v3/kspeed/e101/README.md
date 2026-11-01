# kspeed/e101: E101's session 2, a matmul that streams under aifoundry2's own governor (Q132)

The registration, the kinds, the rules and the frozen clocks are in [`../../kinds/E101.md`](../../kinds/E101.md) and [`../../kinds/predictions-e101.json`](../../kinds/predictions-e101.json). This folder is the session's code, E80's design.

- [`run_e101s.py`](run_e101s.py): E80's `run_kspeed.py` (E64's `run_hpl.py`), imported and run unchanged, with E101's `--values` strings allowed and their tile files checked first.
- [`make_protocol_e101s.py`](make_protocol_e101s.py): writes `protocol.json`, `protocol-dry.json` and `start-modes.json` from session 1's committed `e101.json`, by the rule of E101.md: a cell's start mode follows its board power at 800 MHz.
- [`queue_e101s.py`](queue_e101s.py): E96's queue: detached on the box, launches nothing before the slot's start, waits for E98's probe, the card lock, `et-who` and logins, records the box's state, smoke and its check, the session with its own cap, the hard stop at the slot's end.
- [`reduce_e101s.py`](reduce_e101s.py): E80's and E96's per-run reduction, imported unchanged, then the rules S1-S5.

On aifoundry2, `build/sparsity_t2`, `build/ettelem-hpl` and `tools/claims-v3/kspeed/e98` are not touched: the kernel and host are `build/e101`, built from `tools/claims-v3/rgm`, and the sampler is E98's `build/ettelem-hpl`, read only.
