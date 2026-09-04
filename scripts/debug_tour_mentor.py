#!/usr/bin/env python3
"""Detailed tour mentor overflow investigation."""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 375, 'height': 812}, device_scale_factor=2)
        page = await ctx.new_page()

        for url in ['http://localhost:8765/tour.html?v=mentor', 'http://localhost:8765/tour-cn.html?v=mentor']:
            await page.goto(url, wait_until='domcontentloaded')
            await page.wait_for_timeout(800)

            info = await page.evaluate(r'''
            () => {
                const mentors = document.querySelectorAll('.v10-tour-mentor');
                const result = [];
                for (const m of mentors) {
                    const icon = m.querySelector('.v10-tour-mentor-icon');
                    const body = m.querySelector('.v10-tour-mentor-body');
                    const detail = m.querySelector('.v10-tour-mentor-detail');
                    const docW = document.documentElement.clientWidth;
                    result.push({
                        iconBox: icon ? {
                            left: Math.round(icon.getBoundingClientRect().left),
                            right: Math.round(icon.getBoundingClientRect().right),
                            width: Math.round(icon.getBoundingClientRect().width),
                            html: icon.outerHTML.substring(0, 250),
                        } : null,
                        bodyBox: body ? {
                            left: Math.round(body.getBoundingClientRect().left),
                            right: Math.round(body.getBoundingClientRect().right),
                            width: Math.round(body.getBoundingClientRect().width),
                        } : null,
                        detailBox: detail ? {
                            left: Math.round(detail.getBoundingClientRect().left),
                            right: Math.round(detail.getBoundingClientRect().right),
                            width: Math.round(detail.getBoundingClientRect().width),
                        } : null,
                        docW,
                    });
                }
                return result.slice(0, 3);
            }
            ''')
            print(f"\n=== {url.split('?')[0].split('/')[-1]} ===")
            for r in info:
                if r['iconBox']:
                    print(f"  ICON  left={r['iconBox']['left']} right={r['iconBox']['right']} width={r['iconBox']['width']}")
                    print(f"        html: {r['iconBox']['html'][:200]}")
                if r['bodyBox']:
                    print(f"  BODY  left={r['bodyBox']['left']} right={r['bodyBox']['right']} width={r['bodyBox']['width']}")
                if r['detailBox']:
                    print(f"  DETAIL left={r['detailBox']['left']} right={r['detailBox']['right']} width={r['detailBox']['width']}")
                print(f"  docW={r['docW']}")

            # Check the parent grid container
            grid = await page.evaluate(r'''
            () => {
                const grids = document.querySelectorAll('.v10-tour-mentors, [class*="mentor-grid"], [class*="mentor-list"]');
                const out = [];
                for (const g of grids) {
                    const cs = window.getComputedStyle(g);
                    out.push({
                        cls: g.className,
                        display: cs.display,
                        gridTemplate: cs.gridTemplateColumns,
                        flexWrap: cs.flexWrap,
                        width: Math.round(g.getBoundingClientRect().width),
                    });
                }
                return out;
            }
            ''')
            print(f"\n  Mentor parent grids:")
            for g in grid:
                print(f"    {g}")

        await browser.close()

asyncio.run(main())
