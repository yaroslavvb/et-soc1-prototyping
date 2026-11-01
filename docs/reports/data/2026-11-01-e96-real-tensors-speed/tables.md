### Speed, power and heat per tile (measured)

| tile | what | burst MHz (passes) | burst rate | p800 W | burst limit | sustained MHz (runs) | sustained rate | board W | die °C | limit | c W | board pJ/op (derived) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 resnet18_l2c1 | exact zeros (ReLU) | 741.2 (741.2 / 741.2) | 11.18 TFLOPS | 73.9 | power | 650.1 (650.1) | 9.85 TFLOPS | 55.4 | 65.6 | thermal | 20.91 | 5.62 |
| fp32 resnet18_l3c1 | exact zeros (ReLU) | 800.0 (800.0 / 800.0) | 12.28 TFLOPS | 62.5 | none | 677.2 (677.2) | 10.26 TFLOPS | 51.5 | 65.5 | thermal | 15.29 | 5.03 |
| fp32 vgg16_fc2 | exact zeros (ReLU) | 800.0 (800.0 / 800.0) | 12.28 TFLOPS | 50.4 | none | 784.1 (784.1) | 11.96 TFLOPS | 52.8 | 65.1 | thermal | 9.15 | 4.41 |
| fp32 t5small_l0_down | exact zeros (ReLU) | 800.0 (800.0 / 800.0) | 12.28 TFLOPS | 37.3 | none | 795.4 (795.4) | 12.20 TFLOPS | 39.5 | 59.2 | none | 3.19 | 3.23 |
| fp32 gpt2_l3_mlp_down | no exact zeros | 702.0 (698.0 / 705.9) | 10.54 TFLOPS | 83.1 | power | – () | – TFLOPS | – | – | – | 25.50 | – |
| fp32 gpt2_l9_attn_qk | no exact zeros | 695.2 (707.8 / 682.7) | 10.41 TFLOPS | 82.4 | power | – () | – TFLOPS | – | – | – | 25.09 | – |
| fp32 bert_l6_up | no exact zeros | 702.0 (698.0 / 705.9) | 10.57 TFLOPS | 83.1 | power | 601.5 (601.5) | 9.23 TFLOPS | 53.9 | 66.0 | thermal | 25.44 | 5.84 |
| fp32 vit_l5_down | no exact zeros | 703.0 (709.8 / 696.1) | 10.55 TFLOPS | 82.9 | power | – () | – TFLOPS | – | – | – | 25.56 | – |
| fp32 t5small_l0_up | bf16-grid weights | 725.2 (720.4 / 730.0) | 10.92 TFLOPS | 77.7 | power | 603.1 (603.1) | 9.25 TFLOPS | 51.3 | 66.0 | thermal | 22.89 | 5.55 |
| fp32 vit_l11_down | -0.0 | 740.2 (740.8 / 739.6) | 11.15 TFLOPS | 74.9 | power | 615.6 (615.6) | 9.41 TFLOPS | 51.2 | 65.9 | thermal | 21.40 | 5.44 |
| fp16 resnet18_l3c1 | exact zeros (ReLU) | 800.0 (800.0 / 800.0) | 24.55 TFLOPS | 62.0 | none | 689.5 (689.5) | 20.79 TFLOPS | 52.6 | 65.6 | thermal | 15.15 | 2.53 |
| fp16 vgg16_fc2 | exact zeros (ReLU) | 800.0 (800.0 / 800.0) | 24.55 TFLOPS | 55.0 | none | 744.8 (744.8) | 22.50 TFLOPS | 53.1 | 65.4 | thermal | 11.46 | 2.36 |
| fp16 t5small_l0_down | exact zeros (ReLU) | 800.0 (800.0 / 800.0) | 24.55 TFLOPS | 41.8 | none | 794.9 (794.9) | 24.38 TFLOPS | 43.8 | 61.9 | none | 4.99 | 1.80 |
| fp16 gpt2_l9_attn_qk | no exact zeros | 732.6 (731.2 / 734.0) | 22.10 TFLOPS | 76.3 | power | – () | – TFLOPS | – | – | – | 22.12 | – |
| fp16 bert_l6_up | no exact zeros | 731.2 (740.8 / 721.6) | 22.09 TFLOPS | 77.0 | power | – () | – TFLOPS | – | – | – | 22.96 | – |
| fp16 vit_l5_down | no exact zeros | 734.9 (745.8 / 724.0) | 22.18 TFLOPS | 76.2 | power | 612.0 (612.0) | 18.74 TFLOPS | 52.4 | 65.9 | thermal | 22.73 | 2.80 |
| fp16 gpt2_l6_mlp_down_fp16fwd | fp16 forward | 708.2 (718.4 / 698.0) | 21.40 TFLOPS | 77.9 | power | – () | – TFLOPS | – | – | – | 22.95 | – |
| int8 resnet18_l3c1 | exact zeros (ReLU) | 800.0 (800.0 / 800.0) | 84.30 TOPS | 44.7 | none | – () | – TOPS | – | – | – | 6.32 | – |
| int8 vgg16_fc2 | exact zeros (ReLU) | 800.0 (800.0 / 800.0) | 84.31 TOPS | 43.8 | none | – () | – TOPS | – | – | – | 5.31 | – |
| int8 gpt2_l6_down_per_token | int8 calibration | 800.0 (800.0 / 800.0) | 84.31 TOPS | 46.1 | none | – () | – TOPS | – | – | – | 7.76 | – |
| int8 gpt2_l6_down_p9999 | int8 calibration | 800.0 (800.0 / 800.0) | 84.31 TOPS | 47.0 | none | – () | – TOPS | – | – | – | 6.88 | – |
| int8 gpt2_l6_down_p999 | int8 calibration | 800.0 (800.0 / 800.0) | 84.31 TOPS | 47.1 | none | – () | – TOPS | – | – | – | 7.69 | – |
| int8 gpt2_l11_down_maxabs | int8 calibration | 800.0 (800.0 / 800.0) | 84.30 TOPS | 41.0 | none | – () | – TOPS | – | – | – | 4.45 | – |
| int8 gpt2_l11_down_p999 | int8 calibration | 800.0 (800.0 / 800.0) | 84.30 TOPS | 46.1 | none | – () | – TOPS | – | – | – | 6.84 | – |
| int8 vgg16_fc2_asym | int8 calibration | 800.0 (800.0 / 800.0) | 84.31 TOPS | 45.2 | none | – () | – TOPS | – | – | – | 6.66 | – |
| int8 l0_mlp_up | E87's real int8 | – () | – TOPS | – | – | 793.4 (800.0 / 789.7 / 789.3 / 794.4) | 83.55 TOPS | 51.6 | 64.6 | none | – | 0.62 |
| int8 l6_mlp_down | E87's real int8 | – () | – TOPS | – | – | 797.4 (800.0 / 800.0 / 789.7 / 800.0) | 84.03 TOPS | 50.2 | 63.8 | none | – | 0.60 |
| int8 l6_attn_qk | E87's real int8 | – () | – TOPS | – | – | 795.8 (793.9 / 800.0 / 789.2 / 800.0) | 83.84 TOPS | 49.8 | 63.7 | none | – | 0.59 |
| fp32 randn | anchor | 703.9 (709.8 / 698.0) | 10.55 TFLOPS | 82.8 | power | 601.8 (600.8 / 602.8) | 9.23 TFLOPS | 53.8 | 66.1 | thermal | 25.56 | 5.83 |
| fp32 zeros | anchor | 800.0 (800.0 / 800.0) | 12.28 TFLOPS | 34.2 | none | 800.0 (800.0) | 12.28 TFLOPS | 35.6 | 57.6 | none | 1.60 | 2.90 |
| fp16 randn | anchor | 722.7 (725.0 / 720.4) | 21.82 TFLOPS | 77.4 | power | 608.8 (604.1 / 613.5) | 18.63 TFLOPS | 52.1 | 65.9 | thermal | 23.07 | 2.80 |
| fp16 zeros | anchor | 800.0 (800.0 / 800.0) | 24.55 TFLOPS | 35.0 | none | 800.0 (800.0) | 24.56 TFLOPS | 35.5 | 57.4 | none | 1.47 | 1.45 |
| int8 full | anchor | 800.0 (800.0 / 800.0) | 84.31 TOPS | 49.9 | none | 789.4 (791.6 / 793.4 / 777.2 / 795.4) | 82.97 TOPS | 52.7 | 64.9 | none/none/thermal/none | 8.88 | 0.64 |
| int8 zeros | anchor | 800.0 (800.0 / 800.0) | 84.31 TOPS | 36.2 | none | 794.4 (794.4) | 83.69 TOPS | 36.7 | 58.0 | none | 2.21 | 0.44 |

