#!/usr/bin/env python3
"""P2: Patch 12 Pillar detail pages (immigration/education/career/tour × 3 langs)
with hero bg photo + navy overlay.
- immigration → 01-immigration.jpg (night harbour, overlay 0.88/0.72/0.88)
- education   → 02-education.jpg (daytime urban, overlay 0.78/0.58/0.78)
- career      → 03-career.jpg (night harbour, overlay 0.88/0.72/0.88)
- tour        → 04-tour.jpg (daytime HKUST, overlay 0.78/0.58/0.78)
"""
import re
from pathlib import Path

PILLAR_CONFIG = {
    'immigration': ('01-immigration.jpg', '0.88', '0.72', '0.88'),
    'education':   ('02-education.jpg',   '0.78', '0.58', '0.78'),
    'career':      ('03-career.jpg',      '0.88', '0.72', '0.88'),
    'tour':        ('04-tour.jpg',        '0.78', '0.58', '0.78'),
}

BASE_DIR = Path('/home/ubuntu/workspace/careerforge-site')

# CSS injection: replace `.v10-hero { ... }` opening rule with isolation + bg position,
# add bg + overlay rules after the closing brace. Use double braces for literal {} in CSS.
CSS_INJECT = """
.v10-hero {{ isolation: isolate; }}
.v10-hero-bg-{slug} {{
  position: absolute;
  inset: 0;
  background-image: url('assets/pillars/web/{img}');
  background-size: cover;
  background-position: center 40%;
  z-index: -2;
}}
.v10-hero-overlay-{slug} {{
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(11,25,44,{top}) 0%, rgba(11,25,44,{mid}) 50%, rgba(11,25,44,{bot}) 100%);
  z-index: -1;
}}
"""

# HTML injection: insert bg + overlay after <section class="v10-hero">
HTML_INJECT = """<section class="v10-hero">
  <div class="v10-hero-bg-{slug}"></div>
  <div class="v10-hero-overlay-{slug}"></div>
  <div class="v10-container">"""

def patch_file(html_path, pillar, img, top, mid, bot):
    text = html_path.read_text(encoding='utf-8')
    slug = pillar
    changed = False

    # 1. Insert CSS right after first `.v10-hero {` rule block (before the closing brace)
    #    Strategy: find the FIRST `.v10-hero {` and inject after its block
    css_block = CSS_INJECT.format(slug=slug, img=img, top=top, mid=mid, bot=bot)
    # match first `.v10-hero { ... }` block — but we want to insert AFTER the closing brace
    # Use marker: find first `.v10-hero {` then walk to its closing `}`
    m = re.search(r'(\.v10-hero\s*\{[^{}]*\})', text)
    if m:
        end = m.end()
        text = text[:end] + css_block + text[end:]
        changed = True

    # 2. Insert bg + overlay divs after <section class="v10-hero">
    html_block = HTML_INJECT.format(slug=slug)
    pattern = r'<section class="v10-hero">\s*\n(\s*)<div class="v10-container">'
    new_text, n = re.subn(pattern, html_block, text, count=1)
    if n:
        text = new_text
        changed = True
    else:
        # fallback: try without indent
        pattern2 = r'<section class="v10-hero">\s*<div class="v10-container">'
        new_text, n = re.subn(pattern2, html_block.replace('\n  ', '').replace('\n', ''), text, count=1)
        if n:
            text = new_text
            changed = True

    if changed:
        html_path.write_text(text, encoding='utf-8')
        print(f"  ✓ {html_path.name}: bg={img}, overlay={top}/{mid}/{bot}")
    else:
        print(f"  ✗ {html_path.name}: NO MATCH")

def main():
    for pillar, (img, top, mid, bot) in PILLAR_CONFIG.items():
        for suffix in ['', '-cn', '-en']:
            fname = f"{pillar}{suffix}.html"
            path = BASE_DIR / fname
            if path.exists():
                patch_file(path, pillar, img, top, mid, bot)
            else:
                print(f"  ! {fname} not found")

if __name__ == '__main__':
    main()