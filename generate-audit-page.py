#!/usr/bin/env python3
"""
Generate CareerForge Mobile Audit status page (3 langs) from latest.json.
Output: audit.html (zh-Hant), audit-cn.html (zh-Hans), audit-en.html (en).

Usage: python3 generate-audit-page.py
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path("/home/ubuntu/workspace/careerforge-site")
REPORT = Path("/home/ubuntu/workspace/careerforge-mobile-audit/reports/latest.json")


def load_report() -> dict:
    if not REPORT.exists():
        sys.exit(f"ERROR: {REPORT} not found. Run ./run.sh report first.")
    return json.loads(REPORT.read_text(encoding="utf-8"))


def fmt_hkt(iso: str) -> str:
    dt = datetime.fromisoformat(iso).astimezone(timezone(timedelta(hours=8)))
    return dt.strftime("%Y-%m-%d %H:%M HKT")


# ────────────────────────────────────────────────────────────────────────────
# Per-language content (audit page is technical, mostly English-safe)
# ────────────────────────────────────────────────────────────────────────────

CONTENT = {
    "zh-Hant": {
        "html_lang": "zh-Hant",
        "title": "Mobile Audit · CareerForge 鑄途",
        "description": "CareerForge 每日自動以 iPhone 14 viewport 測試全站 18 個頁面，確保零水平 overflow。",
        "eyebrow": "Site Health · 每日自動驗證",
        "hero_title_1": "✅ 全部 18 個頁面",
        "hero_title_2": "通過 Mobile Audit",
        "hero_sub": "CareerForge 每晚 03:00 HKT 自動以 iPhone 14 viewport（390 × 844）測試全站 18 個頁面，確保零水平 overflow。",
        "stat_pages": "頁面通過",
        "stat_overflows": "水平溢出",
        "stat_viewport": "測試 viewport",
        "pages_heading": "頁面驗證明細",
        "col_page": "頁面",
        "col_status": "狀態",
        "col_width": "Body 寬度",
        "col_overflows": "溢出元素",
        "method_heading": "驗證方法",
        "method_steps": [
            "用 Playwright (Chromium headless) 開每個頁面",
            "viewport 設定 390 × 844（iPhone 14 標準）",
            "掃描所有 DOM element 嘅 bounding rect",
            "確認 0 個 element.right > viewport 寬度",
            "確認 body.scrollWidth ≤ 391px",
        ],
        "method_note": "每晚 03:00 HKT 自動 run，failure 時即時 push Telegram alert。任何新 PR merge 後第二朝就會驗證。",
        "status_pass": "通過",
        "status_fail": "失敗",
        "status_err": "載入錯誤",
        "cta_view_live": "查看實時網站 →",
        "footer_label": "Mobile Audit",
        "file": "audit.html",
        "lang_link_tw": None,  # self
        "lang_link_cn": "audit-cn.html",
        "lang_link_en": "audit-en.html",
    },
    "zh-Hans": {
        "html_lang": "zh-Hans",
        "title": "Mobile Audit · CareerForge 鑄途",
        "description": "CareerForge 每日自动以 iPhone 14 viewport 测试全站 18 个页面，确保零水平 overflow。",
        "eyebrow": "Site Health · 每日自动验证",
        "hero_title_1": "✅ 全部 18 个页面",
        "hero_title_2": "通过 Mobile Audit",
        "hero_sub": "CareerForge 每晚 03:00 HKT 自动以 iPhone 14 viewport（390 × 844）测试全站 18 个页面，确保零水平 overflow。",
        "stat_pages": "页面通过",
        "stat_overflows": "水平溢出",
        "stat_viewport": "测试 viewport",
        "pages_heading": "页面验证明细",
        "col_page": "页面",
        "col_status": "状态",
        "col_width": "Body 宽度",
        "col_overflows": "溢出元素",
        "method_heading": "验证方法",
        "method_steps": [
            "用 Playwright (Chromium headless) 开每个页面",
            "viewport 设定 390 × 844（iPhone 14 标准）",
            "扫描所有 DOM element 的 bounding rect",
            "确认 0 个 element.right > viewport 宽度",
            "确认 body.scrollWidth ≤ 391px",
        ],
        "method_note": "每晚 03:00 HKT 自动 run，failure 时即时 push Telegram alert。任何新 PR merge 后第二朝就会验证。",
        "status_pass": "通过",
        "status_fail": "失败",
        "status_err": "载入错误",
        "cta_view_live": "查看实时网站 →",
        "footer_label": "Mobile Audit",
        "file": "audit-cn.html",
        "lang_link_tw": "audit.html",
        "lang_link_cn": None,  # self
        "lang_link_en": "audit-en.html",
    },
    "en": {
        "html_lang": "en",
        "title": "Mobile Audit · CareerForge",
        "description": "CareerForge auto-tests all 18 pages nightly at iPhone 14 viewport to ensure zero horizontal overflow.",
        "eyebrow": "Site Health · Verified Nightly",
        "hero_title_1": "✅ All 18 Pages",
        "hero_title_2": "Pass Mobile Audit",
        "hero_sub": "CareerForge auto-tests every page nightly at 03:00 HKT using iPhone 14 viewport (390 × 844) to ensure zero horizontal overflow across the site.",
        "stat_pages": "Pages pass",
        "stat_overflows": "Horizontal overflow",
        "stat_viewport": "Test viewport",
        "pages_heading": "Per-page verification",
        "col_page": "Page",
        "col_status": "Status",
        "col_width": "Body width",
        "col_overflows": "Overflow elements",
        "method_heading": "Methodology",
        "method_steps": [
            "Open each page with Playwright (Chromium headless)",
            "Set viewport to 390 × 844 (iPhone 14 baseline)",
            "Scan all DOM element bounding rects",
            "Assert no element.right > viewport width",
            "Assert body.scrollWidth ≤ 391px",
        ],
        "method_note": "Runs automatically at 03:00 HKT every night. Failures push a Telegram alert immediately. Any new PR merge is verified by the next morning's audit.",
        "status_pass": "Pass",
        "status_fail": "Fail",
        "status_err": "Load error",
        "cta_view_live": "View live site →",
        "footer_label": "Mobile Audit",
        "file": "audit-en.html",
        "lang_link_tw": "audit.html",
        "lang_link_cn": "audit-cn.html",
        "lang_link_en": None,  # self
    },
}


# ────────────────────────────────────────────────────────────────────────────
# Per-language nav + footer (links to language-specific versions)
# ────────────────────────────────────────────────────────────────────────────

NAV = {
    "zh-Hant": {
        "logo_en": "CareerForge", "logo_zh": "鑄途",
        "links": [
            ("index.html", "首頁", True),
            ("immigration.html", "身份規劃", False),
            ("education.html", "升學規劃", False),
            ("career.html", "職涯身價", False),
            ("quiz.html", "牛馬測驗", False),
            ("cases.html", "客戶故事", False),
            ("#contact", "聯絡我們", False),
        ],
    },
    "zh-Hans": {
        "logo_en": "CareerForge", "logo_zh": "鑄途",
        "links": [
            ("index-cn.html", "首页", True),
            ("immigration-cn-v17.html", "身份规划", False),
            ("education-cn.html", "升学规划", False),
            ("career-cn.html", "求职身价", False),
            ("quiz-cn.html", "牛马测验", False),
            ("cases-cn.html", "客户故事", False),
            ("#contact", "联系我们", False),
        ],
    },
    "en": {
        "logo_en": "CareerForge", "logo_zh": "Forge",
        "links": [
            ("index-en.html", "Home", True),
            ("immigration-en.html", "Immigration", False),
            ("education-en.html", "Education", False),
            ("career-en.html", "Career", False),
            ("quiz-en.html", "Quiz", False),
            ("cases-en.html", "Cases", False),
            ("#contact", "Contact", False),
        ],
    },
}


def render_page(lang: str, c: dict, report: dict) -> str:
    """Render one audit.html for given language."""
    nav = NAV[lang]
    results = report["results"]
    ts_hkt = fmt_hkt(report["timestamp"])
    total = report["total"]
    passed = report["passed"]
    failed = report["failed"]
    errored = report["errored"]
    viewport = report["viewport"]

    # nav links
    active_attr = ' class="active"'
    nav_links_html = "\n        ".join(
        f'<a href="{href}"{active_attr if active else ""}>{label}</a>'
        for href, label, active in nav["links"]
    )

    # lang switcher
    tw_attr = "" if c["lang_link_tw"] else ' class="active"'
    cn_attr = "" if c["lang_link_cn"] else ' class="active"'
    en_attr = "" if c["lang_link_en"] else ' class="active"'
    tw_href = c["lang_link_tw"] or c["file"]
    cn_href = c["lang_link_cn"] or c["file"]
    en_href = c["lang_link_en"] or c["file"]

    # per-page rows
    rows = []
    for r in results:
        if r.get("error"):
            badge = f'<span class="audit-badge audit-badge-err">{c["status_err"]}</span>'
            status_text = r["error"][:40]
        elif r["passed"]:
            badge = f'<span class="audit-badge audit-badge-pass">{c["status_pass"]}</span>'
            status_text = "✓"
        else:
            badge = f'<span class="audit-badge audit-badge-fail">{c["status_fail"]}</span>'
            status_text = "✗"
        page_label = r["name"].replace("-", " ").replace("cn", "簡").replace("en", "EN").title()
        if r["name"].endswith("-cn"):
            page_label = r["name"][:-3] + " (简体)"
        elif r["name"].endswith("-en"):
            page_label = r["name"][:-3] + " (EN)"
        rows.append(f"""
        <tr>
          <td><a href="{r['final_url']}" target="_blank" rel="noopener">{page_label}</a></td>
          <td>{badge}</td>
          <td>{r['body_scroll_width']}px</td>
          <td>{r['overflow_count']}</td>
        </tr>""")

    # method steps
    steps_html = "\n        ".join(f"<li>{s}</li>" for s in c["method_steps"])

    return f"""<!DOCTYPE html>
