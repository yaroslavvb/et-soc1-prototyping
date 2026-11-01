== A1: (a)'s ratios to random, paired per pass (D over the type's zeros, S over idle, p80 the whole board)
-- D
  fp32.real_l0_mlp_up      E112a 0.9955 ± 0.0047 (n 5)
  fp32.real_l6_mlp_down    E112a 0.9933 ± 0.0046 (n 5)
  fp32.real_l6_attn_qk     E112a 0.9827 ± 0.0028 (n 5)
  fp16.real_l0_mlp_up      E112a 0.9871 ± 0.0044 (n 5)
  fp16.real_l6_mlp_down    E112a 0.9930 ± 0.0037 (n 5)
  fp16.real_l6_attn_qk     E112a 0.9654 ± 0.0040 (n 5)
  int8.real_l0_mlp_up      E112a 0.9047 ± 0.0202 (n 5)
  int8.real_l6_mlp_down    E112a 0.8016 ± 0.0328 (n 5)
  int8.real_l6_attn_qk     E112a 0.7732 ± 0.0237 (n 5)
-- S
  fp32.real_l0_mlp_up      E112a 0.9962 ± 0.0068 (n 5)
  fp32.real_l6_mlp_down    E112a 0.9928 ± 0.0078 (n 5)
  fp32.real_l6_attn_qk     E112a 0.9826 ± 0.0055 (n 5)
  fp16.real_l0_mlp_up      E112a 0.9865 ± 0.0025 (n 5)
  fp16.real_l6_mlp_down    E112a 0.9929 ± 0.0069 (n 5)
  fp16.real_l6_attn_qk     E112a 0.9674 ± 0.0051 (n 5)
  int8.real_l0_mlp_up      E112a 0.9228 ± 0.0096 (n 5)
  int8.real_l6_mlp_down    E112a 0.8520 ± 0.0263 (n 5)
  int8.real_l6_attn_qk     E112a 0.8313 ± 0.0216 (n 5)
-- p80
  fp32.real_l0_mlp_up      E112a 0.9982 ± 0.0015 (n 5)
  fp32.real_l6_mlp_down    E112a 0.9969 ± 0.0016 (n 5)
  fp32.real_l6_attn_qk     E112a 0.9928 ± 0.0014 (n 5)
  fp16.real_l0_mlp_up      E112a 0.9951 ± 0.0016 (n 5)
  fp16.real_l6_mlp_down    E112a 0.9971 ± 0.0007 (n 5)
  fp16.real_l6_attn_qk     E112a 0.9866 ± 0.0013 (n 5)
  int8.real_l0_mlp_up      E112a 0.9845 ± 0.0030 (n 5)
  int8.real_l6_mlp_down    E112a 0.9680 ± 0.0037 (n 5)
  int8.real_l6_attn_qk     E112a 0.9642 ± 0.0033 (n 5)
-- three-tile means (per pass the mean over the three tiles, then over passes)
  D   fp32: E112a 0.9905 ± 0.0032 (n 5); E91 (3 kept) 0.9915 ± 0.0050 (n 3); E86 aifoundry3 0.9878 ± 0.0103 (n 4)
  D   fp16: E112a 0.9818 ± 0.0039 (n 5); E91 (3 kept) 0.9833 ± 0.0015 (n 3); E86 aifoundry3 0.9872 ± 0.0142 (n 4)
  D   int8: E112a 0.8265 ± 0.0206 (n 5); E91 (3 kept) 0.8418 ± 0.0437 (n 3); E86 aifoundry3 0.8269 ± 0.0501 (n 4)
  S   fp32: E112a 0.9906 ± 0.0057 (n 5); E91 (3 kept) 0.9918 ± 0.0094 (n 3); E86 aifoundry3 0.9902 ± 0.0090 (n 4)
  S   fp16: E112a 0.9823 ± 0.0036 (n 5); E91 (3 kept) 0.9809 ± 0.0047 (n 3); E86 aifoundry3 0.9875 ± 0.0107 (n 4)
  S   int8: E112a 0.8687 ± 0.0092 (n 5); E91 (3 kept) 0.8793 ± 0.0012 (n 3); E86 aifoundry3 0.8787 ± 0.0316 (n 4)
  p80 fp32: E112a 0.9959 ± 0.0012 (n 5); E91 (3 kept) 0.9964 ± 0.0019 (n 3); E86 aifoundry3 0.9945 ± 0.0040 (n 4)
  p80 fp16: E112a 0.9929 ± 0.0009 (n 5); E91 (3 kept) 0.9934 ± 0.0004 (n 3); E86 aifoundry3 0.9942 ± 0.0057 (n 4)
  p80 int8: E112a 0.9722 ± 0.0023 (n 5); E91 (3 kept) 0.9741 ± 0.0047 (n 3); E86 aifoundry3 0.9657 ± 0.0110 (n 4)
