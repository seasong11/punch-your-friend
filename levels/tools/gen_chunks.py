#!/usr/bin/env python3
"""Turn the world-unit LDtk export (gen.py) into a chunk library in art pixels on a 16 px grid.

usage: gen_chunks.py <world.ldtk folder> <out/ renders> <items folder> <LDtk sample .ldtk> <dst folder>
"""
import json, os, sys, copy, uuid, math, re
import numpy as np
from PIL import Image

SRC, RENDERS, ITEMS, SAMPLE, DST = sys.argv[1:6]
src = json.load(open(os.path.join(SRC, 'punch-your-friend.ldtk')))
sample = json.load(open(SAMPLE))
info = json.load(open(os.path.join(RENDERS, 'info.json')))
items = json.load(open(os.path.join(ITEMS, 'items.json')))
os.makedirs(os.path.join(DST, 'reference'), exist_ok=True)

G = 16                     # tile size in art pixels
CW, CH = 400, 160          # one screen-sized chunk (25 x 10 tiles)
FLOOR = CH - G             # floor line: top of the bottom tile row (144)
WFLOOR = 550               # floor line in the old world units
iid = lambda: str(uuid.uuid4())
uid_n = [10]
def uid():
    uid_n[0] += 1; return uid_n[0]

# ---------------- which screens become starter chunks ----------------
PICK = {'house': 8, 'dojo': 4, 'bamboo': 4, 'climb': 1, 'rooftop-jumps': 8, 'lake-dive': 1, 'lake': 3, 'volcano': 4, 'snow': 4, 'space': 99}
SECTION = {'house': 'House', 'dojo': 'Dojo', 'bamboo': 'Bamboo', 'climb': 'Climb', 'rooftop-jumps': 'Rooftop', 'lake-dive': 'Lake', 'lake': 'Lake',
           'volcano': 'Volcano', 'snow': 'Snow', 'space': 'Space'}
def lf(L, name):
    return next(f['__value'] for f in L['fieldInstances'] if f['__identifier'] == name)
picked, count, space_kinds = [], {}, {}
for n, L in enumerate(src['levels']):
    sec = lf(L, 'section')
    if sec == 'space':  # two of each space screen kind (lift, landing deck, asteroids, spacewalk, laser deck, gate, core)
        kind = re.sub(r'\d+$', '', L['identifier'].split('_', 1)[1])
        space_kinds[kind] = space_kinds.get(kind, 0) + 1
        if space_kinds[kind] > 2: continue
    else:
        count[sec] = count.get(sec, 0) + 1
        if count[sec] > PICK[sec]: continue
    picked.append((n, L))

# ---------------- entity defs: scaled copies of the world-unit defs ----------------
S_ENT = next(e for e in sample['defs']['entities'] if e['identifier'] == 'EntityFieldsTest')
S_FIELD = sample['defs']['entities'][0]['fieldDefs'][0]
S_LAYER_I = next(l for l in sample['defs']['layers'] if l['type'] == 'IntGrid')
S_LAYER_E = next(l for l in sample['defs']['layers'] if l['type'] == 'Entities')
S_TS = sample['defs']['tilesets'][0]

old_atlas = Image.open(os.path.join(SRC, 'sprites.png')).convert('RGBA')
remap = {}   # old def uid -> new def
new_defs = []
tiles = []
for e in src['defs']['entities']:
    d = copy.deepcopy(e); d['uid'] = uid()
    for f in d['fieldDefs']: f['old'] = f['uid']; f['uid'] = uid()
    d['width'] = max(1, round(e['width'] / 4)); d['height'] = max(1, round(e['height'] / 4))
    if e['tileRect']:
        t = e['tileRect']
        img = old_atlas.crop((t['x'], t['y'], t['x'] + t['w'], t['y'] + t['h']))
        img = img.resize((max(1, round(t['w'] / 4)), max(1, round(t['h'] / 4))), Image.NEAREST)
        tiles.append((d, img))
    remap[e['uid']] = d; new_defs.append(d)

# items sheet -> enum icons and an "Item" picture per value
items_sheet = Image.open(os.path.join(ITEMS, 'sheet.png')).convert('RGBA')
ITEM_IDS = []
for key, it in items['items'].items() if 'items' in items else items.items():
    pass
