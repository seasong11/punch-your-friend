# Art resources

Source art for Punch Your Friend. The game itself stays one file (`index.html`): art from here is cleaned to the
grid and the Endesga 64 palette, then embedded in `index.html`. Nothing in this folder is loaded by the page.

## Folders

| Folder | What goes in it |
| --- | --- |
| `characters/<number>-<name>/` | PixelLab results for that character. `rotations/` holds the 8 reference views. `south-east.png`, the side view that faces the audience, is the one the moves are built from. One PNG per action sits next to it |
| `characters/tools/` | `build_moves.py`, which rebuilds every action PNG from the south-east sprites |
| `characters/lineup.html` | The character lineup page: every sprite, skill and move preview. Open it in a browser |
| `backgrounds/` | Stage backgrounds, tiles and props |
| `effects/` | Effect sprites (most effects come from pixelfx in code) |
| `palette/` | Endesga 64, the game palette. Upload `palette-endesga64-1px.png` to PixelLab as the target palette |

## Naming

`<number>-<character>-<action>.png`, for example `characters/1-hoodie-guy/1-hoodie-guy-run.png`.

Characters: 1 hoodie-guy, 2 monk, 3 ninja, 4 free-runner, 5 diver, 6 firefighter, 7 climber, 8 astronaut, 9 shiba-dog.

Actions: idle, run, jump, block, dash, hurt, ladder, skill, taunt, and the stage moves stairs, slope, slip, dive,
swim, hook, float.

## Action sheets

Each action PNG is a strip of 64x64 frames, read left to right. The feet sit on row 60 and the figure is centred on
column 32; dive, swim and float are centred in the cell instead. `<number>-<character>-all-moves.png` holds all 26
frames in this order: idle 2, run 4, jump 2, block 1, ladder 2, skill 2, stairs 2, slope 2, slip 1, dive 2, swim 2,
hook 2, float 2.

The frames are made by `characters/tools/build_moves.py` (needs Pillow; run `python3 art/characters/tools/build_moves.py`
from the repo root). It splits each south-east sprite into parts (body, arms, legs, and extras such as the Monk's robe
skirt or the Ninja's headband tails) and shifts, slants, shortens or turns those parts. No pixel is repainted, and the
first idle frame is the untouched sprite.

Known limits of that method:

- Monk, Diver, Firefighter and Climber hold gear or joined hands, so only their legs and body move.
- Dive is the jump pose turned upside down and swim is the run pose turned on its side. The Shiba Dog paddles upright.
- The Shiba Dog is on four legs, so its ladder and hook sheets are only a tilted jump pose.
- The Climber's blue motion streak is shown only in the skill frames.
- dash, hurt and taunt are not made yet.
- The frames were checked as stills. They are not embedded in `index.html` yet.

## Uploading from the GitHub website

Open the character's folder, then **Add file → Upload files**, drag the PNGs in, and commit.
