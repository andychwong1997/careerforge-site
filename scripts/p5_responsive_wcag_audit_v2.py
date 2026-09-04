#!/usr/bin/env python3
"""
P5 v2: Improved WCAG audit with real bg detection.
Walks up DOM tree to find effective background (or detects transparent ancestor).
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

PAGES = [
    'index', 'immigration', 'education', 'career', 'tour', 'cases', 'audit', 'consult'
]
LANGS = ['TC', 'CN', 'EN']
VIEWPORTS = {
    'mobile':  {'width': 375, 'height': 812},
    'desktop': {'width': 1440, 'height': 900},
}
BASE_URL = 'http://localhost:8765'
CACHE_BUST = '?v=p5v2'


def page_url(template, lang):
    if lang == 'TC':
        return f"{BASE_URL}/{template}.html{CACHE_BUST}"
    return f"{BASE_URL}/{template}-{lang.lower()}.html{CACHE_BUST}"


def parse_rgb(s):
    import re
    if not s: return None
    if s == 'transparent': return None
    m = re.match(r'rgba?\(([^)]+)\)', s)
    if not m: return None
    parts = [float(x.strip()) for x in m.group(1).split(',')]
    if len(parts) == 4 and parts[3] == 0: return None  # rgba(0,0,0,0)
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


AUDIT_SCRIPT = r'''
() => {
    const samples = [];
    const els = document.querySelectorAll('h1, h2, h3, h4, p, a, span, li, button, .nav-link, .v10-case-quote, .v10-pillar, .v10-why-card, .v10-package, .v10-step, .v10-track, .v10-stat, .footer-link');
    let count = 0;
    els.forEach(el => {
        if (count >= 200) return;
        const text = (el.innerText || '').trim();
        if (text.length < 2) return;
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;
        const cs = window.getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') return;

        // Walk up DOM tree to find effective bg
        let bg = null;
        let bgEl = el;
        let hasImageBg = false;
        while (bgEl && bgEl !== document.documentElement) {
            const bcs = window.getComputedStyle(bgEl);
            const bgc = bcs.backgroundColor;
            const bgi = bcs.backgroundImage;
            if (bgi && bgi !== 'none' && !bgi.startsWith('linear-gradient') && !bgi.startsWith('radial-gradient')) {
                hasImageBg = true;
                break;
            }
            const rgb = parseRgba(bgc);
            if (rgb) {
                bg = rgb;
                break;
            }
            bgEl = bgEl.parentElement;
        }
        if (hasImageBg) {
            // Skip — cannot reliably test contrast over photo
            return;
        }
        if (!bg) bg = [255, 255, 255];  // body default

        samples.push({
            text: text.substring(0, 30),
            color: cs.color,
            colorOpacity: cs.color.includes('rgba'),
            bg: 'rgb({}, {}, {})'.format(...bg),
            fontSize: cs.fontSize,
            fontWeight: cs.fontWeight,
        });
        count++;
    });

    function parseRgba(s) {
        if (!s || s === 'transparent') return null;
        const m = s.match(/rgba?\(([^)]+)\)/);
        if (!m) return null;
        const parts = m[1].split(',').map(x => parseFloat(x.trim()));
        if (parts.length === 4 && parts[3] === 0) return null;
        return parts.slice(0, 3);
    }
    return samples;
}
'''


async def main():
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for vp_name, vp in VIEWPORTS.items():
            for template in PAGES:
                for lang in LANGS:
                    url = page_url(template, lang)
                    ctx = await browser.new_context(viewport=vp, device_scale_factor=2)
                    page = await ctx.new_page()
                    findings = {
                        'template': template,
                        'lang': lang,
                        'viewport': vp_name,
                        'url': url,
                        'contrast_failures': [],
                        'small_targets': [],
                        'overflow': None,
                    }
                    try:
                        resp = await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                        await page.wait_for_timeout(800)

                        # Layout overflow
                        layout = await page.evaluate('''() => {
                            const body = document.body;
                            const html = document.documentElement;
                            return {
                                scrollW: Math.max(body.scrollWidth, html.scrollWidth),
                                clientW: html.clientWidth,
                                overflowPx: Math.max(body.scrollWidth, html.scrollWidth) - html.clientWidth,
                            };
                        }''')
                        if layout['overflowPx'] > 1:
                            findings['overflow'] = layout['overflowPx']

                        # Contrast (with bg detection)
                        samples = await page.evaluate(AUDIT_SCRIPT)
                        for s in samples:
                            text_rgb = parse_rgb(s['color'])
                            bg_rgb = parse_rgb(s['bg'])
                            if not text_rgb or not bg_rgb: continue
                            ratio = contrast_ratio(text_rgb, bg_rgb)
                            font_size_px = float(s['fontSize'].rstrip('px'))
                            font_weight = int(s['fontWeight']) if s['fontWeight'].isdigit() else 400
                            is_large = font_size_px >= 18 or (font_size_px >= 14 and font_weight >= 700)
                            threshold = 3.0 if is_large else 4.5
                            if ratio < threshold:
                                findings['contrast_failures'].append({
                                    'text': s['text'],
                                    'ratio': round(ratio, 2),
                                    'threshold': threshold,
                                    'color': s['color'],
                                    'bg': s['bg'],
                                    'fontSize': s['fontSize'],
                                    'is_large': is_large,
                                })

                        # Touch target (mobile only)
                        if vp_name == 'mobile':
                            targets = await page.evaluate('''() => {
                                const skip = new Set(['HTML','HEAD','META','SCRIPT','STYLE','LINK']);
                                const els = document.querySelectorAll('a, button');
                                const small = [];
                                els.forEach(el => {
                                    if (skip.has(el.tagName)) return;
                                    const text = (el.innerText || '').trim();
                                    // Skip if empty (decorative) or logo/branding
                                    if (!text && el.tagName !== 'BUTTON') return;
                                    if (el.classList.contains('nav-logo')) return;
                                    if (el.classList.contains('footer-logo-text')) return;
                                    const rect = el.getBoundingClientRect();
                                    if (rect.width === 0 && rect.height === 0) return;
                                    if (rect.width < 44 || rect.height < 44) {
                                        small.push({
                                            tag: el.tagName,
                                            text: text.substring(0, 25),
                                            w: Math.round(rect.width),
                                            h: Math.round(rect.height),
                                            cls: el.className.substring(0, 40)
                                        });
                                    }
                                });
                                return small;
                            }''')
                            # Group by signature (cls + w + h)
                            from collections import Counter
                            sigs = Counter()
                            for t in targets:
                                sigs[(t['cls'], t['w'], t['h'], t['tag'])] += 1
                            findings['small_targets'] = [
                                {'cls': k[0], 'w': k[1], 'h': k[2], 'tag': k[3], 'count': v}
                                for k, v in sigs.most_common(10)
                            ]

                    except Exception as e:
                        findings['error'] = str(e)
                    finally:
                        await ctx.close()
                    results.append(findings)
                    print(f"[{vp_name[:3]}] {template:12}/{lang} overflow={findings['overflow'] or 'OK'} contrast={len(findings['contrast_failures'])} targets={len(findings['small_targets'])}")
        await browser.close()

    out = Path('/home/ubuntu/.hermes/hermes-agent/p5_audit_v2_results.json')
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved: {out}")


if __name__ == '__main__':
    asyncio.run(main())
