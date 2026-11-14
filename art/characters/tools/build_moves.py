"""Run from the repo root:  python3 art/characters/tools/build_moves.py
Rebuilds art/characters/<n>-<name>/<n>-<name>-<action>.png from each character's rotations/south-east.png.
Needs Pillow. Each PNG is a strip of 64x64 frames (feet on row 60, figure centred on column 32;
dive, swim and float are centred in the cell instead).

Movesets for all nine PixelLab sprites, built by moving groups of the sprite's own pixels.
Core: idle, run, jump, block, ladder, skill.  Stage: stairs, slope, slip, dive, swim, hang, float."""
import json, os, io, base64, copy
from collections import Counter
from PIL import Image

CHARS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = {'hoodie': '1-hoodie-guy', 'monk': '2-monk', 'ninja': '3-ninja', 'runner': '4-free-runner', 'diver': '5-diver', 'fire': '6-firefighter', 'climber': '7-climber', 'astro': '8-astronaut', 'dog': '9-shiba-dog'}
CW = CH = 64
OFF = 8


def load(cid):
    im = Image.open(os.path.join(CHARS, FOLDER[cid], 'rotations', 'south-east.png')).convert('RGBA'); px = im.load()
    return [[('#%02x%02x%02x' % px[x, y][:3]) if px[x, y][3] >= 128 else None for x in range(48)] for y in range(48)]


def rgb(c): return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
def lum(c): r, g, b = rgb(c); return r * 0.3 + g * 0.59 + b * 0.11
def bluish(c): r, g, b = rgb(c); return b > r + 25 and b > 110


# ---- part masks: (name, fn(x, y, colour)); first match wins ----
PARTS = {
    'hoodie': [('armN', lambda x, y, c: (x <= 18 and 21 <= y <= 32) or (x <= 17 and 33 <= y <= 38)), ('armF', lambda x, y, c: x >= 33 and 22 <= y <= 36),
               ('legN', lambda x, y, c: y >= 33 and x <= 25), ('legF', lambda x, y, c: y >= 33 and x >= 26), ('body', lambda x, y, c: True)],
    'monk': [('legF', lambda x, y, c: 39 <= y <= 42 and x >= 23), ('legN', lambda x, y, c: y >= 39), ('skirt', lambda x, y, c: y >= 33), ('body', lambda x, y, c: True)],
    'ninja': [('tail', lambda x, y, c: x <= 16 and 11 <= y <= 21), ('armN', lambda x, y, c: 15 <= x <= 22 and 23 <= y <= 34), ('armF', lambda x, y, c: x >= 33 and 26 <= y <= 33),
              ('legN', lambda x, y, c: y >= 35 and x <= 25), ('legF', lambda x, y, c: y >= 34 and x >= 26), ('body', lambda x, y, c: True)],
    'runner': [('armN', lambda x, y, c: x <= 19 and 20 <= y <= 35), ('armF', lambda x, y, c: x >= 27 and 28 <= y <= 34),
               ('legN', lambda x, y, c: y >= 36 and x <= 23), ('legF', lambda x, y, c: y >= 36 and x >= 24), ('body', lambda x, y, c: True)],
    'diver': [('legF', lambda x, y, c: 38 <= y <= 42 and x >= 24), ('legN', lambda x, y, c: y >= 36 and x >= 15), ('body', lambda x, y, c: True)],
    'fire': [('legF', lambda x, y, c: y >= 37 and x >= 24), ('legN', lambda x, y, c: y >= 39 and 15 <= x <= 23), ('body', lambda x, y, c: True)],
    'climber': [('fx', lambda x, y, c: bluish(c) and ((x <= 17 and y >= 33) or (x <= 5 and 28 <= y <= 32) or (x >= 39 and y <= 22))),
                ('legN', lambda x, y, c: y >= 35 and 15 <= x <= 24), ('legF', lambda x, y, c: y >= 37 and 25 <= x <= 35 and not bluish(c)), ('body', lambda x, y, c: True)],
    'astro': [('armN', lambda x, y, c: 16 <= x <= 22 and 22 <= y <= 37), ('armF', lambda x, y, c: x >= 31 and 29 <= y <= 36),
              ('legN', lambda x, y, c: y >= 38 and 17 <= x <= 25), ('legF', lambda x, y, c: y >= 37 and x >= 26), ('body', lambda x, y, c: True)],
    'dog': [('tail', lambda x, y, c: x <= 15 and y <= 24), ('legBN', lambda x, y, c: y >= 37 and x <= 10), ('legBF', lambda x, y, c: y >= 38 and 11 <= x <= 17),
            ('legFF', lambda x, y, c: y >= 38 and 24 <= x <= 27), ('legFN', lambda x, y, c: y >= 37 and x >= 28), ('head', lambda x, y, c: x >= 23 and y <= 26), ('body', lambda x, y, c: True)],
}
ORDER = {
    'hoodie': ['armF', 'legF', 'legN', 'body', 'armN'], 'monk': ['legF', 'legN', 'skirt', 'body'],
    'ninja': ['tail', 'armF', 'legF', 'legN', 'body', 'armN'], 'runner': ['armF', 'legF', 'legN', 'body', 'armN'],
    'diver': ['legF', 'legN', 'body'], 'fire': ['legF', 'legN', 'body'], 'climber': ['legF', 'legN', 'body'],
    'astro': ['armF', 'legF', 'legN', 'body', 'armN'], 'dog': ['tail', 'legFF', 'legBF', 'legBN', 'legFN', 'body', 'head'],
}
RIDE = {'monk': ['skirt'], 'ninja': ['tail'], 'dog': ['tail', 'head'], 'climber': []}   # parts that follow the body
ARMS = {'hoodie': (24, 4, -1), 'ninja': (25, 3, -2), 'runner': (22, 4, -3), 'astro': (24, 2, -1)}  # shoulder row, dx near, dx far when raised


