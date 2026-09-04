#!/usr/bin/env python3
"""Detailed tour overflow debug."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 375, 'height': 812}, device_scale_factor=2)
        page = await ctx.new_page()
        await page.goto('http://localhost:8765/tour.html?v=debug3', wait_until='domcontentloaded')
        await page.wait_for_timeout(800)

        info = await page.evaluate(r'''
        () => {
            const mentors = document.querySelectorAll('.v10-tour-mentor');
            const out = [];
            for (const m of mentors) {
                const detail = m.querySelector('.v10-tour-mentor-detail');
                const body = m.querySelector('.v10-tour-mentor-body');
                const icon = m.querySelector('.v10-tour-mentor-icon');
                const detailCs = window.getComputedStyle(detail);
                const bodyCs = window.getComputedStyle(body);
                const detailRect = detail.getBoundingClientRect();
                const bodyRect = body.getBoundingClientRect();
                out.push({
                    detailDisplay: detailCs.display,
                    detailWidth: detailCs.width,
                    detailBoxSizing: detailCs.boxSizing,
                    detailLeft: Math.round(detailRect.left),
                    detailRight: Math.round(detailRect.right),
                    detailWidthPx: Math.round(detailRect.width),
                    bodyDisplay: bodyCs.display,
                    bodyWidth: bodyCs.width,
                    bodyMinWidth: bodyCs.minWidth,
                    bodyLeft: Math.round(bodyRect.left),
                    bodyRight: Math.round(bodyRect.right),
                    bodyWidthPx: Math.round(bodyRect.width),
                    bodyOverflowWrap: bodyCs.overflowWrap,
                    // Also: the parent .v10-tour-mentor grid info
                    parentDisplay: window.getComputedStyle(m).display,
                    parentGridCols: window.getComputedStyle(m).gridTemplateColumns,
                });
            }
            return out;
        }
        ''')
        import json
        print(json.dumps(info, indent=2, ensure_ascii=False))
        await browser.close()

asyncio.run(main())
