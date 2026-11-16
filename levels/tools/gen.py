#!/usr/bin/env python3
"""Build an LDtk 1.5.3 project from the prototype's ROOMS (rendered by run.js into out/)."""
import json, os, sys, uuid, copy, math, re
import numpy as np
from PIL import Image

SRC = sys.argv[1]          # out/ folder from run.js
DST = sys.argv[2]          # output folder
SAMPLE = sys.argv[3]       # LDtk sample project, used as a template for exact key sets
COMMIT = sys.argv[4]

W, H, FLOOR, FH, WALL, GRID = 1600, 640, 550, 200, 40, 10
info = json.load(open(os.path.join(SRC, 'info.json')))
sample = json.load(open(SAMPLE))
os.makedirs(os.path.join(DST, 'backgrounds'), exist_ok=True)

uid_n = [100]
def uid():
    uid_n[0] += 1; return uid_n[0]
iid = lambda: str(uuid.uuid4())

# ---------------- images ----------------
_cache = {}
def img(name):
    if name not in _cache:
        _cache[name] = np.array(Image.open(os.path.join(SRC, name)).convert('RGBA'))
    return _cache[name]
def diff_rgba(i, name):
    a, b = img(f'bg_{i}.png'), img(name)
    m = (a[..., :3] != b[..., :3]).any(2)
    out = b.copy(); out[..., 3] = np.where(m, 255, 0)
    return out, m
def bbox(m):  # world units
    ys, xs = np.nonzero(m)
    if not len(xs): return None
    return xs.min() * 4, ys.min() * 4, (xs.max() + 1) * 4, (ys.max() + 1) * 4
def crop(rgba, x, y, w, h):  # world-unit rect, out of the art-pixel image, upscaled x4
    big = np.kron(rgba, np.ones((4, 4, 1), dtype=np.uint8))
    x0, y0 = max(0, int(x)), max(0, int(y)); x1, y1 = min(big.shape[1], int(x + w)), min(big.shape[0], int(y + h))
    out = np.zeros((int(h), int(w), 4), dtype=np.uint8)
    if x1 > x0 and y1 > y0: out[y0 - int(y):y1 - int(y), x0 - int(x):x1 - int(x)] = big[y0:y1, x0:x1]
    return out

# ---------------- entity definitions ----------------
CAT_COLOR = {'solid': '#BE4A2F', 'plat': '#2CE8F5', 'ghost': '#63C74D', 'climb': '#FEAE34', 'decor': '#B55088', 'marker': '#FFFFFF'}
DEFS = {}      # name -> dict
ORDER = []
def define(name, cat, tag, pivot, size, resX=False, resY=False, fields=(), doc=None):
    if name in DEFS: return DEFS[name]
    d = dict(name=name, cat=cat, tag=tag, pivot=pivot, size=size, resX=resX, resY=resY, fields=list(fields), tile=None, doc=doc, uid=uid())
    for f in d['fields']: f['uid'] = uid()
    DEFS[name] = d; ORDER.append(name); return d
def fld(ident, typ, null=True, show='NameAndValue', doc=None):
    return dict(ident=ident, typ=typ, null=null, show=show, doc=doc)

SEC_TAG = {'house': 'House', 'dojo': 'Dojo', 'bamboo': 'Bamboo', 'climb': 'Climb', 'rooftop-jumps': 'RooftopRun', 'lake-dive': 'Lake', 'lake': 'Lake',
           'volcano': 'Volcano', 'snow': 'Snow', 'space': 'Space'}
def sec_of(r):
    rm = ROOMS[r['i']]
    return 'climb' if r['climb'] else rm.get('sec') or 'house'

