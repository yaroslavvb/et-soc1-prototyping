# 1119-mmsweep4: the fourth matrix-multiply sweep on ET-SoC-1 cards (the kit)

The fourth sweep of E136's large-GEMM binary `rgm136`, unchanged, with the third sweep's kit (1118-mmsweep3, itself the second
and the first sweep's in behaviour) unchanged in behaviour: its arms, their data tiles and each card's sessions come from the
sweep's plan (`plan.json` in the request's folder, read at the desk by `make_schedule2.py`), with E190's session form: one
telemetry sampler for the session, live stop lines, the card's identity gated and watched, every device process under
`timeout 10`, reads only. The lab's host rule since aifoundry2's crash of 17 Nov (every host job single-threaded, the box's
load under 6) is kept: the build runs one job, and the preflight refuses a box whose one-minute load is 6 or more. What is
new is at the desk only: the tile generator's periodic index sets and structured zeros, and its pair check read wider (the
lab's kinds and every tile file run before, a pair refused unless its counted switches agree). Every file here is
written from public sources: the public lab repo, the public instruction-set and programmer's manuals, and the open SDK.
Nothing is set on a card: no clock, voltage, limit, firmware or governor.

## Where the copied files come from (the public lab repo, main of 16 Nov 2026; each unchanged)