### Against Q132(r)'s frozen predictions (scoring intervals; the frozen D-propagated ranges beside them)

| tile | burst | frozen | scoring | inside | D range | sustained | frozen | scoring | inside | D range | limit (predicted) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 resnet18_l2c1 | 741.2 | 755.5 | 718.7–793.9 | yes | 725.2–787.8 | 650.1 | 631.8 | 603.0–670.1 | yes | 608.2–666.3 | thermal (thermal) |
| fp32 resnet18_l3c1 | 800.0 | 799.5 | 774.4–800.0 | yes | 785.4–800.0 | 677.2 | 703.0 | 659.7–747.3 | yes | 662.9–744.2 | thermal (thermal) |
| fp32 vgg16_fc2 | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | 784.1 | 793.2 | 746.1–800.0 | yes | 749.1–800.0 | thermal (none) |
| fp32 t5small_l0_down | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | 795.4 | 800.0 | 800.0–800.0 | no | 800.0–800.0 | none (none) |
| fp32 gpt2_l3_mlp_down | 702.0 | 711.5 | 681.8–741.6 | yes | 690.3–733.3 | – | 602.7 | 600.0–622.3 | – | 600.2–613.4 | – (thermal) |
| fp32 gpt2_l9_attn_qk | 695.2 | 710.5 | 680.9–740.6 | yes | 689.3–732.2 | – | 602.4 | 600.0–621.8 | – | 600.2–612.6 | – (thermal) |
| fp32 bert_l6_up | 702.0 | 711.3 | 681.6–741.3 | yes | 690.1–733.0 | 601.5 | 602.6 | 600.0–622.2 | yes | 600.2–613.2 | thermal (thermal) |
| fp32 vit_l5_down | 703.0 | 711.2 | 681.5–741.3 | yes | 690.0–733.0 | – | 602.6 | 600.0–622.1 | – | 600.2–613.1 | – (thermal) |
| fp32 t5small_l0_up | 725.2 | 728.3 | 698.4–759.8 | yes | 706.8–752.0 | 603.1 | 610.1 | 600.0–634.9 | yes | 601.7–628.6 | thermal (thermal) |
| fp32 vit_l11_down | 740.2 | 747.6 | 716.5–781.0 | yes | 724.5–773.8 | 615.6 | 624.8 | 601.2–654.4 | yes | 607.8–649.4 | thermal (thermal) |
| fp16 resnet18_l3c1 | 800.0 | 799.8 | 776.7–800.0 | yes | 789.6–800.0 | 689.5 | 709.5 | 666.0–754.7 | yes | 669.2–751.6 | thermal (thermal) |
| fp16 vgg16_fc2 | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | 744.8 | 770.3 | 722.1–800.0 | yes | 725.0–799.3 | thermal (thermal) |
| fp16 t5small_l0_down | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | 794.9 | 800.0 | 783.5–800.0 | yes | 799.6–800.0 | none (none) |
| fp16 gpt2_l9_attn_qk | 732.6 | 737.5 | 702.6–776.1 | yes | 709.4–770.0 | – | 616.5 | 600.0–649.9 | – | 602.2–645.6 | – (thermal) |
| fp16 bert_l6_up | 731.2 | 737.5 | 702.6–776.1 | yes | 709.4–770.0 | – | 616.5 | 600.0–649.9 | – | 602.2–645.6 | – (thermal) |
| fp16 vit_l5_down | 734.9 | 736.3 | 701.4–774.7 | yes | 708.3–768.7 | 612.0 | 615.5 | 600.0–648.6 | yes | 601.9–644.2 | thermal (thermal) |
| fp16 gpt2_l6_mlp_down_fp16fwd | 708.2 | 739.9 | 704.8–778.8 | yes | 711.6–772.8 | – | 618.4 | 600.0–652.6 | – | 602.7–648.4 | – (thermal) |
| int8 resnet18_l3c1 | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | – | 800.0 | 783.5–800.0 | – | 799.6–800.0 | – (none) |
| int8 vgg16_fc2 | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | – | 800.0 | 800.0–800.0 | – | 800.0–800.0 | – (none) |
| int8 gpt2_l6_down_per_token | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | – | 798.5 | 781.0–800.0 | – | 792.8–799.9 | – (none) |
| int8 gpt2_l6_down_p9999 | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | – | 798.8 | 781.6–800.0 | – | 793.8–799.9 | – (none) |
| int8 gpt2_l6_down_p999 | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | – | 798.2 | 780.7–800.0 | – | 792.1–799.8 | – (none) |
| int8 gpt2_l11_down_maxabs | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | – | 800.0 | 800.0–800.0 | – | 800.0–800.0 | – (none) |
| int8 gpt2_l11_down_p999 | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | – | 799.0 | 781.9–800.0 | – | 794.4–799.9 | – (none) |
| int8 vgg16_fc2_asym | 800.0 | 800.0 | 800.0–800.0 | yes | 800.0–800.0 | – | 799.9 | 783.4–800.0 | – | 799.0–800.0 | – (none) |

