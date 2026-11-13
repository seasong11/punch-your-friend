import json, sys
from PIL import Image, ImageDraw
D = sys.argv[1]; d = json.load(open(D + '/punch-your-friend.ldtk'))
atlas = Image.open(D + '/sprites.png').convert('RGBA')
cols = {v['value']: v['color'] for v in d['defs']['layers'][1]['intGridValues']}
defs = {e['uid']: e for e in d['defs']['entities']}
def level_img(L, grid=True):
    im = Image.open(D + '/' + L['bgRelPath']).convert('RGBA')
    li_e, li_i = L['layerInstances']
    if grid:
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); dr = ImageDraw.Draw(ov); g = li_i['__gridSize']; cw = li_i['__cWid']
        for k, v in enumerate(li_i['intGridCsv']):
            if v: c = cols[v]; dr.rectangle([(k % cw) * g, (k // cw) * g, (k % cw) * g + g - 1, (k // cw) * g + g - 1], fill=tuple(int(c[j:j + 2], 16) for j in (1, 3, 5)) + (90,))
        im = Image.alpha_composite(im, ov)
    dr = ImageDraw.Draw(im)
    for e in li_e['entityInstances']:
        df = defs[e['defUid']]; x = e['px'][0] - df['pivotX'] * e['width']; y = e['px'][1] - df['pivotY'] * e['height']
        t = e['__tile']
        if t: im.alpha_composite(atlas.crop((t['x'], t['y'], t['x'] + t['w'], t['y'] + t['h'])).resize((e['width'], e['height']), Image.NEAREST), (int(x), int(y)))
        dr.rectangle([x, y, x + e['width'] - 1, y + e['height'] - 1], outline=df['color'])
    return im
if sys.argv[2] == 'world':
    ls = d['levels']; x0 = min(l['worldX'] for l in ls); y0 = min(l['worldY'] for l in ls)
    x1 = max(l['worldX'] + l['pxWid'] for l in ls); y1 = max(l['worldY'] + l['pxHei'] for l in ls); k = 24
    out = Image.new('RGBA', ((x1 - x0) // k, (y1 - y0) // k), (38, 43, 68, 255))
    for L in ls:
        im = level_img(L, False); out.alpha_composite(im.resize((im.width // k, im.height // k), Image.NEAREST), ((L['worldX'] - x0) // k, (L['worldY'] - y0) // k))
    out.save(sys.argv[3]); print(out.size)
else:
    for n in sys.argv[3:]:
        level_img(d['levels'][int(n)]).save(f'prev_{n}.png')
