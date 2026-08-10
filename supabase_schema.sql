create table if not exists public.reading_progress (
  user_id uuid not null references auth.users(id) on delete cascade,
  reading_id text not null,
  completed boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (user_id, reading_id)
);

create table if not exists public.vocab_srs (
  user_id uuid not null references auth.users(id) on delete cascade,
  card_id text not null,
  correct integer not null default 0,
  wrong integer not null default 0,
  reviews integer not null default 0,
  lapses integer not null default 0,
  interval_days double precision not null default 0,
  ease double precision not null default 2.5,
  due timestamptz,
  mastered boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (user_id, card_id)
);

create table if not exists public.user_stats (
  user_id uuid primary key references auth.users(id) on delete cascade,
  correct integer not null default 0,
  wrong integer not null default 0,
  attempts integer not null default 0,
  card_views integer not null default 0,
  updated_at timestamptz not null default now()
);

alter table public.reading_progress enable row level security;
alter table public.vocab_srs enable row level security;
alter table public.user_stats enable row level security;

create policy "reading_select_own" on public.reading_progress for select to authenticated using ((select auth.uid()) = user_id);
create policy "reading_insert_own" on public.reading_progress for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "reading_update_own" on public.reading_progress for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "reading_delete_own" on public.reading_progress for delete to authenticated using ((select auth.uid()) = user_id);

create policy "vocab_select_own" on public.vocab_srs for select to authenticated using ((select auth.uid()) = user_id);
create policy "vocab_insert_own" on public.vocab_srs for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "vocab_update_own" on public.vocab_srs for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy "vocab_delete_own" on public.vocab_srs for delete to authenticated using ((select auth.uid()) = user_id);

create policy "stats_select_own" on public.user_stats for select to authenticated using ((select auth.uid()) = user_id);
create policy "stats_insert_own" on public.user_stats for insert to authenticated with check ((select auth.uid()) = user_id);
create policy "stats_update_own" on public.user_stats for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);

create index if not exists reading_progress_user_idx on public.reading_progress(user_id);
create index if not exists vocab_srs_user_idx on public.vocab_srs(user_id);
create index if not exists vocab_srs_due_idx on public.vocab_srs(user_id,due);