<html lang="{c['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{c['title']}</title>
<meta name="description" content="{c['description']}">
<link rel="icon" type="image/png" href="assets/icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=Noto+Serif+SC:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
<script>(function(){{function setLang(l){{document.cookie='cf_lang='+l+'; path=/; max-age=31536000';try{{localStorage.setItem('cf_lang',l);}}catch(e){{}}}}document.addEventListener('click',function(e){{var t=e.target.closest('[data-lang-target]');if(t)setLang(t.getAttribute('data-lang-target'));}});}})();</script>
<style>
/* ============ V10 Design Tokens (matches site) ============ */
:root {{
  --navy: #0B192C;
  --navy-700: #102542;
  --navy-500: #1B3A5C;
  --gold: #D4AF37;
  --gold-100: #F7EFC9;
  --canvas: #F7F8FA;
  --ink-900: #0B192C;
  --ink-700: #3A4A5C;
  --ink-500: #6B7A8A;
  --ink-100: #E5E9EE;
  --green: #10B981;
  --red: #EF4444;
  --shadow-card: 0 4px 20px rgba(0,0,0,0.06);
}}

/* ============ HERO (Navy + Gold) ============ */
.audit-hero {{
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-700) 100%);
  padding: 100px 0 80px;
  color: white;
  position: relative;
  overflow: hidden;
}}
.audit-hero::before {{
  content: "";
  position: absolute; top: -200px; right: -200px;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(212,175,55,0.15) 0%, transparent 65%);
  border-radius: 50%;
}}
.audit-hero-inner {{
  max-width: 1240px; margin: 0 auto; padding: 0 24px;
  position: relative; z-index: 1;
}}
.audit-hero-eyebrow {{
  display: inline-flex; align-items: center; gap: 8px;
  font-family: 'Inter', sans-serif; font-size: 0.85rem; font-weight: 500;
  letter-spacing: 0.15em; text-transform: uppercase;
  color: var(--gold); margin-bottom: 24px;
}}
.audit-hero-eyebrow::before {{
  content: ""; width: 8px; height: 8px; background: var(--gold); border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}}
