#!/usr/bin/env python3
"""Debug tour mobile overflow + white text on cream."""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 375, 'height': 812}, device_scale_factor=2)
        page = await ctx.new_page()

        # 1. Tour overflow investigation
        await page.goto('http://localhost:8765/tour.html?v=overflow', wait_until='domcontentloaded')
        await page.wait_for_timeout(800)

        # Find elements that overflow horizontally
        overflow_elems = await page.evaluate(r'''
        () => {
            const docW = document.documentElement.clientWidth;
            const offenders = [];
            const all = document.querySelectorAll('*');
            for (const el of all) {
                const rect = el.getBoundingClientRect();
                if (rect.right > docW + 1 && rect.width > 0) {
                    offenders.push({
                        tag: el.tagName,
                        cls: (el.className || '').substring(0, 40) || '(no-class)',
                        text: (el.innerText || '').substring(0, 50),
                        right: Math.round(rect.right),
                        left: Math.round(rect.left),
                        width: Math.round(rect.width),
                        overflow: Math.round(rect.right - docW),
                    });
                }
            }
            return offenders;
        }
        ''')
        print(f"\n=== TOUR MOBILE OVERFLOW (12px) ===")
        print(f"Found {len(overflow_elems)} elements extending beyond 375px viewport:")
        # Dedup by cls + overflow amount
        from collections import Counter
        sigs = Counter()
        for o in overflow_elems:
            sigs[(o['tag'], o['cls'], o['overflow'])] += 1
        for sig, count in sigs.most_common(10):
            print(f"  {count}x <{sig[0]} class='{sig[1]}'>  overflow={sig[2]}px")

        # 2. White-on-cream investigation — find rgba(255,255,255, 0.x) text and check ancestor
        await page.goto('http://localhost:8765/index.html?v=white', wait_until='domcontentloaded')
        await page.wait_for_timeout(800)

        white_text = await page.evaluate(r'''
        () => {
            const all = document.querySelectorAll('*');
            const findings = [];
            for (const el of all) {
                const cs = window.getComputedStyle(el);
                const c = cs.color;
                if (!c.includes('rgba(255, 255, 255')) continue;
                const rect = el.getBoundingClientRect();
                if (rect.width === 0) continue;
                const text = (el.innerText || '').trim().substring(0, 30);
                if (!text) continue;
                // Get first 5 ancestors bg
                const ancestors = [];
                let a = el;
                for (let i = 0; i < 6 && a; i++) {
                    const acs = window.getComputedStyle(a);
                    ancestors.push({
                        tag: a.tagName,
                        cls: a.className?.substring(0, 30) || '',
                        bg: acs.backgroundColor,
                        bgImg: acs.backgroundImage?.substring(0, 30) || 'none',
                    });
                    a = a.parentElement;
                }
                findings.push({
                    text,
                    color: c,
                    fontSize: cs.fontSize,
                    cls: el.className?.substring(0, 30) || '',
                    ancestors,
                });
            }
            return findings.slice(0, 15);
        }
        ''')
        print(f"\n=== WHITE-ISH TEXT (rgba 255,255,255, 0.x) ON INDEX ===")
        for f in white_text:
            print(f"\n  '{f['text']}' color={f['color']} font={f['fontSize']} cls='{f['cls']}'")
            for i, a in enumerate(f['ancestors'][:4]):
                print(f"    {i}: <{a['tag']} class='{a['cls']}'> bg={a['bg']} bgImg={a['bgImg']}")

        await browser.close()

asyncio.run(main())
