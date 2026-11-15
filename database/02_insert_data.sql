-- =====================================================================
-- 02_insert_data.sql
-- Purpose : Populates the "students" table with the initial data set
--           provided in the assignment.
-- Note    : student_id is NOT listed because it is generated
--           automatically by the SERIAL column (1, 2, 3).
-- =====================================================================

INSERT INTO students (first_name, last_name, email, enrollment_date) VALUES
('John', 'Doe', 'john.doe@example.com', '2023-09-01'),
('Jane', 'Smith', 'jane.smith@example.com', '2023-09-01'),
('Jim', 'Beam', 'jim.beam@example.com', '2023-09-02');

-- Quick check: show the inserted rows.
SELECT * FROM students ORDER BY student_id;