item_map = items['items'] if 'items' in items else items
for key, it in item_map.items():
    if not isinstance(it, dict) or 'sheet_xy' not in it: continue
    x, y = it['sheet_xy']; ITEM_IDS.append((key, it, items_sheet.crop((x, y, x + it['frame_w'], y + it['frame_h']))))

# pack the sprite atlas (entity pictures, then item icons)
AW, x, y, rowh = 512, 0, 0, 0
placed = []
for owner, img in [(d, im) for d, im in tiles] + [(('item', k), im) for k, _, im in ITEM_IDS]:
    w, h = img.size
    if x + w > AW: x, y, rowh = 0, y + rowh + 1, 0
    placed.append((owner, img, x, y)); x += w + 1; rowh = max(rowh, h)
AH = y + rowh
atlas = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
TS_UID = uid(); ITEM_RECT = {}
for owner, img, ax, ay in placed:
    atlas.paste(img, (ax, ay))
    r = {'tilesetUid': TS_UID, 'x': ax, 'y': ay, 'w': img.size[0], 'h': img.size[1]}
    if isinstance(owner, tuple): ITEM_RECT[owner[1]] = r
    else: owner['tileRect'] = r; owner['tilesetId'] = TS_UID
atlas.save(os.path.join(DST, 'sprites.png'), optimize=True)

# ---------------- enums ----------------
def enum(ident, vals, icons=None):
    u = uid()
    return {'identifier': ident, 'uid': u, 'values': [{'id': v, 'tileRect': (icons or {}).get(v), 'color': c} for v, c in vals],
            'iconTilesetUid': TS_UID if icons else None, 'externalRelPath': None, 'externalFileChecksum': None, 'tags': []}
def hexint(h): return int(h.lstrip('#'), 16)
E_SECTION = enum('Section', [(v, hexint(c)) for v, c in [('House', '#b86f50'), ('Dojo', '#e4a672'), ('Bamboo', '#3e8948'), ('Climb', '#0099db'), ('Rooftop', '#5a6988'),
                                                         ('Lake', '#124e89'), ('Volcano', '#e43b44'), ('Snow', '#c0cbdc'), ('Space', '#68386c')]])
E_BEAT = enum('Beat', [(v, hexint(c)) for v, c in [('Warmup', '#63c74d'), ('Challenge', '#e43b44'), ('Rest', '#2ce8f5'), ('Checkpoint', '#fee761'),
                                                   ('SetPiece', '#b55088'), ('Finale', '#feae34')]])
ITEM_NAMES = {k: re.sub(r'(^|_)(\w)', lambda m: m.group(2).upper(), k) for k, _, _ in ITEM_IDS}
E_ITEM = enum('Item', [(ITEM_NAMES[k], 0xead4aa) for k, _, _ in ITEM_IDS], {ITEM_NAMES[k]: ITEM_RECT[k] for k, _, _ in ITEM_IDS})

# ---------------- field helpers ----------------
def fdef(ident, typ, null=True, arr=False, enum_def=None, show='NameAndValue', doc=None, mn=None, mx=None, default=None):
    d = copy.deepcopy(S_FIELD)
    if enum_def:
        t, tt = f"F_Enum({enum_def['uid']})", f"LocalEnum.{enum_def['identifier']}"
    else:
        t, tt = {'Int': ('F_Int', 'Int'), 'Float': ('F_Float', 'Float'), 'Bool': ('F_Bool', 'Bool'), 'String': ('F_String', 'String')}[typ]
    if arr: tt = f'Array<{tt}>'
    dv = None
    if default is not None:
        dv = {'id': {'Int': 'V_Int', 'Float': 'V_Float'}.get(typ, 'V_String'), 'params': [default]}
    d.update(identifier=ident, doc=doc, __type=tt, uid=uid(), type=t, isArray=arr, canBeNull=null, editorDisplayMode=show,
             editorDisplayPos='Above', editorAlwaysShow=False, editorShowInWorld=True, min=mn, max=mx, defaultOverride=dv, searchable=False)
    d['_typ'] = typ; d['_enum'] = enum_def is not None
    return d
def finst(fd, v):
    if fd['isArray']:
        v = v or []
        rev = [{'id': 'V_String', 'params': [x]} for x in v]
    elif v is None: rev = []
    elif fd['_enum'] or fd['_typ'] == 'String': rev = [{'id': 'V_String', 'params': [v]}]
    elif fd['_typ'] == 'Bool': rev = [{'id': 'V_Bool', 'params': [True]}] if v else [None]
    elif fd['_typ'] == 'Int': v = int(v); rev = [{'id': 'V_Int', 'params': [v]}]
    else: v = float(v); rev = [{'id': 'V_Float', 'params': [v]}]
    if fd['_typ'] == 'Bool' and v is None: v = False
    return {'__identifier': fd['identifier'], '__type': fd['__type'], '__value': v, '__tile': None, 'defUid': fd['uid'], 'realEditorValues': rev}
