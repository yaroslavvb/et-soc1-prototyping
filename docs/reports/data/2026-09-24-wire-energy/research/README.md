# Research behind the heat-per-millimetre report (24 September 2026)

A seven-agent workflow (four researchers, two adversarial verifiers, one synthesis) gathered what is needed to turn
the measured per-hop mesh energy into joules per bit per metre. `SYNTHESIS.md` is its result; `workflow-result.json`
holds every agent's structured return (numbers, sources, quotes, verdicts).

| Path | What it is |
|---|---|
| `SYNTHESIS.md` | Written before the 24 September runs; its measured numbers are superseded by `../wire.json` (see its first paragraph). Inputs with sources and confidence: die size and tile pitch, NoC width/clock/voltage/routing, Dally's figure verbatim and its (absent) conditions, other literature values, a first-principles estimate at 0.485 V, the conversion of the 23 September (E27) measurement, and the critique's design changes. |
| `geometry/pitch.py`, `pitch.json`, `measure.py` | The tile pitch measured in pixels on Esperanto's published die plot (IEEE Micro 42(3) 2022, Fig. 7: https://www.esperanto.ai/wp-content/uploads/2022/05/Dave-IEEE-Micro.pdf; also HC33 slide 20 and MPR Dec 2020 Fig. 1), scaled to the published 570 mm². The images are not re-hosted here; extract them with `pdfimages -j`. Result: x 3.73 mm, y 3.70 mm, mean hop 3.72 mm (3.64-3.74). |
| `critique/toggles.py`, `toggles.json`, `gen_sources.cpp` | The exact byte image the old 'random' prefill wrote (a verbatim copy of `sources()`), and its bit-toggle rate between consecutive flits: 0.445 per bit for 64 B flits in address order. |
| `critique/railfit.py`, `railfit.json` | The E27 wire slopes refitted per rail (board, NoC, SRAM, minion) and per card, with and without d = 8. |
| `critique/linkload.py`, `linkload.json`, `confounds.py`, `empty_cells.py` | Link sharing, readers and bandwidth against hop distance in E27 (XY routing), and the d = 8 anomaly. |
| `lit/wire_calc.py`, `first-principles-estimate.md` | Wire energy from capacitance per mm (ASAP7 predictive 7 nm values) at 0.485 V, and the V^2 scaling to other voltages; the markdown is the table of results. |
| `synthesis/convert.py` | The unit conversions of the synthesis (pJ/B/hop to fJ/bit/mm, per transition, effective capacitance, V^2 scaling). Superseded by `../wire.json`: it uses the E27 inputs and the provisional 3.64–3.76 mm pitch range, as does the last section of `lit/wire_calc.py`. |

`critique/railfit.py` and `critique/confounds.py` read the energy catalogue (`catalogue.json`) by absolute path; edit
the path at the top to run them from another checkout.
`geometry/README.md` says which die-plot readings in `pitch.py` are by hand.

Third-party PDFs and their text extractions were read but are not committed; every number in `SYNTHESIS.md` cites
its URL and page.
