import json, sys
from PIL import Image, ImageDraw
D = sys.argv[1]; d = json.load(open(D + '/punch-your-friend.ldtk'))
atlas = Image.open(D + '/sprites.png').convert('RGBA')
lay = {l['uid']: l for l in d['defs']['layers']}
defs = {e['uid']: e for e in d['defs']['entities']}
def img(L):
    im = Image.open(D + '/' + L['bgRelPath']).convert('RGBA')
    for li in reversed(L['layerInstances']):
        if li['__type'] == 'IntGrid':
            cols = {v['value']: v['color'] for v in lay[li['layerDefUid']]['intGridValues']}
            ov = Image.new('RGBA', im.size); dr = ImageDraw.Draw(ov); g = li['__gridSize']; cw = li['__cWid']
            for k, v in enumerate(li['intGridCsv']):
                if v: c = cols[v]; dr.rectangle([(k % cw) * g, (k // cw) * g, (k % cw) * g + g - 1, (k // cw) * g + g - 1], fill=tuple(int(c[j:j+2], 16) for j in (1, 3, 5)) + (110,))
            im = Image.alpha_composite(im, ov)
        else:
            dr = ImageDraw.Draw(im)
            for e in li['entityInstances']:
                df = defs[e['defUid']]; x = e['px'][0] - df['pivotX'] * e['width']; y = e['px'][1] - df['pivotY'] * e['height']; t = e['__tile']
                if t: im.alpha_composite(atlas.crop((t['x'], t['y'], t['x'] + t['w'], t['y'] + t['h'])).resize((max(1,e['width']), max(1,e['height'])), Image.NEAREST), (int(x), int(y)))
                dr.rectangle([x, y, x + e['width'] - 1, y + e['height'] - 1], outline=df['color'])
    return im
names = sys.argv[3:]
ims = [img(next(L for L in d['levels'] if L['identifier'] == n)) for n in names]
out = Image.new('RGBA', (800, sum(i.height * 2 + 8 for i in ims)), (0, 0, 0, 255)); y = 0
for i in ims: out.paste(i.resize((i.width * 2, i.height * 2), Image.NEAREST), (0, y)); y += i.height * 2 + 8
out.save(sys.argv[2])