### The gate and the clock: gated tiles against same-session random data of their format

| tile | gate closes | c W measured | c W (a) | c W gate law | burst | − randn | relation on measured c | gate law | sustained | − randn | relation on measured c | gate law |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 resnet18_l2c1 | 0.191 | 20.91 | 20.742 | 21.2 | 741.2 | 37.3 | 753.7 | 750.6 | 650.1 | 48.3 | 630.2 | 627.4 |
| fp32 resnet18_l3c1 | 0.445 | 15.29 | 14.842 | 15.215 | 800.0 | 96.1 | 798.9 | 799.1 | 677.2 | 75.4 | 697.1 | 698.1 |
| fp32 vgg16_fc2 | 0.723 | 9.15 | 8.335 | 8.678 | 800.0 | 96.1 | 800.0 | 800.0 | 784.1 | 182.3 | 784.0 | 789.8 |
| fp32 t5small_l0_down | 0.949 | 3.19 | 2.596 | 3.338 | 800.0 | 96.1 | 800.0 | 800.0 | 795.4 | 193.6 | 800.0 | 800.0 |
| fp16 resnet18_l3c1 | 0.367 | 15.15 | 14.342 | 15.421 | 800.0 | 77.3 | 799.1 | 798.7 | 689.5 | 80.7 | 699.0 | 695.4 |
| fp16 vgg16_fc2 | 0.551 | 11.46 | 10.061 | 11.557 | 800.0 | 77.3 | 800.0 | 800.0 | 744.8 | 136.0 | 748.5 | 747.1 |
| fp16 t5small_l0_down | 0.871 | 4.99 | 3.71 | 4.814 | 800.0 | 77.3 | 800.0 | 800.0 | 794.9 | 186.1 | 800.0 | 800.0 |

