-- ============================================================================
-- Migration: align tasks table with Task domain model
-- File: 20260628_002_align_tasks_table.sql
--
-- Application model (app/models/task.py, app/schemas/task.py):
--   id, family_id, title, description, due_date, priority, status,
--   assigned_member_id, inbox_item_id, created_at, updated_at, deleted_at
--
-- Observed runtime error:
--   Could not find the 'assigned_member_id' column of 'tasks' in the schema cache
--
-- Strategy:
--   Add any missing columns with IF NOT EXISTS (preserves existing rows).
--   Apply sensible defaults aligned with TaskCreate / Task domain defaults.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- PRE-FLIGHT: inspect current tasks schema and row count
-- ----------------------------------------------------------------------------

-- Current columns on public.tasks
SELECT
    column_name,
    data_type,
    udt_name,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'tasks'
ORDER BY ordinal_position;

-- Existing foreign-key constraints on public.tasks
SELECT
    con.conname AS constraint_name,
    pg_get_constraintdef(con.oid) AS definition
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
WHERE nsp.nspname = 'public'
  AND rel.relname = 'tasks'
  AND con.contype = 'f'
ORDER BY con.conname;

-- Row count (should be unchanged after migration)
SELECT COUNT(*) AS task_row_count FROM public.tasks;

-- ============================================================================
-- MIGRATION (transactional)
-- ============================================================================

BEGIN;

-- Core content and scheduling fields
ALTER TABLE public.tasks
    ADD COLUMN IF NOT EXISTS description text,
    ADD COLUMN IF NOT EXISTS due_date date;

-- Lifecycle fields (application sends text enum values: MEDIUM, NEW, etc.)
ALTER TABLE public.tasks
    ADD COLUMN IF NOT EXISTS priority text,
    ADD COLUMN IF NOT EXISTS status text;

-- Relationship fields (reported missing: assigned_member_id)
ALTER TABLE public.tasks
    ADD COLUMN IF NOT EXISTS assigned_member_id uuid,
    ADD COLUMN IF NOT EXISTS inbox_item_id uuid;

-- Audit / soft-delete timestamps
ALTER TABLE public.tasks
    ADD COLUMN IF NOT EXISTS created_at timestamptz,
    ADD COLUMN IF NOT EXISTS updated_at timestamptz,
    ADD COLUMN IF NOT EXISTS deleted_at timestamptz;

-- Defaults for columns that may have existed without defaults
ALTER TABLE public.tasks
    ALTER COLUMN priority SET DEFAULT 'MEDIUM',
    ALTER COLUMN status SET DEFAULT 'NEW';

-- Backfill NULLs on existing rows before enforcing NOT NULL where needed
UPDATE public.tasks
SET priority = 'MEDIUM'
WHERE priority IS NULL;

UPDATE public.tasks
SET status = 'NEW'
WHERE status IS NULL;

UPDATE public.tasks
SET created_at = NOW() AT TIME ZONE 'UTC'
WHERE created_at IS NULL;

UPDATE public.tasks
SET updated_at = NOW() AT TIME ZONE 'UTC'
WHERE updated_at IS NULL;

-- Optional NOT NULL enforcement (only affects columns now fully backfilled)
ALTER TABLE public.tasks
    ALTER COLUMN priority SET NOT NULL,
    ALTER COLUMN status SET NOT NULL,
    ALTER COLUMN created_at SET NOT NULL,
    ALTER COLUMN updated_at SET NOT NULL;

-- Foreign keys (added only when absent)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'tasks_assigned_member_id_fkey'
    ) THEN
        ALTER TABLE public.tasks
            ADD CONSTRAINT tasks_assigned_member_id_fkey
            FOREIGN KEY (assigned_member_id)
            REFERENCES public.family_members(id)
            ON DELETE SET NULL;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'tasks_inbox_item_id_fkey'
    ) THEN
        ALTER TABLE public.tasks
            ADD CONSTRAINT tasks_inbox_item_id_fkey
            FOREIGN KEY (inbox_item_id)
            REFERENCES public.inbox_items(id)
            ON DELETE SET NULL;
    END IF;
END $$;

COMMIT;

-- ----------------------------------------------------------------------------
-- POST-FLIGHT: verify schema alignment and row preservation
-- ----------------------------------------------------------------------------

-- Expected columns after migration:
--   id, family_id, title, description, due_date, priority, status,
--   assigned_member_id, inbox_item_id, created_at, updated_at, deleted_at
SELECT
    column_name,
    data_type,
    udt_name,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'tasks'
ORDER BY ordinal_position;

-- Confirm required columns exist
SELECT
    required.column_name,
    CASE
        WHEN c.column_name IS NOT NULL THEN 'present'
        ELSE 'MISSING'
    END AS status
FROM (
    VALUES
        ('id'),
        ('family_id'),
        ('title'),
        ('description'),
        ('due_date'),
        ('priority'),
        ('status'),
        ('assigned_member_id'),
        ('inbox_item_id'),
        ('created_at'),
        ('updated_at'),
        ('deleted_at')
) AS required(column_name)
LEFT JOIN information_schema.columns c
    ON c.table_schema = 'public'
   AND c.table_name = 'tasks'
   AND c.column_name = required.column_name
ORDER BY required.column_name;

-- Row count unchanged
SELECT COUNT(*) AS task_row_count FROM public.tasks;

-- Sample of existing rows (sanity check)
SELECT
    id,
    family_id,
    title,
    priority,
    status,
    assigned_member_id,
    inbox_item_id,
    deleted_at
FROM public.tasks
ORDER BY created_at DESC NULLS LAST
LIMIT 5;
