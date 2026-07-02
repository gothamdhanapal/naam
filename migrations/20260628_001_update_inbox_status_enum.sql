-- ============================================================================
-- Migration: update inbox_status enum to M3 lifecycle
-- File: 20260628_001_update_inbox_status_enum.sql
--
-- Current DB values:  NEW, PROCESSED, ARCHIVED
-- Target values:      RECEIVED, PROCESSING, PROCESSED, FAILED
--
-- Row mapping:
--   NEW       -> RECEIVED
--   PROCESSED -> PROCESSED
--   ARCHIVED  -> PROCESSED
-- ============================================================================

-- ----------------------------------------------------------------------------
-- PRE-FLIGHT: run these queries and confirm output before applying the migration
-- ----------------------------------------------------------------------------

-- Current enum labels for inbox_items.status
SELECT e.enumlabel AS enum_label
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
JOIN pg_attribute a ON a.atttypid = t.oid
        AND a.attnum > 0 AND NOT a.attisdropped
JOIN pg_class c ON c.oid = a.attrelid
WHERE c.relname = 'inbox_items'
  AND a.attname = 'status'
ORDER BY e.enumsortorder;

-- Count of rows by current status
SELECT status::text AS status, COUNT(*) AS row_count
FROM public.inbox_items
GROUP BY status
ORDER BY status;

-- ============================================================================
-- MIGRATION (transactional)
-- ============================================================================

BEGIN;

CREATE TYPE inbox_status_new AS ENUM (
    'RECEIVED',
    'PROCESSING',
    'PROCESSED',
    'FAILED'
);

ALTER TABLE public.inbox_items
    ALTER COLUMN status DROP DEFAULT;

ALTER TABLE public.inbox_items
    ALTER COLUMN status TYPE inbox_status_new
    USING (
        CASE status::text
            WHEN 'NEW'       THEN 'RECEIVED'::inbox_status_new
            WHEN 'PROCESSED' THEN 'PROCESSED'::inbox_status_new
            WHEN 'ARCHIVED'  THEN 'PROCESSED'::inbox_status_new
            ELSE 'RECEIVED'::inbox_status_new
        END
    );

ALTER TABLE public.inbox_items
    ALTER COLUMN status SET DEFAULT 'RECEIVED'::inbox_status_new;

DROP TYPE public.inbox_status;

ALTER TYPE inbox_status_new RENAME TO inbox_status;

COMMIT;

-- ----------------------------------------------------------------------------
-- POST-FLIGHT: run these queries after COMMIT to verify the migration succeeded
-- ----------------------------------------------------------------------------

-- Final enum labels (expected: RECEIVED, PROCESSING, PROCESSED, FAILED)
SELECT e.enumlabel AS enum_label
FROM pg_type t
JOIN pg_enum e ON t.oid = e.enumtypid
WHERE t.typname = 'inbox_status'
ORDER BY e.enumsortorder;

-- Count of rows by final status
SELECT status::text AS status, COUNT(*) AS row_count
FROM public.inbox_items
GROUP BY status
ORDER BY status;
