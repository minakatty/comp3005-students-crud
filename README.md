# COMP 3005 – Assignment 03 (Question 01)

A Python console application that connects to a PostgreSQL database and performs
CRUD (Create, Read, Update, Delete) operations on a `students` table.

video link: 
https://youtu.be/ubBRV9linR0?si=_Z2SzEpy_eQrRayb
---

## Repository Structure

```
comp3005-students-crud/
├── database/
│   ├── 01_create_table.sql   # Creates the students table (schema)
│   └── 02_insert_data.sql    # Inserts the initial data
├── app/
│   ├── students_app.py       # Python application with the 4 CRUD functions
│   └── requirements.txt      # Python dependency (psycopg2-binary)
├── .gitignore
└── README.md
```

## Database Schema

Table: `students`

| Field             | Type and Constraints                  | PostgreSQL definition       |
|-------------------|---------------------------------------|-----------------------------|
| `student_id`      | Integer, Primary Key, Auto-increment  | `SERIAL PRIMARY KEY`        |
| `first_name`      | Text, Not Null                        | `TEXT NOT NULL`             |
| `last_name`       | Text, Not Null                        | `TEXT NOT NULL`             |
| `email`           | Text, Not Null, Unique                | `TEXT NOT NULL UNIQUE`      |
| `enrollment_date` | Date                                  | `DATE`                      |

## Application Functions

All functions are in `app/students_app.py`.

| Function | Operation | What it does |
|----------|-----------|--------------|
| `getAllStudents()` | READ | Runs `SELECT` on the `students` table and prints every record, ordered by `student_id`. |
| `addStudent(first_name, last_name, email, enrollment_date)` | CREATE | Runs `INSERT` to add a new student. `student_id` is generated automatically and printed back. Reports an error if the email already exists. |
| `updateStudentEmail(student_id, new_email)` | UPDATE | Runs `UPDATE` to change the email of the given student. Reports if the ID does not exist or the new email is already taken. |
| `deleteStudent(student_id)` | DELETE | Runs `DELETE` to remove the given student. Reports if the ID does not exist. |

Other design points:
- **Parameterized queries** (`%s` placeholders) are used everywhere, preventing SQL injection.
- **Transactions:** each change is `commit()`ed on success and `rollback()`ed on error.
- **Error handling:** duplicate emails, missing required fields, unknown IDs, invalid dates
  and connection failures are caught and shown as clear messages instead of crashing.
- **Input validation:** IDs must be whole numbers, dates must be `YYYY-MM-DD`, and required
  fields cannot be empty.

---

## Setup and Running the Application

### Prerequisites
- [PostgreSQL](https://www.postgresql.org/download/) (includes **pgAdmin 4**)
- [Python 3.8+](https://www.python.org/downloads/)

### Step 1 – Create the database
In **pgAdmin**: right-click **Databases → Create → Database…**, name it `students_db`, and click **Save**.

(Or from a terminal: `psql -U postgres -c "CREATE DATABASE students_db;"`)

### Step 2 – Create the table and insert the initial data
In pgAdmin, select `students_db` → **Tools → Query Tool**, then open and run (▶ / F5), in order:
1. `database/01_create_table.sql`
2. `database/02_insert_data.sql`

(Or from a terminal, in the repository folder:)
```bash
psql -U postgres -d students_db -f database/01_create_table.sql
psql -U postgres -d students_db -f database/02_insert_data.sql
```

Re-running both scripts resets the table to the original 3 students.

### Step 3 – Install the Python dependency
From the repository folder:
```bash
pip install -r app/requirements.txt
```

### Step 4 – Run the application
```bash
python app/students_app.py
```

The program asks for your PostgreSQL password, connects, and shows this menu:

```
========== Students Database ==========
1. getAllStudents()      - Show all students
2. addStudent()          - Add a new student
3. updateStudentEmail()  - Update a student's email
4. deleteStudent()       - Delete a student
5. Exit
=======================================
```

Enter a number to call the matching function, then follow the prompts.

### Connection settings (optional)
The defaults are `host=localhost`, `port=5432`, `dbname=students_db`, `user=postgres`.
To change them, set environment variables before running:

| Variable | Default |
|----------|---------|
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `students_db` |
| `DB_USER` | `postgres` |
| `DB_PASSWORD` | *(asked at startup)* |

Example (Windows PowerShell): `$env:DB_PASSWORD="yourpassword"; python app/students_app.py`
Example (macOS/Linux): `DB_PASSWORD=yourpassword python3 app/students_app.py`

---

##example Run

```
Choose an option (1-5): 1

ID   First Name      Last Name       Email                            Enrollment Date
-------------------------------------------------------------------------------------
1    John            Doe             john.doe@example.com             2023-09-01
2    Jane            Smith           jane.smith@example.com           2023-09-01
3    Jim             Beam            jim.beam@example.com             2023-09-02

3 students found.
```
