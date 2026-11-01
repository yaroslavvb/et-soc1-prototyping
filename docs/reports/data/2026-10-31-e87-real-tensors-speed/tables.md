### Speed, power and heat per tile (measured)

| tile | burst MHz (passes) | burst rate | p800 W | burst limit | sustained MHz (runs) | sustained rate | board W | die °C | limit | c W | board pJ/op (derived) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 real l0_mlp_up | 708.8 (709.8 / 707.8) | 10.59 TFLOPS | 82.2 | power | 608.2 (608.2) | 9.32 TFLOPS | 54.8 | 66.0 | thermal | 25.47 | 5.88 |
| fp32 real l6_mlp_down | 699.0 (700.0 / 698.0) | 10.52 TFLOPS | 83.1 | power | 600.5 (600.5) | 9.21 TFLOPS | 53.8 | 66.3 | thermal | 25.46 | 5.84 |
| fp32 real l6_attn_qk | 702.0 (705.9 / 698.0) | 10.54 TFLOPS | 82.7 | power | 602.8 (602.8) | 9.25 TFLOPS | 53.9 | 66.1 | thermal | 25.22 | 5.83 |
| fp16 real l0_mlp_up | 727.0 (728.0 / 726.0) | 21.86 TFLOPS | 77.9 | power | 619.9 (619.9) | 18.92 TFLOPS | 53.2 | 65.8 | thermal | 22.90 | 2.81 |
| fp16 real l6_mlp_down | 725.5 (726.0 / 725.0) | 21.91 TFLOPS | 77.8 | power | 602.8 (602.8) | 18.51 TFLOPS | 51.5 | 66.0 | thermal | 22.92 | 2.78 |
| fp16 real l6_attn_qk | 734.4 (736.7 / 732.0) | 22.14 TFLOPS | 76.8 | power | 612.3 (612.3) | 18.74 TFLOPS | 51.6 | 65.9 | thermal | 22.34 | 2.75 |
| int8 real l0_mlp_up | 777.0 (800.0 / 754.0) | 81.61 TOPS | 47.6 | none | 794.4 (794.4) | 83.70 TOPS | 51.6 | 64.5 | none | 8.24 | 0.62 |
| int8 real l6_mlp_down | 800.0 (800.0 / 800.0) | 84.31 TOPS | 46.8 | none | 793.6 (793.6) | 83.63 TOPS | 50.2 | 64.3 | none | 7.56 | 0.60 |
| int8 real l6_attn_qk | 800.0 (800.0 / 800.0) | 84.31 TOPS | 47.1 | none | 800.0 (800.0) | 84.33 TOPS | 50.7 | 64.5 | none | 7.53 | 0.60 |
| fp32 randn | 706.0 (706.0 / 705.9) | 10.66 TFLOPS | 81.9 | power | 600.1 (600.3 / 600.0) | 9.21 TFLOPS | 53.8 | 66.4 | thermal | 25.59 | 5.84 |
| fp32 zeros | 800.0 (800.0 / 800.0) | 12.28 TFLOPS | 34.3 | none | 800.0 (800.0) | 12.28 TFLOPS | 35.7 | 57.9 | none | 1.55 | 2.91 |
| fp16 randn | 721.2 (720.4 / 722.0) | 21.82 TFLOPS | 78.4 | power | 610.0 (604.6 / 615.3) | 18.69 TFLOPS | 52.4 | 66.0 | thermal | 23.15 | 2.81 |
| fp16 zeros | 800.0 (800.0 / 800.0) | 24.55 TFLOPS | 33.9 | none | 800.0 (800.0) | 24.56 TFLOPS | 35.8 | 58.0 | none | 1.75 | 1.46 |
| int8 full | 800.0 (800.0 / 800.0) | 84.31 TOPS | 49.5 | none | 774.7 (774.7) | 80.85 TOPS | 51.4 | 65.1 | thermal | 8.88 | 0.64 |
| int8 zeros | 800.0 (800.0 / 800.0) | 84.31 TOPS | 35.7 | none | 788.5 (788.5) | 83.03 TOPS | 36.6 | 58.4 | none | 2.19 | 0.44 |

### Against Q130(n)'s frozen predictions (Amendment 1's scoring intervals; frozen D-propagated ranges)

