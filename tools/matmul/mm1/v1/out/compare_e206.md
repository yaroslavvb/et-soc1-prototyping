| group | quantity | MM1-v0 blind | MM1-v1 in sample | MM1-v1 held out (E206 fold) |
|---|---|---|---|---|
| all | cycles an op, wall (the slowest minion) | 9.0% (-2.5%), n = 119 | 4.46% (-0.7%), n = 119 | 6.47% (+0.3%), n = 119 |
| all | cycles an op, the counter's mean | 9.54% (-2.8%), n = 119 | 4.63% (-1.6%), n = 119 | 7.87% (+0.0%), n = 119 |
| all | cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample) | - | - | 6.37% (-0.7%), n = 119 |
| all | seconds a GEMM | 9.02% (-2.6%), n = 119 | 4.48% (-0.8%), n = 119 | 6.48% (+0.2%), n = 119 |
| all | W over idle, given the measured seconds | 8.42% (-5.6%), n = 101 | 5.74% (-1.9%), n = 107 | 7.02% (-3.5%), n = 101 |
| all | J over idle, given the measured seconds | 8.42% (-5.6%), n = 101 | 5.74% (-1.9%), n = 107 | 7.02% (-3.5%), n = 101 |
| all | J over idle, seconds forecast | 9.15% (-6.0%), n = 101 | 6.1% (-2.1%), n = 107 | 7.57% (-3.7%), n = 101 |
| all | J at rest, given the measured seconds (measured rest) | 2.55% (-1.7%), n = 109 | 1.89% (-0.7%), n = 115 | 2.33% (-1.2%), n = 109 |
| all | J at rest, seconds forecast (measured rest) | 7.6% (-3.4%), n = 109 | 4.26% (-1.3%), n = 115 | 6.25% (-0.8%), n = 109 |
| full chip, random | cycles an op, wall (the slowest minion) | 7.88% (-1.9%), n = 81 | 4.28% (-0.8%), n = 81 | 4.89% (-1.3%), n = 81 |
| full chip, random | cycles an op, the counter's mean | 7.84% (-2.7%), n = 81 | 4.35% (-1.5%), n = 81 | 5.08% (-2.1%), n = 81 |
| full chip, random | cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample) | - | - | 5.08% (-2.1%), n = 81 |
| full chip, random | seconds a GEMM | 7.91% (-2.0%), n = 81 | 4.29% (-0.8%), n = 81 | 4.9% (-1.4%), n = 81 |
| full chip, random | W over idle, given the measured seconds | 7.17% (-5.2%), n = 81 | 4.78% (-2.0%), n = 81 | 6.34% (-3.7%), n = 81 |
| full chip, random | J over idle, given the measured seconds | 7.17% (-5.2%), n = 81 | 4.78% (-2.0%), n = 81 | 6.34% (-3.7%), n = 81 |
| full chip, random | J over idle, seconds forecast | 7.64% (-5.5%), n = 81 | 5.1% (-2.2%), n = 81 | 6.78% (-4.0%), n = 81 |
| full chip, random | J at rest, given the measured seconds (measured rest) | 2.79% (-2.0%), n = 81 | 2.06% (-0.9%), n = 81 | 2.6% (-1.5%), n = 81 |
| full chip, random | J at rest, seconds forecast (measured rest) | 6.78% (-3.4%), n = 81 | 4.18% (-1.5%), n = 81 | 5.19% (-2.5%), n = 81 |
| subsets | cycles an op, wall (the slowest minion) | 10.95% (-0.5%), n = 14 | 5.67% (+0.8%), n = 14 | 12.33% (+10.7%), n = 14 |
| subsets | cycles an op, the counter's mean | 14.35% (+2.8%), n = 14 | 6.11% (-1.1%), n = 14 | 17.48% (+14.2%), n = 14 |
| subsets | cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample) | - | - | 11.14% (+8.6%), n = 14 |
| subsets | seconds a GEMM | 10.97% (-0.5%), n = 14 | 5.68% (+0.8%), n = 14 | 12.32% (+10.6%), n = 14 |
| subsets | W over idle, given the measured seconds | 6.97% (-0.9%), n = 6 | 5.96% (+4.1%), n = 6 | 5.95% (+3.6%), n = 6 |
| subsets | J over idle, given the measured seconds | 6.97% (-0.9%), n = 6 | 5.96% (+4.1%), n = 6 | 5.95% (+3.6%), n = 6 |
| subsets | J over idle, seconds forecast | 5.98% (-0.9%), n = 6 | 5.92% (+4.7%), n = 6 | 6.54% (+5.3%), n = 6 |
| subsets | J at rest, given the measured seconds (measured rest) | 1.19% (-0.6%), n = 14 | 0.77% (+0.4%), n = 14 | 0.77% (+0.3%), n = 14 |
| subsets | J at rest, seconds forecast (measured rest) | 9.48% (-1.3%), n = 14 | 4.85% (+0.8%), n = 14 | 10.88% (+9.8%), n = 14 |
| zeros | cycles an op, wall (the slowest minion) | 9.2% (-3.8%), n = 14 | 3.48% (-0.9%), n = 14 | 5.04% (-0.6%), n = 14 |
| zeros | cycles an op, the counter's mean | 9.21% (-4.6%), n = 14 | 3.96% (-1.8%), n = 14 | 5.47% (-1.5%), n = 14 |
| zeros | cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample) | - | - | 5.47% (-1.5%), n = 14 |
| zeros | seconds a GEMM | 9.22% (-3.9%), n = 14 | 3.5% (-1.0%), n = 14 | 5.04% (-0.7%), n = 14 |
| zeros | W over idle, given the measured seconds | 13.89% (-9.8%), n = 14 | 9.55% (-4.8%), n = 14 | 10.36% (-5.7%), n = 14 |
| zeros | J over idle, given the measured seconds | 13.89% (-9.8%), n = 14 | 9.55% (-4.8%), n = 14 | 10.36% (-5.7%), n = 14 |
| zeros | J over idle, seconds forecast | 15.87% (-11.1%), n = 14 | 10.3% (-5.2%), n = 14 | 11.35% (-6.1%), n = 14 |
| zeros | J at rest, given the measured seconds (measured rest) | 2.06% (-1.4%), n = 14 | 1.44% (-0.7%), n = 14 | 1.56% (-0.9%), n = 14 |
| zeros | J at rest, seconds forecast (measured rest) | 9.64% (-4.9%), n = 14 | 4.11% (-1.6%), n = 14 | 5.45% (-1.5%), n = 14 |
| real (kind term, scored only) | cycles an op, wall (the slowest minion) | 12.06% (-7.2%), n = 6 | 4.72% (-1.9%), n = 6 | 6.91% (-0.6%), n = 6 |
| real (kind term, scored only) | cycles an op, the counter's mean | 12.17% (-7.8%), n = 6 | 4.87% (-2.6%), n = 6 | 7.08% (-1.3%), n = 6 |
| real (kind term, scored only) | cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample) | - | - | 7.08% (-1.3%), n = 6 |
| real (kind term, scored only) | seconds a GEMM | 12.1% (-7.2%), n = 6 | 4.75% (-2.0%), n = 6 | 6.92% (-0.7%), n = 6 |
| real (kind term, scored only) | W over idle, given the measured seconds | - | 5.62% (+0.3%), n = 6 | - |
| real (kind term, scored only) | J over idle, given the measured seconds | - | 5.62% (+0.3%), n = 6 | - |
| real (kind term, scored only) | J over idle, seconds forecast | - | 5.55% (-0.1%), n = 6 | - |
| real (kind term, scored only) | J at rest, given the measured seconds (measured rest) | - | 2.25% (-0.3%), n = 6 | - |
| real (kind term, scored only) | J at rest, seconds forecast (measured rest) | - | 4.23% (-1.9%), n = 6 | - |
| int8 gemmL KB <= 2 | cycles an op, wall (the slowest minion) | 19.11% (-17.1%), n = 13 | 6.9% (-4.1%), n = 13 | 10.95% (+0.5%), n = 13 |
| int8 gemmL KB <= 2 | cycles an op, the counter's mean | 19.19% (-17.2%), n = 13 | 7.02% (-4.7%), n = 13 | 10.77% (+0.4%), n = 13 |
| int8 gemmL KB <= 2 | cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample) | - | - | 10.32% (-0.2%), n = 13 |
| int8 gemmL KB <= 2 | seconds a GEMM | 19.17% (-17.2%), n = 13 | 6.94% (-4.1%), n = 13 | 10.94% (+0.5%), n = 13 |
| int8 gemmL KB <= 2 | W over idle, given the measured seconds | 10.8% (-7.3%), n = 8 | 7.73% (-1.8%), n = 10 | 9.8% (-6.1%), n = 8 |
| int8 gemmL KB <= 2 | J over idle, given the measured seconds | 10.8% (-7.3%), n = 8 | 7.73% (-1.8%), n = 10 | 9.8% (-6.1%), n = 8 |
| int8 gemmL KB <= 2 | J over idle, seconds forecast | 12.61% (-9.8%), n = 8 | 8.45% (-2.6%), n = 10 | 10.95% (-6.2%), n = 8 |
| int8 gemmL KB <= 2 | J at rest, given the measured seconds (measured rest) | 2.73% (-1.9%), n = 9 | 2.01% (-0.5%), n = 11 | 2.46% (-1.6%), n = 9 |
| int8 gemmL KB <= 2 | J at rest, seconds forecast (measured rest) | 17.06% (-15.5%), n = 9 | 6.55% (-3.5%), n = 11 | 10.39% (-0.6%), n = 9 |
| stride pair 1x15x4 / 1x16x4 | cycles an op, wall (the slowest minion) | 12.92% (+5.2%), n = 4 | 3.37% (+0.6%), n = 4 | 3.23% (+0.6%), n = 4 |
| stride pair 1x15x4 / 1x16x4 | cycles an op, the counter's mean | 13.08% (+5.3%), n = 4 | 3.5% (+0.7%), n = 4 | 3.36% (+0.6%), n = 4 |
| stride pair 1x15x4 / 1x16x4 | cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample) | - | - | 3.36% (+0.6%), n = 4 |
| stride pair 1x15x4 / 1x16x4 | seconds a GEMM | 12.88% (+5.1%), n = 4 | 3.37% (+0.5%), n = 4 | 3.23% (+0.5%), n = 4 |
| stride pair 1x15x4 / 1x16x4 | W over idle, given the measured seconds | 4.54% (-3.8%), n = 4 | 1.26% (-0.7%), n = 4 | 2.59% (-2.4%), n = 4 |
| stride pair 1x15x4 / 1x16x4 | J over idle, given the measured seconds | 4.54% (-3.8%), n = 4 | 1.26% (-0.7%), n = 4 | 2.59% (-2.4%), n = 4 |
| stride pair 1x15x4 / 1x16x4 | J over idle, seconds forecast | 4.95% (-3.3%), n = 4 | 1.65% (-0.8%), n = 4 | 2.76% (-2.5%), n = 4 |
| stride pair 1x15x4 / 1x16x4 | J at rest, given the measured seconds (measured rest) | 1.32% (-1.2%), n = 4 | 0.34% (-0.2%), n = 4 | 0.79% (-0.8%), n = 4 |
| stride pair 1x15x4 / 1x16x4 | J at rest, seconds forecast (measured rest) | 8.82% (+2.1%), n = 4 | 2.47% (+0.0%), n = 4 | 2.26% (-0.6%), n = 4 |
| law arms | cycles an op, wall (the slowest minion) | 4.35% (+1.8%), n = 11 | 3.83% (+1.9%), n = 11 | 4.05% (+1.6%), n = 11 |
| law arms | cycles an op, the counter's mean | 4.33% (+1.5%), n = 11 | 3.78% (+1.7%), n = 11 | 4.03% (+1.4%), n = 11 |
| law arms | cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample) | - | - | 4.03% (+1.4%), n = 11 |
| law arms | seconds a GEMM | 4.31% (+1.7%), n = 11 | 3.78% (+1.8%), n = 11 | 4.01% (+1.5%), n = 11 |
| law arms | W over idle, given the measured seconds | 7.12% (-2.6%), n = 11 | 5.86% (-1.9%), n = 11 | 6.98% (-2.5%), n = 11 |
| law arms | J over idle, given the measured seconds | 7.12% (-2.6%), n = 11 | 5.86% (-1.9%), n = 11 | 6.98% (-2.5%), n = 11 |
| law arms | J over idle, seconds forecast | 7.52% (-2.3%), n = 11 | 6.24% (-1.6%), n = 11 | 7.4% (-2.2%), n = 11 |
| law arms | J at rest, given the measured seconds (measured rest) | 3.13% (-1.4%), n = 11 | 2.65% (-1.1%), n = 11 | 3.1% (-1.4%), n = 11 |
| law arms | J at rest, seconds forecast (measured rest) | 5.06% (-0.1%), n = 11 | 4.06% (+0.2%), n = 11 | 4.84% (-0.2%), n = 11 |
| fp32 | cycles an op, wall (the slowest minion) | 6.9% (-0.3%), n = 53 | 4.15% (+0.4%), n = 53 | 5.95% (+0.9%), n = 53 |
| fp32 | cycles an op, the counter's mean | 7.68% (-0.7%), n = 53 | 4.25% (-0.7%), n = 53 | 7.73% (+0.6%), n = 53 |
| fp32 | cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample) | - | - | 5.89% (-0.2%), n = 53 |
| fp32 | seconds a GEMM | 6.91% (-0.4%), n = 53 | 4.14% (+0.3%), n = 53 | 5.93% (+0.8%), n = 53 |
| fp32 | W over idle, given the measured seconds | 8.11% (-4.8%), n = 46 | 6.3% (-2.0%), n = 48 | 7.21% (-3.0%), n = 46 |
| fp32 | J over idle, given the measured seconds | 8.11% (-4.8%), n = 46 | 6.3% (-2.0%), n = 48 | 7.21% (-3.0%), n = 46 |
| fp32 | J over idle, seconds forecast | 8.64% (-4.9%), n = 46 | 6.65% (-2.0%), n = 48 | 7.72% (-3.1%), n = 46 |
| fp32 | J at rest, given the measured seconds (measured rest) | 2.73% (-1.7%), n = 49 | 2.15% (-0.8%), n = 51 | 2.6% (-1.2%), n = 49 |
| fp32 | J at rest, seconds forecast (measured rest) | 5.71% (-1.8%), n = 49 | 4.09% (-0.6%), n = 51 | 5.97% (-0.3%), n = 49 |
| fp16 | cycles an op, wall (the slowest minion) | 5.43% (-0.6%), n = 21 | 3.41% (-0.8%), n = 21 | 3.79% (-1.4%), n = 21 |
| fp16 | cycles an op, the counter's mean | 5.45% (-1.6%), n = 21 | 3.84% (-1.8%), n = 21 | 4.4% (-2.4%), n = 21 |
| fp16 | cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample) | - | - | 4.4% (-2.4%), n = 21 |
| fp16 | seconds a GEMM | 5.46% (-0.7%), n = 21 | 3.4% (-0.8%), n = 21 | 3.8% (-1.5%), n = 21 |
| fp16 | W over idle, given the measured seconds | 8.07% (-5.0%), n = 19 | 5.67% (-2.6%), n = 21 | 6.73% (-3.5%), n = 19 |
| fp16 | J over idle, given the measured seconds | 8.07% (-5.0%), n = 19 | 5.67% (-2.6%), n = 21 | 6.73% (-3.5%), n = 19 |
| fp16 | J over idle, seconds forecast | 8.44% (-5.2%), n = 19 | 5.9% (-2.8%), n = 21 | 7.12% (-3.8%), n = 19 |
| fp16 | J at rest, given the measured seconds (measured rest) | 2.79% (-1.8%), n = 19 | 2.23% (-1.0%), n = 21 | 2.62% (-1.3%), n = 19 |
| fp16 | J at rest, seconds forecast (measured rest) | 5.26% (-2.5%), n = 19 | 3.53% (-1.6%), n = 21 | 4.42% (-2.3%), n = 19 |
| int8 | cycles an op, wall (the slowest minion) | 12.0% (-6.0%), n = 45 | 5.19% (-2.0%), n = 45 | 7.9% (+0.3%), n = 45 |
| int8 | cycles an op, the counter's mean | 12.54% (-5.8%), n = 45 | 5.35% (-2.6%), n = 45 | 9.19% (+0.5%), n = 45 |
| int8 | cycles an op, the counter's mean, row-group imbalance fitted on 4 of E206's points (in sample) | - | - | 7.58% (-0.4%), n = 45 |
| int8 | seconds a GEMM | 12.04% (-6.0%), n = 45 | 5.23% (-2.1%), n = 45 | 7.93% (+0.2%), n = 45 |
| int8 | W over idle, given the measured seconds | 8.96% (-6.9%), n = 36 | 4.99% (-1.5%), n = 38 | 6.91% (-4.2%), n = 36 |
| int8 | J over idle, given the measured seconds | 8.96% (-6.9%), n = 36 | 4.99% (-1.5%), n = 38 | 6.91% (-4.2%), n = 36 |
| int8 | J over idle, seconds forecast | 10.1% (-7.8%), n = 36 | 5.46% (-1.9%), n = 38 | 7.61% (-4.5%), n = 36 |
| int8 | J at rest, given the measured seconds (measured rest) | 2.19% (-1.7%), n = 41 | 1.27% (-0.4%), n = 43 | 1.77% (-1.0%), n = 41 |
| int8 | J at rest, seconds forecast (measured rest) | 10.08% (-5.6%), n = 41 | 4.76% (-1.9%), n = 43 | 7.22% (-0.6%), n = 41 |