### Real against random, no zero word, and the special cases

| tile | what | burst | − randn | sustained | − randn |
|---|---|---|---|---|---|
| fp32 gpt2_l3_mlp_down | no exact zeros | 702.0 | -1.9 | – | – |
| fp32 gpt2_l9_attn_qk | no exact zeros | 695.2 | -8.7 | – | – |
| fp32 bert_l6_up | no exact zeros | 702.0 | -1.9 | 601.5 | -0.3 |
| fp32 vit_l5_down | no exact zeros | 703.0 | -0.9 | – | – |
| fp32 t5small_l0_up | bf16-grid weights | 725.2 | 21.3 | 603.1 | 1.3 |
| fp32 vit_l11_down | -0.0 | 740.2 | 36.3 | 615.6 | 13.8 |
| fp16 gpt2_l9_attn_qk | no exact zeros | 732.6 | 9.9 | – | – |
| fp16 bert_l6_up | no exact zeros | 731.2 | 8.5 | – | – |
| fp16 vit_l5_down | no exact zeros | 734.9 | 12.2 | 612.0 | 3.2 |
| fp16 gpt2_l6_mlp_down_fp16fwd | fp16 forward | 708.2 | -14.5 | – | – |
| S3 mean, fp32 | | 700.5 | -3.4 | | |
| S3 mean, fp16 | | 732.9 | 10.2 | | |

