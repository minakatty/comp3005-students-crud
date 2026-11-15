-- =====================================================================
-- 01_create_table.sql
-- Purpose : Creates the "students" table exactly as given in the
--           assignment schema.
-- Run on  : the "students_db" database (see README for how to create it)
-- =====================================================================

-- Drop the table first (if it already exists) so this script can be
-- re-run safely to reset the database to a clean state.
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    -- Integer primary key that auto-increments.
    -- SERIAL = INTEGER column + an automatically created sequence,
    -- so PostgreSQL assigns 1, 2, 3, ... on every insert.
    student_id      SERIAL PRIMARY KEY,

    -- Text fields that must always have a value.
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,

    -- Email must have a value AND no two students may share one.
    email           TEXT NOT NULL UNIQUE,

    -- Date the student enrolled (optional, so NULL is allowed).
    enrollment_date DATE
);
