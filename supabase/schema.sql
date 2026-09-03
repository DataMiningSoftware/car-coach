-- car-coach schema (Supabase)

create table if not exists cars (
  id bigint generated always as identity primary key,
  make text not null,
  model text not null,
  year text,
  specs jsonb not null default '{}'::jsonb,
  history text,
  created_at timestamptz not null default now()
);

create table if not exists owner_reviews (
  id bigint generated always as identity primary key,
  car_id bigint references cars (id) on delete cascade,
  rating int check (rating between 1 and 5),
  remark text not null,
  created_at timestamptz not null default now()
);

create table if not exists garages (
  id bigint generated always as identity primary key,
  user_id text not null,
  make text,
  model text,
  year text,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists workshops (
  id bigint generated always as identity primary key,
  name text not null,
  specialty text,
  location text,
  rating text,
  source text,
  created_at timestamptz not null default now()
);