-- three-tile means of D / random at each leakage arm of (a) (the arms' own reductions)
  leak0.1994: fp32 0.9905 ± 0.0062 (n 5); fp16 0.9817 ± 0.0061 (n 5); int8 0.8352 ± 0.0194 (n 5)
  leak0.545: fp32 0.9904 ± 0.0018 (n 5); fp16 0.9819 ± 0.0027 (n 5); int8 0.8210 ± 0.0240 (n 5)
  leak0.3803: fp32 0.9905 ± 0.0036 (n 5); fp16 0.9818 ± 0.0042 (n 5); int8 0.8279 ± 0.0200 (n 5)
  leak0: fp32 0.9921 ± 0.0121 (n 4); fp16 0.9831 ± 0.0104 (n 4); int8 0.8448 ± 0.0331 (n 4)
-- idle level (W): E112a 33.009 | E91 32.986 | E86 25.873
-- leakage slope auto (W/C): E112a 0.4137 | E91 0.4219 | E86 0.229

== A2: pass times (s), from logs/e112-queue.log
  12:55:11 a:11210 starts at T0+78 s (projected 390 s, end by T0+468 s)
  13:00:39 a:11210 rc=0 (328 s)
  13:00:54 a:11211 starts at T0+421 s (projected 328 s, end by T0+749 s)
  13:06:14 a:11211 rc=0 (320 s)
  13:06:29 a:11212 starts at T0+756 s (projected 328 s, end by T0+1084 s)
  13:11:50 a:11212 rc=0 (321 s)
  13:12:05 a:11213 starts at T0+1092 s (projected 328 s, end by T0+1420 s)
  13:17:39 a:11213 rc=0 (334 s)
  13:17:54 b:11250 starts at T0+1441 s (projected 560 s, end by T0+2001 s)
  13:26:16 b:11250 rc=0 (502 s)
  13:26:31 b:11251 starts at T0+1958 s (projected 502 s, end by T0+2460 s)
  13:34:42 b:11251 rc=0 (491 s)
  13:34:57 b:11252 starts at T0+2464 s (projected 502 s, end by T0+2966 s)
  13:43:18 b:11252 rc=0 (501 s)
  13:43:33 a:11214 starts at T0+2980 s (projected 334 s, end by T0+3314 s)
  13:48:47 a:11214 rc=0 (314 s)
  13:49:02 budget: skipping b:11253 (now T0+3309 s, projected 502 s, ends T0+3811 s > T0+3480 s)

== B1: (b)'s per-tile ratio to random (D over zeros, per pass D/D(random), mean over passes) against E95 on aifoundry3
-- registered reduction, two kept passes (11250, 11251)
  fp32: 11 tiles; max |r(card 1) - r(aifoundry3)| 0.0089 (fp32.r2_t5small_l0_down); median |diff| 0.0018; mean diff +0.0008
  fp16: 10 tiles; max |r(card 1) - r(aifoundry3)| 0.0061 (fp16.real_l6_attn_qk); median |diff| 0.0033; mean diff -0.0028
  int8: 12 tiles; max |r(card 1) - r(aifoundry3)| 0.0156 (int8.r2_vgg16_fc2); median |diff| 0.0094; mean diff -0.0005
  B2 card scale: median D(aifoundry3, E95 dips removed) / D(card 1) over the 24 X4-eligible tiles 1.0448 (IQR 1.0422-1.0483)
-- POST HOC, three passes, the zeros-line limit raised to 0.26 W
  fp32: 11 tiles; max |r(card 1) - r(aifoundry3)| 0.0100 (fp32.r2_t5small_l0_down); median |diff| 0.0013; mean diff +0.0009
  fp16: 10 tiles; max |r(card 1) - r(aifoundry3)| 0.0057 (fp16.r2_vgg16_fc2); median |diff| 0.0014; mean diff -0.0010
  int8: 12 tiles; max |r(card 1) - r(aifoundry3)| 0.0233 (int8.r2_t5small_l0_down); median |diff| 0.0120; mean diff +0.0042
  B2 card scale: median D(aifoundry3, E95 dips removed) / D(card 1) over the 24 X4-eligible tiles 1.0432 (IQR 1.0399-1.0444)

== B3: the pass gates of (b) at every reduction
  e112b.json: kept [11250, 11251], leak 0.4172, set aside [{"pass": 11252, "why": ["fp32.zeros departs -0.253 W from its straight line"]}]
  e112b-dipskept.json: kept [], leak 0.4030, set aside [{"pass": 11250, "why": ["fp16.randn spans 1.283 W"]}, {"pass": 11251, "why": ["fp16.randn spans 1.611 W"]}, {"pass": 11252, "why": ["fp32.zeros departs -0.253 W from its straight line"]}]
  e112b-leak0.1994.json: kept [11250, 11251], leak 0.1994, set aside [{"pass": 11252, "why": ["fp32.zeros departs -0.253 W from its straight line"]}]
  e112b-leak0.545.json: kept [11250], leak 0.5450, set aside [{"pass": 11251, "why": ["int8.zeros departs -0.251 W from its straight line"]}, {"pass": 11252, "why": ["fp32.zeros departs -0.253 W from its straight line", "int8.zeros departs +0.311 W from its straight line"]}]
  e112b-leak0.3803.json: kept [11250, 11251], leak 0.3803, set aside [{"pass": 11252, "why": ["fp32.zeros departs -0.253 W from its straight line"]}]
  e112b-leak0.json: kept [11251], leak 0.0000, set aside [{"pass": 11250, "why": ["fp32.zeros departs +0.298 W from its straight line", "fp16.zeros departs -0.434 W from its straight line", "int8.zeros departs -0.283 W from its straight line"]}, {"pass": 11252, "why": ["fp32.zeros departs -0.253 W from its straight line"]}]
  posthoc-gate026/e112b-posthoc-gate026.json: kept [11250, 11251, 11252], leak 0.4172, set aside []
  (a), for comparison:
  e91.json: kept [11210, 11211, 11212, 11213, 11214], leak 0.4137, set aside []
  e91-dipskept.json: kept [11210, 11213], leak 0.3991, set aside [{"pass": 11211, "why": ["fp32.randn spans 1.737 W"]}, {"pass": 11212, "why": ["fp32.randn spans 1.811 W"]}, {"pass": 11214, "why": ["fp32.randn spans 2.064 W"]}]
  e91-leak0.1994.json: kept [11210, 11211, 11212, 11213, 11214], leak 0.1994, set aside []
  e91-leak0.545.json: kept [11210, 11211, 11212, 11213, 11214], leak 0.5450, set aside []
  e91-leak0.3803.json: kept [11210, 11211, 11212, 11213, 11214], leak 0.3803, set aside []
  e91-leak0.json: kept [11210, 11211, 11212, 11214], leak 0.0000, set aside [{"pass": 11213, "why": ["fp16.zeros departs -0.317 W from its straight line"]}]

== B4: the budget rule's arithmetic at the spare's decision (claim + 2,980 s)
  a:11214 projected 334 s: end claim + 3,314 s, limit claim + 3,480 s, margin 166 s
  had b:11253 stood in its place, projected 502 s: end claim + 3,482 s, past the limit by 2 s

== T: card time, claim post to release edit (logs/push-and-claim-times.txt)
  claim 12:53:53.736 PST (Discord's timestamp); release saved about 13:49:2x PST (the save returned 13:49:24): 55.5 card-minutes of 60