| here | there | sha256 |
|---|---|---|
| `rgm136/CMakeLists.txt` | `tools/claims-v3/e136/rgm136/CMakeLists.txt` | `123ef6e4ac1572d31914b6049fa700b30af1338c13cc96ec850cd047966dfcfd` |
| `rgm136/README.md` | `tools/claims-v3/e136/rgm136/README.md` | `52815705cbea14c0aea28c81a9e094bbe9e16a04280cb67db5a975aa35d5f8ef` |
| `rgm136/sparsity_args.h` | `tools/claims-v3/e136/rgm136/sparsity_args.h` | `a7e0144ef468dec18ed2d20ec150688a825d6482f17fa7be4dc23c7d17a15332` |
| `rgm136/host/CMakeLists.txt` | `tools/claims-v3/e136/rgm136/host/CMakeLists.txt` | `6b6c1c80139ec0eadc8940bb93c264806412ab93ae90779d9ec6ad13d88a0477` |
| `rgm136/host/Constants.h.in` | `tools/claims-v3/e136/rgm136/host/Constants.h.in` | `c464f57f54f0efd6d5659483c9121a0299bf86d82eacacc66938c8226f7ceebb` |
| `rgm136/host/main.cpp` | `tools/claims-v3/e136/rgm136/host/main.cpp` | `f9b2279f838ad30444748f2a5abad5dd646df631735fc029a6ac01f9036e2fda` |
| `rgm136/kernel/CMakeLists.txt` | `tools/claims-v3/e136/rgm136/kernel/CMakeLists.txt` | `061b87dfa8850f7f6714121f0313dee587fb85509db684693b5f38091ab10948` |
| `rgm136/kernel/crt.S` | `tools/claims-v3/e136/rgm136/kernel/crt.S` | `dffcc2a9668d87bf21501cb6ac5331206e3e86b066453ba0fe530e6e3ab902c4` |
| `rgm136/kernel/sections.ld` | `tools/claims-v3/e136/rgm136/kernel/sections.ld` | `b595c374f947fd8a7e3545e934a0946de651c2bd5d6d93a6a64f3f597f1a8c09` |
| `rgm136/kernel/sparsity.c` | `tools/claims-v3/e136/rgm136/kernel/sparsity.c` | `4be70db597aa2120b9c9904643ff9fc6108ef5eb1f4fb17ac844f9e037619f74` |
| `ettelem/ettelem.cpp` | `tools/ettelem/ettelem.cpp` (the device-command table's reviewed variant `ettelem`) | `a6cf931b2a123e88699c046eb45f438b06d1648cabb86fc114577a32ec153377` |
| `ettelem/CMakeLists.txt` | `tools/ettelem/CMakeLists.txt` | `64793f7eeeea9d7371cd36680e2c8324b1ba6b9547fd1815fd04a0dec9f7ad39` |
| `dmcmd/dmcmd_audit.py` | `tools/claims-v3/dmcmd_audit.py` | `f29e91ca97705454f67c46c28974a085c5bb70ff43e940538b1f670b88ae844e` |
| `dmcmd/dmcmd_table.json` | `tools/claims-v3/dmcmd_table.json` | `50168632931fd8c1fab40794cbaaac6aca3d31f01d4367d8a21fcf69c0bdc638` |
| `tiles/fp32/randn.bin`, `zeros.bin`, `ones.bin` | `tools/claims-v3/kinds/tiles/fp32/` (kinds.json) | `34b2add3...`, `e5a00aa9...`, `fef951e6...` |
| `tiles/fp16/randn.bin`, `zeros.bin`, `ones.bin` | `tools/claims-v3/kinds/tiles/fp16/` | `2ab30f0f...`, `e5a00aa9...`, `c02234fb...` |
| `tiles/int8/full.bin`, `zeros.bin`, `ones.bin` | `tools/claims-v3/kinds/tiles/int8/` | `f5a5f3bf...`, `e5a00aa9...`, `7c7d2eb3...` |

The kit's own files, written for this sweep from the forms of E190's kit (`tools/claims-v3/e190/`: `run_e190_v2.py`,
`e190_common.py`, `e190_note1.py`, `ettelem_guard_e190.sh`, `build_e190_v2.sh`, `check_e190_v2.py`, `reduce_e190.py`):

| file | what |
|---|---|
| `make_schedule2.py` → `arms.json`, `sched/<card>-<S>.json`, the plan's tiles | the arms and each card's sessions S1 to S9 from the plan, by the first sweep's laws (its `make_schedule.py`, copied): the estimates and planning lines, the `time` role, the anchor first, between blocks and last, the null runs, the seeded order (seeded; `--check`) |
| `tiles_gen.py` → `tiles/<type>/<name>.bin` | the plan's tile files, seeded, in the layout the host reads (raw words, constants, cycles, draws; alternations for density and toggle rate, with periodic index sets for rates along K; drawn fields; exact sparsity, seeded or structured zeros), and the reader that decodes every tile file back and checks it (finite, no subnormal, the check of C exact or approx at every K an arm runs it at; `--check`, `--read`); the pair check over the tile set (no two tiles of a type at equal input toggles unless their counted switches agree; `--pairs`), and at the desk its wider form against the lab's kinds and every tile file run before (`--priors`, a desk list never pushed) |
| `mms_common.py` | the cards, the layout, the process form, the counted launch by clock band, the stop lines; its self-check |
| `mms_ident.py` | the card's identity (config read, holder read, the host watch); its self-check |
| `run_mms.py` | one card's session from its schedule; `--dry` runs it with the doubles and prints every device call |
| `fake_card_mms.py` | the doubles (config, et-who, the sampler, the host) for `--dry` and the desk tests: arbitrary test values, not a forecast; a warming die with leakage, lagged rails, a governed clock with a power cap |
| `guard_ettelem.sh` | the only way a session calls the reader: `config`, and `sample --seconds --every-ms` |
| `session_mms.sh`, `start_mms.sh`, `status_mms.sh`, `stop_mms.sh`, `dry_mms.sh` | the box-side session, start (detached), status, stop and dry pass |
| `build_mms.sh`, `preflight_mms.sh` | the box build (nice 10, 1 job) and the preflight looks (NO-GO at a one-minute load of 6 or more, the reading kept in `run/preflight-load.txt`) with the device-command audit |
| `check_mms.py`, `SRC-SHA256SUMS` | the harness: every file here at its sha256 (`--prune` removes from a box's src/ the files a re-push no longer lists) |
| `reduce_mms.py`, `collect_mms.py` | the reduction (its registered rules: the views, the capped rule, three baselines, the rails undone over the board's window, the DDR droop, the null runs, the die-start correction; `--combine` across sessions), and the desk's collection of a pulled session (copy-back, privacy read, reduction) |
| `selftest_mms.py` | the desk tests |

## The arms (from the plan: `arms.json` lists them, with the plan's tiles and sessions)

`gemmL<MB>x<NB>x<KB>` computes C (MB x NB blocks of 1,024 x 512) = A (MB x KB blocks) x B (KB x NB blocks), so M = 1,024 MB,
N = 512 NB and K = 512 KB (fp32), 1,024 KB (fp16), 2,048 KB (int8); a tensor op is 4,096, 8,192 or 16,384 multiply-adds; a
minion runs MB x NB x 2 x KB x 32 ops a pass. Data: `rnd` is the host's drawn pool (`randn`: normal values in fp32 and fp16,
uniform -128..127 in int8, the pool's first tile pair the file's); `zeros` and `ones` repeat the file's tile through the pool.
A shire mask other than `0xffffffff` runs the arm on part of the chip (here 1 to 24 shires), each shire its own part of C.
Run forms: `burst` (10 s at rest, one 6 s process, 5 s at rest), `sus3` (20 s at rest, three processes back to back, 20 s at
rest) and `null` (the same windows with no process: what the baseline rules read at zero signal).

A plan tile `<name>` is a data kind of its type: `tiles:src/tiles/<type>/<name>.bin` (the pool repeats its one tile pair), or
`<gen>:src/tiles/<type>/<name>.bin` for the host's drawn pools (`randn`, `sparse50`, `sparse25`, `e37`: the file is pair 0).
An arm on the n low shires is named `-s<n>` (`0x1`, `0xf`, `0xff`, `0xffff`, `0xffffff`: `-s1`, `-s4`, `-s8`, `-s16`, `-s24`), on
any other mask `-m<hex>`: `1x1x4-fp32-rnd-mf0f0f0f0`.

## Build (on a box, from the kit's root `~/claude/work/ee-1119-mmsweep4`)

`bash src/build_mms.sh`: `nice -n 10 cmake -G "Unix Makefiles" -S src/rgm136 -B build/rgm -DCMAKE_PREFIX_PATH=/opt/et
-Wno-dev`, `nice -n 10 cmake --build build/rgm -j1`, the same for `src/ettelem` into `build/ettelem`; the kernel ELF must be
E136's build record's `aace138c...`; on aifoundry1 the host and the reader must carry `ET_DEVICES`. Record:
`build/BUILD-mms.json`. The build, the dry pass and a session each hold the kit's box lock `run/box.lock` while they run
(`src/start_mms.sh` takes it before its checks and hands it to the session), so none of them runs beside another.

SPDX-License-Identifier: Apache-2.0
