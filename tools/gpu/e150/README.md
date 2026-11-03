# tools/gpu/e150 — E150, E149's frozen toggle model on a second GPU type

The registration is [`E150.md`](E150.md). [`e150_app.py`](e150_app.py) is the Modal harness (E149's, with the GPU
type, the sizes, the two phases and the holds changed); [`analyze_e150.py`](analyze_e150.py) chooses the GPU and sizes
from the smoke, reduces each phase, freezes the per-board scales and blind predictions from phase L, and scores phase
H; it imports E149's analysis (`../e149/analyze_e149.py`) for the windows, the features, the frozen models and the heat
fit. [`selftest_e150.py`](selftest_e150.py) runs the chain on synthetic logs ([`selftest.txt`](selftest.txt)).

    MODAL_PROFILE=yaroslavvb modal run e150_app.py --mode dry
    MODAL_PROFILE=yaroslavvb modal run e150_app.py --mode smoke --run-id <id>
    MODAL_PROFILE=yaroslavvb modal run --detach e150_app.py --mode main --gpu <L4|A10G> --sizes '<json>' --run-id <id>

Data: `docs/reports/data/2026-11-02-e150-second-gpu/`.
