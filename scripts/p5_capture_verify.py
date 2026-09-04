#!/usr/bin/env python3
"""P5 Phase 2 verification: cap before/after screenshots + vision check critical pages."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path('/home/ubuntu/workspace/.hermes/hermes-agent')
OUT.mkdir(parents=True, exist_ok=True)

# 4 most critical pages to verify after fixes
PAGES = [
    ('index', 'mobile', 375, 812),
    ('index', 'desktop', 1440, 900),
    ('immigration', 'mobile', 375, 812),
    ('immigration', 'desktop', 1440, 900),
    ('tour', 'mobile', 375, 812),
    ('tour', 'desktop', 1440, 900),
    ('cases', 'mobile', 375, 812),
    ('audit', 'mobile', 375, 812),
    ('education', 'mobile', 375, 812),
]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for page_name, view, w, h in PAGES:
            ctx = await browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2)
            page = await ctx.new_page()
            url = f'http://localhost:8765/{page_name}.html?v=p5fix&t={int(asyncio.get_event_loop().time()*1000)}'
            await page.goto(url, wait_until='networkidle')
            await page.wait_for_timeout(500)
            out_path = OUT / f'p5v2_{page_name}_{view}.png'
            await page.screenshot(path=str(out_path), full_page=False)
            print(f"  ✓ {out_path.name}")
            await ctx.close()
        await browser.close()
    print("Done")


asyncio.run(main())