### Like with like: switching above zeros as a share of the same-session reference (measured c, bursts)

| tile | reference | measured share | (a) over E78's measured reference | gate law over it | c W measured | c W (a) |
|---|---|---|---|---|---|---|
| fp32 resnet18_l2c1 | fp32/randn | 0.8058 | 0.7952 | 0.8141 | 20.907 | 20.742 |
| fp32 resnet18_l3c1 | fp32/randn | 0.5714 | 0.5522 | 0.5676 | 15.292 | 14.842 |
| fp32 vgg16_fc2 | fp32/randn | 0.3149 | 0.2841 | 0.2982 | 9.149 | 8.335 |
| fp32 t5small_l0_down | fp32/randn | 0.0662 | 0.0476 | 0.0781 | 3.191 | 2.596 |
| fp32 gpt2_l3_mlp_down | fp32/randn | 0.9973 | 0.9856 | – | 25.495 | 25.363 |
| fp32 gpt2_l9_attn_qk | fp32/randn | 0.9802 | 0.9903 | – | 25.085 | 25.476 |
| fp32 bert_l6_up | fp32/randn | 0.9948 | 0.9869 | – | 25.436 | 25.394 |
| fp32 vit_l5_down | fp32/randn | 1.0001 | 0.9871 | – | 25.563 | 25.4 |
| fp32 t5small_l0_up | fp32/randn | 0.8887 | 0.9082 | – | 22.895 | 23.485 |
| fp32 vit_l11_down | fp32/randn | 0.8265 | 0.8260 | – | 21.404 | 21.489 |
| fp16 resnet18_l3c1 | fp16/randn | 0.6336 | 0.5952 | 0.6448 | 15.153 | 14.342 |
| fp16 vgg16_fc2 | fp16/randn | 0.4627 | 0.3984 | 0.4672 | 11.462 | 10.061 |
| fp16 t5small_l0_down | fp16/randn | 0.1633 | 0.1064 | 0.1571 | 4.993 | 3.71 |
| fp16 gpt2_l9_attn_qk | fp16/randn | 0.9561 | 0.9705 | – | 22.120 | 22.508 |
| fp16 bert_l6_up | fp16/randn | 0.9948 | 0.9705 | – | 22.956 | 22.508 |
| fp16 vit_l5_down | fp16/randn | 0.9841 | 0.9762 | – | 22.725 | 22.634 |
| fp16 gpt2_l6_mlp_down_fp16fwd | fp16/randn | 0.9943 | 0.9590 | – | 22.946 | 22.258 |
| int8 resnet18_l3c1 | int8/full | 0.6164 | 0.5124 | 0.8342 | 6.321 | 5.673 |
| int8 vgg16_fc2 | int8/full | 0.4644 | 0.3833 | 0.6831 | 5.306 | 4.778 |
| int8 gpt2_l6_down_per_token | int8/full | 0.8324 | 0.7587 | – | 7.764 | 7.379 |
| int8 gpt2_l6_down_p9999 | int8/full | 0.7004 | 0.7403 | – | 6.882 | 7.251 |
| int8 gpt2_l6_down_p999 | int8/full | 0.8209 | 0.7691 | – | 7.687 | 7.451 |
| int8 gpt2_l11_down_maxabs | int8/full | 0.3360 | 0.1644 | 0.3995 | 4.449 | 3.262 |
| int8 gpt2_l11_down_p999 | int8/full | 0.6941 | 0.7304 | – | 6.840 | 7.183 |
| int8 vgg16_fc2_asym | int8/full | 0.6673 | 0.5812 | – | 6.661 | 6.149 |

### The int8 arm, by round: sustained MHz, board W, die °C, limit

