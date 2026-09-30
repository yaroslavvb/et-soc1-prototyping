"""sheet.py RUN.json CASTDIR OUTPREFIX [cols] [n]: a contact sheet of each camera move's frames (n evenly spaced), cropped to the svg."""
import json, sys, os, glob
from PIL import Image, ImageDraw
R = json.load(open(sys.argv[1])); cast = sys.argv[2]; outp = sys.argv[3]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 4; N = int(sys.argv[5]) if len(sys.argv) > 5 else 12
frames = sorted((float(os.path.basename(f).split('_')[1][:-4]), f) for f in glob.glob(cast + '/*.jpg'))
W = R['wall']; sx, sy, sw, sh = R['svg']
moves = []
for i, (t, key) in enumerate(W):
    step, z = key.rsplit('|', 1)
    if z == 'true':
        t1 = W[i + 1][0] if i + 1 < len(W) else t + 3
        moves.append((step, t - 0.05, t1 + 0.1))
for mi, (step, t0, t1) in enumerate(moves):
    fs = [f for t, f in frames if t0 <= t <= t1]
    if not fs: continue
    pick = [fs[round(k * (len(fs) - 1) / (N - 1))] for k in range(N)] if len(fs) >= N else fs
    ims = [Image.open(f).crop((int(sx), int(sy), int(sx + sw), int(sy + sh))) for f in pick]
    w, h = ims[0].size; sc = 0.5; tw, th = int(w * sc), int(h * sc)
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * tw, rows * (th + 18)), 'white'); d = ImageDraw.Draw(S)
    for k, im in enumerate(ims):
        x, y = (k % cols) * tw, (k // cols) * (th + 18)
        S.paste(im.resize((tw, th)), (x, y + 18)); d.text((x + 4, y + 3), f"{k}", fill='black')
    fn = f"{outp}-{mi}-{step.split(':')[0].replace(' ', '')}.png"; S.save(fn); print(fn, len(fs), 'frames')