def split(cid, g):
    parts = {n: [] for n, _ in PARTS[cid]}
    for y in range(48):
        for x in range(48):
            if g[y][x] is None: continue
            for n, fn in PARTS[cid]:
                if fn(x, y, g[y][x]): parts[n].append((x, y, g[y][x])); break
    return parts


def xform(pix, t):
    if not pix: return []
    ys = [p[1] for p in pix]; y0, y1 = min(ys), max(ys)
    piv = t.get('top', y0); span = max(1, y1 - piv)
    sq = t.get('squash', 0); sq_at = t.get('squash_at', piv + 2)
    out = []
    for x, y, c in pix:
        ny = y
        if sq:
            if sq_at <= y < sq_at + sq: continue
            if t.get('keep_foot'):
                if y < sq_at: ny = y + sq
            elif y >= sq_at + sq: ny = y - sq
        k = max(0, ny - piv) / span
        nx = x + round(t.get('shear', 0) * k)
        if 'flipv' in t: ny = 2 * t['flipv'] - ny
        out.append((nx + t.get('dx', 0), ny + t.get('dy', 0), c))
    return out


def close_outline(cv, ol):
    add = []
    for y in range(CH):
        for x in range(CW):
            if cv[y][x] is not None: continue
            for ax, ay in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= ax < CW and 0 <= ay < CH and cv[ay][ax] is not None and lum(cv[ay][ax]) > 45:
                    add.append((x, y)); break
    for x, y in add: cv[y][x] = ol
    return cv


def compose(cid, parts, spec, ol):
    cv = [[None] * CW for _ in range(CH)]
    order = list(spec.get('_order', ORDER[cid]))
    if spec.get('_fx') and 'fx' in parts: order = ['fx'] + order
    for n in order:
        t = dict(spec.get(n, {}))
        if n in RIDE.get(cid, []) or n == 'fx':
            b = spec.get('body', {})
            t['dx'] = t.get('dx', 0) + b.get('dx', 0); t['dy'] = t.get('dy', 0) + b.get('dy', 0)
        for x, y, c in xform(parts[n], t):
            X, Y = x + OFF, y + OFF
            if 0 <= X < CW and 0 <= Y < CH: cv[Y][X] = c
    cv = close_outline(cv, ol)
    p = spec.get('_post')
    if p: cv = close_outline(post(cv, p), ol)
    return cv


