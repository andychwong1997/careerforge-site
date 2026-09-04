#!/usr/bin/env python3
"""Debug tour mentor box layout after fixes."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 375, 'height': 812}, device_scale_factor=2)
        page = await ctx.new_page()
        await page.goto('http://localhost:8765/tour.html?v=debug2', wait_until='domcontentloaded')
        await page.wait_for_timeout(800)

        info = await page.evaluate(r'''
        () => {
            const mentors = document.querySelectorAll('.v10-tour-mentor');
            const out = [];
            for (const m of mentors) {
                const icon = m.querySelector('.v10-tour-mentor-icon');
                const detail = m.querySelector('.v10-tour-mentor-detail');
                const docW = document.documentElement.clientWidth;
                const iconRect = icon.getBoundingClientRect();
                const detailRect = detail.getBoundingClientRect();
                const mRect = m.getBoundingClientRect();
                const iconCs = window.getComputedStyle(icon);
                const detailCs = window.getComputedStyle(detail);
                const mCs = window.getComputedStyle(m);
                out.push({
                    mentor: {
                        left: Math.round(mRect.left),
                        right: Math.round(mRect.right),
                        width: Math.round(mRect.width),
                        padding: mCs.padding,
                        boxSizing: mCs.boxSizing,
                    },
                    icon: {
                        left: Math.round(iconRect.left),
                        right: Math.round(iconRect.right),
                        width: Math.round(iconRect.width),
                        width_css: iconCs.width,
                        justifySelf: iconCs.justifySelf,
                        margin: iconCs.margin,
                    },
                    detail: {
                        left: Math.round(detailRect.left),
                        right: Math.round(detailRect.right),
                        width: Math.round(detailRect.width),
                        maxWidth: detailCs.maxWidth,
                        whiteSpace: detailCs.whiteSpace,
                        wordBreak: detailCs.wordBreak,
                    },
                    docW,
                });
            }
            return out.slice(0, 2);
        }
        ''')
        import json
        print(json.dumps(info, indent=2, ensure_ascii=False))
        await browser.close()

asyncio.run(main())
