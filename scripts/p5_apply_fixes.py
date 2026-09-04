#!/usr/bin/env python3
"""
P5 Phase 2 Fix Script
Applies all WCAG AA + touch target + overflow fixes systematically.

Strategy:
- color contrast fixes: change specific class colors (not global var --gold)
  to avoid breaking hero gold (on dark bg, already passes)
- ink-500: darken #6B7A8A → #5B6A7A on each page root
- footer dark: lightens footer-audit + footer-bottom
- touch target: adds padding to small tap targets
- tour overflow: fixes mentor box on mobile
"""
import re
import sys
from pathlib import Path

SITE = Path('/home/ubuntu/workspace/careerforge-site')

# 24 files: 8 templates × 3 langs
FILES = []
for t in ['index', 'immigration', 'education', 'career', 'tour', 'cases', 'audit', 'consult']:
    FILES.append(SITE / f'{t}.html')          # TC
    FILES.append(SITE / f'{t}-cn.html')      # CN
    FILES.append(SITE / f'{t}-en.html')      # EN

# Color palette
GOLD_DARK = '#7A5E12'        # for gold text on white/cream (5.5:1)
GOLD_NAVY = '#0B192C'        # for big numbers if we want to swap to navy (best contrast)
SLATE_DARK = '#5B6A7A'       # for --ink-500 (4.9:1 on white)
EMERALD_DARK = '#047857'     # for audit-badge-pass (5.3:1)
FOOTER_LIGHT = '#A1A1A6'     # for footer text on dark bg (5.6:1)


def patch_file(path, old, new, label, count_holder):
    """Patch file: replace old with new if found."""
    if not path.exists():
        return False
    text = path.read_text()
    if old not in text:
        return False
    new_text = text.replace(old, new)
    path.write_text(new_text)
    count_holder[label] = count_holder.get(label, 0) + 1
    return True


