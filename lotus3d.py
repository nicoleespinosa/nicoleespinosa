import math, functools
from ascii_art import ART

BEND = 0.45
RELIEF = 0.12
DIST = 3.5
WEIGHT = {'@': 1, '%': .9, '#': .85, '*': .7, '+': .6, '=': .5, '-': .35, ':': .3, '.': .15}

def _grid():
    rows = ART.split("\n")
    W = max(len(r) for r in rows); H = len(rows)
    g = [r.ljust(W) for r in rows]

    d = [[WEIGHT.get(g[r][c], 0) for c in range(W)] for r in range(H)]
    sm = [[0.0]*W for _ in range(H)]
    R = 1
    for r in range(H):
        for c in range(W):
            s = n = 0
            for dr in range(-R, R+1):
                for dc in range(-2*R, 2*R+1):
                    rr, cc = r+dr, c+dc
                    if 0 <= rr < H and 0 <= cc < W:
                        s += d[rr][cc]; n += 1
            sm[r][c] = s / n
    mx = max(max(x) for x in sm) or 1
    return g, [[v/mx for v in row] for row in sm], W, H

def frame(theta_deg):
    g, dens, W, H = _grid_cached()
    cx, cy = (W - 1) / 2, (H - 1) / 2
    th = math.radians(theta_deg); ct, st = math.cos(th), math.sin(th)
    out = [[" "]*W for _ in range(H)]
    zb = [[1e9]*W for _ in range(H)]
    half = W / 2
    bend, relief, dist = BEND * half, RELIEF * half, DIST * half
    for r in range(H):
        for c in range(W):
            ch = g[r][c]
            if ch == " ": continue
            for sub in (-0.33, 0.0, 0.33):
                X = (c + sub) - cx
                Y = (r - cy) * 2.0
                Z = bend * (X/half)**2 - relief * (dens[r][c] - 0.5)
                Xr = X*ct + Z*st
                Zr = -X*st + Z*ct
                f = (dist + Z) / (dist + Zr)
                sc = int(round(cx + Xr*f)); sr = r
                if 0 <= sc < W and 0 <= sr < H and Zr < zb[sr][sc]:
                    zb[sr][sc] = Zr; out[sr][sc] = ch
    return "\n".join("".join(row).rstrip() for row in out)

@functools.lru_cache(maxsize=None)
def _grid_cached():
    return _grid()

@functools.lru_cache(maxsize=None)
def frames(n=36):

    return tuple(frame(180 * i / n) for i in range(n))

if __name__ == "__main__":
    print(frame(35))
