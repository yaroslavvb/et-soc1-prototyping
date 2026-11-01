#!/usr/bin/env python3
"""Fetch the public model files for Q132(r) into <dl>/<slug>/, one directory per model, and write manifest.json.
Each large file is checked against the Hub's own LFS oid (or torchvision's hash prefix in the file name)."""
import hashlib, json, os, subprocess, sys, urllib.request

DL = sys.argv[1]
HF = {
    "gpt2": ("openai-community/gpt2", "607a30d783dfa663caf39e06633721c8d4cfcd7e",
             ["model.safetensors", "vocab.json", "merges.txt", "config.json"]),
    "t5-small": ("google-t5/t5-small", "df1b051c49625cf57a3d0d8d3863ed4d13564fe4",
                 ["model.safetensors", "config.json", "spiece.model", "tokenizer.json", "tokenizer_config.json"]),
    "distilbert": ("distilbert/distilbert-base-uncased", None,
                   ["model.safetensors", "config.json", "vocab.txt", "tokenizer.json", "tokenizer_config.json"]),
    "vit-b16": ("google/vit-base-patch16-224", None, ["model.safetensors", "config.json", "preprocessor_config.json"]),
    "bert": ("google-bert/bert-base-uncased", None,
             ["model.safetensors", "config.json", "vocab.txt", "tokenizer.json", "tokenizer_config.json"]),
}
TV = {"resnet18": "https://download.pytorch.org/models/resnet18-f37072fd.pth",
      "vgg16": "https://download.pytorch.org/models/vgg16-397923af.pth"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fetch(url, out):
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return
    subprocess.run(["curl", "-sS", "-L", "--fail", "--retry", "3", "--max-time", "1200", "-o", out + ".part", url], check=True)
    os.rename(out + ".part", out)


def api(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


man = {}
for slug, (repo, rev, files) in HF.items():
    os.makedirs(os.path.join(DL, slug), exist_ok=True)
    info = api(f"https://huggingface.co/api/models/{repo}")
    rev2 = rev or info["sha"]
    tree = {t["path"]: t for t in api(f"https://huggingface.co/api/models/{repo}/tree/{rev2}")}
    rec = {"hf_repo": repo, "revision": rev2, "licence": (info.get("cardData") or {}).get("license"),
           "lastModified": info.get("lastModified"), "files": {}}
    for fn in files:
        url = f"https://huggingface.co/{repo}/resolve/{rev2}/{fn}"
        out = os.path.join(DL, slug, fn)
        fetch(url, out)
        s = sha(out)
        t = tree.get(fn, {})
        oid = (t.get("lfs") or {}).get("oid")
        if oid and oid != s:
            sys.exit(f"refused: {slug}/{fn} sha256 {s} != LFS oid {oid}")
        rec["files"][fn] = {"url": url, "bytes": os.path.getsize(out), "sha256": s, "hub_lfs_oid": oid,
                            "git_blob": t.get("oid")}
        print(slug, fn, os.path.getsize(out), s[:16], "lfs-ok" if oid else "no-lfs", flush=True)
    man[slug] = rec
for slug, url in TV.items():
    os.makedirs(os.path.join(DL, slug), exist_ok=True)
    fn = url.rsplit("/", 1)[1]
    out = os.path.join(DL, slug, fn)
    fetch(url, out)
    s = sha(out)
    want = fn.rsplit("-", 1)[1].split(".")[0]
    if not s.startswith(want):
        sys.exit(f"refused: {fn} sha256 {s} does not start with {want}")
    man[slug] = {"source": "torchvision IMAGENET1K_V1", "url": url, "bytes": os.path.getsize(out), "sha256": s,
                 "file": fn, "licence": "BSD-3-Clause (torchvision)"}
    print(slug, fn, os.path.getsize(out), s[:16], "prefix-ok", flush=True)
json.dump(man, open(os.path.join(DL, "manifest-models.json"), "w"), indent=1)
print("DONE models")
