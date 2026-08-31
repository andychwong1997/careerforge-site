# CareerForge Consult Form — Setup Checklist

## Frontend (✅ Done)
- `/consult.html`, `/consult-cn.html`, `/consult-en.html` — 3 langs
- 4-step state machine with dynamic Step 3 (5 channel-specific question sets)
- Form validation (per-step required + conditional advisor_name)
- Mobile-first responsive (390px-1440px+)
- Brand tokens: navy + gold + Playfair Display + Noto Serif SC

## Backend (✅ Code ready, ⚠️ Needs env setup)

### Option A: Cloudflare Pages Function + Resend + Bark (recommended for ND)
1. **Cloudflare Pages env vars** (Settings → Environment variables):
   ```
   RESEND_API_KEY = re_xxxxxxxxxxxxxx
   NOTIFY_EMAIL   = hello@careerforgehk.com
   BARK_WEBHOOK_URL = https://bark.hestocket.com/XXXXX
   ```
2. **Resend setup** (https://resend.com):
   - Sign up free (10k emails/month)
   - Verify sender domain `careerforgehk.com` (DNS records auto-provided)
   - Create API key → paste into CF Pages env

3. **Bark URL** — already in ND's env (memory). Paste as `BARK_WEBHOOK_URL`.

### Option B: Supabase DB (optional, for record-keeping)
1. Create new project at https://supabase.com (free tier: 500MB)
2. Run `supabase-consult-migration.sql` in SQL Editor
3. Set env vars:
   ```
   SUPABASE_URL        = https://xxx.supabase.co
   SUPABASE_SERVICE_KEY = eyJ...  (⚠️ keep secret, server-side only)
   ```

## Wire CTA Buttons (✅ ready to do)
- `index.html` line 1129: Pillar 01 "了解詳情" → `/consult.html`
- `immigration.html` line 1948-1955: bottom CTA "WhatsApp" + "牛馬測驗" → `/consult.html`
- (Optional) `consult.html` link in nav as well

## Deploy
```bash
cd ~/workspace/careerforge-site
git add consult.html consult-cn.html consult-en.html functions/api/consult.js supabase-consult-migration.sql
git commit -m "feat: 4-step consult form (Modal/page) + /api/consult backend"
git push origin master --force-with-lease
git push origin main --force-with-lease
# CF Pages will auto-deploy; env vars are set per-project in dashboard
```
