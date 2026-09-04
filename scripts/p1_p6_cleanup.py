#!/usr/bin/env python3
"""P1 + P6 batch cleanup — remove ALL 牛馬測驗 references + anonymize real 公司/校名."""
import re, os
from pathlib import Path

ROOT = Path("/home/ubuntu/workspace/careerforge-site")

# ── P1: Quiz → Consult replacement rules ─────────────────────────────
# (regex, replacement) tuples — order matters
P1_RULES = [
    # hrefs first (most critical)
    (r'href="quiz\.html"', 'href="consult.html"'),
    (r'href="quiz-cn\.html"', 'href="consult-cn.html"'),
    (r'href="quiz-en\.html"', 'href="consult-en.html"'),
    # 繁體 labels
    (r'>牛馬測驗</a>', '>5 分鐘免費初評</a>'),
    (r'>牛馬身價測驗</a>', '>免費身價諮詢</a>'),
    (r'>先做 3 分鐘牛馬測驗</a>', '>預約 30 分鐘免費諮詢</a>'),
    (r'>先做 <span class="num-unit">3 分鐘</span>牛馬測驗</a>', '>預約 <span class="num-unit">30 分鐘</span>免費諮詢</a>'),
    (r'>先做牛馬測驗</a>', '>預約免費諮詢</a>'),
    # 简体 (career-cn)
    (r'>牛马测验</a>', '>5 分钟免费初评</a>'),
    (r'>先做 3 分钟牛马测验</a>', '>预约 30 分钟免费咨询</a>'),
    # EN labels
    (r'>Quiz</a>', '>Free Assessment</a>'),
    (r'>Try the 3-min Career Quiz</a>', '>Book a 30-min Free Consult</a>'),
    # EN labels (education-en)
    (r'>牛馬test</a>', '>Free Assessment</a>'),
    (r'>牛馬身價test</a>', '>Free Consult</a>'),
    # Eyebrow / inline labels (inside quiz.html mostly — but also reference pages)
    (r'>牛馬測驗 · 3 分鐘見未來<', '>5 分鐘免費初評 · CareerForge 鑄途<'),
    (r'牛馬測驗', 'CareerForge 諮詢'),
    # Footer service list
    (r'<li><a href="consult\.html">5 分鐘免費初評</a></li>', '<li><a href="consult.html">5 分鐘免費初評</a></li>'),
    # mailto subjects
    (r'hello@careerforgehk\.com\?subject=CareerForge 諮詢預約',
     'hello@careerforgehk.com?subject=CareerForge 諮詢預約'),
    # EN mailto subject
    (r'hello@careerforgehk\.com\?subject=CareerForge 諮詢預約 後諮詢',
     'hello@careerforgehk.com?subject=CareerForge%20Consultation'),
]

# ── P6: Privacy anonymization ────────────────────────────────────────
# (regex, replacement) — case-sensitive, exact match
P6_RULES = [
    # 貝恩 (Bain & Company)
    (r'入貝恩公司', '入全球頂尖戰略顧問公司'),
    # McKinsey (both cases.html)
    (r'最後入 McKinsey', '最後入全球頂尖戰略顧問公司'),
    # Goldman Sachs
    (r'前 Google / Goldman Sachs / McKinsey recruitment lead',
     '前全球頂尖科技 / 投行 / 戰略顧問公司 recruitment lead'),
    # Google PM
    (r'拿到 Google PM offer', '拿到全球 Top 5 科技巨頭 PM offer'),
    # 九龍真光 (real school name)
    (r'九龍真光中學', '香港知名九龍區女子名校'),
    # Google 客戶評分
    (r'>Google 客戶評分<', '>客戶評分<'),
    # Sub brand names in copy (defensive)
    (r'\bBain\b', '頂尖戰略顧問'),
    (r'\bMcKinsey\b', '頂尖戰略顧問'),
    (r'\bGoldman Sachs\b', '頂尖投行'),
    (r'\bHSBC\b', '頂尖國際銀行'),
]

def apply_rules(text, rules):
    for pat, rep in rules:
        text = re.sub(pat, rep, text)
    return text

def process_file(path: Path, rules, dry_run=False):
    text = path.read_text(encoding="utf-8")
    new_text = apply_rules(text, rules)
    if new_text != text:
        if dry_run:
            diff_count = sum(1 for a, b in zip(text.split("\n"), new_text.split("\n")) if a != b)
            print(f"  [DRY] {path.name}: {diff_count} lines would change")
            return False
        path.write_text(new_text, encoding="utf-8")
        print(f"  ✓ {path.name}: updated")
        return True
    return False

# ── Main ──────────────────────────────────────────────────────────────
HTML_FILES = sorted(ROOT.glob("*.html"))
print(f"=== P1 + P6 batch on {len(HTML_FILES)} HTML files ===\n")

print("--- P1: Quiz → Consult cleanup ---")
p1_changed = 0
for f in HTML_FILES:
    if process_file(f, P1_RULES):
        p1_changed += 1
print(f"P1 changes: {p1_changed} files")

print("\n--- P6: Privacy anonymization ---")
p6_changed = 0
for f in HTML_FILES:
    if process_file(f, P6_RULES):
        p6_changed += 1
print(f"P6 changes: {p6_changed} files")

# Delete quiz pages (and their cn/en variants)
print("\n--- Delete quiz.html / quiz-cn.html / quiz-en.html ---")
for f in ["quiz.html", "quiz-cn.html", "quiz-en.html"]:
    p = ROOT / f
    if p.exists():
        p.unlink()
        print(f"  ✓ deleted {f}")
    else:
        print(f"  - {f} not found")

# Also delete immigration-cn-v17.html (stale backup per task 1 cleanup spirit)
print("\n--- Delete stale immigration-cn-v17.html backup ---")
p = ROOT / "immigration-cn-v17.html"
if p.exists():
    p.unlink()
    print(f"  ✓ deleted immigration-cn-v17.html")
else:
    print(f"  - not found")

# Note: audit.html is internal QA tool — leave alone (not customer-facing)
print("\n--- NOTE: audit.html / audit-cn.html / audit-en.html are internal QA tools (ND never made public) — left alone ---")

print("\n=== Verification: any remaining 牛馬 / quiz refs? ===")
os.system(f"cd {ROOT} && grep -rn '牛馬\\|quiz\\.html\\|quiz-cn\\.html\\|quiz-en\\.html\\|McKinsey\\|Goldman\\|Google PM\\|九龍真光\\|貝恩' *.html | head -20")
print("(empty = all clean)")

print("\n=== Files remaining ===")
remaining = sorted(ROOT.glob("*.html"))
print(f"Total HTML files: {len(remaining)}")
print("Files:", " | ".join(f.name for f in remaining))
