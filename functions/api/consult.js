/**
 * Cloudflare Pages Function — POST /api/consult
 * Handles 4-step consult form submissions
 * 
 * Env vars (set in CF Pages dashboard):
 *   RESEND_API_KEY       — Resend transactional email API key (https://resend.com)
 *   NOTIFY_EMAIL         — recipient email (default: hello@careerforgehk.com)
 *   BARK_WEBHOOK_URL     — Bark push notification webhook (optional)
 *   SUPABASE_URL         — optional, for DB insert
 *   SUPABASE_SERVICE_KEY — optional, for DB insert
 * 
 * Returns:
 *   200 { ok: true, id: <submission_id> }
 *   400 { error: 'invalid payload' }
 *   500 { error: 'submission failed' }
 */

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function onRequestPost(context) {
  const { request, env } = context;

  let payload;
  try {
    payload = await request.json();
  } catch (e) {
    return new Response(JSON.stringify({ error: 'invalid payload' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json', ...CORS },
    });
  }

  // ─── Validate minimal fields ───
  if (!payload || !payload.contact_name || !payload.contact_phone || !payload.step1) {
    return new Response(JSON.stringify({ error: 'missing required fields' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json', ...CORS },
    });
  }

  const submission_id = 'cf_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8);
  const submitted_at = payload.submitted_at || new Date().toISOString();

  // ─── Compose email ───
  const subject = `[顧問: ${payload.advisor_name || '未指定'}] 收到新初評表單 — ${payload.contact_name || '匿名'}`;
  const htmlBody = renderEmailHtml(payload, submission_id);
  const textBody = renderEmailText(payload, submission_id);

  // ─── Send via Resend ───
  const resendKey = env.RESEND_API_KEY;
  const notifyEmail = env.NOTIFY_EMAIL || 'hello@careerforgehk.com';

  let emailOk = false;
  let emailErr = null;

  if (resendKey) {
    try {
      const res = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + resendKey,
        },
        body: JSON.stringify({
          from: 'CareerForge Consult <noreply@careerforgehk.com>',
          to: [notifyEmail],
          subject,
          html: htmlBody,
          text: textBody,
        }),
      });
      emailOk = res.ok;
      if (!res.ok) emailErr = await res.text();
    } catch (e) {
      emailErr = e.message;
    }
  } else {
    // Dev mode: log to console
    console.log('[DEV MODE] No RESEND_API_KEY. Would send email:');
    console.log('Subject:', subject);
    console.log('Body:', textBody);
  }

  // ─── Bark webhook (optional) ───
  if (env.BARK_WEBHOOK_URL) {
    try {
      const advisorTag = payload.advisor_name ? ' · 顧問: ' + payload.advisor_name : '';
      await fetch(env.BARK_WEBHOOK_URL + '/' + encodeURIComponent(
        `[HA02] 新初評表單${advisorTag}\n${payload.contact_name} (${payload.contact_phone})\n通道: ${(payload.step2_channels || []).join(', ')}\nID: ${submission_id}`
      ));
    } catch (e) {
      console.error('Bark webhook failed:', e.message);
    }
  }

  // ─── Supabase (optional) ───
  let dbOk = false;
  if (env.SUPABASE_URL && env.SUPABASE_SERVICE_KEY) {
    try {
      const res = await fetch(env.SUPABASE_URL + '/rest/v1/consult_submissions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': env.SUPABASE_SERVICE_KEY,
          'Authorization': 'Bearer ' + env.SUPABASE_SERVICE_KEY,
          'Prefer': 'return=minimal',
        },
        body: JSON.stringify({
          submission_id,
          submitted_at,
          lang: payload.lang,
          contact_name: payload.contact_name,
          contact_phone: payload.contact_phone,
          advisor_name: payload.advisor_name,
          step1: payload.step1,
          step2_channels: payload.step2_channels,
          step3: payload.step3,
          step4: payload.step4,
        }),
      });
      dbOk = res.ok;
    } catch (e) {
      console.error('Supabase insert failed:', e.message);
    }
  } else {
    console.log('[DEV MODE] No Supabase. Submission logged:');
    console.log(JSON.stringify({ submission_id, ...payload }, null, 2));
  }

  return new Response(JSON.stringify({
    ok: true,
    id: submission_id,
    channels: new URL(request.url).searchParams.get('debug') === '1' ? {
      email: emailOk ? 'sent' : ('skipped: ' + (emailErr || 'no RESEND_API_KEY')),
      db: dbOk ? 'inserted' : 'skipped: no Supabase config',
    } : undefined,
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS });
}

