#!/usr/bin/env python3
"""Analyze v3 audit results to find systematic issues."""
import json
from pathlib import Path
from collections import Counter, defaultdict

results = json.loads(Path('/home/ubuntu/.hermes/hermes-agent/p5_audit_v3_results.json').read_text())

print("=" * 80)
print("OVERFLOW — which pages, how many px")
print("=" * 80)
for r in results:
    if r['overflow_px'] > 1:
        print(f"  [{r['viewport']}] {r['template']:12}/{r['lang']}  overflow={r['overflow_px']}px")

print()
print("=" * 80)
print("CONTRAST FAILURES — top signatures (color / bg / ratio / threshold)")
print("=" * 80)
all_issues = []
for r in results:
    for issue in r['contrast_failures']:
        all_issues.append({
            **issue,
            '_ctx': f"{r['template']}/{r['lang']}/{r['viewport']}",
            '_cls_short': (issue['cls'] or '').strip()[:30] or '(no-class)',
        })

sig_counter = Counter()
sig_examples = defaultdict(list)
for issue in all_issues:
    sig = (issue['color'], issue['bg'], issue['ratio'], issue['threshold'], issue['fontSize'], issue['_cls_short'])
    sig_counter[sig] += 1
    if len(sig_examples[sig]) < 3:
        sig_examples[sig].append((issue['text'], issue['_ctx']))

print(f"Total contrast failures: {len(all_issues)}")
print(f"Unique (color+bg+ratio+thresh+fontSize+cls) signatures: {len(sig_counter)}")
print()
print("Top 25 signatures:")
for sig, count in sig_counter.most_common(25):
    print(f"  {count:3}x {sig[0]:28} / {sig[1]:28} ratio={sig[2]:5.2f} thresh={sig[3]} font={sig[4]:7} cls='{sig[5]}'")
    for text, ctx in sig_examples[sig][:2]:
        print(f"        ex: '{text}' [{ctx}]")

print()
print("=" * 80)
print("CONTRAST — by class (which CSS class causes most failures)")
print("=" * 80)
class_counter = Counter()
for issue in all_issues:
    class_counter[issue['_cls_short']] += 1
for cls, count in class_counter.most_common(15):
    print(f"  {count:4}x  {cls}")

print()
print("=" * 80)
print("CONTRAST — by color (which color is problematic)")
print("=" * 80)
color_counter = Counter()
for issue in all_issues:
    color_counter[issue['color']] += 1
for color, count in color_counter.most_common(10):
    print(f"  {count:4}x  {color}")

print()
print("=" * 80)
print("EDUCATION page — has most failures (92-102) — what classes?")
print("=" * 80)
edu_counter = Counter()
for issue in all_issues:
    if 'education' in issue['_ctx']:
        edu_counter[issue['_cls_short']] += 1
for cls, count in edu_counter.most_common(15):
    print(f"  {count:4}x  {cls}")

print()
print("=" * 80)
print("SMALL TARGETS — top patterns across all mobile audits")
print("=" * 80)
target_counter = Counter()
for r in results:
    if r['viewport'] != 'mobile': continue
    for t in r['small_targets']:
        target_counter[(t['cls'], t['size'], t['tag'])] += t['count']
for sig, count in target_counter.most_common(15):
    print(f"  {count:3}x  <{sig[2]} class='{sig[0][:35]}'>  {sig[1]}px")
