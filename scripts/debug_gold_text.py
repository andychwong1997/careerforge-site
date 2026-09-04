#!/usr/bin/env python3
"""Debug: what is the actual bg of gold text on real pages?"""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 375, 'height': 812})
        await page.goto('http://localhost:8765/index.html?v=debug', wait_until='domcontentloaded')
        await page.wait_for_timeout(1000)

        # Check gold text and its ancestor bgs
        result = await page.evaluate(r'''
        () => {
            const findings = [];
            // Find any element with gold-ish text color
            const all = document.querySelectorAll('*');
            for (const el of all) {
                const cs = window.getComputedStyle(el);
                const c = cs.color;
                const m = c.match(/rgb\((\d+),\s*(\d+),\s*(\d+)/);
                if (!m) continue;
                const [_, r, g, b] = m.map(Number);
                const isGoldish = (r > 150 && g > 120 && b < 100);
                const isSlate = (r > 80 && r < 140 && g > 100 && g < 150 && b > 120 && b < 170);
                if (!isGoldish && !isSlate) continue;
                const text = (el.innerText || '').trim().substring(0, 40);
                if (text.length < 1) continue;
                // Walk ancestors
                const ancestors = [];
                let a = el;
                for (let i = 0; i < 5 && a; i++) {
                    const acs = window.getComputedStyle(a);
                    ancestors.push({
                        tag: a.tagName,
                        cls: a.className?.substring(0, 30) || '',
                        bg: acs.backgroundColor,
                        bgImg: acs.backgroundImage?.substring(0, 40) || 'none',
                    });
                    a = a.parentElement;
                }
                findings.push({
                    text,
                    color: c,
                    fontSize: cs.fontSize,
                    fontWeight: cs.fontWeight,
                    ancestors,
                });
            }
            return findings.slice(0, 20);
        }
        ''')
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        await browser.close()

asyncio.run(main())