def main():
    counts = {}

    for f in FILES:
        if not f.exists():
            print(f"  MISSING: {f.name}")
            continue
        text = f.read_text()
        original = text

        # ============ Touch target: hamburger (inline per file) ============
        # .hamburger has padding: 8px — bump to 12px so button is ≥44×44
        if '.hamburger' in text:
            # Add min-width/height + padding bump
            text = re.sub(
                r'(\.hamburger\s*\{[^}]*?padding:\s*)8px(;)',
                r'\g<1>12px\g<2>',
                text, count=1
            )
            if not re.search(r'\.hamburger\s*\{[^}]*?min-(?:width|height)', text):
                text = re.sub(
                    r'(\.hamburger\s*\{)',
                    r'\1\n  min-width: 44px;\n  min-height: 44px;',
                    text, count=1
                )

        # ============ Touch target: .v10-lang-btn ============
        # Often inline per page; bump padding/height to ≥44px
        text = re.sub(
            r'(\.v10-lang-btn\s*\{[^}]*?)(\n\})',
            r'\1\n  min-height: 44px;\n  padding-top: 12px;\n  padding-bottom: 12px;\2',
            text, count=1
        )

        # ============ Touch target: .v10-pillar (card link height) ============
        # Card link should have ≥44 height — add min-height
        text = re.sub(
            r'(\.v10-pillar\s*\{[^}]*?)(\n\})',
            r'\1\n  min-height: 44px;\2',
            text, count=1
        )

        # ============ Touch target: .nav-menu a (active) — bump padding 8→10 ============
        text = re.sub(
            r'(\.nav-menu a\.active\s*\{[^}]*?padding:\s*)8px 14px(;)',
            r'\g<1>10px 16px\g<2>',
            text
        )

        # ============ Tour-specific: mentor overflow fix ============
        # Only on pages that override it (6 pages: index, immigration, education, career, tour, audit)
        # cases and consult use different color tokens
        text = text.replace('--ink-500:     #6B7A8A;', f'--ink-500:     {SLATE_DARK};')
        text = text.replace('--ink-500: #6B7A8A;', f'--ink-500: {SLATE_DARK};')

        # ============ C2: gold eyebrow colors (--gold on white) → darker ============
        # Pattern: .eyebrow { ... color: var(--gold); ... }
        # Need to scope: only when on white bg. .eyebrow is used in white sections.
        # Safe to change globally because darker gold on dark hero also still has contrast.
        # But to be safe, change color values in specific class blocks.
        # Search for "color: var(--gold);" inside .eyebrow class block.

        # Replace specific gold color in eyebrow/cta-eyebrow blocks (not the global --gold var)
        # We'll do regex-based scoping.

        # .eyebrow class color
        text = re.sub(
            r'(\.eyebrow\s*\{[^}]*?color:\s*)var\(--gold[^)]*\)([^;]*;)',
            rf'\1{GOLD_DARK}\2',
            text, flags=re.DOTALL
        )
        text = re.sub(
            r'(\.eyebrow\s*\{[^}]*?color:\s*)#D4AF37([^;]*;)',
            rf'\1{GOLD_DARK}\2',
            text, flags=re.DOTALL
        )

        # .v10-cta-eyebrow color
        text = re.sub(
            r'(\.v10-cta-eyebrow\s*\{[^}]*?color:\s*)var\(--gold[^)]*\)([^;]*;)',
            rf'\1{GOLD_DARK}\2',
            text, flags=re.DOTALL
        )

        # .v10-track-tag color
        text = re.sub(
            r'(\.v10-track-tag\s*\{[^}]*?color:\s*)var\(--gold[^)]*\)([^;]*;)',
            rf'\1{GOLD_DARK}\2',
            text, flags=re.DOTALL
        )
        text = re.sub(
            r'(\.v10-track-tag\s*\{[^}]*?color:\s*)#B8941F([^;]*;)',
            rf'\1{GOLD_DARK}\2',
            text, flags=re.DOTALL
        )

        # .v10-tutor-summary-eyebrow color
        text = re.sub(
            r'(\.v10-tutor-summary-eyebrow\s*\{[^}]*?color:\s*)var\(--gold[^)]*\)([^;]*;)',
            rf'\1{GOLD_DARK}\2',
            text, flags=re.DOTALL
        )

        # .v10-why-num (large gold number)
        text = re.sub(
            r'(\.v10-why-num\s*\{[^}]*?color:\s*)var\(--gold[^)]*\)([^;]*;)',
            rf'\1{GOLD_DARK}\2',
            text, flags=re.DOTALL
        )

        # .v10-process-step-num (large gold number)
        text = re.sub(
            r'(\.v10-process-step-num\s*\{[^}]*?color:\s*)var\(--gold[^)]*\)([^;]*;)',
            rf'\1{GOLD_DARK}\2',
            text, flags=re.DOTALL
        )

        # .v10-package-tag (small uppercase gold label on white)
        text = re.sub(
            r'(\.v10-package-tag\s*\{[^}]*?color:\s*)var\(--gold[^)]*\)([^;]*;)',
            rf'\1{GOLD_DARK}\2',
            text, flags=re.DOTALL
        )

        # .v10-track-icon (gold icon on navy gradient — already passes 3:1 large,
        # but keep darker for consistency)
        text = re.sub(
            r'(\.v10-track-icon\s*\{[^}]*?color:\s*)var\(--gold[^)]*\)([^;]*;)',
            rf'\1{GOLD_DARK}\2',
            text, flags=re.DOTALL
        )

        # .v10-pillar-num (large gold pillar number) — actually light gold #E0C076 on #F7F8FA
        # Replace rgb(224,192,118) with darker variant
        text = text.replace(
            'rgb(224, 192, 118)',
            GOLD_DARK  # use darker gold on light bg for WCAG AA
        )

        # .audit-badge-pass color (emerald)
        text = re.sub(
            r'(\.audit-badge-pass\s*\{[^}]*?color:\s*)#10B981([^;]*;)',
            rf'\1{EMERALD_DARK}\2',
            text, flags=re.DOTALL
        )
        text = re.sub(
            r'(\.audit-badge-pass\s*\{[^}]*?color:\s*)#059669([^;]*;)',
            rf'\1{EMERALD_DARK}\2',
            text, flags=re.DOTALL
        )
        text = re.sub(
            r'(\.audit-badge-pass\s*\{[^}]*?color:\s*)var\(--success[^)]*\)([^;]*;)',
            rf'\1{EMERALD_DARK}\2',
            text, flags=re.DOTALL
        )

        # .audit-badge-fail color (red) — also for consistency, use darker red
        # (Currently #EF4444 on white = ~3.8:1, borderline pass for large text)
        text = re.sub(
            r'(\.audit-badge-fail\s*\{[^}]*?color:\s*)#EF4444([^;]*;)',
            r'\1#C62828\2',
            text, flags=re.DOTALL
        )

        # --green variable (used by audit-badge-pass via var(--green))
        text = re.sub(
            r'(--green:\s*)#10B981([^;]*;)',
            r'\1#047857\2',
            text
        )

        # .stat-label (cases page) — used on dark stat panel with `color: rgb(66,66,69)`
        # Change to lighter for dark bg contrast
        text = text.replace(
            '.stat-label { color: rgb(66,66,69); font-size: 0.78rem;',
            '.stat-label { color: #B8B8BC; font-size: 0.78rem;'
        )

        # Footer audit color in inline style blocks (rare - usually in style.css)
        # Skip — handled by style.css patch

        # ============ Tour-specific: mentor overflow fix ============
        if 'tour' in f.name:
            # .v10-tour-mentor-icon: width fit-content + center
            text = re.sub(
                r'(\.v10-tour-mentor-icon\s*\{[^}]*?)(\}\s*\.v10-tour-mentor-body)',
                r'\1\n  width: fit-content;\n  justify-self: center;\n  margin: 0 auto;\2',
                text, count=1
            )
            # Detail pill: switch from inline-block to block so width:100% works
            text = re.sub(
                r'(\.v10-tour-mentor-detail\s*\{[^}]*?)(\n\})',
                r'\1\n  display: block;\n  max-width: 100%;\n  width: 100%;\n  box-sizing: border-box;\n  white-space: normal;\n  word-break: break-word;\n  text-align: center;\2',
                text, count=1
            )
            # Mobile override: use minmax(0, 1fr) so column doesn't expand to min-content
            text = text.replace(
                '.v10-tour-mentor { grid-template-columns: 1fr; gap: 18px; padding: 28px 22px; text-align: center; }',
                '.v10-tour-mentor { grid-template-columns: minmax(0, 1fr); gap: 18px; padding: 28px 22px; text-align: center; }'
            )
            # Also fix desktop grid to prevent expansion
            text = text.replace(
                '.v10-tour-mentor {\n  display: grid;\n  grid-template-columns: auto 1fr;',
                '.v10-tour-mentor {\n  display: grid;\n  grid-template-columns: auto minmax(0, 1fr);'
            )
            # Force body min-width:0 via inline style attribute is hacky; instead override with selector
            # Add a new rule .v10-tour-mentor-body { min-width:0; }
            if '.v10-tour-mentor-body {' not in text:
                text = text.replace(
                    '.v10-tour-mentor-detail {',
                    '.v10-tour-mentor-body { min-width: 0; overflow-wrap: break-word; }\n.v10-tour-mentor-detail {'
                )

        if text != original:
            f.write_text(text)
            counts[f.name] = counts.get(f.name, 0) + 1

    # ============ Central css/style.css changes ============
    css = SITE / 'css/style.css'
    css_text = css.read_text()
    css_orig = css_text

    # Footer audit color: --ink-700 (#424245) → lighter on dark
    css_text = css_text.replace(
        "  font-weight: 500;\n  color: var(--ink-700);\n  margin: 0 0 0 16px;\n}\n.footer-audit::before,",
        f"  font-weight: 500;\n  color: {FOOTER_LIGHT};\n  margin: 0 0 0 16px;\n}}\n.footer-audit::before,"
    )
    # Try a simpler match
    css_text = re.sub(
        r'(\.footer-audit,\s*\n\.footer-v4-audit\s*\{[^}]*?color:\s*var\(--ink-700\))',
        rf'\1-replaced',  # placeholder
        css_text, flags=re.DOTALL
    )
    # Replace the var(--ink-700) in the footer-audit block with FOOTER_LIGHT
    css_text = re.sub(
        r'(\.footer-audit,\s*\n\.footer-v4-audit\s*\{[^}]*?color:\s*)(var\(--ink-700\))',
        rf'\1{FOOTER_LIGHT}',
        css_text, flags=re.DOTALL
    )

    # Footer bottom color: #6E6E73 → #A1A1A6
    css_text = css_text.replace(
        ".footer-bottom {\n  display: flex; justify-content: space-between; align-items: center;\n  font-size: 0.8125rem; color: #6E6E73;",
        f".footer-bottom {{\n  display: flex; justify-content: space-between; align-items: center;\n  font-size: 0.8125rem; color: {FOOTER_LIGHT};"
    )

    # stat-label on dark sections (cases page uses .section-v4.dark for stats)
    # Currently inherits --ink-700 = #424245 which fails 1.68:1 on dark bg
    if '.section-v4.dark .stat-row .stat-item .stat-label' not in css_text:
        css_text = css_text.replace(
            '.section-v4.dark .stat-row .stat-item .stat-num { color: #fff; }',
            '.section-v4.dark .stat-row .stat-item .stat-num { color: #fff; }\n'
            '.section-v4.dark .stat-row .stat-item .stat-label { color: #B8B8BC; }'
        )

    # Logo CN color in nav (line 191): var(--gold) → GOLD_DARK
    css_text = css_text.replace(
        ".nav-logo .logo-cn { color: var(--gold, #D4AF37); font-weight: 700; }",
        f".nav-logo .logo-cn {{ color: {GOLD_DARK}; font-weight: 700; }}"
    )

    # Hamburger: add 44x44 padding
    # Find .hamburger and ensure min 44x44 tap area
    if '.hamburger' in css_text:
        # If min-width/min-height already there, skip; else add
        if not re.search(r'\.hamburger[^{]*\{[^}]*min-(?:width|height):\s*44px', css_text):
            css_text = re.sub(
                r'(\.hamburger\s*\{)',
                r'\1\n  min-width: 44px; min-height: 44px;',
                css_text, count=1
            )

    # Footer link touch target: add padding to .footer-col a
    css_text = re.sub(
        r'(\.footer-col a\s*\{[^}]*?transition:\s*color\s*0\.15s;)(\s*\})',
        r'\1\n  padding: 8px 0;\n  min-height: 44px;\n  display: inline-flex;\n  align-items: center;\2',
        css_text, count=1
    )

    # Nav-link active touch target: padding 8 → 10 (height 40 → 44)
    # The .nav-menu a.active rule
    css_text = re.sub(
        r'(\.nav-menu a\.active\s*\{[^}]*?padding:\s*)8px 14px(;)',
        r'\g<1>10px 16px\g<2>',
        css_text
    )

    if css_text != css_orig:
        css.write_text(css_text)
        counts['css/style.css'] = 1

    print("=" * 60)
    print("Files patched:")
    for name, n in sorted(counts.items()):
        print(f"  {n:>2}x  {name}")
    print(f"Total files touched: {len(counts)}")


if __name__ == '__main__':
    main()
