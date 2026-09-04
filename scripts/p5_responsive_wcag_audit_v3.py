#!/usr/bin/env python3
"""
P5 v3: Proper WCAG audit
- Treats rgba(..., 0) as fully transparent (walk up)
- Treats rgba(..., alpha>=0.5) as solid bg (stop)
- Treats rgba(..., 0<alpha<0.5) as semi-transparent (walk up to find solid behind)
- Caps walk at 6 ancestors
"""
import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright

PAGES = ['index', 'immigration', 'education', 'career', 'tour', 'cases', 'audit', 'consult']
LANGS = ['TC', 'CN', 'EN']
VIEWPORTS = {
    'mobile':  {'width': 375, 'height': 812},
    'desktop': {'width': 1440, 'height': 900},
}
BASE_URL = 'http://localhost:8765'
CACHE_BUST = '?v=p5v3'


def page_url(t, l):
    if l == 'TC': return f"{BASE_URL}/{t}.html{CACHE_BUST}"
    return f"{BASE_URL}/{t}-{l.lower()}.html{CACHE_BUST}"


def parse_rgb_alpha(s):
    if not s: return None
    if s == 'transparent': return None
    m = re.match(r'rgba?\(([^)]+)\)', s)
    if not m: return None
    parts = [float(x.strip()) for x in m.group(1).split(',')]
    if len(parts) == 3:
        return (*parts, 1.0)
    return (*parts,)


