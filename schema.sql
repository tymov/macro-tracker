-- Run this in the Supabase SQL editor before deploying the new app.
-- It's additive/non-destructive: existing columns (quantity, unit) are
-- left in place, and old rows automatically get food_type = 'food'.

alter table food_logs
    add column if not exists food_type text default 'food',
    add column if not exists quantity_value numeric,
    add column if not exists quantity_unit text;

-- Backfill quantity_value / quantity_unit from the old quantity/unit
-- columns for any existing rows (safe to skip if this is a fresh table).
update food_logs
set
    quantity_value = quantity,
    quantity_unit = unit
where
    quantity_value is null
    and quantity is not null;

-- Optional: quick_entries gets the same category column for consistency
-- with the dashboard's meals/drinks split.
alter table quick_entries
    add column if not exists food_type text default 'food';

-- Once you've confirmed the new app is working and you don't need the
-- old columns anymore, you can drop them:
-- alter table food_logs drop column quantity, drop column unit;