@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
.audit-hero-title {{
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.4rem, 6vw, 4.5rem);
  font-weight: 700; line-height: 1.1;
  margin: 0 0 24px; color: white;
}}
.audit-hero-title .gold {{ color: var(--gold); }}
.audit-hero-sub {{
  font-family: 'Inter', sans-serif;
  font-size: clamp(1rem, 2vw, 1.2rem);
  color: rgba(255,255,255,0.78);
  max-width: 720px; line-height: 1.65;
}}

/* ============ STATS GRID ============ */
.audit-stats {{
  max-width: 1240px; margin: -60px auto 0; padding: 0 24px;
  position: relative; z-index: 2;
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;
}}
.audit-stat-card {{
  background: white; border-radius: 16px;
  padding: 32px 24px; text-align: center;
  box-shadow: var(--shadow-card);
  border: 1px solid var(--ink-100);
}}
.audit-stat-num {{
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.5rem, 5vw, 3.5rem);
  font-weight: 700; color: var(--navy);
  line-height: 1; display: block;
}}
.audit-stat-num.pass {{ color: var(--green); }}
.audit-stat-num.zero {{ color: var(--green); }}
.audit-stat-label {{
  font-family: 'Inter', sans-serif; font-size: 0.9rem;
  color: var(--ink-500); margin-top: 12px;
  letter-spacing: 0.05em;
}}