def luminance(rgb):
    def c(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * c(rgb[0]) + 0.7152 * c(rgb[1]) + 0.0722 * c(rgb[2])


def contrast(c1, c2):
    L1 = luminance(c1)
    L2 = luminance(c2)
    if L1 < L2: L1, L2 = L2, L1
    return (L1 + 0.05) / (L2 + 0.05)


JS_AUDIT = r'''
() => {
    const samples = [];
    const els = document.querySelectorAll('h1, h2, h3, h4, p, a, span, li, button, .nav-link, .footer-link, .v10-case-quote, .v10-pillar, .v10-why-card, .v10-package, .v10-step, .v10-track, .v10-stat, [class*="eyebrow"], [class*="meta"]');
    let count = 0;

    function parseRgba(s) {
        if (!s || s === 'transparent') return null;
        const m = s.match(/rgba?\(([^)]+)\)/);
        if (!m) return null;
        const parts = m[1].split(',').map(x => parseFloat(x.trim()));
        if (parts.length === 4 && parts[3] === 0) return null;  // fully transparent
        return parts.slice(0, 3);
    }

    function findEffectiveBg(el) {
        let cur = el;
        for (let i = 0; i < 6 && cur; i++) {
            const cs = window.getComputedStyle(cur);
            const bgi = cs.backgroundImage;
            // Skip if this element has bg image AND i==0 (the element itself has photo bg — unlikely for text)
            if (i === 0 && bgi && bgi !== 'none' && !bgi.startsWith('linear-') && !bgi.startsWith('radial-')) {
                return { bg: null, hasImage: true };
            }
            const rgb = parseRgba(cs.backgroundColor);
            const alpha = cs.backgroundColor.match(/rgba\([^,]+,[^,]+,[^,]+,\s*([\d.]+)\)/);
            const a = alpha ? parseFloat(alpha[1]) : 1.0;
            if (rgb && a >= 0.5) {
                // Solid enough bg — use this
                return { bg: rgb, hasImage: false };
            }
            // else keep walking (transparent or semi-transparent)
            cur = cur.parentElement;
        }
        // Fallback to body bg
        const bodyCs = window.getComputedStyle(document.body);
        const bodyBg = parseRgba(bodyCs.backgroundColor) || [255, 255, 255];
        return { bg: bodyBg, hasImage: false };
    }

    for (const el of els) {
        if (count >= 250) break;
        const text = (el.innerText || '').trim();
        if (text.length < 2) continue;
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) continue;
        const cs = window.getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') continue;

        const textRgb = parseRgba(cs.color);
        if (!textRgb) continue;

        const { bg, hasImage } = findEffectiveBg(el);
        if (hasImage) continue;  // skip elements over photos (can't reliably test)

        const ratio = (function() {
            const L1 = (function(rgb) {
                function c(v) { v = v/255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); }
                return 0.2126*c(rgb[0]) + 0.7152*c(rgb[1]) + 0.0722*c(rgb[2]);
            })(textRgb);
            const L2 = (function(rgb) {
                function c(v) { v = v/255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); }
                return 0.2126*c(rgb[0]) + 0.7152*c(rgb[1]) + 0.0722*c(rgb[2]);
            })(bg);
            const lighter = Math.max(L1, L2);
            const darker = Math.min(L1, L2);
            return (lighter + 0.05) / (darker + 0.05);
        })();

        const fontSizePx = parseFloat(cs.fontSize);
        const fontWeight = parseInt(cs.fontWeight) || 400;
        const isLarge = fontSizePx >= 18 || (fontSizePx >= 14 && fontWeight >= 700);
        const threshold = isLarge ? 3.0 : 4.5;

        if (ratio < threshold) {
            samples.push({
                text: text.substring(0, 35),
                ratio: Math.round(ratio * 100) / 100,
                threshold,
                color: cs.color,
                bg: `rgb(${bg[0]}, ${bg[1]}, ${bg[2]})`,
                fontSize: cs.fontSize,
                fontWeight: cs.fontWeight,
                cls: el.className?.substring(0, 40) || '',
            });
        }
        count++;
    }

    return samples;
}
'''


async def audit(browser, template, lang, vp_name, vp):
    url = page_url(template, lang)
    ctx = await browser.new_context(viewport=vp, device_scale_factor=2)
    page = await ctx.new_page()
    findings = {'template': template, 'lang': lang, 'viewport': vp_name, 'url': url,
                'overflow_px': 0, 'contrast_failures': [], 'small_targets': []}
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=15000)
        await page.wait_for_timeout(800)

        # Layout overflow
        layout = await page.evaluate('''() => ({
            scrollW: Math.max(document.body.scrollWidth, document.documentElement.scrollWidth),
            clientW: document.documentElement.clientWidth,
        })''')
        findings['overflow_px'] = layout['scrollW'] - layout['clientW']

        # Contrast
        findings['contrast_failures'] = await page.evaluate(JS_AUDIT)

        # Touch target (mobile)
        if vp_name == 'mobile':
            sigs = await page.evaluate('''() => {
                const skip = ['HTML','HEAD','META','SCRIPT','STYLE','LINK'];
                const els = document.querySelectorAll('a, button');
                const counts = {};
                for (const el of els) {
                    if (skip.includes(el.tagName)) continue;
                    const text = (el.innerText || '').trim();
                    if (!text && el.tagName !== 'BUTTON') continue;
                    if (el.classList.contains('nav-logo')) continue;
                    if (el.classList.contains('footer-logo-text')) continue;
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 && rect.height === 0) continue;
                    if (rect.width < 44 || rect.height < 44) {
                        const cls = el.className.substring(0, 40) || '(no-class)';
                        const key = cls + '|' + Math.round(rect.width) + 'x' + Math.round(rect.height) + '|' + el.tagName;
                        counts[key] = (counts[key] || 0) + 1;
                    }
                }
                return Object.entries(counts).map(([k, v]) => {
                    const [cls, size, tag] = k.split('|');
                    return { cls, size, tag, count: v };
                }).sort((a,b) => b.count - a.count);
            }''')
            findings['small_targets'] = sigs[:10]
    finally:
        await ctx.close()
    return findings


async def main():
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for vp_name, vp in VIEWPORTS.items():
            for t in PAGES:
                for l in LANGS:
                    r = await audit(browser, t, l, vp_name, vp)
                    print(f"[{vp_name[:3]}] {t:12}/{l} overflow={r['overflow_px'] or 'OK'} contrast={len(r['contrast_failures'])} targets={len(r['small_targets'])}")
                    results.append(r)
        await browser.close()

    Path('/home/ubuntu/.hermes/hermes-agent/p5_audit_v3_results.json').write_text(
        json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(results)} audits")


if __name__ == '__main__':
    asyncio.run(main())