def post(cv, p):
    """whole-figure transforms: lean (top shifts by n px), flipv, rot (90 deg clockwise)"""
    pts = [(x, y, cv[y][x]) for y in range(CH) for x in range(CW) if cv[y][x]]
    ys = [q[1] for q in pts]; y0, y1 = min(ys), max(ys)
    out = [[None] * CW for _ in range(CH)]
    for x, y, c in pts:
        nx, ny = x, y
        if p.get('lean'): nx = x + round(p['lean'] * (y1 - y) / max(1, y1 - y0))
        if p.get('flipv'): ny = y0 + y1 - ny
        if p.get('rot'): nx, ny = (y1 - y) + 8, x + 0
        nx += p.get('dx', 0); ny += p.get('dy', 0)
        if 0 <= nx < CW and 0 <= ny < CH: out[ny][nx] = c
    return out


def cell(cv, cx, foot, free=False):
    """centre into a 64x64 cell. normal frames: column cx -> 32, row foot -> 60. free frames: centre the bbox."""
    pts = [(x, y) for y in range(CH) for x in range(CW) if cv[y][x]]
    if free:
        xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
        dx = 32 - (min(xs) + max(xs) + 1) // 2; dy = 34 - (min(ys) + max(ys) + 1) // 2
    else:
        dx, dy = 32 - cx, 60 - foot
    g = [[None] * 64 for _ in range(64)]
    for x, y in pts:
        X, Y = x + dx, y + dy
        if 0 <= X < 64 and 0 <= Y < 64: g[Y][X] = cv[y][x]
    return g