| round | int8 full | int8 l0_mlp_up | int8 l6_mlp_down | int8 l6_attn_qk | mean(real) − full, MHz |
|---|---|---|---|---|---|
| 1 | 791.6 / 52.66 / 64.7 / none | 800.0 / 51.94 / 64.4 / none | 800.0 / 49.90 / 62.8 / none | 793.9 / 49.59 / 63.5 / none | 6.4 |
| 2 | 793.4 / 53.19 / 64.9 / none | 789.7 / 51.51 / 64.9 / none | 800.0 / 50.87 / 64.5 / none | 800.0 / 50.39 / 64.2 / none | 3.2 |
| 3 | 777.2 / 51.65 / 65.0 / thermal | 789.3 / 51.30 / 64.6 / none | 789.7 / 49.77 / 64.1 / none | 789.2 / 48.59 / 62.7 / none | 12.2 |
| 4 | 795.4 / 53.32 / 64.9 / none | 794.4 / 51.57 / 64.5 / none | 800.0 / 50.41 / 63.8 / none | 800.0 / 50.41 / 64.3 / none | 2.7 |

- **E96-I1**: SAME_WITHIN_BAR; mean 6.117, 95% [-0.832, 13.065], n 4, at the cap False
- **E96-I2**: BELOW; mean -2.184, 95% [-2.686, -1.682], n 4
- **E96-I3**: BELOW; mean -0.85, 95% [-1.472, -0.228], n 4
- labelled, int8 l0_mlp_up − full: mean 3.95 MHz, 95% [-8.0, 15.9], reads INCONCLUSIVE
- labelled, int8 l6_mlp_down − full: mean 8.025 MHz, 95% [2.675, 13.375], reads DIFFERENT_SMALL
- labelled, int8 l6_attn_qk − full: mean 6.375 MHz, 95% [-0.214, 12.964], reads SAME_WITHIN_BAR
- labelled, clock with dips left out: mean 6.617 MHz, 95% [-0.397, 13.631], reads SAME_WITHIN_BAR
- labelled, fine W at 800 MHz: mean -2.125 W, 95% [-2.8, -1.45], reads BELOW
- labelled, clock, pooled two-way: mean 6.117 MHz, 95% [1.232, 11.001], reads DIFFERENT_SMALL (9 df, residual sd 3.74)
- labelled, one run's sd in this arm, pooled over the kinds: 6.07 MHz; per kind {'int8/full': 8.28, 'int8/l0_mlp_up': 5.0, 'int8/l6_mlp_down': 5.15, 'int8/l6_attn_qk': 5.24}

### The heat path

- die line, all sustained runs: die = 41.408 + 0.4539 W, rms 0.589 °C, n 34, shift at E80's slope 0.12 °C (E87's: 0.515)
- E98's line, die − 0.4573 W, over ['fp16/zeros', 'int8/zeros', 'int8/full', 'fp32/randn']: 41.16 °C (E87's 41.665, difference -0.505); over all runs 41.237; trend 0.01103 °C/min
- a-adj E96: W* 49.502 W, sustained rms on the frozen c 13.56, on the measured c 9.75 MHz
- rest, smoke_last_60s: {"n": 600, "t_first_ms": 1793527516676, "t_last_ms": 1793527576674, "die": 47, "w": 22.146, "mhz": 600, "config": {"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": 600, "minion_mv": 519}, "w_first_half": 22.161, "w_second_half": 22.131}
- rest, history_before_first_session_launch: {"rows": 0, "w": null, "die_raw": null, "nic": null, "nvme": null, "since_busy_min": 0.1, "t_end_ms": 1793527599635}
- rest, first_launch: {"rows": 204, "w": 22.145, "die_raw": 46.79, "nic": 44.45, "nvme": 37.6, "since_busy_min": 27.0, "t_end_ms": 1793527500058}
- rest, p2: {"rows": 240, "w": 22.066, "die_raw": 46.67, "nic": 44.43, "nvme": 37.61, "since_busy_min": 36.2, "t_end_ms": 1793525400054}
- rest, p3: {"rows": 177, "w": 21.897, "die_raw": 46.09, "nic": 43.92, "nvme": 36.9, "since_busy_min": 24.7, "t_end_ms": 1793533200051}