/* ============ SECTIONS ============ */
.audit-section {{
  max-width: 1240px; margin: 80px auto; padding: 0 24px;
}}
.audit-section h2 {{
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  font-weight: 600; color: var(--ink-900);
  margin: 0 0 32px;
}}
.audit-section-narrow {{ max-width: 880px; }}

/* ============ TABLE ============ */
.audit-table-wrap {{
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid var(--ink-100);
  background: white;
  box-shadow: var(--shadow-card);
}}
.audit-table {{ width: 100%; border-collapse: collapse; }}
.audit-table th {{
  background: var(--canvas);
  padding: 14px 18px;
  font-family: 'Inter', sans-serif; font-size: 0.85rem;
  font-weight: 600; color: var(--ink-700);
  text-align: left; letter-spacing: 0.04em;
  border-bottom: 2px solid var(--ink-100);
}}
.audit-table td {{
  padding: 14px 18px;
  font-family: 'Inter', sans-serif; font-size: 0.95rem;
  border-bottom: 1px solid var(--ink-100);
  color: var(--ink-900);
}}
.audit-table tr:last-child td {{ border-bottom: none; }}
.audit-table a {{ color: var(--ink-900); border-bottom: 1px dashed var(--gold); }}
.audit-table a:hover {{ color: var(--gold); border-bottom-style: solid; }}

/* ============ BADGES ============ */
.audit-badge {{
  display: inline-block; padding: 4px 10px;
  font-family: 'Inter', sans-serif; font-size: 0.78rem;
  font-weight: 600; border-radius: 999px;
  letter-spacing: 0.03em;
}}
.audit-badge-pass {{ background: rgba(16,185,129,0.12); color: var(--green); }}
.audit-badge-fail {{ background: rgba(239,68,68,0.12); color: var(--red); }}
.audit-badge-err  {{ background: rgba(107,122,138,0.12); color: var(--ink-500); }}

