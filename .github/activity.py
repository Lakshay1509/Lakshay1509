"""Draw assets/activity.svg (+ dark copy) from the public GitHub contributions calendar. Stdlib only."""
import datetime
import re
import sys
import urllib.request
from pathlib import Path

user = sys.argv[1] if len(sys.argv) > 1 else 'Lakshay1509'
html = urllib.request.urlopen(f'https://github.com/users/{user}/contributions').read().decode()

counts = {m[1]: 0 if m[2] == 'No' else int(m[2].replace(',', ''))
          for m in re.finditer(r'for="(contribution-day-component-\d+-\d+)"[^>]*>(No|[\d,]+) contribution', html)}
cells = []  # (week, weekday, date, level, count)
for td in re.findall(r'<td[^>]*contribution-day-component[^>]*>', html):
    cid = re.search(r'id="(contribution-day-component-(\d+)-(\d+))"', td)
    date = re.search(r'data-date="([\d-]+)"', td)[1]
    level = int(re.search(r'data-level="(\d)"', td)[1])
    cells.append((int(cid[3]), int(cid[2]), date, level, counts.get(cid[1], 0)))

# ponytail: scrapes GitHub's HTML; if the markup changes this fails here instead of committing an empty chart
assert len(cells) > 300 and len(counts) > 300, f'parsed {len(cells)} cells, {len(counts)} counts'

X, Y, STEP, SIZE = 84, 80, 16, 13
total = sum(c[4] for c in cells)
best = max(cells, key=lambda c: c[4])
out = []
for week, day, date, level, n in cells:
    out.append(f'<rect x="{X + week * STEP}" y="{Y + day * STEP}" width="{SIZE}" height="{SIZE}" rx="2" '
               f'fill-opacity="{(.07, .3, .55, .8, 1)[level]}"><title>{n} on {date}</title></rect>')

last_col = -9
for week in sorted({c[0] for c in cells}):
    first = min(c[2] for c in cells if c[0] == week)
    if first[8:] <= '07' and week - last_col > 3:  # week holds the 1st-7th: a month starts here
        month = datetime.date.fromisoformat(first).strftime('%b').upper()
        out.append(f'<text class="m" fill-opacity=".6" x="{X + week * STEP}" y="70" font-size="10" letter-spacing="1.5">{month}</text>')
        last_col = week
for day, name in ((1, 'MON'), (3, 'WED'), (5, 'FRI')):
    out.append(f'<text class="m" fill-opacity=".45" x="48" y="{Y + day * STEP + 10}" font-size="9" letter-spacing="1">{name}</text>')
for i, op in enumerate((.07, .3, .55, .8, 1)):
    out.append(f'<rect x="{858 + i * 16}" y="206" width="{SIZE}" height="{SIZE}" rx="2" fill-opacity="{op}"/>')

svg = f'''<svg viewBox="0 0 1000 236" fill="#000000" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{total} contributions in the last year">
  <style>.m {{ font-family: ui-monospace, "SFMono-Regular", "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; fill: #000000; }}</style>
  <line x1="48" y1="40" x2="952" y2="40" stroke="#000000"/>
  <text class="m" fill-opacity=".6" x="48" y="28" font-size="11" letter-spacing="3.5">CONTRIBUTIONS · LAST 12 MONTHS</text>
  <text class="m" fill-opacity=".6" x="952" y="28" font-size="11" letter-spacing="3.5" text-anchor="end">{total:,} TOTAL</text>
  {chr(10).join('  ' + o for o in out).strip()}
  <text class="m" fill-opacity=".45" x="48" y="217" font-size="10" letter-spacing="1.5">best day {best[4]} on {best[2]} · updated {datetime.date.today()}</text>
  <text class="m" fill-opacity=".45" x="850" y="217" font-size="10" letter-spacing="1.5" text-anchor="end">less</text>
  <text class="m" fill-opacity=".45" x="944" y="217" font-size="10" letter-spacing="1.5">more</text>
</svg>
'''
assets = Path(__file__).resolve().parent.parent / 'assets'
(assets / 'activity.svg').write_text(svg)
(assets / 'dark' / 'activity.svg').write_text(svg.replace('#000000', '#FFFFFF'))
print(f'{len(cells)} days, {total} contributions')
