#!/usr/bin/env python3
"""Scratch: why ViT layer 11's GELU output is -0.0: the pre-activations, and where torch's GELU underflows on this build."""
import os, sys
import numpy as np, torch
import torch.nn.functional as F
from transformers import ViTForImageClassification
sys.argv[1:]
DL = sys.argv[1]
x = torch.tensor([-1., -3., -5., -6., -8., -9., -10., -11., -12., -13., -14., -15., -20., -40.], dtype=torch.float32)
y = F.gelu(x)
print("x", x.tolist())
print("gelu", y.tolist())
print("signbit-zero", [bool(v == 0 and np.signbit(v.item())) for v in y])
xx = torch.linspace(-20, 0, 2001, dtype=torch.float32)
yy = F.gelu(xx)
z = (yy == 0)
print("largest x with gelu(x) == 0:", float(xx[z].max()) if z.any() else None)
m = ViTForImageClassification.from_pretrained(os.path.join(DL, "vit-b16"), local_files_only=True, attn_implementation="eager").eval()
from PIL import Image
from torchvision import transforms as T
import json, random
man = json.load(open(os.path.join(DL, "images", "manifest-images.json")))
ids = sorted(man["images"].keys()); random.Random("Q132(r)/images").shuffle(ids)
tf = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])])
b = torch.stack([tf(Image.open(os.path.join(DL, "images", i + ".jpg")).convert("RGB")) for i in ids[:8]])
g = {}
for L in (5, 11):
    m.vit.encoder.layer[L].intermediate.dense.register_forward_hook(lambda mod, inp, out, L=L: g.__setitem__(L, out.detach().clone()))
with torch.no_grad():
    m(b)
for L, u in g.items():
    u = u.numpy().ravel()
    print(f"layer {L} pre-GELU: min {u.min():.2f} max {u.max():.2f} p1 {np.quantile(u, 0.01):.2f} p10 {np.quantile(u, 0.1):.2f} median {np.median(u):.2f} p90 {np.quantile(u, 0.9):.2f} share<-5 {np.mean(u < -5):.4f} share<-10 {np.mean(u < -10):.4f} share<-13 {np.mean(u < -13):.4f}")
    a = F.gelu(torch.tensor(u)).numpy()
    print(f"   gelu output: -0.0 share {np.mean((a == 0) & np.signbit(a)):.4f}, max {a.max():.3f}")
print("torch", torch.__version__, torch.backends.cpu.get_cpu_capability() if hasattr(torch.backends, "cpu") else "")
