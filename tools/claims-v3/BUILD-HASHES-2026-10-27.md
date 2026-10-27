# The builds and operand sets E74, E75 and E76 were prepared on (aifoundry1, 27 Oct 2026)

Every number aifoundry3 produces for E74 (`tools/claims-v3/rf`), E75 (`tools/claims-v3/mf`) or E76
(`tools/claims-v3/tr`) is comparable to a number from another box only if the code that ran is the same code.
These are the hashes of what was built and generated on **aifoundry1** at 14:2x–14:3x PDT on Tue 27 Oct 2026,
where the three experiments were built and dry-run and **no card was opened**. Before the first measured pass,
run the same two commands on the box that will run them and compare:

    bash tools/claims-v3/text_hash.sh build/enercat-df/host/enercat_host build/enercat-hl/host/enercat_host \
         build/enercat-tr/host/enercat_host build/sparsity/host/sparsity_host
    for g in rf-gen mf-gen tr-gen; do ( cd build/$g && sha256sum manifest.json srcs/*.bin ); done

`file` is the whole binary, `text` its `.text` section, and `code` the sha256 of its disassembly — which is the
line to compare, because two boxes build their hosts against their own `/opt/et` and the files differ in paths
and build ids while the code that runs can be identical. A device kernel has no section called `.text` (crt.S
puts `_start` in `.text.init`), so it has a `code` line and no `text` line; an `--only-section=.text` of one
hashes the empty string, which would compare equal between two different kernels.

The operand sets are written by `make_rf.py` and `make_mf.py`, which are deterministic: those sha256s **must**
match exactly, on any box, or the ladders are not the same ladders. (The three line levels of E75 share one
element geometry, so `mf_l2_k0`, `mf_l3_k0` and `mf_dram_k0` are the same 256 bytes — as are the k256 and k512
rungs. That is correct: the levels differ in `--slice-bytes`, not in the image.)

## Binaries

```
file   host 49dd09933ce803f1c58a47e0e5715c8f9d78bee62844cbf6ba765fb9be060bf6 3663216 build/enercat-df/host/enercat_host
text   host f1078ff2139a79c6bc4fbd2f6a4c47016df414a2720e1208cba14e259d2f3f40 build/enercat-df/host/enercat_host
code   host 99cb7cbbaf71d20abec9f479a77215a70337f634682069b63ea3c2a3de1d968c build/enercat-df/host/enercat_host
file   kernel 17b4b249b4a51de0e18dcd387b53313e394d52af7f5e0eee69466de4f6bb5e28 85024 build/enercat-df/host/../kernel/enercat.elf
code   kernel 82923db2c27ff677e54200c94855126770599d503486de337a5e3e9ab8c71f3f build/enercat-df/host/../kernel/enercat.elf
file   host 697728a2434921806c63e58a5d9bf1abbfda43f0ba401a9bb01be883e14f6f1d 3662584 build/enercat-hl/host/enercat_host
text   host 8c13b1729d2b240bd75483c9bc652043c8148e6efb12f09acb717c764f2176a4 build/enercat-hl/host/enercat_host
code   host ef52ce047fd422011bd1d6d7711624f26f43f8daa4f33a53c69f61b91a746058 build/enercat-hl/host/enercat_host
file   kernel 7e7ce13f2753c246d2aed1e806ec692044f6c2763f6ffcdc843348e36c081af4 80280 build/enercat-hl/host/../kernel/enercat.elf
code   kernel a5743c3c5198edcb213f89047c38a4fe038ca3f719924ec456b5c73d200e6658 build/enercat-hl/host/../kernel/enercat.elf
file   host aafa0e3ac1c6eab09be8cdae13038466e524ee964b9e6ad623f9f9a440404ed1 3663632 build/enercat-tr/host/enercat_host
text   host f99cb6d7061b72f516500c2b90dbc1987bb9ba2a2aae48a07e961e699a31d4cb build/enercat-tr/host/enercat_host
code   host e5d4638f86e86afc735d2d943cc93f28df9d7ff9468b5b65cd5b4db2151388ac build/enercat-tr/host/enercat_host
file   kernel 455ce7feba169336a4cb906e673eb5609dd561acf46855e94dfd01c4e6cf14a6 89192 build/enercat-tr/host/../kernel/enercat.elf
code   kernel 0351795216bb5f3f5ab68c89ef9623b75fba66af053badaaa93eb2515ea19244 build/enercat-tr/host/../kernel/enercat.elf
file   host e0fbecce35f252c546e6e8390f6a4694519674dc4d6dea359b0db9c4d1a3fbbe 3652752 build/sparsity/host/sparsity_host
text   host b5f7a7b21038e1af08f312f70f0f80d5945751c3b94f0fed0e2639b194634006 build/sparsity/host/sparsity_host
code   host 2e55e96cc0768c1c4f1f0819b66c9b975227096a31d2ffeff3cbbcb2d6c61368 build/sparsity/host/sparsity_host
```

Which build each experiment uses: **E74** `build/enercat-df` (`-DENERCAT_DF=ON`, for `df.un1a.fnot` and
`df.un1b.fnot`); **E75** `build/enercat-hl` (any build with `--operands file:`, for `ld_l1` and `flw_pat`);
**E76** `build/enercat-tr` (`-DENERCAT_TR=ON`, built here for the first time on 27 Oct: all thirteen trapping
mnemonics assemble, and the kernel carries 64 of each). `build/sparsity` is the `anchor_pi` drift anchor and the
heater.

## Operand sets

```
rf-gen f7e09dc8482996f3839a714a25353fedd7d868d7fed0bbd2373987b3e9e9142f  manifest.json
rf-gen d64162dcb3ecb8ae9a904d3f9a1bc1943bc9e492d849e9ad83731a39e1bbe927  srcs/rf_k128.bin
rf-gen 13c096e8a86c07c875468c1c064056563ba54c2d979fee2d88c9d6bfcf79c8c2  srcs/rf_k160.bin
rf-gen 0089d40530407aaebf6bafbc12b9a96d2cb3980324cac72e57339c8f41363d0b  srcs/rf_k192.bin
rf-gen 2e242903a62d02454e8523cbc665040fd3c4b9c7592638020b2ba6616de34e34  srcs/rf_k32.bin
rf-gen f17b338c29a17e9fa76246fee008b7a439b273301ce102dc45a0a1d54c4d375d  srcs/rf_k64.bin
rf-gen eb439c2795ccad992d9561ad483a40462e8324311a9f91867d2ee1fbec24e392  srcs/rf_k96.bin
rf-gen 0089d40530407aaebf6bafbc12b9a96d2cb3980324cac72e57339c8f41363d0b  srcs/rfz_k192.bin
rf-gen 2e242903a62d02454e8523cbc665040fd3c4b9c7592638020b2ba6616de34e34  srcs/rfz_k32.bin
rf-gen eb439c2795ccad992d9561ad483a40462e8324311a9f91867d2ee1fbec24e392  srcs/rfz_k96.bin
mf-gen 56be14434d1d48432d7fe9813b623c2badb536a5b2029a23d0cccf4d33f28d29  manifest.json
mf-gen 2a38626552ade992a10ec2fb2eebfcc0017fbc9027f461101ece87f8f5cadcb4  srcs/mf_dram_k0.bin
mf-gen d2c572efec824c2e68947345484d206f0deca001bc713477bca44c6d5c05301d  srcs/mf_dram_k128.bin
mf-gen 5c4297caa2aefc44b8e8493b4d23684d76fb565806b3ce74ceb380398d664bb6  srcs/mf_dram_k256.bin
mf-gen 340682418b53a8ddf710e1b18fc81d161317905ab1e1b9fcfd7772c108c4fd9f  srcs/mf_dram_k384.bin
mf-gen 29bf91e396562f5e03579fe10e13bb742fa29a6deecae8a0aa8fbe2743a47cc9  srcs/mf_dram_k512.bin
mf-gen cac291adab59e85b7a99f9fcfabba6d823e2603a5c02e082fb99dced2ee5c438  srcs/mf_dram_w128.bin
mf-gen a7bf8fd6d1adf243418b2b4c4bd94e4911eed487ebb0552ff42e82bbacdf1f8a  srcs/mf_dram_w384.bin
mf-gen b8f1a74f5053067ac9a152195b5f2a62f8bee6d60d767c747c86e506ed2c6959  srcs/mf_l1_k0.bin
mf-gen 96fb825ade37e2ffb053cd3f47ed2401d7655de8cbb83fd3223c7222549233cb  srcs/mf_l1_k128.bin
mf-gen 2fd06e4d0daef36bbdd2fef62b1704ee61435b419ff50f081f37a508576dae02  srcs/mf_l1_k192.bin
mf-gen f77f1a361a172eecaecd078022837861561130b421e26d9d5f9ed61f2b950c28  srcs/mf_l1_k256.bin
mf-gen 60ba0404f353da8ca899a01e7203875c1b1536fd6cdfa7c53185c8ddcf3beb5f  srcs/mf_l1_k64.bin
mf-gen 1db43a485f6235a402cd7f30b13b93e41d5a8f324fc98593f0610e35304fdb79  srcs/mf_l1_w192.bin
mf-gen 6271a3b52ffee030520d951aff05894474242c6365e7c1c63f92618e807291b4  srcs/mf_l1_w64.bin
mf-gen 2a38626552ade992a10ec2fb2eebfcc0017fbc9027f461101ece87f8f5cadcb4  srcs/mf_l2_k0.bin
mf-gen 5c4297caa2aefc44b8e8493b4d23684d76fb565806b3ce74ceb380398d664bb6  srcs/mf_l2_k256.bin
mf-gen 29bf91e396562f5e03579fe10e13bb742fa29a6deecae8a0aa8fbe2743a47cc9  srcs/mf_l2_k512.bin
mf-gen 2a38626552ade992a10ec2fb2eebfcc0017fbc9027f461101ece87f8f5cadcb4  srcs/mf_l3_k0.bin
mf-gen 5c4297caa2aefc44b8e8493b4d23684d76fb565806b3ce74ceb380398d664bb6  srcs/mf_l3_k256.bin
mf-gen 29bf91e396562f5e03579fe10e13bb742fa29a6deecae8a0aa8fbe2743a47cc9  srcs/mf_l3_k512.bin
tr-gen 16a6d1a754ac696c788ba92b17ecd80075c9d9ef0bd3e5022ae508d9a0ae86ac  manifest.json
```

## The box this was prepared on

```
et_soc1      version=0.20.0 srcversion=47D26A305A0428B29FB7FC4
/opt/et/lib/libetrt.so        sha256 d2412f178ba5434c...
/opt/et/lib/libdeviceLayer.a  sha256 3bc495140db40b0a...
/opt/et/bin/dev_mngt_service  sha256 a3d4c722d9505aa9...
```

Heavy desk compute is aifoundry1's job in this campaign (another user's CPU work on a card host splits passes:
E67), so the builds and the generators ran there with `nice -n 19`, and the card lanes stay on aifoundry2 and
aifoundry3.
