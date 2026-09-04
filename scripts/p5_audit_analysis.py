#!/usr/bin/env python3
"""Deep dive into P5 audit findings."""
import json
from pathlib import Path
from collections import Counter, defaultdict

results = json.loads(Path('/home/ubuntu/.hermes/hermes-agent/p5_audit_results.json').read_text())

print("=" * 80)
print("LAYOUT OVERFLOW — which pages, how many px")
print("=" * 80)
for r in results:
    layout = r['checks'].get('layout', {})
    if layout.get('overflow'):
        print(f"  [{r['viewport']:7}] {r['template']:12}/{r['lang']:2}  overflow={layout['overflowPx']}px  scrollW={layout['scrollWidth']} clientW={layout['clientWidth']}")

print()
print("=" * 80)
print("CONTRAST FAILURES — top patterns (text color + bg + ratio)")
print("=" * 80)
all_contrast_issues = []
for r in results:
    for issue in r['checks'].get('contrast_failures', []):
        issue['_ctx'] = f"{r['template']}/{r['lang']}/{r['viewport']}"
        all_contrast_issues.append(issue)

# Group by signature (color + bg + ratio)
sig_counter = Counter()
sig_details = {}
for issue in all_contrast_issues:
    sig = (issue['color'], issue['bg'], issue['ratio'], issue['threshold'], issue['fontSize'])
    sig_counter[sig] += 1
    if sig not in sig_details:
        sig_details[sig] = issue['text']

print(f"Total contrast failures across 48 audits: {len(all_contrast_issues)}")
print(f"Unique signatures: {len(sig_counter)}")
print()
print("Top 15 signatures (color / bg / ratio / threshold / fontSize):")
for sig, count in sig_counter.most_common(15):
    print(f"  {count:3}x  {sig[0]:25} / {sig[1]:25} ratio={sig[2]:5.2f}  thresh={sig[3]}  font={sig[4]:8}  ex='{sig_details[sig]}'")

print()
print("=" * 80)
print("CONTRAST — by page (count per page)")
print("=" * 80)
page_count = Counter()
for r in results:
    page_count[(r['template'], r['lang'], r['viewport'])] = len(r['checks'].get('contrast_failures', []))
for k, v in sorted(page_count.items(), key=lambda x: -x[1])[:15]:
    print(f"  {k[2]:7} {k[0]:12}/{k[1]:2}  {v} failures")

print()
print("=" * 80)
print("CONSULT page contrast — full detail (anomaly: only 2 vs 10 elsewhere)")
print("=" * 80)
for r in results:
    if r['template'] == 'consult':
        for issue in r['checks'].get('contrast_failures', []):
            print(f"  [{r['viewport']}] {r['lang']}: '{issue['text']}' color={issue['color']} bg={issue['bg']} ratio={issue['ratio']} thresh={issue['threshold']} font={issue['fontSize']}")

print()
print("=" * 80)
print("SMALL TARGETS — top patterns (tag / cls / w×h)")
print("=" * 80)
target_counter = Counter()
target_examples = defaultdict(list)
for r in results:
    if r['viewport'] != 'mobile': continue
    for t in r['checks'].get('small_targets', []):
        sig = (t['tag'], t['cls'], t['w'], t['h'])
        target_counter[sig] += 1
        if len(target_examples[sig]) < 3:
            target_examples[sig].append(t['text'])

for sig, count in target_counter.most_common(15):
    print(f"  {count:3}x  <{sig[0]} class='{sig[1][:20]}'>  {sig[2]}×{sig[3]}px  ex={target_examples[sig][:2]}")

print()
print("=" * 80)
print("PAGES WITH 0 contrast failures (sanity check)")
print("=" * 80)
zero_contrast = [k for k, v in page_count.items() if v == 0]
print(f"Count: {len(zero_contrast)} / {len(page_count)}")
for k in zero_contrast:
    print(f"  {k}")