| tile | burst | frozen point | scoring | inside | frozen range | sustained | frozen point | scoring | inside | frozen range | limit (predicted) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 real l0_mlp_up | 708.8 | 710.7 | 681.3–740.5 | yes | 691.8–730.0 | 608.2 | 602.5 | 600.0–621.7 | yes | 600.2–611.1 | thermal (thermal) |
| fp32 real l6_mlp_down | 699.0 | 711.5 | 682.1–741.3 | yes | 692.6–730.8 | 600.5 | 602.7 | 600.0–622.1 | yes | 600.3–611.7 | thermal (thermal) |
| fp32 real l6_attn_qk | 702.0 | 710.7 | 681.3–740.5 | yes | 691.8–730.0 | 602.8 | 602.5 | 600.0–621.7 | yes | 600.2–611.1 | thermal (thermal) |
| fp16 real l0_mlp_up | 727.0 | 735.6 | 706.0–767.0 | yes | 719.3–753.4 | 619.9 | 615.0 | 600.0–641.0 | yes | 605.3–629.9 | thermal (thermal) |
| fp16 real l6_mlp_down | 725.5 | 738.9 | 709.2–770.7 | yes | 722.4–757.1 | 602.8 | 617.6 | 600.0–644.4 | yes | 606.8–633.3 | thermal (thermal) |
| fp16 real l6_attn_qk | 734.4 | 737.2 | 707.6–768.8 | yes | 720.8–755.2 | 612.3 | 616.2 | 600.0–642.7 | yes | 606.0–631.5 | thermal (thermal) |
| int8 real l0_mlp_up | 777.0 | 800.0 | 800.0–800.0 | no | 800.0–800.0 | 794.4 | 796.2 | 775.3–800.0 | yes | 788.7–799.2 | none (none) |
| int8 real l6_mlp_down | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | 793.6 | 798.9 | 780.9–800.0 | yes | 795.1–799.9 | none (none) |
| int8 real l6_attn_qk | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | 800.0 | 797.0 | 776.7–800.0 | yes | 790.3–799.4 | none (none) |

### Like with like: switching above zeros as a share of the same-session reference (measured c, bursts)

| tile | reference | measured ratio | Q130(n) predicted | S3 interval | frozen interval | c W measured | c W predicted (amended interval) |
|---|---|---|---|---|---|---|---|
| fp32 real l0_mlp_up | fp32/randn | 0.9953 | 0.9894 | 0.8918–1.087 | 0.9006–1.0781 | 25.472 | 25.454 (23.085–27.823) |
| fp32 real l6_mlp_down | fp32/randn | 0.9948 | 0.9858 | 0.8882–1.0834 | 0.897–1.0745 | 25.459 | 25.367 (22.998–27.735) |
| fp32 real l6_attn_qk | fp32/randn | 0.9850 | 0.9893 | 0.8917–1.0869 | 0.9006–1.0781 | 25.224 | 25.453 (23.084–27.822) |
| fp16 real l0_mlp_up | fp16/randn | 0.9884 | 0.9798 | 0.8736–1.0859 | 0.8984–1.0612 | 22.900 | 22.71 (20.401–25.019) |
| fp16 real l6_mlp_down | fp16/randn | 0.9895 | 0.9637 | 0.8575–1.0698 | 0.8823–1.0451 | 22.924 | 22.36 (20.051–24.669) |
| fp16 real l6_attn_qk | fp16/randn | 0.9624 | 0.9718 | 0.8657–1.0779 | 0.8904–1.0532 | 22.344 | 22.537 (20.228–24.846) |
| int8 real l0_mlp_up | int8/full | 0.9040 | 0.8347 | 0.6478–1.0216 | 0.7088–0.9604 | 8.239 | 7.905 (6.61–9.2) |
| int8 real l6_mlp_down | int8/full | 0.8029 | 0.7345 | 0.5476–0.9214 | 0.6088–0.8603 | 7.563 | 7.211 (5.916–8.506) |
| int8 real l6_attn_qk | int8/full | 0.7974 | 0.8147 | 0.6278–1.0016 | 0.6889–0.9404 | 7.526 | 7.767 (6.472–9.062) |

### Real against random, same session

| format | real tiles' mean burst | randn burst | difference | real mean sustained | randn sustained | difference |
|---|---|---|---|---|---|---|
| fp32 | 703.3 | 706.0 | -2.7 | 603.8 | 600.1 | 3.7 |
| fp16 | 729.0 | 721.2 | 7.8 | 611.7 | 610.0 | 1.7 |
| int8 (vs full) | 792.3 | 800.0 | -7.7 | 796.0 | 774.7 | 21.3 |