for d in new_defs:
    for f in d['fieldDefs']: f['_typ'] = f['__type'] if f['__type'] in ('Int', 'Float', 'Bool', 'String') else 'String'; f['_enum'] = False

# ---------------- new spawn entities ----------------
def ent_def(ident, color, w, h, pivot, fields, doc, tag, hollow=False, resizable=False, tile=None):
    e = copy.deepcopy(S_ENT)
    e.update(identifier=ident, uid=uid(), tags=[tag], exportToToc=False, allowOutOfBounds=False, doc=doc, width=w, height=h,
             resizableX=resizable, resizableY=resizable, minWidth=None, maxWidth=None, minHeight=None, maxHeight=None, keepAspectRatio=False,
             tileOpacity=1, fillOpacity=0.15 if hollow else 0.35, lineOpacity=1, hollow=hollow, color=color,
             renderMode='Tile' if tile else 'Rectangle', showName=True, tilesetId=TS_UID if tile else None, tileRenderMode='FitInside',
             tileRect=tile, uiTileRect=None, nineSliceBorders=[], maxCount=0, limitScope='PerLevel', limitBehavior='MoveLastOne',
             pivotX=pivot[0], pivotY=pivot[1], fieldDefs=fields)
    return e
first_item = ITEM_RECT[ITEM_IDS[0][0]]
D_ITEM = ent_def('ItemSpawn', '#FEE761', 16, 16, (0.5, 1), [
    fdef('chance', 'Float', null=False, show='ValueOnly', doc='0 to 1: how likely an item appears here each run.', mn=0, mx=1, default=0.5),
    fdef('pool', None, arr=True, enum_def=E_ITEM, show='Hidden', doc='Items that may appear here (one is picked). Empty = any item allowed in this section.'),
    fdef('group', 'String', show='Hidden', doc='Optional: spawns sharing a group name give at most one item between them.')],
    'A spot where a random item may appear. Bottom-centre is where the item stands.', 'Spawns', tile=first_item)
D_VAR = ent_def('VariantZone', '#B55088', 64, 64, (0, 0), [
    fdef('group', 'String', null=False, show='NameAndValue', doc='Zones with the same group name are alternatives.', default='A'),
    fdef('variant', 'Int', null=False, show='NameAndValue', doc='Each run keeps one variant of the group; the others are removed with everything inside them.', default=1),
    fdef('weight', 'Float', null=False, show='Hidden', default=1.0)],
    'Pick-one region: everything inside belongs to this variant. Make two or more zones with the same group and different variant numbers.',
    'Spawns', hollow=True, resizable=True)
D_HAZ = ent_def('HazardSpawn', '#E43B44', 16, 16, (0.5, 1), [
    fdef('chance', 'Float', null=False, show='ValueOnly', mn=0, mx=1, default=0.5),
    fdef('kind', 'String', show='NameAndValue', doc='Which hazard or prop entity to place (its name), e.g. LaserGate, SteppingSlab.')],
    'A spot where a hazard or prop may appear.', 'Spawns')
spawn_defs = [D_ITEM, D_VAR, D_HAZ]

# ---------------- level fields ----------------
LF = [fdef('section', None, null=False, enum_def=E_SECTION, show='ValueOnly', doc='Which section this chunk can appear in.'),
      fdef('beats', None, arr=True, enum_def=E_BEAT, show='ValueOnly', doc='Beat slots this chunk can fill in the section\'s beat list.'),
      fdef('difficulty', 'Int', null=False, show='NameAndValue', mn=1, mx=5, default=2, doc='1 easy to 5 hard.'),
      fdef('weight', 'Float', null=False, show='Hidden', default=1.0, doc='How often it is picked relative to other chunks that fit.'),
      fdef('setPiece', 'Bool', null=False, show='Hidden', doc='Placed by the beat list on purpose, never at random (the rooftop climb, the finale).'),
      fdef('void', 'Bool', null=False, show='Hidden', doc='No ground: falling out costs a heart.'),
      fdef('slide', 'Bool', null=False, show='Hidden', doc='Snow: slopes slide 我 back.'),
      fdef('vacuum', 'Bool', null=False, show='Hidden', doc='Spacewalk physics.'),
      fdef('gravityScale', 'Float', show='Hidden'), fdef('speedScale', 'Float', show='Hidden'),
      fdef('fromScreen', 'String', show='Hidden', doc='The prototype screen this chunk was made from.')]

