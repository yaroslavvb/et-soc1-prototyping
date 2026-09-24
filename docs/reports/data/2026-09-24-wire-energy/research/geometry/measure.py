"""Measure the ET-SoC-1 die plot: cyan frame (die edge), and the blue shire-outline grid lines."""
import sys
import numpy as np
from PIL import Image

def runs(idx):
    """Group consecutive indices into (start, end) runs."""
    out = []
    for i in idx:
        if out and i - out[-1][1] <= 2:
            out[-1][1] = i
        else:
            out.append([i, i])
    return [tuple(r) for r in out]

def measure(path, ymax=None, thr_frac=0.5):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    if ymax: a = a[:ymax]
    H, W, _ = a.shape
    cyan = (a[:, :, 0] > 60) & (a[:, :, 0] < 200) & (a[:, :, 1] > 200) & (a[:, :, 2] > 150)
    blue = (a[:, :, 0] < 100) & (a[:, :, 1] > 120) & (a[:, :, 1] < 210) & (a[:, :, 2] > 200)
    def first_run_end(line):
        end = None
        for i, v in enumerate(line):
            if v: end = i
            elif end is not None and i - end > 3: break
        return end
    # die edge = inner edge of cyan frame, sampled on many lines; take the median
    L = [first_run_end(cyan[y]) for y in range(H // 10, 9 * H // 10, 10)]
    R = [W - 1 - e for e in (first_run_end(cyan[y][::-1]) for y in range(H // 10, 9 * H // 10, 10)) if e is not None]
    T = [first_run_end(cyan[:, x]) for x in range(W // 10, 9 * W // 10, 10)]
    B = [H - 1 - e for e in (first_run_end(cyan[:, x][::-1]) for x in range(W // 10, 9 * W // 10, 10)) if e is not None]
    med = lambda v: float(np.median([x for x in v if x is not None]))
    edges = dict(left=med(L) + 1, right=med(R) - 1, top=med(T) + 1, bottom=med(B) - 1)
    # grid lines: columns/rows where the blue outline mask covers a large part of the line
    cs, rs = blue.sum(0), blue.sum(1)
    vcols = runs([x for x in range(W) if cs[x] > thr_frac * H * 0.55])
    hrows = runs([y for y in range(H) if rs[y] > thr_frac * W * 0.55])
    return dict(size=(W, H), edges=edges, vlines=vcols, hlines=hrows,
                outer_cyan=dict(x=(int(np.where(cyan.any(0))[0].min()), int(np.where(cyan.any(0))[0].max())),
                                y=(int(np.where(cyan.any(1))[0].min()), int(np.where(cyan.any(1))[0].max()))))

if __name__ == '__main__':
    r = measure(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else None)
    for k, v in r.items(): print(k, v)
