# Art resources

Source art for Punch Your Friend. The game itself stays one file (`index.html`): art from here is cleaned to the
grid and the Endesga 64 palette, then embedded in `index.html`. Nothing in this folder is loaded by the page.

## Folders

| Folder | What goes in it |
| --- | --- |
| `characters/<number>-<name>/` | PixelLab results for that character: the reference views and one PNG per action |
| `backgrounds/` | Stage backgrounds, tiles and props |
| `effects/` | Effect sprites (most effects come from pixelfx in code) |
| `palette/` | Endesga 64, the game palette. Upload `palette-endesga64-1px.png` to PixelLab as the target palette |

## Naming

`<number>-<character>-<action>.png`, for example `characters/1-hoodie-guy/1-hoodie-guy-run.png`.

Characters: 1 hoodie-guy, 2 monk, 3 ninja, 4 free-runner, 5 diver, 6 firefighter, 7 climber, 8 astronaut, 9 shiba-dog.

Actions: idle, run, jump, block, dash, hurt, ladder, skill, taunt, and the stage moves stairs, slope, slip, dive,
swim, hook, float.

## Uploading from the GitHub website

Open the character's folder, then **Add file → Upload files**, drag the PNGs in, and commit.
