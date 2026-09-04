#!/usr/bin/env python3
"""P2-fix: Remove parent .v10-hero navy gradient background so .v10-hero-bg-{slug} shows.
Replace with `background: transparent`. The bg-{slug} + overlay-{slug} handle all visuals now.
"""
import re
from pathlib import Path

BASE_DIR = Path('/home/ubuntu/workspace/careerforge-site')
PAGES = ['immigration', 'education', 'career', 'tour']

for pillar in PAGES:
    for suffix in ['', '-cn', '-en']:
        fname = f"{pillar}{suffix}.html"
        p = BASE_DIR / fname
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        original = text

        # Replace `.v10-hero { background: linear-gradient(...); ... }` block's `background:` line with `background: transparent;`
        # Match the first `.v10-hero {` block (which contains the original navy gradient)
        # and replace its background property line
        text = re.sub(
            r'(\.v10-hero\s*\{\s*)background:\s*linear-gradient\([^;]+\);',
            r'\1background: transparent;',
            text,
            count=1
        )

        if text != original:
            p.write_text(text, encoding='utf-8')
            print(f"  ✓ {fname}: parent bg → transparent")
        else:
            print(f"  - {fname}: no change needed")