[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/romdhoncom/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/romdhoncom/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

# news-image-20261126

Thursday 26 November 2026 in one image — morning edition. A newspaper front page ("THE WORLD TODAY") summing up the day's world news: US tariffs on 14 partners, Russia's war dead near half a million, the Cairo tanker fire, the FCC clearing SpaceX's million-satellite Starmind plan, and the UK-EU reset deal, plus 24 more stories from the morning. Drawn by a pure Python standard-library program (own raster canvas, own 5x7 bitmap font, own PNG encoder — no PIL).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` runs `gen.py` with python3 when it can and copies the resulting `entry.png` to the output directory; when the generator cannot run (no python3, or a read-only repository) it copies the committed `entry.png` instead — the same bytes either way, since the generator is deterministic. Regenerate the image directly with `python3 gen.py` (two runs are byte-identical).

---

<sub>Entered on [make.fun](https://make.fun/?ref=j1qv1zx6&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
