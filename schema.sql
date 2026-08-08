-- Run this in the Supabase SQL editor. Safe to re-run.

-- === Fixes: "new row for relation profiles violates check
-- constraint profiles_activity_level_check" ===
-- Your profiles.activity_level column has a check constraint whose
-- allowed values don't match what the app sends. The app sends
-- exactly these five (lowercase, spaces replaced with underscores):
--   sedentary, lightly_active, moderately_active, very_active,
--   extremely_active
-- This replaces whatever the existing constraint allows with that
-- exact set. If you'd rather keep your original constraint, change
-- ACTIVITY_MULTIPLIERS in services/nutrition.py to match its values
-- instead of running this.

alter table profiles drop constraint if exists profiles_activity_level_check;

alter table profiles add constraint profiles_activity_level_check
    check (activity_level in (
        'sedentary', 'lightly_active', 'moderately_active',
        'very_active', 'extremely_active'
    ));

-- The app also sends a `goal` column as one of: lose_weight,
-- maintain, gain_weight. If profiles has a check constraint on
-- `goal` too and it doesn't allow these exact values, you'll hit the
-- same error there — the app's error handling now catches this kind
-- of mismatch automatically (it drops the offending field and saves
-- the rest, with a warning telling you which field failed), but fix
-- it here the same way if you want it persisted:
--
-- alter table profiles drop constraint if exists profiles_goal_check;
-- alter table profiles add constraint profiles_goal_check
--     check (goal in ('lose_weight', 'maintain', 'gain_weight'));

-- === Fixes the crash you hit earlier ===
-- "null value in column quantity of relation food_logs violates
-- not-null constraint" — the app now writes quantity_value (numeric)
-- instead of quantity. The app itself also now fills the old
-- `quantity`/`unit` columns as a fallback, so this ALTER is a
-- belt-and-suspenders fix, not strictly required — but worth doing
-- so the schema matches what the app actually models.

alter table food_logs alter column quantity drop not null;
alter table food_logs alter column unit drop not null;

-- Make sure eaten_at always gets a value even if some future insert
-- path forgets to set it (the app now sets it explicitly on every
-- insert, but a DB-level default is good defense-in-depth).
alter table food_logs alter column eaten_at set default now();

-- === New columns this refactor introduced ===

alter table food_logs
    add column if not exists food_type text default 'food',
    add column if not exists quantity_value numeric,
    add column if not exists quantity_unit text;

-- Backfill quantity_value / quantity_unit from the old columns for
-- any existing rows (safe to skip on a fresh table).
update food_logs
set
    quantity_value = quantity,
    quantity_unit = unit
where
    quantity_value is null
    and quantity is not null;

alter table quick_entries
    add column if not exists food_type text default 'food';

-- Once you've confirmed the new app is working and don't need the
-- old columns anymore:
-- alter table food_logs drop column quantity, drop column unit;
