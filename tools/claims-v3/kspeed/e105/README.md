# kspeed/e105: does the gap come back when the tiles fit the L2? (Q132)

The registration is [`E105.md`](E105.md); the frozen numbers are `predictions-e105.json` and `.txt`, written by `make_predictions_e105.py` from the desk L2 model (`desk/`) and E101's record. The binary is `../../rgm105/`, built into `build/e105`.

- `make_protocol_e105.py`: writes `protocol.json` and `protocol-dry.json`, printed in `protocol.txt`.
- `run_e105.py`: E101 session 2's runner, unchanged, plus the registered power rule. Every other safety path is run_hpl.py's.
- `queue_e105.py`: the detached queue, E101 session 2's with E105's names.
- `reduce_e105.py`: the reduction, the fit T = C/f + M per layout and format, and the rules. `selftest_e105.py` shows every rule failing on made-up rows, and the power rule refusing, in `selftest.txt`.
