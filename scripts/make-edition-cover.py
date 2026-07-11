#!/usr/bin/env python3
"""Render a Grewal RE Group Library edition cover: brand-fonts + gold rules
over a full-bleed photo, matching the Relocation Edition cover treatment.
Uses headless Chrome (already installed) exactly like the guide pipeline."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / 'assets' / 'fonts'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'GRG Serif'; src: url('file://{serif_bold}') format('truetype'); font-weight: 700; }}
@font-face {{ font-family: 'GRG Sans'; src: url('file://{sans}') format('truetype'); font-weight: 600; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1200px; height: 1680px; overflow: hidden; }}
.cover {{ position: relative; width: 1200px; height: 1680px; background: #000; }}
.cover img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: {photo_opacity}; }}
.cover::after {{ content: ""; position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,.94) 0%, rgba(0,0,0,.35) 45%, rgba(0,0,0,.55) 100%); }}
.frame {{ position: absolute; inset: 46px; border: 1.5px solid rgba(184,150,62,.55); z-index: 3; }}
.content {{ position: absolute; inset: 0; z-index: 4; display: flex; flex-direction: column; justify-content: flex-end; padding: 110px 90px; color: #fff; }}
.kicker {{ font-family: 'GRG Sans', sans-serif; font-weight: 600; font-size: 22px; letter-spacing: 6px; text-transform: uppercase; color: #d4b366; margin-bottom: 28px; }}
.rule {{ width: 90px; height: 2px; background: #B8963E; margin-bottom: 28px; }}
.title {{ font-family: 'GRG Serif', serif; font-weight: 700; font-size: {title_size}px; line-height: 1.02; letter-spacing: -0.01em; }}
.title em {{ font-style: italic; color: #d4b366; display: block; font-weight: 700; }}
.sub {{ font-family: 'GRG Sans', sans-serif; font-size: 24px; margin-top: 26px; color: rgba(255,255,255,.82); max-width: 800px; line-height: 1.5; }}
.imprint {{ font-family: 'GRG Sans', sans-serif; font-weight: 600; font-size: 18px; letter-spacing: 4px; text-transform: uppercase; color: rgba(255,255,255,.68); margin-top: 60px; }}
</style></head>
<body>
<div class="cover">
  <img src="file://{photo}">
  <div class="frame"></div>
  <div class="content">
    <div class="kicker">{kicker}</div>
    <div class="rule"></div>
    <div class="title">{title_html}</div>
    <div class="sub">{sub}</div>
    <div class="imprint">Grewal RE Group</div>
  </div>
</div>
</body></html>"""

EDITIONS = [
    dict(slug='westlake-edition', kicker='Neighborhood Edition',
         title_html='The<br><em>Westlake</em><br>Edition', title_size=92,
         sub='Zones, schools, and homes on the market now in Westlake Hills.',
         photo='westlake-bg.jpg'),
    dict(slug='tarrytown-edition', kicker='Neighborhood Edition',
         title_html='The<br><em>Tarrytown</em><br>Edition', title_size=88,
         sub='Old Austin charm on Lake Austin, block by block.',
         photo='tarrytown-bg.jpg'),
    dict(slug='buying-edition', kicker='Process Guide',
         title_html='The<br><em>Buying</em><br>Edition', title_size=96,
         sub='Search to keys: the complete Grewal RE Group playbook.',
         photo='buying-bg.jpg'),
    dict(slug='selling-edition', kicker='Process Guide',
         title_html='The<br><em>Selling</em><br>Edition', title_size=96,
         sub='Pricing, prep, and top-dollar strategy, start to close.',
         photo='selling-bg.jpg'),
    dict(slug='results-edition', kicker='Client Stories',
         title_html='The<br><em>Results</em><br>Edition', title_size=96,
         sub='How Grewal RE Group has helped, told honestly.',
         photo='results-bg.jpg'),
    dict(slug='client-experience', kicker='Client Experience',
         title_html='Working With<br><em>Grewal RE Group</em>', title_size=68,
         sub='What it is actually like, from first call to closing day.',
         photo='client-bg.jpg'),
]


def main():
    src_dir = Path(sys.argv[1])
    out_dir = ROOT / 'assets' / 'covers'
    out_dir.mkdir(parents=True, exist_ok=True)
    serif_bold = FONTS / 'GrewalREGroupSerif-Bold.ttf'
    sans = FONTS / 'GrewalREGroupSans-Bold.ttf'

    for ed in EDITIONS:
        photo = src_dir / ed['photo']
        html = TEMPLATE.format(
            serif_bold=serif_bold, sans=sans,
            photo=photo, photo_opacity=0.72,
            kicker=ed['kicker'], title_html=ed['title_html'],
            title_size=ed['title_size'], sub=ed['sub'],
        )
        html_path = out_dir / f"{ed['slug']}.html"
        html_path.write_text(html, encoding='utf-8')
        png_path = out_dir / f"{ed['slug']}.png"
        subprocess.run([
            CHROME, '--headless', '--disable-gpu', '--screenshot=' + str(png_path),
            '--window-size=1200,1680', '--default-background-color=00000000',
            'file://' + str(html_path),
        ], check=True, capture_output=True)
        jpg_path = out_dir / f"{ed['slug']}.jpg"
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '90',
                         str(png_path), '--out', str(jpg_path)], check=True, capture_output=True)
        png_path.unlink()
        html_path.unlink()
        print(f"cover: {ed['slug']}.jpg")


if __name__ == '__main__':
    main()
