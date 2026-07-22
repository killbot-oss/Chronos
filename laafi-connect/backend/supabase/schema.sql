-- Laafi-Connect Supabase schema
-- Run this in the Supabase SQL editor (Project > SQL Editor > New query)

-- ── PROFILES ─────────────────────────────────────────────────────
create table if not exists profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  full_name text,
  pathology text,
  stade text,
  blood_group text,
  allergies text,
  dob date,
  avatar text,
  treating_doctor_id bigint,
  updated_at timestamptz default now()
);

alter table profiles enable row level security;

create policy "profiles_select_own" on profiles
  for select using (auth.uid() = id);
create policy "profiles_upsert_own" on profiles
  for insert with check (auth.uid() = id);
create policy "profiles_update_own" on profiles
  for update using (auth.uid() = id);

-- ── VITALS (offline-first: client generates local_id to dedupe on sync) ──
create table if not exists vitals (
  id bigserial primary key,
  user_id uuid references auth.users (id) on delete cascade not null,
  local_id text,
  type text not null,          -- ta | glycemie | poids | spo2 | pouls | temperature
  value jsonb not null,        -- e.g. {"ta_sys":128,"ta_dia":82} or {"val":1.05}
  recorded_at timestamptz not null default now(),
  synced_at timestamptz default now(),
  unique (user_id, local_id)
);

alter table vitals enable row level security;

create policy "vitals_select_own" on vitals
  for select using (auth.uid() = user_id);
create policy "vitals_insert_own" on vitals
  for insert with check (auth.uid() = user_id);
create policy "vitals_upsert_own" on vitals
  for update using (auth.uid() = user_id);

-- ── MEDICATIONS ──────────────────────────────────────────────────
create table if not exists medications (
  id bigserial primary key,
  user_id uuid references auth.users (id) on delete cascade not null,
  name text not null,
  dose text,
  times text[] default '{}',
  checked_today boolean default false,
  updated_at timestamptz default now()
);

alter table medications enable row level security;

create policy "meds_select_own" on medications
  for select using (auth.uid() = user_id);
create policy "meds_write_own" on medications
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ── PHARMACIES (public reference data, read via service role) ──────
create table if not exists pharmacies (
  id bigserial primary key,
  name text not null,
  address text,
  phone text,
  on_duty boolean default true,
  lat double precision,
  lon double precision,
  updated_at timestamptz default now()
);
-- No RLS: read through backend's service role only (frontend never calls
-- Supabase directly for this table).

-- ── DOCTORS (public reference data) ─────────────────────────────
create table if not exists doctors (
  id bigserial primary key,
  name text not null,
  specialty text,
  specialty_label text,
  address text,
  phone text,
  availability text,
  hours text,
  lat double precision,
  lon double precision,
  distance_km double precision,
  avatar text,
  updated_at timestamptz default now()
);

-- ── DEVICE TOKENS (for future FCM push notifications) ───────────
create table if not exists device_tokens (
  id bigserial primary key,
  user_id uuid references auth.users (id) on delete cascade not null,
  token text not null,
  platform text default 'android',
  created_at timestamptz default now(),
  unique (user_id, token)
);

alter table device_tokens enable row level security;

create policy "device_tokens_own" on device_tokens
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
