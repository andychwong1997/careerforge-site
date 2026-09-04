#!/usr/bin/env python3
"""Check .v10-hero background on every page."""
import asyncio
from playwright.async_api import async_playwright

PAGES = ['index', 'immigration', 'education', 'career', 'tour', 'cases', 'audit', 'consult']

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 375, 'height': 812})
        print(f"{'page':<14} {'bg-color':<35} {'bg-image':<50} {'opacity':<8} {'overlay?'}")
        print("=" * 120)
        for t in PAGES:
            for l in ['TC', 'CN', 'EN']:
                url = f'http://localhost:8765/{t}.html?v=herobg' if l == 'TC' else f'http://localhost:8765/{t}-{l.lower()}.html?v=herobg'
                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                await page.wait_for_timeout(500)
                info = await page.evaluate(r'''
                () => {
                    const hero = document.querySelector('.v10-hero, .hero, [class*="hero"]');
                    if (!hero) return { exists: false };
                    const cs = window.getComputedStyle(hero);
                    // Also check for overlay div
                    const overlay = hero.querySelector('[class*="overlay"]');
                    return {
                        exists: true,
                        tag: hero.tagName,
                        cls: hero.className,
                        bgColor: cs.backgroundColor,
                        bgImage: cs.backgroundImage?.substring(0, 60),
                        opacity: cs.opacity,
                        hasOverlay: !!overlay,
                        overlayBg: overlay ? window.getComputedStyle(overlay).backgroundColor : null,
                    };
                }
                ''')
                if info.get('exists'):
                    print(f"{t}/{l:<3} {info['bgColor']:<35} {str(info.get('bgImage','?'))[:48]:<50} {str(info.get('opacity','?'))[:6]:<8} {'YES ' + str(info.get('overlayBg')) if info.get('hasOverlay') else 'no'}")
                else:
                    print(f"{t}/{l:<3}  no .hero element found")
        await browser.close()

asyncio.run(main())
