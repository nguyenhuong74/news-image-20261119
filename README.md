# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/nguyenhuong74/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/nguyenhuong74/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# The World in One Page — Thursday 19 November 2026

A newspaper front page summing up Thursday 19 November 2026's world news — the first-ever Trump–Xi–Putin trilateral summit in Shenzhen, the ICJ ruling that Myanmar committed genocide against the Rohingya, Ukraine striking the Kerch Bridge a third time, Anthropic's record-breaking Nasdaq debut, deadly unrest in Bangladesh, and Denmark ratifying the Greenland security deal 109–0 — drawn in code as one 1024x1024 PNG with the Python standard library.

## How it works

`main.py` draws the whole front page programmatically: a hand-written 5x7 bitmap font for all text, simple geometric pictograms (globe, scales of justice, broken bridge, rising chart, flame, ice peaks), and a PNG encoder built from `zlib` + `struct`. No network, no time, no randomness, no dependencies — the grader runs it twice and both runs write byte-identical `entry.png` files.

Stories covered: Donald Trump, Xi Jinping and Vladimir Putin holding their first three-way summit in Shenzhen and issuing a joint declaration on nuclear risks; the International Court of Justice ruling 9–6 that Myanmar committed genocide against the Rohingya in 2017, the first time the court has held a state guilty of genocide; Ukraine hitting the railway section of the Crimean Bridge with Neptune missiles, the third strike in a week, halting train traffic; Anthropic debuting on Nasdaq at $83 a share and raising $81.3 billion, the largest IPO ever, at a $1.5 trillion valuation; a banned Awami League lockdown bringing bombs, arson and clashes to 28 districts of Bangladesh, killing four, with Nobel laureate Muhammad Yunus's ancestral home torched; and Denmark's parliament unanimously ratifying the US security deal for Greenland. The briefs strip adds Israel ending its first ground raid past the Gaza ceasefire line, the IAEA warning that North Korea has expanded its Yongbyon enrichment plant, and dozens missing after a migrant boat capsizes off Senegal.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, under 1 MiB), byte-identical on every run.

---

<sub>Entered on [make.fun](https://make.fun/?ref=6nfavmbn&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