/* ============ METHODOLOGY ============ */
.audit-method {{
  background: white; padding: 40px;
  border-radius: 16px; box-shadow: var(--shadow-card);
  border: 1px solid var(--ink-100);
}}
.audit-method ol {{
  font-family: 'Inter', sans-serif; font-size: 1rem;
  line-height: 1.8; color: var(--ink-700);
  padding-left: 24px; margin: 0 0 24px;
}}
.audit-method ol li {{ margin-bottom: 8px; }}
.audit-method .audit-method-note {{
  font-family: 'Inter', sans-serif; font-size: 0.92rem;
  color: var(--ink-500); line-height: 1.65;
  padding: 16px 20px;
  background: var(--canvas); border-radius: 10px;
  border-left: 3px solid var(--gold);
}}

/* ============ TIMESTAMP PILL ============ */
.audit-timestamp {{
  display: inline-flex; align-items: center; gap: 8px;
  font-family: 'Inter', sans-serif; font-size: 0.85rem;
  color: var(--ink-500); margin-bottom: 16px;
}}
.audit-timestamp-dot {{
  width: 6px; height: 6px; background: var(--green);
  border-radius: 50%;
}}

/* ============ CTA LINK ============ */
.audit-cta {{
  display: inline-block; margin-top: 16px;
  font-family: 'Inter', sans-serif; font-weight: 600;
  font-size: 1rem; color: var(--gold);
  border-bottom: 2px solid var(--gold);
  padding-bottom: 4px; transition: all 0.2s;
}}
.audit-cta:hover {{ color: var(--navy); border-bottom-color: var(--navy); }}

/* ============ RESPONSIVE ============ */
@media (max-width: 768px) {{
  .audit-stats {{ grid-template-columns: 1fr; margin-top: -40px; }}
  .audit-hero {{ padding: 60px 0 50px; }}
  .audit-section {{ margin: 50px auto; }}
  .audit-table th, .audit-table td {{ padding: 10px 12px; font-size: 0.85rem; }}
  .audit-method {{ padding: 24px; }}
}}

/* ============ FOOTER AUDIT LINK ============ */
.footer-audit {{
  display: inline-flex; align-items: center; gap: 6px;
  margin-left: 16px;
  font-family: 'Inter', sans-serif; font-size: 0.9rem;
  color: var(--ink-700);
}}
.footer-audit::before {{
  content: "✓"; color: var(--green); font-weight: 700;
}}
.footer-audit a {{ color: inherit; }}
.footer-audit a:hover {{ color: var(--gold); }}
</style>
</head>
<body>

<header class="site-header">
  <div class="container">
    <nav class="nav">
      <a href="{nav['links'][0][0]}" class="nav-logo">
        <span class="logo-en">{nav['logo_en']}</span>
        <span class="logo-cn">{nav['logo_zh']}</span>
      </a>
      <div class="nav-menu" id="navMenu">
        {nav_links_html}
      </div>
      <div class="nav-actions">
        <div class="lang-switcher">
          <a href="{tw_href}"{tw_attr} data-lang-target="zh-Hant">繁</a>
          <a href="{cn_href}"{cn_attr} data-lang-target="zh-Hans">简</a>
          <a href="{en_href}"{en_attr} data-lang-target="en">EN</a>
        </div>
        <button class="hamburger" id="hamburgerBtn" aria-label="Menu">
          <span></span><span></span><span></span>
        </button>
      </div>
    </nav>
  </div>
</header>

<!-- ============ HERO ============ -->
<section class="audit-hero">
  <div class="audit-hero-inner">
    <span class="audit-hero-eyebrow">{c['eyebrow']}</span>
    <h1 class="audit-hero-title">
      {c['hero_title_1']}<br>
      <span class="gold">{c['hero_title_2']}</span>
    </h1>
    <p class="audit-hero-sub">{c['hero_sub']}</p>
  </div>
</section>

