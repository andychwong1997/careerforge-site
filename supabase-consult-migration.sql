-- CareerForge Consult Submissions Table
-- Run this in Supabase SQL Editor when ready

create table if not exists consult_submissions (
  id bigserial primary key,
  submission_id text unique not null,
  submitted_at timestamptz not null default now(),
  lang text,
  contact_name text not null,
  contact_phone text not null,
  advisor_name text,
  step1 jsonb not null,
  step2_channels text[] not null default '{}',
  step3 jsonb not null default '{}'::jsonb,
  step4 jsonb not null default '{}'::jsonb,
  processed boolean default false,
  assigned_to text,
  notes text,
  created_at timestamptz default now()
);

-- Index for fast lookup by submission_id
create index if not exist idx_consult_submissions_id on consult_submissions(submission_id);
create index if not exist idx_consult_submissions_advisor on consult_submissions(advisor_name);
create index if not exist idx_consult_submissions_processed on consult_submissions(processed);

-- Row Level Security: deny all by default; service_role bypasses
alter table consult_submissions enable row level security;