def merge(a, b):
    o = copy.deepcopy(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(o.get(k), dict): o[k].update(v)
        else: o[k] = v
    return o


def humanoid(cid, st=3, lift=3, arms_swing=3, bob=1):
    """generic biped specs. legs: legN (near), legF (far). arms optional."""
    A = ARMS.get(cid)
    s = {}
    s['idle'] = [{}, {'body': {'dy': 1}, 'armN': {'dy': 1}, 'armF': {'dy': 1}}]
    s['run'] = [
        {'body': {'dy': bob, 'dx': 1}, 'legN': {'shear': st}, 'legF': {'shear': -st, 'dy': -1}, 'armN': {'shear': -arms_swing, 'dy': bob, 'dx': 1}, 'armF': {'shear': arms_swing, 'dy': bob, 'dx': 1}},
        {'body': {'dy': -1, 'dx': 1}, 'legN': {'shear': 1}, 'legF': {'squash': lift, 'shear': 2, 'dy': -1}, 'armN': {'shear': -1, 'dy': -1, 'dx': 1}, 'armF': {'shear': 1, 'dy': -1, 'dx': 1}},
        {'body': {'dy': bob, 'dx': 1}, 'legN': {'shear': -st, 'dy': -1}, 'legF': {'shear': st}, 'armN': {'shear': arms_swing, 'dy': bob, 'dx': 1}, 'armF': {'shear': -arms_swing, 'dy': bob, 'dx': 1}},
        {'body': {'dy': -1, 'dx': 1}, 'legN': {'squash': lift, 'shear': 2, 'dy': -1}, 'legF': {}, 'armN': {'shear': 1, 'dy': -1, 'dx': 1}, 'armF': {'shear': -1, 'dy': -1, 'dx': 1}},
    ]
    s['jump'] = [
        {'body': {'dy': -5}, 'armN': {'dy': -7, 'shear': -3}, 'armF': {'dy': -7, 'shear': 3}, 'legN': {'squash': lift, 'dy': -5, 'shear': -2}, 'legF': {'squash': max(1, lift - 1), 'dy': -5, 'shear': 2}},
        {'body': {'dy': -3}, 'armN': {'dy': -5, 'shear': -4}, 'armF': {'dy': -5, 'shear': 4}, 'legN': {'dy': -3, 'shear': -2}, 'legF': {'dy': -3, 'shear': 3}},
    ]
    wide = {'body': {'dy': 2}, 'legN': {'shear': -2}, 'legF': {'shear': 3}, 'armN': {'dy': 2}, 'armF': {'dy': 2}}
    if A:
        sh, dn, df = A
        front = ORDER[cid][:]; front.remove('armF'); front.insert(front.index('body') + 1, 'armF')
        up = lambda dyn, dyf: {'armN': {'flipv': sh, 'dx': dn, 'dy': dyn}, 'armF': {'flipv': sh, 'dx': df, 'dy': dyf}, '_order': front}
        s['block'] = [merge(wide, {'armN': {'flipv': sh, 'dx': dn, 'dy': 2}})]
        s['ladder'] = [merge(up(-1, 3), {'legN': {'squash': lift, 'dy': -1}}), merge(up(3, -1), {'legF': {'squash': lift, 'dy': -1}})]
        s['skill'] = [merge(wide, up(2, 2)), merge(merge(wide, up(3, 3)), {'body': {'dy': 3}})]
        s['hang'] = [merge(up(0, 0), {'legN': {'shear': 2}, 'legF': {'shear': 2}}), merge(up(0, 0), {'legN': {'shear': -2}, 'legF': {'shear': -2}})]
    else:
        s['block'] = [merge(wide, {'body': {'dy': 3}})]
        s['ladder'] = [{'legN': {'squash': lift, 'dy': -1}, 'legF': {'dy': 1}}, {'body': {'dy': -1}, 'legN': {}, 'legF': {'squash': max(1, lift - 1), 'dy': -1}}]
        s['skill'] = [merge(wide, {'body': {'dy': 1}}), wide]
        s['hang'] = [{'legN': {'shear': 2}, 'legF': {'shear': 2}}, {'legN': {'shear': -2}, 'legF': {'shear': -2}}]
    return s


def stage(s):
    """stage actions derived from the core poses with whole-figure transforms"""
    r, j = s['run'], s['jump']
    s['stairs'] = [merge(r[1], {'_post': {'lean': 1}}), merge(r[3], {'_post': {'lean': 1}})]
    s['slope'] = [merge(r[0], {'_post': {'lean': 4}}), merge(r[2], {'_post': {'lean': 4}})]
    s['slip'] = [merge(j[1], {'_post': {'lean': -5, 'dy': 3}})]
    s['dive'] = [s['block'][0], merge(j[0], {'_post': {'flipv': True}, '_free': True})]
    s['swim'] = [merge(r[0], {'_post': {'rot': True}, '_free': True}), merge(r[2], {'_post': {'rot': True}, '_free': True})]
    s['float'] = [merge(j[1], {'_post': {'lean': 2}, '_free': True}), merge(j[1], {'_post': {'lean': -1, 'dy': 1}, '_free': True})]
    return s


S = {}
S['hoodie'] = humanoid('hoodie', st=4, lift=4, arms_swing=4)
S['runner'] = humanoid('runner', st=4, lift=3, arms_swing=4)
S['runner']['skill'] = [merge(S['runner']['jump'][0], {'_post': {'lean': 5}, 'armN': {'shear': -5}, 'armF': {'shear': -4}}), merge(S['runner']['jump'][1], {'_post': {'lean': 6}, 'armN': {'shear': -5}, 'armF': {'shear': -4}})]
S['ninja'] = humanoid('ninja', st=3, lift=3, arms_swing=3)
for i, f in enumerate(S['ninja']['run']): f['tail'] = {'dy': (-1, 0, 1, 0)[i], 'dx': -1}
S['ninja']['idle'][1]['tail'] = {'dy': 1}
S['ninja']['skill'] = S['ninja']['ladder']          # Wall Walk: he climbs
S['astro'] = humanoid('astro', st=2, lift=2, arms_swing=2)
S['astro']['skill'] = [merge(S['astro']['jump'][1], {'armN': {'shear': -5}, 'armF': {'shear': 5}}), merge(S['astro']['jump'][1], {'body': {'dy': -4}, 'armN': {'shear': -5, 'dy': -6}, 'armF': {'shear': 5, 'dy': -6}, 'legN': {'dy': -4}, 'legF': {'dy': -4}})]
S['diver'] = humanoid('diver', st=2, lift=2)
S['fire'] = humanoid('fire', st=3, lift=3)
S['climber'] = humanoid('climber', st=3, lift=3)
S['climber']['skill'] = [merge(S['climber']['block'][0], {'_fx': True, '_post': {'lean': 2}}), merge(S['climber']['block'][0], {'_fx': True, 'body': {'dy': 4}, '_post': {'lean': 3}})]
m = humanoid('monk', st=3, lift=3)
m['idle'] = [{}, {'body': {'dy': 1}}]
for i, f in enumerate(m['run']):
    f['skirt'] = {'shear': (-1, 0, 1, 0)[i]}
    f['legF'] = [{'dx': -3, 'dy': -1}, {'dx': -1, 'dy': -2}, {'dx': 3, 'dy': 1}, {'dx': 1, 'dy': 1}][i]
m['run'][3]['legN'] = {'squash': 3, 'squash_at': 40, 'dy': -1}
m['jump'] = [{'body': {'dy': -5}, 'legN': {'squash': 3, 'squash_at': 40, 'dy': -5}, 'legF': {'dy': -7, 'dx': 1}}, {'body': {'dy': -3}, 'skirt': {'dy': -1}, 'legN': {'dy': -3, 'shear': -2}, 'legF': {'dy': -3, 'dx': 3}}]
m['block'] = [{'body': {'dy': 3}, 'skirt': {'shear': -1}, 'legN': {'dx': -3, 'squash': 2, 'squash_at': 40, 'keep_foot': True}, 'legF': {'dx': 5, 'dy': 2}}]
m['skill'] = [{'body': {'dy': 1}, 'legN': {'dx': -1}, 'legF': {'dx': 3, 'dy': 1}}, {'body': {'dy': 2}, 'legN': {'dx': -1}, 'legF': {'dx': 3, 'dy': 1}}]
m['ladder'] = [{'legN': {'squash': 3, 'squash_at': 40, 'dy': -1}, 'legF': {'dy': 1}}, {'body': {'dy': -1}, 'legF': {'dy': -2}}]
m['hang'] = [{'legN': {'shear': 2}, 'legF': {'dx': 2}}, {'legN': {'shear': -2}, 'legF': {'dx': -2}}]
S['monk'] = m
# hoodie: keep the hand-tuned skill (both arms guard)
for cid in S: stage(S[cid])
S['diver']['skill'] = S['diver']['swim']            # Deep Dive: he swims

# ---- the dog: four legs ----
d = {}
L = lambda bn=None, bf=None, fn=None, ff=None: {k: v for k, v in (('legBN', bn), ('legBF', bf), ('legFN', fn), ('legFF', ff)) if v}
d['idle'] = [{'tail': {'shear': 0}}, {'body': {'dy': 1}, 'tail': {'dx': 1, 'dy': -1}}]
d['run'] = [
    merge({'body': {'dy': 0, 'dx': 1}, 'tail': {'dy': 1}}, L({'shear': -3}, {'shear': -4}, {'shear': 4}, {'shear': 3})),
    merge({'body': {'dy': -2, 'dx': 1}, 'tail': {'dy': -1}}, L({'squash': 2, 'dy': -2, 'shear': -2}, {'squash': 3, 'dy': -2, 'shear': -2}, {'squash': 2, 'dy': -2, 'shear': 3}, {'squash': 2, 'dy': -2, 'shear': 3})),
    merge({'body': {'dy': 0, 'dx': 1}, 'tail': {'dy': 0}}, L({'shear': 3}, {'shear': 2}, {'shear': -3}, {'shear': -2})),
    merge({'body': {'dy': 1, 'dx': 1}, 'tail': {'dy': 1}}, L({'shear': 1}, {'shear': 1}, {'shear': -1}, {'shear': 0})),
]
d['jump'] = [
    merge({'body': {'dy': -6}, 'head': {'dy': -1}}, L({'squash': 3, 'dy': -6, 'shear': 2}, {'squash': 3, 'dy': -6, 'shear': 2}, {'squash': 3, 'dy': -6, 'shear': -2}, {'squash': 2, 'dy': -6, 'shear': -2})),
    merge({'body': {'dy': -3}}, L({'dy': -3, 'shear': -3}, {'dy': -3, 'shear': -3}, {'dy': -3, 'shear': 3}, {'dy': -3, 'shear': 3})),
]
d['block'] = [merge({'body': {'dy': 3}, 'head': {'dy': 1}, 'tail': {'dy': 1}}, L({'squash': 3, 'keep_foot': True}, {'squash': 3, 'keep_foot': True}, {'squash': 3, 'keep_foot': True, 'shear': 2}, {'squash': 2, 'keep_foot': True, 'shear': 2}))]
d['skill'] = [
    merge({'body': {'dy': 2, 'dx': -1}, 'head': {'dx': -1, 'dy': 1}}, L({'squash': 2, 'keep_foot': True}, {'squash': 2, 'keep_foot': True}, {'shear': 1}, {'shear': 1})),
    merge({'body': {'dy': 0, 'dx': 1}, 'head': {'dx': 3, 'dy': -2}, 'tail': {'dy': -1}}, L({'shear': -1}, {'shear': -1}, {'shear': 2}, {'shear': 2})),
]
d['hang'] = [merge({}, L({'shear': 2}, {'shear': 2}, {'shear': 2}, {'shear': 2})), merge({}, L({'shear': -2}, {'shear': -2}, {'shear': -2}, {'shear': -2}))]
stage(d)
d['ladder'] = [merge(d['jump'][1], {'_post': {'lean': -6}}), merge(d['jump'][0], {'_post': {'lean': -6}})]
d['hang'] = [merge(f, {'_post': {'lean': -6}, '_free': True}) for f in d['hang']]
d['swim'] = [merge(d['run'][0], {'_free': True}), merge(d['run'][2], {'_free': True})]   # dog paddle, upright
S['dog'] = d

MODES = ['idle', 'run', 'jump', 'block', 'ladder', 'skill', 'stairs', 'slope', 'slip', 'dive', 'swim', 'hang', 'float']
CIDS = ['hoodie', 'monk', 'ninja', 'runner', 'diver', 'fire', 'climber', 'astro', 'dog']


def png(frames):
    im = Image.new('RGBA', (64 * len(frames), 64), (0, 0, 0, 0)); px = im.load()
    for i, f in enumerate(frames):
        for y in range(64):
            for x in range(64):
                if f[y][x]: px[i * 64 + x, y] = rgb(f[y][x]) + (255,)
    return im


def build():
    count = {}
    for cid in CIDS:
        g = load(cid)
        cols = Counter(c for row in g for c in row if c and lum(c) < 30); ol = cols.most_common(1)[0][0]
        xs = [x for y in range(48) for x in range(48) if g[y][x]]; ys = [y for y in range(48) for x in range(48) if g[y][x]]
        parts = split(cid, g)
        if cid == 'climber':   # centre on the climber himself, not on the motion streak
            xs = [x for n in parts if n != 'fx' for x, _, _ in parts[n]]
        cx, foot = (min(xs) + max(xs) + 1) // 2 + OFF, max(ys) + OFF
        out = os.path.join(CHARS, FOLDER[cid]); name = lambda a: os.path.join(out, FOLDER[cid] + '-' + a + '.png')
        allf = []
        for mode in MODES:
            frames = [cell(compose(cid, parts, sp, ol), cx, foot, sp.get('_free')) for sp in S[cid][mode]]
            png(frames).save(name('hook' if mode == 'hang' else mode), 'PNG', optimize=True)
            allf += frames
        png(allf).save(name('all-moves'), 'PNG', optimize=True)
        count[cid] = len(allf)
    return count


if __name__ == '__main__':
    print(build())