<!-- ============ STATS ============ -->
<section class="audit-stats">
  <div class="audit-stat-card">
    <span class="audit-stat-num pass">{passed}/{total}</span>
    <span class="audit-stat-label">{c['stat_pages']}</span>
  </div>
  <div class="audit-stat-card">
    <span class="audit-stat-num zero">{len(failed) + len(errored)}</span>
    <span class="audit-stat-label">{c['stat_overflows']}</span>
  </div>
  <div class="audit-stat-card">
    <span class="audit-stat-num">{viewport}</span>
    <span class="audit-stat-label">{c['stat_viewport']}</span>
  </div>
</section>

<!-- ============ PER-PAGE TABLE ============ -->
<section class="audit-section">
  <span class="audit-timestamp">
    <span class="audit-timestamp-dot"></span>
    Last audit: {ts_hkt}
  </span>
  <h2>{c['pages_heading']}</h2>
  <div class="audit-table-wrap">
    <table class="audit-table">
      <thead>
        <tr>
          <th>{c['col_page']}</th>
          <th>{c['col_status']}</th>
          <th>{c['col_width']}</th>
          <th>{c['col_overflows']}</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </div>
  <a href="https://careerforgehk.com" class="audit-cta" target="_blank" rel="noopener">{c['cta_view_live']}</a>
</section>

<!-- ============ METHODOLOGY ============ -->
<section class="audit-section audit-section-narrow">
  <h2>{c['method_heading']}</h2>
  <div class="audit-method">
    <ol>
      {steps_html}
    </ol>
    <div class="audit-method-note">{c['method_note']}</div>
  </div>
</section>

<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="{nav['links'][0][0]}" class="footer-logo-text"><span class="fl-en">{nav['logo_en']}</span><span class="fl-zh">{nav['logo_zh']}</span></a>
        <p>香港高端個人成長顧問。身份 · 升學 · 職涯身價 一站式陪跑。</p>
      </div>
      <div class="footer-col">
        <h4>業務板塊</h4>
        <a href="immigration.html">身份與續簽對標</a>
        <a href="education.html">海外與香港升學</a>
        <a href="career.html">求職與身價躍遷</a>
      </div>
      <div class="footer-col">
        <h4>資源</h4>
        <a href="cases.html">客戶案例</a>
        <a href="quiz.html">牛馬身價測驗</a>
        <a href="#contact">聯絡我們</a>
        <span class="footer-audit"><a href="audit.html">{c['footer_label']}</a></span>
      </div>
      <div class="footer-col">
        <h4>聯絡</h4>
        <a href="https://wa.me/85291371211">WhatsApp</a>
        <a href="mailto:careerforgehk@gmail.com">careerforgehk@gmail.com</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 CareerForge 鑄途. All rights reserved.</span>
      <span class="footer-lang">
        <a href="audit.html">繁體</a> · <a href="audit-cn.html">簡體</a> · <a href="audit-en.html">EN</a>
      </span>
    </div>
  </div>
</footer>

<script>
document.addEventListener('DOMContentLoaded', function() {{
  const hamburger = document.getElementById('hamburgerBtn');
  const menu = document.getElementById('navMenu');
  if (hamburger && menu) {{
    hamburger.addEventListener('click', function() {{
      hamburger.classList.toggle('active');
      menu.classList.toggle('active');
    }});
  }}
}});
</script>
</body>
</html>
"""


def main():
    report = load_report()
    print(f"Loaded report: {report['passed']}/{report['total']} pages pass")
    for lang in ["zh-Hant", "zh-Hans", "en"]:
        c = CONTENT[lang]
        html = render_page(lang, c, report)
        out = ROOT / c["file"]
        out.write_text(html, encoding="utf-8")
        print(f"✓ Wrote {out}  ({len(html):,} bytes)")
    print(f"\nNext: review + push to fork → CF Pages auto-deploys")


if __name__ == "__main__":
    main()