export async function onRequestGet() {
  return new Response(JSON.stringify({
    name: 'CareerForge Consult API',
    method: 'POST',
    endpoint: '/api/consult',
    description: '4-step consult form submission handler',
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}

// ─── Email templates ───
function renderEmailHtml(p, id) {
  const step1Rows = Object.entries(p.step1 || {})
    .map(([k, v]) => `<tr><td style="padding:6px 12px;color:#666;border-bottom:1px solid #eee;">${labelOf(k)}</td><td style="padding:6px 12px;border-bottom:1px solid #eee;font-weight:600;">${v}</td></tr>`)
    .join('');
  const channels = (p.step2_channels || []).map(c => `<span style="display:inline-block;background:#0B192C;color:#D4AF37;padding:4px 10px;border-radius:999px;margin:2px;font-size:12px;">${channelLabel(c)}</span>`).join('');
  const step3Qs = Object.entries(p.step3 || {}).map(([ch, qa]) => `
    <div style="margin: 12px 0; padding: 12px; background: #f9f9f9; border-left: 3px solid #D4AF37;">
      <strong style="color:#0B192C;">${channelLabel(ch)}</strong>
      <ul style="margin: 6px 0 0 18px; color: #444;">${
        Object.entries(qa).map(([q, a]) => `<li style="margin: 4px 0;">${labelOf(q)}: <strong>${a}</strong></li>`).join('')
      }</ul>
    </div>`).join('');

  return `
  <div style="font-family: -apple-system, 'Helvetica Neue', sans-serif; max-width: 640px; margin: 0 auto; padding: 24px; background: #f5f5f5;">
    <div style="background: #0B192C; color: #fff; padding: 24px; border-radius: 8px 8px 0 0; text-align: center;">
      <h1 style="margin:0;font-family:'Playfair Display',serif;font-size:24px;">CareerForge 鑄途</h1>
      <p style="margin:8px 0 0;opacity:0.85;font-size:14px;">新初評表單通知</p>
    </div>
    <div style="background: #fff; padding: 24px; border-radius: 0 0 8px 8px;">
      <p style="margin:0 0 8px;"><strong>提交編號:</strong> <code>${id}</code></p>
      <p style="margin:0 0 16px;color:#666;font-size:13px;">${p.submitted_at}</p>

      <h2 style="font-size:18px;color:#0B192C;border-bottom:2px solid #D4AF37;padding-bottom:6px;">聯絡資料</h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
        <tr><td style="padding:6px 12px;color:#666;">姓名</td><td style="padding:6px 12px;font-weight:600;">${p.contact_name || ''}</td></tr>
        <tr><td style="padding:6px 12px;color:#666;">電話</td><td style="padding:6px 12px;font-weight:600;">${p.contact_phone || ''}</td></tr>
        <tr><td style="padding:6px 12px;color:#666;">顧問</td><td style="padding:6px 12px;font-weight:600;">${p.advisor_name || '(未指定)'}</td></tr>
      </table>

      <h2 style="font-size:18px;color:#0B192C;border-bottom:2px solid #D4AF37;padding-bottom:6px;">意向通道</h2>
      <div style="margin-bottom:20px;">${channels || '(無)'}</div>

      <h2 style="font-size:18px;color:#0B192C;border-bottom:2px solid #D4AF37;padding-bottom:6px;">Step 1 — 通用資訊</h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">${step1Rows}</table>

      <h2 style="font-size:18px;color:#0B192C;border-bottom:2px solid #D4AF37;padding-bottom:6px;">Step 3 — 通道專屬問題</h2>
      ${step3Qs || '<p style="color:#999;">(無)</p>'}

      <p style="margin-top: 24px; font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 12px;">
        此通知由 CareerForge 鑄途 網站 /api/consult 自動發送。
      </p>
    </div>
  </div>`;
}

function renderEmailText(p, id) {
  const lines = [
    `CareerForge 鑄途 — 新初評表單`,
    `提交編號: ${id}`,
    `提交時間: ${p.submitted_at}`,
    ``,
    `=== 聯絡資料 ===`,
    `姓名: ${p.contact_name || ''}`,
    `電話: ${p.contact_phone || ''}`,
    `顧問: ${p.advisor_name || '(未指定)'}`,
    ``,
    `=== 意向通道 ===`,
    (p.step2_channels || []).map(c => `- ${channelLabel(c)}`).join('\n'),
    ``,
    `=== Step 1 — 通用資訊 ===`,
    Object.entries(p.step1 || {}).map(([k, v]) => `${labelOf(k)}: ${v}`).join('\n'),
    ``,
    `=== Step 3 — 通道專屬問題 ===`,
    Object.entries(p.step3 || {}).map(([ch, qa]) =>
      `[${channelLabel(ch)}]\n` + Object.entries(qa).map(([q, a]) => `  ${labelOf(q)}: ${a}`).join('\n')
    ).join('\n\n'),
  ];
  return lines.join('\n');
}

const LABELS = {
  age: '年齡', passport: '國籍/護照', education: '最高學歷', work_exp: '工作經驗',
  industry: '行業', compliance: '背景合規', family: '隨行意向', timeline: '預計辦理時間',
  has_advisor: '有專屬顧問', advisor_name: '顧問名稱', contact_name: '聯絡姓名', contact_phone: '聯絡電話',
  ttps_income: 'TTPS-收入', ttps_exec: 'TTPS-高管/核心技術',
  gep_cert: 'GEP-專業資格', gep_exp: 'GEP-相關經驗', gep_offer: 'GEP-HK僱主Offer', gep_business: 'GEP-在港創業',
  qmas_english: 'QMAS-英語', qmas_industry: 'QMAS-重點行業', qmas_award: 'QMAS-獎項/專利',
  qmas_mnc: 'QMAS-MNC經驗', qmas_overseas: 'QMAS-海外經驗', qmas_income: 'QMAS-收入', qmas_business: 'QMAS-業務',
  ciis_net: 'CIES-淨資產', ciis_invest: 'CIES-投資意願',
  study_english: '留學-英語', study_stage: '留學-申請階段', study_mode: '留學-就讀時間',
  study_stay: '留學-留港發展', study_goal: '留學-核心需求', study_family: '留學-配偶子女',
};
const CH_LABELS = {
  ttps: '高才通 (TTPS)', gep: '專才 (GEP)', qmas: '優才 (QMAS)', ciis: '投資移民 (CIES)', study: '留學進修',
};
function labelOf(k) { return LABELS[k] || k; }
function channelLabel(c) { return CH_LABELS[c] || c; }
