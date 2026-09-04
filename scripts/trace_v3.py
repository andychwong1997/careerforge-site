#!/usr/bin/env python3
"""Trace v3 audit logic for immigration hero text."""
import asyncio
import json
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 375, 'height': 812}, device_scale_factor=2)
        page = await ctx.new_page()
        await page.goto('http://localhost:8765/immigration.html?v=trace', wait_until='domcontentloaded')
        await page.wait_for_timeout(800)

        # Simulate v3 audit logic for one element
        result = await page.evaluate(r'''
        () => {
            function parseRgba(s) {
                if (!s || s === 'transparent') return null;
                const m = s.match(/rgba?\(([^)]+)\)/);
                if (!m) return null;
                const parts = m[1].split(',').map(x => parseFloat(x.trim()));
                if (parts.length === 4 && parts[3] === 0) return null;
                return parts.slice(0, 3);
            }

            function findEffectiveBg(el) {
                let cur = el;
                for (let i = 0; i < 6 && cur; i++) {
                    const cs = window.getComputedStyle(cur);
                    const bgi = cs.backgroundImage;
                    if (i === 0 && bgi && bgi !== 'none' && !bgi.startsWith('linear-') && !bgi.startsWith('radial-')) {
                        return { bg: null, hasImage: true };
                    }
                    const rgb = parseRgba(cs.backgroundColor);
                    const alpha = cs.backgroundColor.match(/rgba\([^,]+,[^,]+,[^,]+,\s*([\d.]+)\)/);
                    const a = alpha ? parseFloat(alpha[1]) : 1.0;
                    if (rgb && a >= 0.5) {
                        return { bg: rgb, hasImage: false };
                    }
                    cur = cur.parentElement;
                }
                const bodyCs = window.getComputedStyle(document.body);
                const bodyBg = parseRgba(bodyCs.backgroundColor) || [255, 255, 255];
                return { bg: bodyBg, hasImage: false };
            }

            // Find the hero trust text
            const trustItems = document.querySelectorAll('.v10-hero-trust-item');
            const out = [];
            for (const item of trustItems) {
                const span = item.querySelector('span');
                if (!span) continue;
                const cs = window.getComputedStyle(span);
                const { bg, hasImage } = findEffectiveBg(span);
                out.push({
                    text: span.innerText,
                    color: cs.color,
                    bgFound: bg,
                    hasImage,
                    bodyBg: window.getComputedStyle(document.body).backgroundColor,
                });
            }
            return out;
        }
        ''')
        print(json.dumps(result, indent=2, ensure_ascii=False))

        # Also trace what's at section.v10-hero
        hero_info = await page.evaluate(r'''
        () => {
            const hero = document.querySelector('.v10-hero');
            const cs = window.getComputedStyle(hero);
            return {
                bgColor: cs.backgroundColor,
                bgImage: cs.backgroundImage?.substring(0, 80),
                classes: hero.className,
            };
        }
        ''')
        print(f"\n=== .v10-hero on immigration ===")
        print(json.dumps(hero_info, indent=2, ensure_ascii=False))

        await browser.close()

asyncio.run(main())
