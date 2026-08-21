# CareerForge Deploy Checklist — Service Worker Version Bump

## Why this matters
iPhone Safari disk cache for HTML pages ignores server `Cache-Control: no-store`.
Service Worker (SW) at `/sw.js` is the permanent fix. **Every deploy MUST bump
the SW version** so returning iPhone users reload-fresh automatically.

## Deploy checklist (MANDATORY before commit)

1. **Bump SW VERSION in `/sw.js`**
   ```bash
   sed -i 's|const VERSION = .v18\.[0-9]*.;|const VERSION = "v18.N";|' sw.js
   ```

2. **Bump HTML register URL query string in all 22 HTML files**
   ```bash
   sed -i 's|sw.js?v=v18\.[0-9]*|sw.js?v=v18.N|g' *.html
   ```

3. **Verify diff before commit**
   ```bash
   git diff --stat | tail -3
   # Expect: sw.js + 22 HTML files = 23 changed
   ```

4. **Commit + push**
   ```bash
   git add -A
   git commit -m "v18.N: <change summary>"
   git push origin master
   ```

5. **Wait ~30s for CF Pages auto-deploy**

6. **Verify live**
   ```bash
   curl -s "https://careerforgehk.com/?v=v18.N" | grep "v18.N"
   # Should show updated version in SW query string
   ```

## One-liner automation (paste this whole block)

```bash
cd /home/ubuntu/workspace/careerforge-site
NEW_VER="v18.N"  # ← set new version here
OLD_VER_PATTERN='v18\.[0-9]+'

# Bump SW
sed -i "s|const VERSION = \"${OLD_VER_PATTERN}\"|const VERSION = \"${NEW_VER}\"|" sw.js

# Bump HTML register URLs
sed -i "s|sw.js?${OLD_VER_PATTERN}|sw.js?${NEW_VER}|g" *.html

# Verify
echo "=== SW VERSION ==="
grep "const VERSION" sw.js
echo "=== HTML register (sample) ==="
grep -h "sw.js?v=" index.html | head -1

# Commit + push
git add -A
git commit -m "${NEW_VER}: deploy"
git push origin master
```

## Why this works (technical)

- **HTML register URL** uses `?v=v18.N` query string → CF Pages treats as different cache key → browser fetches server fresh on every page load
- **SW `skipWaiting()`** in install handler → new SW skips waiting state, takes control immediately
- **SW `clients.claim()`** in activate handler → new SW claims all open clients right away (no double-reload needed)
- **`CACHE_NAME = 'cf-v18.N'`** in SW → activate handler wipes all `cf-v18.X` (X≠N) caches
- **Network-first for navigation requests** → fresh HTML every page load
- **Cache-first for static assets** (CSS/JS/images) → speed, revalidated in background

## Gotchas

- ❌ **Never forget to bump version** — if you don't, browser keeps using cached old SW → user sees stale content (iPhone Safari disk cache bug surfaces again)
- ❌ **Don't use `?v=${Date.now()}`** — changes every build, defeats cache efficiency
- ✅ **Use semantic versioning** `v18.6`, `v18.7` etc. — predictable, traceable in git log
- ✅ **Bump MAJOR on breaking changes** (e.g. v19.0) — signals user should expect redesign

## Reference

- CareerForge live: `https://careerforgehk.com`
- Fork: `https://github.com/andychwong1997/careerforge-site`
- Auto-publish cron: `0 19 * * *` UTC (HKT 03:00) — runs `audit-and-publish.sh`, auto-bumps `/audit*` pages with current timestamp