PROP_NAMES = {'side': 'SideTable', 'tv': 'Tv', 'stalk': 'BambooStalk', 'thick': 'BambooThicket', 'leaf': 'LeafCanopy', 'shroom': 'BounceShroom',
              'roof': 'Roof', 'sign': 'Sign', 'vent': 'RoofVent', 'cable': 'ZipCable', 'board': 'Billboard', 'aster': 'Asteroid', 'ufo': 'Ufo', 'laser': 'LaserGate', 'slab': 'SteppingSlab', 'pod': 'Pod', 'panel': 'Panel', 'beam': 'BeamPlank', 'dummy': 'Dummy'}
HP_KINDS = {k for r in info for p in r['props'] for k in [p['k']] if 'hp' in p}

# ---------------- rooms ----------------
# info carries props/decor/climb; read the room flags from the prototype's own ROOMS list too
ROOMS = json.load(open(os.path.join(SRC, 'rooms.json')))

def ident(s):
    s = re.sub(r'[^A-Za-z0-9]+', ' ', s).title().replace(' ', '')
    return s

levels_out = []
worldY = 0
for r in info:
    i, rm = r['i'], ROOMS[r['i']]
    LH = r['LH']; off = LH - H
    ly = lambda h: off + FLOOR - h
    sec = sec_of(r); tag = SEC_TAG.get(sec, 'House')
    ents = []

    def add(dname, rgba, rect, anchor, w, h, values):
        d = DEFS[dname]
        if d['tile'] is None:
            d['tile'] = crop(rgba, *rect)
        ents.append(dict(d=dname, px=[int(round(anchor[0])), int(round(anchor[1]))], w=int(round(w)), h=int(round(h)), values=values))

    # props
    for k, p in enumerate(r['props']):
        rgba, m = diff_rgba(i, f'p_{i}_{k}.png'); bb = bbox(m)
        kind = p['k']
        if r['climb']:  # pillars, shaft walls and AC units stand on floor lv
            name = 'ShaftWall' if p.get('wall') else 'AcUnit' if p.get('ac') else 'Pillar'
            ph = 96 if p.get('ac') else FH - 12
            define(name, 'solid', 'Climb', (0.5, 1), (p['w'], ph), resX=True, fields=[fld('hp', 'Int')],
                   doc='Cover from side punches. Stands on the floor its bottom edge sits on.')
            base = ly(p['lv'] * FH)
            vis = (bb[0], base - ph, bb[2] - bb[0], ph) if bb else (p['x'] - p['w'] / 2, base - ph, p['w'], ph)
            add(name, rgba, vis, (p['x'], base), p['w'], ph, {'hp': p.get('hp')})
            continue
        name = 'SnowRock' if p.get('snow') else PROP_NAMES.get(kind, kind[:1].upper() + kind[1:])
        cat = 'plat' if p.get('plat') else 'ghost' if p.get('ghost') else 'solid'
        top = ly(p['h'])
        EXTRA = [k2 for k2 in ('cx0', 'cy0', 'cx1', 'cy1', 'bx', 'bw', 'bh', 'off') if k2 in p]
        if p['h'] <= 0:  # drawn above its base (laser gates, zip cables): pivot on the base, box up to the sprite's top
            hh = max(12, top - bb[1]) if bb else 12
            fields = [fld(k2, 'Float' if k2 == 'off' else 'Int') for k2 in EXTRA]
            define(name, cat, tag, (0.5, 1), (p['w'], hh), resX=True, fields=fields,
                   doc='Not solid. Its bottom edge is its base height. ' + ('cx0/cy0 to cx1/cy1 are the cable ends (x in the room, y as height above the floor line).' if kind == 'cable' else 'off = seconds into its on/off cycle.' if kind == 'laser' else ''))
            add(name, rgba, (p['x'] - p['w'] / 2, top - hh, p['w'], hh), (p['x'], top), p['w'], hh, {k2: p[k2] for k2 in EXTRA})
            continue
        if cat == 'plat':
            hh = max(12, (bb[3] - top) if bb else 12); hh = min(hh, 60)
        elif p.get('snow'): hh = p['hh']
        elif p.get('raw') and rm.get('void'): hh = H - (FLOOR - p['h'])
        else: hh = p['h']
        fields = []
        if kind in HP_KINDS: fields.append(fld('hp', 'Int', doc='Punches it takes before it breaks. Empty = unbreakable.'))
        if kind in ('tv', 'fridge'): fields.append(fld('elec', 'Bool', null=False, doc='Sparks for a second before it clears.'))
        if 'drift' in p or kind in ('turtle', 'ufo'): fields += [fld('driftRange', 'Int'), fld('driftSpeed', 'Float'), fld('driftPhase', 'Float')]
        fields += [fld(k2, 'Float' if k2 == 'off' else 'Int') for k2 in EXTRA]
        doc = {'plat': 'One-way platform: its top edge is the standing height. Drop through with down.',
               'ghost': 'Not solid. Its top edge is the height used by the game.',
               'solid': 'Solid box. Its top edge is the standing height (h above the floor line).'}[cat]
        if p.get('snow'): doc = 'Rock on a slope: the box is the visible rock, its top edge is the standing height.'
        define(name, cat, tag, (0.5, 0), (p['w'], hh), resX=True, resY=True, fields=fields, doc=doc)
        vals = {}
        if kind in HP_KINDS: vals['hp'] = p.get('hp')
        if kind in ('tv', 'fridge'): vals['elec'] = bool(p.get('elec'))
        if 'drift' in p: vals.update(driftRange=p['drift'][0], driftSpeed=p['drift'][1], driftPhase=p['drift'][2])
        vals.update({k2: p[k2] for k2 in EXTRA})
        add(name, rgba, (p['x'] - p['w'] / 2, top, p['w'], hh), (p['x'], top), p['w'], hh, vals)

    # wall decor (anchor: the sprite's top-left corner; DECOR_DX in the README turns it back into the game's x)
    for k, dd in enumerate(r['decor']):
        rgba, m = diff_rgba(i, f'd_{i}_{k}.png'); bb = bbox(m)
        kind = dd[0]; name = 'Decor' + kind[:1].upper() + kind[1:] + (['Circle', 'Mountain', 'Bamboo'][dd[2]] if kind == 'scroll' else '')
        fields = []
        d = define(name, 'decor', 'Decor', (0, 0), (bb[2] - bb[0], bb[3] - bb[1]), fields=fields,
                   doc='Wall decoration. Only its x is used by the game; y is fixed per kind.')
        vals = {}
        w0, h0 = d['size']
        add(name, rgba, (bb[0], bb[1], w0, h0), (bb[0], bb[1]), w0, h0, vals)
        d.setdefault('dx', bb[0] - dd[1])

    # climb features
    cl = r['climb']
    if cl:
        def feat(key, k): return diff_rgba(i, f'f_{i}_{key}_{k}.png')[0]
        for k, s in enumerate(cl['stairs']):
            lo = min(s['x0'], s['x1']); right = s['x1'] > s['x0']
            name = 'StairsUpRight' if right else 'StairsUpLeft'
            define(name, 'climb', 'Climb', (0.5, 1), (400, FH), resX=True, doc='A staircase from the floor it stands on to the floor above.')
            add(name, feat('stairs', k), (lo, ly((s['lv'] + 1) * FH), 400, FH), (lo + 200, ly(s['lv'] * FH)), 400, FH, {})
        for k, l in enumerate(cl['ladders']):
            timed = bool(l.get('timed')); name = 'Window' if timed else 'Ladder'; w = 88 if timed else 72
            define(name, 'climb', 'Climb', (0.5, 1), (w, FH), fields=[fld('offset', 'Float', doc='Seconds into the 5 s open/shut cycle.')] if timed else [],
                   doc='Timed window on the facade: open 3 s, shut 2 s.' if timed else 'Up at its foot climbs one floor.')
            add(name, feat('ladders', k), (l['x'] - w / 2, ly((l['lv'] + 1) * FH), w, FH), (l['x'], ly(l['lv'] * FH)), w, FH, {'offset': l.get('off')} if timed else {})
        for k, hk in enumerate(cl['hooks']):
            define('Hook', 'climb', 'Climb', (0.5, 0), (32, 24), doc='Jump into it to be pulled up a floor. Sits 150 above its floor.')
            y = ly(hk['lv'] * FH + 150)
            add('Hook', feat('hooks', k), (hk['x'] - 16, y, 32, 24), (hk['x'], y), 32, 24, {})
        for key, name, w, doc, extra in [('pipes', 'DrainPipe', 32, 'Auto-climb pipe, n floors tall.', []),
                                         ('ropes', 'Rope', 64, 'Rope from a beam n floors up.', []),
                                         ('plats', 'WindowLift', 144, 'Window-cleaning lift riding n floors.', ['off']),
                                         ('els', 'Elevator', 128, 'Elevator shaft, n floors.', [])]:
            for k, q in enumerate(cl[key]):
                define(name, 'climb', 'Climb', (0.5, 1), (w, q['n'] * FH), resY=True,
                       fields=[fld('offset', 'Float')] if extra else [], doc=doc + ' Height = n x 200.')
                hgt = q['n'] * FH
                add(name, feat(key, k), (q['x'] - w / 2, ly(q['lv'] * FH) - hgt, w, hgt), (q['x'], ly(q['lv'] * FH)), w, hgt,
                    {'offset': q.get('off')} if extra else {})
        for k, g in enumerate(cl['ledges']):
            define('Ledge', 'climb', 'Climb', (0.5, 0), (g['w'], 12), resX=True, doc='Half-height ledge, 100 above its floor.')
            y = ly(g['lv'] * FH + 100)
            add('Ledge', feat('ledges', k), (g['x'] - g['w'] / 2, y, g['w'], 12), (g['x'], y), g['w'], 12, {})

    # start marker for rooms that drop 我 in from a height
    if rm.get('enterY') is not None:
        define('PlayerStart', 'marker', 'Markers', (0.5, 1), (54, 120), doc='Where 我 enters this room (only rooms with enterY).')
        ents.append(dict(d='PlayerStart', px=[27, ly(rm['enterY'])], w=54, h=120, values={}))

    # terrain IntGrid: 1 ground, 2 water, 3 lava, 4 floor slab (one-way), 5 glass wall
    cw, ch = W // GRID, LH // GRID
    g = np.zeros((ch, cw), dtype=int)
    if cl:
        g[(off + FLOOR) // GRID:, :] = 1
        o0, o1 = cl['out']
        for kk in range(1, cl['top'] + 1):
            y = ly(kk * FH) // GRID
            out = o0 <= kk <= o1 and kk < cl['top']
            x0 = (WALL - 12) // GRID if out else 0; x1 = cw - x0 if out else cw
            g[y, x0:x1] = 4
        for kk in range(cl['top']):
            if o0 <= kk < o1: continue
            y0, y1 = ly((kk + 1) * FH) // GRID + 1, ly(kk * FH) // GRID
            g[y0:y1, 0:WALL // GRID] = 5; g[y0:y1, cw - WALL // GRID:] = 5
    elif not rm.get('void'):
        for c in range(cw):
            hgt = r['heights'][c]
            top = int(round(ly(hgt) / GRID))
            g[max(0, top):, c] = 1
            xc = c * GRID + 5
            if r['water'] and xc > r['water']['x0']:
                wt = int(round(ly(r['water']['top']) / GRID))
                g[max(0, wt):max(0, top), c] = 2
            if r['lava'] and any(a < xc < b for a, b in r['lava']):
                g[top:top + 2, c] = 3
    # level fields
    wall = rm.get('wall'); floor = rm.get('floor')
    lf = {
        'section': sec, 'scene': rm.get('scene'), 'style': rm.get('style'), 'music': rm.get('music'),
        'wallColors': ','.join(wall) if wall else None, 'floorColors': ','.join(floor) if floor else None,
        'outdoor': bool(rm.get('outdoor')), 'gate': bool(rm.get('gate')), 'void': bool(rm.get('void')), 'slide': bool(rm.get('slide')),
        'stars': bool(rm.get('stars')), 'speedScale': rm.get('fast'), 'gravityScale': rm.get('grav'), 'rideSeconds': rm.get('ride'),
        'climbOutsideRows': f"{cl['out'][0]}-{cl['out'][1]}" if cl else None,
        'checkpoint': bool(rm.get('cp')), 'vacuum': bool(rm.get('vac')), 'enterY': rm.get('enterY'),
    }
    lname = f"R{i + 1:03d}_{ident(r['name'])}"
    bgname = f"backgrounds/{lname}.png"
    big = np.kron(img(f'bg_{i}.png'), np.ones((4, 4, 1), dtype=np.uint8))
    Image.fromarray(big).save(os.path.join(DST, bgname), optimize=True)
    levels_out.append(dict(name=lname, title=r['name'], i=i, LH=LH, off=off, sec=sec, worldX=0, worldY=worldY, ents=ents, grid=g, fields=lf, bg=bgname))
    if i < len(info) - 1:
        nxt = info[i + 1]
        worldY = worldY + off - (nxt['LH'] - H) - r['pairD']

# ---------------- world layout: each section on its own row, rooms joined left to right ----------------
groups = []
for L in levels_out:
    if not groups or groups[-1][-1]['sec'] != L['sec']: groups.append([])
    groups[-1].append(L)
rowY = 0
for g in groups:
    mn = min(l['worldY'] for l in g)
    for k, l in enumerate(g): l['rel'] = l['worldY'] - mn; l['worldX'] = k * W; l['worldY'] = rowY + l['rel']
    rowY += max(l['rel'] + l['LH'] for l in g) + 600

# ---------------- sprite atlas ----------------
tiles = [(n, DEFS[n]['tile']) for n in ORDER if DEFS[n]['tile'] is not None]
for n in ORDER:
    if DEFS[n]['tile'] is None: DEFS[n]['rect'] = (0, 0, 0, 0)
AW, x, y, rowh = 2048, 0, 0, 0
for n, t in tiles:
    th, tw = t.shape[:2]
    if x + tw > AW: x, y, rowh = 0, y + rowh + 4, 0
    DEFS[n]['rect'] = (x, y, tw, th); x += tw + 4; rowh = max(rowh, th)
AH = y + rowh
atlas = np.zeros((AH, AW, 4), dtype=np.uint8)
for n, t in tiles:
    ax, ay, tw, th = DEFS[n]['rect']; atlas[ay:ay + th, ax:ax + tw] = t
Image.fromarray(atlas).save(os.path.join(DST, 'sprites.png'), optimize=True)

# ---------------- JSON assembly (key sets copied from LDtk's own sample) ----------------
S_FIELD = sample['defs']['entities'][0]['fieldDefs'][0]
S_ENT = next(e for e in sample['defs']['entities'] if e['identifier'] == 'EntityFieldsTest')
S_LAYER_I = next(l for l in sample['defs']['layers'] if l['type'] == 'IntGrid')
S_LAYER_E = next(l for l in sample['defs']['layers'] if l['type'] == 'Entities')
S_TS = sample['defs']['tilesets'][0]
TS_UID = uid()
TYPES = {'Int': ('F_Int', 'Int'), 'Float': ('F_Float', 'Float'), 'Bool': ('F_Bool', 'Bool'), 'String': ('F_String', 'String')}

def field_def(f):
    d = copy.deepcopy(S_FIELD)
    t, tt = TYPES[f['typ']]
    d.update(identifier=f['ident'], doc=f.get('doc'), __type=tt, uid=f['uid'], type=t, isArray=False, canBeNull=f['null'],
             editorDisplayMode=f['show'], editorDisplayPos='Above' if f['show'] != 'Hidden' else 'Beneath', editorAlwaysShow=False,
             editorShowInWorld=True, defaultOverride=None, searchable=False)
    return d
def field_inst(f, v):
    t, tt = TYPES[f['typ']]
    if v is None: rev = []
    elif f['typ'] == 'Bool': rev = [{'id': 'V_Bool', 'params': [bool(v)]}] if v else [None]
    elif f['typ'] == 'Int': v = int(v); rev = [{'id': 'V_Int', 'params': [v]}]
    elif f['typ'] == 'Float': v = float(v); rev = [{'id': 'V_Float', 'params': [v]}]
    else: rev = [{'id': 'V_String', 'params': [v]}]
    if f['typ'] == 'Bool' and v is None: v = False
    return {'__identifier': f['ident'], '__type': tt, '__value': v, '__tile': None, 'defUid': f['uid'], 'realEditorValues': rev}

ent_defs = []
for n in ORDER:
    d = DEFS[n]; e = copy.deepcopy(S_ENT); ax, ay, tw, th = d['rect']
    e.update(identifier=n, uid=d['uid'], tags=[d['tag']], exportToToc=False, allowOutOfBounds=True, doc=d['doc'],
             width=int(d['size'][0]), height=int(d['size'][1]), resizableX=d['resX'], resizableY=d['resY'],
             minWidth=None, maxWidth=None, minHeight=None, maxHeight=None, keepAspectRatio=False,
             tileOpacity=1, fillOpacity=0.08, lineOpacity=0.6, hollow=False, color=CAT_COLOR[d['cat']],
             renderMode='Tile' if tw else 'Rectangle', showName=not tw, tilesetId=TS_UID if tw else None, tileRenderMode='Stretch',
             tileRect={'tilesetUid': TS_UID, 'x': ax, 'y': ay, 'w': tw, 'h': th} if tw else None, uiTileRect=None, nineSliceBorders=[],
             maxCount=0, limitScope='PerLevel', limitBehavior='MoveLastOne', pivotX=d['pivot'][0], pivotY=d['pivot'][1],
             fieldDefs=[field_def(f) for f in d['fields']])
    ent_defs.append(e)

LVL_FIELDS = [fld('section', 'String', show='Hidden'), fld('scene', 'String', show='Hidden'), fld('style', 'String', show='Hidden'),
              fld('music', 'String', show='Hidden'), fld('wallColors', 'String', show='Hidden'), fld('floorColors', 'String', show='Hidden'),
              fld('outdoor', 'Bool', False, 'Hidden'), fld('gate', 'Bool', False, 'Hidden'), fld('void', 'Bool', False, 'Hidden'),
              fld('slide', 'Bool', False, 'Hidden'), fld('stars', 'Bool', False, 'Hidden'), fld('speedScale', 'Float', show='Hidden'),
              fld('gravityScale', 'Float', show='Hidden'), fld('rideSeconds', 'Int', show='Hidden'), fld('climbOutsideRows', 'String', show='Hidden'),
              fld('checkpoint', 'Bool', False, 'Hidden'), fld('vacuum', 'Bool', False, 'Hidden'), fld('enterY', 'Int', show='Hidden')]
LF_DOC = {'section': 'Section id (also its music id): house, dojo, bamboo, climb, rooftop-jumps, lake-dive, lake, volcano, snow, space.',
          'void': 'No floor: only props hold 我 up (the rooftop run).', 'slide': 'Snow: slopes slide 我 back unless pushing uphill.',
          'rideSeconds': 'Lift rooms: the exit opens after this many seconds.', 'climbOutsideRows': 'Rooftop climb: floors a..b-1 are outside on the facade.', 'checkpoint': 'A lost turn restarts here.', 'vacuum': 'Spacewalk: water physics as a jetpack.', 'enterY': 'Height 我 enters at.'}
for f in LVL_FIELDS: f['uid'] = uid(); f['doc'] = LF_DOC.get(f['ident'])

INT_VALUES = [(1, 'ground', '#733E39'), (2, 'water', '#0099DB'), (3, 'lava', '#F77622'), (4, 'floor_slab', '#C0CBDC'), (5, 'glass_wall', '#2CE8F5')]
L_ENT_UID, L_INT_UID = uid(), uid()
lay_e = copy.deepcopy(S_LAYER_E); lay_e.update(identifier='Entities', uid=L_ENT_UID, gridSize=GRID, displayOpacity=1, doc='Props, decor and climb pieces. The picture of each thing is drawn from the prototype.')
lay_i = copy.deepcopy(S_LAYER_I); lay_i.update(identifier='Terrain', uid=L_INT_UID, gridSize=GRID, displayOpacity=0.45, tilesetDefUid=None, autoRuleGroups=[],
                                               doc='Ground, water, lava, floor slabs and glass walls, in 10 px cells.',
                                               intGridValues=[{'value': v, 'identifier': n, 'color': c, 'tile': None, 'groupUid': 0} for v, n, c in INT_VALUES])

ts = copy.deepcopy(S_TS)
ts.update(__cWid=math.ceil(AW / 20), __cHei=math.ceil(AH / 20), identifier='PrototypeSprites', uid=TS_UID, relPath='sprites.png', embedAtlas=None,
          pxWid=AW, pxHei=AH, tileGridSize=20, spacing=0, padding=0, tags=[], tagsSourceEnumUid=None, enumTags=[], customData=[], savedSelections=[], cachedPixelData=None)

def hexcol(c): return c
levels = []
for n, L in enumerate(levels_out):
    cw, ch = W // GRID, L['LH'] // GRID
    einst = []
    for e in L['ents']:
        d = DEFS[e['d']]; ax, ay, tw, th = d['rect']
        einst.append({'__identifier': e['d'], '__grid': [e['px'][0] // GRID, e['px'][1] // GRID], '__pivot': list(d['pivot']), '__tags': [d['tag']],
                      '__tile': {'tilesetUid': TS_UID, 'x': ax, 'y': ay, 'w': tw, 'h': th} if tw else None, '__smartColor': CAT_COLOR[d['cat']], 'iid': iid(),
                      'width': e['w'], 'height': e['h'], 'defUid': d['uid'], 'px': e['px'],
                      'fieldInstances': [field_inst(f, e['values'].get(f['ident'])) for f in d['fields']],
                      '__worldX': L['worldX'] + e['px'][0], '__worldY': L['worldY'] + e['px'][1]})
    base = {'__pxTotalOffsetX': 0, '__pxTotalOffsetY': 0, '__tilesetDefUid': None, '__tilesetRelPath': None, 'levelId': 0, 'pxOffsetX': 0, 'pxOffsetY': 0,
            'visible': True, 'optionalRules': [], 'autoLayerTiles': [], 'overrideTilesetUid': None, 'gridTiles': [], '__opacity': 1}
    li_e = dict(base, **{'__identifier': 'Entities', '__type': 'Entities', '__cWid': cw, '__cHei': ch, '__gridSize': GRID, 'iid': iid(), 'layerDefUid': L_ENT_UID,
                         'intGridCsv': [], 'seed': 1000 + n, 'entityInstances': einst})
    li_i = dict(base, **{'__identifier': 'Terrain', '__type': 'IntGrid', '__cWid': cw, '__cHei': ch, '__gridSize': GRID, 'iid': iid(), 'layerDefUid': L_INT_UID,
                         'intGridCsv': [int(v) for v in L['grid'].flatten()], 'seed': 2000 + n, 'entityInstances': [], '__opacity': 0.45})
    order = ['__identifier', '__type', '__cWid', '__cHei', '__gridSize', '__opacity', '__pxTotalOffsetX', '__pxTotalOffsetY', '__tilesetDefUid', '__tilesetRelPath',
             'iid', 'levelId', 'layerDefUid', 'pxOffsetX', 'pxOffsetY', 'visible', 'optionalRules', 'intGridCsv', 'autoLayerTiles', 'seed', 'overrideTilesetUid', 'gridTiles', 'entityInstances']
    li_e = {k: li_e[k] for k in order}; li_i = {k: li_i[k] for k in order}
    L['iid'] = iid(); L['uid'] = n
    levels.append({'identifier': L['name'], 'iid': L['iid'], 'uid': n, 'worldX': L['worldX'], 'worldY': L['worldY'], 'worldDepth': 0,
                   'pxWid': W, 'pxHei': L['LH'], '__bgColor': '#181425', 'bgColor': '#181425', 'useAutoIdentifier': False,
                   'bgRelPath': L['bg'], 'bgPos': 'Unscaled', 'bgPivotX': 0, 'bgPivotY': 0, '__smartColor': '#8B9BB4',
                   '__bgPos': {'topLeftPx': [0, 0], 'scale': [1, 1], 'cropRect': [0, 0, W, L['LH']]}, 'externalRelPath': None,
                   'fieldInstances': [field_inst(f, L['fields'].get(f['ident'])) for f in LVL_FIELDS], '__neighbours': [],
                   'layerInstances': [li_e, li_i]})
for n, lv in enumerate(levels):
    nb = []
    if n > 0: nb.append({'levelIid': levels[n - 1]['iid'], 'dir': 'w'})
    if n < len(levels) - 1: nb.append({'levelIid': levels[n + 1]['iid'], 'dir': 'e'})
    lv['__neighbours'] = nb
for n, L in enumerate(levels_out):
    for li in levels[n]['layerInstances']: li['levelId'] = n

proj = {k: copy.deepcopy(v) for k, v in sample.items() if k not in ('defs', 'levels', 'worlds', 'toc')}
proj.update(iid=iid(), nextUid=uid() + 1, identifierStyle='Free', toc=[], worldLayout='Free', worldGridWidth=W, worldGridHeight=H,
            defaultLevelWidth=W, defaultLevelHeight=H, defaultPivotX=0, defaultPivotY=0, defaultGridSize=GRID, defaultEntityWidth=20, defaultEntityHeight=20,
            bgColor='#262B44', defaultLevelBgColor='#181425', minifyJson=False, externalLevels=False, exportTiled=False, simplifiedExport=False,
            imageExportMode='None', exportLevelBg=True, pngFilePattern=None, backupOnSave=True, backupLimit=10, backupRelPath=None,
            levelNamePattern='R%idx', tutorialDesc=f'Punch Your Friend journey prototype, generated from branch house-prototype @ {COMMIT}. See README.md next to this file.',
            customCommands=[], flags=['UseMultilinesType'], dummyWorldIid=iid())
proj['defs'] = {'layers': [lay_e, lay_i], 'entities': ent_defs, 'tilesets': [ts], 'enums': [], 'externalEnums': [], 'levelFields': [field_def(f) for f in LVL_FIELDS]}
proj['levels'] = levels
proj['worlds'] = []
order = list(sample.keys())
proj = {k: proj[k] for k in order}
CSV = {}
for lv in proj['levels']:
    for li in lv['layerInstances']:
        if li['intGridCsv']:
            key = '@@CSV' + li['iid'] + '@@'; CSV[key] = ','.join(map(str, li['intGridCsv'])); li['intGridCsv'] = key
txt = json.dumps(proj, indent='\t')
for key, v in CSV.items(): txt = txt.replace('"' + key + '"', '[' + v + ']')
open(os.path.join(DST, 'punch-your-friend.ldtk'), 'w').write(txt)
json.dump({n: {'dx': DEFS[n].get('dx'), 'tag': DEFS[n]['tag'], 'cat': DEFS[n]['cat'], 'pivot': DEFS[n]['pivot']} for n in ORDER},
          open(os.path.join(DST, '..', 'defs-summary.json'), 'w'), indent=1, default=int)
print('levels', len(levels), 'entities', sum(len(L['ents']) for L in levels_out), 'defs', len(ORDER), 'atlas', AW, AH)
