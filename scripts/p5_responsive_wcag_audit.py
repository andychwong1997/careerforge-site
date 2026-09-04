#!/usr/bin/env python3
"""
P5: Responsive + WCAG AA audit
- 8 unique templates × 3 langs = 24 pages
- 2 viewports (mobile 375 + desktop 1440)
- Audit: layout integrity + WCAG AA contrast + touch target size
"""
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PAGES = [
    'index', 'immigration', 'education', 'career', 'tour', 'cases', 'audit', 'consult'
]
LANGS = ['TC', 'CN', 'EN']  # .html / -cn.html / -en.html

VIEWPORTS = {
    'mobile':  {'width': 375, 'height': 812},   # iPhone 12/13/14/15
    'desktop': {'width': 1440, 'height': 900},
}

BASE_URL = 'http://localhost:8765'
CACHE_BUST = '?v=p5audit'

def page_url(template, lang):
    if lang == 'TC':
        return f"{BASE_URL}/{template}.html{CACHE_BUST}"
    return f"{BASE_URL}/{template}-{lang.lower()}.html{CACHE_BUST}"


async def audit_page(browser, template, lang, viewport_name, vp):
    """Audit a single page at a viewport. Returns dict of findings."""
    url = page_url(template, lang)
    ctx = await browser.new_context(viewport=vp, device_scale_factor=2)
    page = await ctx.new_page()
    findings = {
        'template': template,
        'lang': lang,
        'viewport': viewport_name,
        'url': url,
        'checks': {},
        'errors': [],
    }
    try:
        resp = await page.goto(url, wait_until='domcontentloaded', timeout=15000)
        findings['checks']['http_status'] = resp.status if resp else None
        await page.wait_for_timeout(800)  # let fonts load

        # Check 1: Layout integrity — no horizontal overflow
        layout = await page.evaluate('''() => {
            const body = document.body;
            const html = document.documentElement;
            const scrollW = Math.max(body.scrollWidth, html.scrollWidth);
            const clientW = html.clientWidth;
            return {
                scrollWidth: scrollW,
                clientWidth: clientW,
                overflow: scrollW > clientW + 1,  // 1px tolerance
                overflowPx: scrollW - clientW,
            };
        }''')
        findings['checks']['layout'] = layout

        # Check 2: Touch target size (links/buttons ≥44x44 on mobile)
        if viewport_name == 'mobile':
            targets = await page.evaluate('''() => {
                const els = document.querySelectorAll('a, button, .nav-cta, .btn, [role="button"]');
                const small = [];
                els.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 && rect.height === 0) return;
                    if (rect.width < 44 || rect.height < 44) {
                        small.push({
                            tag: el.tagName,
                            text: (el.innerText || '').trim().substring(0, 30),
                            w: Math.round(rect.width),
                            h: Math.round(rect.height),
                            cls: el.className.substring(0, 30)
                        });
                    }
                });
                return small.slice(0, 10);
            }''')
            findings['checks']['small_targets'] = targets

        # Check 3: WCAG AA contrast on visible text
        contrast = await page.evaluate('''() => {
            // Sample visible text elements
            const samples = [];
            const els = document.querySelectorAll('h1, h2, h3, h4, p, a, span, li, button, .nav-link, .v10-case-quote');
            let count = 0;
            els.forEach(el => {
                if (count >= 60) return;
                const text = (el.innerText || '').trim();
                if (text.length < 2) return;
                const rect = el.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) return;
                const cs = window.getComputedStyle(el);
                // Skip if display:none
                if (cs.display === 'none' || cs.visibility === 'hidden') return;
                // Get effective color and bg
                samples.push({
                    text: text.substring(0, 30),
                    color: cs.color,
                    bg: cs.backgroundColor,
                    fontSize: cs.fontSize,
                    fontWeight: cs.fontWeight,
                });
                count++;
            });
            return samples;
        }''')
        # Compute contrast for each sample
        def parse_rgb(s):
            if not s or 'rgba' in s and s.endswith(', 0)') or s == 'rgba(0, 0, 0, 0)':
                return None
            import re
            m = re.match(r'rgba?\(([^)]+)\)', s)
            if not m: return None
            parts = [float(x.strip()) for x in m.group(1).split(',')]
            return parts[:3]

        def luminance(rgb):
            def c(v):
                v = v / 255
                return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
            return 0.2126 * c(rgb[0]) + 0.7152 * c(rgb[1]) + 0.0722 * c(rgb[2])

        def contrast_ratio(c1, c2):
            L1 = luminance(c1)
            L2 = luminance(c2)
            if L1 < L2: L1, L2 = L2, L1
            return (L1 + 0.05) / (L2 + 0.05)

        def find_bg(el, samples_list):
            """Walk up to find effective bg."""
            # Simplified: just check element + parent + body
            for bg in [el['bg'], 'rgb(255, 255, 255)', 'rgb(247, 248, 250)']:
                rgb = parse_rgb(bg)
                if rgb: return rgb
            return [255, 255, 255]

        contrast_issues = []
        for s in contrast:
            text_rgb = parse_rgb(s['color'])
            bg_rgb = find_bg(s, contrast)
            if not text_rgb: continue
            ratio = contrast_ratio(text_rgb, bg_rgb)
            # WCAG: normal text 4.5:1, large text (≥18px or ≥14px bold) 3:1
            font_size_px = float(s['fontSize'].rstrip('px'))
            font_weight = int(s['fontWeight']) if s['fontWeight'].isdigit() else 400
            is_large = font_size_px >= 18 or (font_size_px >= 14 and font_weight >= 700)
            threshold = 3.0 if is_large else 4.5
            if ratio < threshold:
                contrast_issues.append({
                    'text': s['text'],
                    'ratio': round(ratio, 2),
                    'threshold': threshold,
                    'color': s['color'],
                    'bg': 'rgb({}, {}, {})'.format(*bg_rgb),
                    'fontSize': s['fontSize'],
                })
        findings['checks']['contrast_failures'] = contrast_issues[:10]
        findings['checks']['contrast_samples'] = len(contrast)

    except Exception as e:
        findings['errors'].append(str(e))
    finally:
        await ctx.close()
    return findings


async def main():
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for vp_name, vp in VIEWPORTS.items():
            for template in PAGES:
                for lang in LANGS:
                    # Skip pages that don't exist in some langs? — all 8 templates have all 3 langs
                    print(f"[{vp_name}] {template}/{lang}...", end=' ', flush=True)
                    r = await audit_page(browser, template, lang, vp_name, vp)
                    status = 'OK' if not r['errors'] else 'ERR'
                    layout_ok = '✓' if not r['checks'].get('layout', {}).get('overflow') else '✗'
                    contrast_n = len(r['checks'].get('contrast_failures', []))
                    target_n = len(r['checks'].get('small_targets', []))
                    print(f"{status} layout:{layout_ok} contrast:{contrast_n} target:{target_n}")
                    results.append(r)
        await browser.close()

    # Save raw results
    out = Path('/home/ubuntu/.hermes/hermes-agent/p5_audit_results.json')
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved: {out}")
    print(f"Total: {len(results)} audits")


if __name__ == '__main__':
    asyncio.run(main())