# ---------------- layers ----------------
INT_VALUES = [(1, 'ground', '#733E39'), (2, 'platform', '#C0CBDC'), (3, 'water', '#0099DB'), (4, 'lava', '#F77622'), (5, 'wall', '#3A4466')]
L_SPAWN, L_ENT, L_INT = uid(), uid(), uid()
lay_s = copy.deepcopy(S_LAYER_E); lay_s.update(identifier='Spawns', uid=L_SPAWN, gridSize=G, doc='Random parts: item spawns, hazard spawns, pick-one zones.')
lay_e = copy.deepcopy(S_LAYER_E); lay_e.update(identifier='Entities', uid=L_ENT, gridSize=G, doc='Fixed props and climbing pieces (pictures from the prototype).')
lay_i = copy.deepcopy(S_LAYER_I); lay_i.update(identifier='Terrain', uid=L_INT, gridSize=G, displayOpacity=0.55, tilesetDefUid=None, autoRuleGroups=[],
                                               doc='Collision terrain. Tile auto-layers will read this once the art bundles are in.',
                                               intGridValues=[{'value': v, 'identifier': n, 'color': c, 'tile': None, 'groupUid': 0} for v, n, c in INT_VALUES])

# ---------------- levels ----------------
levels, rows, rowY = [], {}, 0
for n, L in picked:
    r = info[n]
    sec = lf(L, 'section'); S = SECTION[sec]
    climb = sec == 'climb'
    LHw = L['pxHei']; Hn = CH if not climb else math.ceil(LHw / 4 / G) * G
    floorW = (LHw - 640) + WFLOOR; floorN = Hn - G
    tx = lambda xw: xw / 4
    ty = lambda yw: (yw - floorW) / 4 + floorN
    # terrain
    cw, ch = CW // G, Hn // G
    g = np.zeros((ch, cw), dtype=int)
    old = next(li for li in L['layerInstances'] if li['__type'] == 'IntGrid')
    og = np.array(old['intGridCsv']).reshape(old['__cHei'], old['__cWid'])
    # resample: a new cell takes the most common non-empty old value under it (old cells are 10 world units)
    for cy in range(ch):
        for cx in range(cw):
            x0w, x1w = cx * G * 4, (cx + 1) * G * 4
            y0w = (cy * G - floorN) * 4 + floorW; y1w = y0w + G * 4
            sub = og[max(0, int(y0w // 10)):max(0, int(math.ceil(y1w / 10))), int(x0w // 10):int(math.ceil(x1w / 10))]
            sub = sub[sub > 0]
            if sub.size * 2 >= ((y1w - y0w) / 10) * ((x1w - x0w) / 10) * (0.5 if climb else 1):
                v = np.bincount(sub).argmax()
                g[cy, cx] = {1: 1, 2: 3, 3: 4, 4: 2, 5: 5}[v]
    if not lf(L, 'void') and not climb:
        g[ch - 1, :] = np.where(g[ch - 1, :] == 0, 1, g[ch - 1, :])
    # entities
    li_old = next(li for li in L['layerInstances'] if li['__type'] == 'Entities')
    einst = []
    for e in li_old['entityInstances']:
        d = remap[e['defUid']]
        w, h = max(1, round(e['width'] / 4)), max(1, round(e['height'] / 4))
        px = [round(tx(e['px'][0])), round(ty(e['px'][1]))]
        fis = []
        for f in d['fieldDefs']:
            ov = next((fi['__value'] for fi in e['fieldInstances'] if fi['defUid'] == f['old']), None)
            if f['__type'] == 'Int' and ov is not None and f['identifier'] in ('cx0', 'cx1', 'bx', 'bw'): ov = round(ov / 4)
            if f['__type'] == 'Int' and ov is not None and f['identifier'] in ('cy0', 'cy1', 'bh', 'driftRange'): ov = round(ov / 4)
            fis.append(finst(f, ov))
        einst.append(dict(d=d, px=px, w=w, h=h, fis=fis))
    # a few starter item spawns so the idea is visible: on top of the first two props, chance 0.5
    spawns = []
    tops = sorted([e for e in einst if e['d']['pivotY'] == 0 and not e['d']['identifier'].startswith('Decor')], key=lambda e: e['px'][0])[:2]
    for e in tops:
        spawns.append(dict(d=D_ITEM, px=[e['px'][0], e['px'][1]], w=16, h=16, fis=[finst(D_ITEM['fieldDefs'][0], 0.5), finst(D_ITEM['fieldDefs'][1], []), finst(D_ITEM['fieldDefs'][2], None)]))
    # reference picture (the prototype's own drawing, floor moved onto the tile edge)
    bg = Image.open(os.path.join(RENDERS, f'bg_{n}.png')).convert('RGBA')
    ref = Image.new('RGBA', (CW, Hn), (0, 0, 0, 0))
    dy = round(floorN - (bg.size[1] - 640 / 4 + WFLOOR / 4))
    ref.paste(bg, (0, dy))
    if dy > 0: ref.paste(bg.crop((0, 0, CW, 1)).resize((CW, dy)), (0, 0))
    name = f"{S}_{len([l for l in levels if l['_sec'] == S]) + 1:02d}"
    refp = f'reference/{name}.png'; ref.save(os.path.join(DST, refp), optimize=True)
    beats = {'House': ['Warmup'], 'Climb': ['SetPiece'], 'Space': ['Challenge']}.get(S, ['Challenge'])
    if 'Core' in L['identifier'] or 'Gate' in L['identifier']: beats = ['Finale']
    if 'Lift' in L['identifier'] or 'Elevator' in L['identifier']: beats = ['SetPiece']
    vals = {'section': S, 'beats': beats, 'difficulty': 2, 'weight': 1.0, 'setPiece': beats[0] in ('SetPiece', 'Finale'),
            'void': lf(L, 'void'), 'slide': lf(L, 'slide'), 'vacuum': lf(L, 'vacuum'), 'gravityScale': lf(L, 'gravityScale'),
            'speedScale': lf(L, 'speedScale'), 'fromScreen': L['identifier']}
    levels.append(dict(_sec=S, name=name, H=Hn, g=g, ents=einst, spawns=spawns, ref=refp, vals=vals))

# world: one row per section, chunks left to right with a small gap (they join seamlessly in the game)
x_of, y_of, rowY, cur = {}, {}, 0, None
rowH = {}
for L in levels:
    if L['_sec'] != cur:
        if cur is not None: rowY += rowH[cur] + 96
        cur = L['_sec']; x = 0
    L['wx'] = x; L['wy'] = rowY; x += CW + 32; rowH[cur] = max(rowH.get(cur, 0), L['H'])

# ---------------- assemble ----------------
ts = copy.deepcopy(S_TS)
ts.update(__cWid=math.ceil(AW / G), __cHei=math.ceil(AH / G), identifier='PrototypeSprites', uid=TS_UID, relPath='sprites.png', embedAtlas=None, pxWid=AW, pxHei=AH,
          tileGridSize=G, spacing=0, padding=0, tags=[], tagsSourceEnumUid=None, enumTags=[], customData=[], savedSelections=[], cachedPixelData=None)
def clean(d):
    d = copy.deepcopy(d)
    for f in d['fieldDefs']:
        for k in ('old', '_typ', '_enum'): f.pop(k, None)
    return d
def inst(e, L, lay):
    d = e['d']
    return {'__identifier': d['identifier'], '__grid': [e['px'][0] // G, e['px'][1] // G], '__pivot': [d['pivotX'], d['pivotY']], '__tags': d['tags'],
            '__tile': d['tileRect'], '__smartColor': d['color'], 'iid': iid(), 'width': e['w'], 'height': e['h'], 'defUid': d['uid'], 'px': e['px'],
            'fieldInstances': e['fis'], '__worldX': L['wx'] + e['px'][0], '__worldY': L['wy'] + e['px'][1]}
order = ['__identifier', '__type', '__cWid', '__cHei', '__gridSize', '__opacity', '__pxTotalOffsetX', '__pxTotalOffsetY', '__tilesetDefUid', '__tilesetRelPath',
         'iid', 'levelId', 'layerDefUid', 'pxOffsetX', 'pxOffsetY', 'visible', 'optionalRules', 'intGridCsv', 'autoLayerTiles', 'seed', 'overrideTilesetUid', 'gridTiles', 'entityInstances']
out_levels = []
for k, L in enumerate(levels):
    cw, ch = CW // G, L['H'] // G
    def layer(ident, typ, luid, ents=(), csv=(), op=1):
        li = {'__identifier': ident, '__type': typ, '__cWid': cw, '__cHei': ch, '__gridSize': G, '__opacity': op, '__pxTotalOffsetX': 0, '__pxTotalOffsetY': 0,
              '__tilesetDefUid': None, '__tilesetRelPath': None, 'iid': iid(), 'levelId': k, 'layerDefUid': luid, 'pxOffsetX': 0, 'pxOffsetY': 0,
              'visible': True, 'optionalRules': [], 'intGridCsv': list(csv), 'autoLayerTiles': [], 'seed': 100 + k, 'overrideTilesetUid': None,
              'gridTiles': [], 'entityInstances': [inst(e, L, ident) for e in ents]}
        return {o: li[o] for o in order}
    out_levels.append({'identifier': L['name'], 'iid': iid(), 'uid': k, 'worldX': L['wx'], 'worldY': L['wy'], 'worldDepth': 0, 'pxWid': CW, 'pxHei': L['H'],
                       '__bgColor': '#181425', 'bgColor': '#181425', 'useAutoIdentifier': False, 'bgRelPath': L['ref'], 'bgPos': 'Unscaled', 'bgPivotX': 0, 'bgPivotY': 0,
                       '__smartColor': '#8B9BB4', '__bgPos': {'topLeftPx': [0, 0], 'scale': [1, 1], 'cropRect': [0, 0, CW, L['H']]}, 'externalRelPath': None,
                       'fieldInstances': [finst(f, L['vals'].get(f['identifier'])) for f in LF], '__neighbours': [],
                       'layerInstances': [layer('Spawns', 'Entities', L_SPAWN, L['spawns']), layer('Entities', 'Entities', L_ENT, L['ents']),
                                          layer('Terrain', 'IntGrid', L_INT, csv=[int(v) for v in L['g'].flatten()], op=0.55)]})

proj = {k: copy.deepcopy(v) for k, v in sample.items() if k not in ('defs', 'levels', 'worlds', 'toc')}
proj.update(iid=iid(), nextUid=uid() + 1, identifierStyle='Free', toc=[], worldLayout='Free', worldGridWidth=CW, worldGridHeight=CH,
            defaultLevelWidth=CW, defaultLevelHeight=CH, defaultPivotX=0, defaultPivotY=0, defaultGridSize=G, defaultEntityWidth=16, defaultEntityHeight=16,
            bgColor='#262B44', defaultLevelBgColor='#181425', minifyJson=False, externalLevels=False, exportTiled=False, simplifiedExport=False,
            imageExportMode='None', exportLevelBg=True, pngFilePattern=None, backupOnSave=True, backupLimit=10, backupRelPath=None,
            levelNamePattern='Chunk%idx', tutorialDesc='Punch Your Friend chunk library: 16 px tiles, art pixels. See README.md.',
            customCommands=[], flags=['UseMultilinesType'], dummyWorldIid=iid())
proj['defs'] = {'layers': [lay_s, lay_e, lay_i], 'entities': spawn_defs + [clean(d) for d in new_defs], 'tilesets': [ts], 'enums': [E_SECTION, E_BEAT, E_ITEM],
                'externalEnums': [], 'levelFields': [clean({'fieldDefs': LF})['fieldDefs'][i] for i in range(len(LF))]}
for e in spawn_defs:
    for f in e['fieldDefs']: f.pop('_typ', None); f.pop('_enum', None)
proj['levels'] = out_levels; proj['worlds'] = []
proj = {k: proj[k] for k in sample.keys()}
CSV = {}
for lv in proj['levels']:
    for li in lv['layerInstances']:
        if li['intGridCsv']:
            key = '@@' + li['iid'] + '@@'; CSV[key] = ','.join(map(str, li['intGridCsv'])); li['intGridCsv'] = key
txt = json.dumps(proj, indent='\t')
for key, v in CSV.items(): txt = txt.replace('"' + key + '"', '[' + v + ']')
open(os.path.join(DST, 'punch-your-friend.ldtk'), 'w').write(txt)
print('chunks', len(out_levels), {s: sum(1 for l in levels if l['_sec'] == s) for s in SECTION.values()}, 'items', len(ITEM_IDS), 'atlas', AW, AH)
