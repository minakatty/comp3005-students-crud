"""
students_app.py
---------------------------------------------------------------------------
COMP 3005 

A small Python console application that connects to a PostgreSQL database
and performs CRUD (Create, Read, Update, Delete) operations on the
"students" table:

    getAllStudents()                                        -> READ
    addStudent(first_name, last_name, email, enrollment_date) -> CREATE
    updateStudentEmail(student_id, new_email)               -> UPDATE
    deleteStudent(student_id)                               -> DELETE

The program shows a numbered menu so each function can be called one at a
time (and its effect checked in pgAdmin).

Library used: psycopg2 
---------------------------------------------------------------------------
"""

import os
import sys
from datetime import datetime
from getpass import getpass

import psycopg2
from psycopg2 import errors


# Database connection settings
# Each value can be overridden with an environment variable, so the code
# never has to be edited to run on a different machine
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "students_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),  # asked for at startup if not set
}


def get_connection():
    """
    Opens and returns a new connection to the PostgreSQL database using the
    settings in DB_CONFIG. Every CRUD function below opens its own
    connection and closes it when finished, so the functions keep the exact
    signatures given in the assignment.
    """
    return psycopg2.connect(**DB_CONFIG)


# READ
def getAllStudents():
    """
    Retrieves every record from the students table and displays them
    in a formatted table, ordered by student_id.
    Returns the list of rows so the result can also be used by other code.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT student_id, first_name, last_name, email, enrollment_date "
                "FROM students ORDER BY student_id;"
            )
            rows = cur.fetchall()

        # Print the results as a simple aligned table.
        header = f"{'ID':<4} {'First Name':<15} {'Last Name':<15} {'Email':<32} {'Enrollment Date':<15}"
        print("\n" + header)
        print("-" * len(header))
        for student_id, first_name, last_name, email, enrollment_date in rows:
            # enrollment_date may be NULL (None) because the column is optional.
            date_text = str(enrollment_date) if enrollment_date else "NULL"
            print(f"{student_id:<4} {first_name:<15} {last_name:<15} {email:<32} {date_text:<15}")
        print(f"\n{len(rows)} student(s) found.")
        return rows

    except psycopg2.Error as e:
        print(f"[ERROR] Could not retrieve students: {e}")
        return []
    finally:
        # Always release the connection, even if an error happened.
        if conn:
            conn.close()

# CREATE
def addStudent(first_name, last_name, email, enrollment_date):
    """
    Inserts a new student record into the students table.
    student_id is not supplied - PostgreSQL generates it (SERIAL).
    enrollment_date must be in YYYY-MM-DD format, or None for no date.
    Returns the new student's ID, or None if the insert failed.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # %s placeholders = parameterized query. psycopg2 safely escapes
            cur.execute(
                "INSERT INTO students (first_name, last_name, email, enrollment_date) "
                "VALUES (%s, %s, %s, %s) RETURNING student_id;",
                (first_name, last_name, email, enrollment_date),
            )
            new_id = cur.fetchone()[0]
        conn.commit()  # make the change permanent
        print(f"[OK] Student {first_name} {last_name} added with student_id = {new_id}.")
        return new_id

    except errors.UniqueViolation:
        if conn:
            conn.rollback()
        print(f"[ERROR] The email '{email}' is already used by another student.")
    except errors.NotNullViolation:
        if conn:
            conn.rollback()
        print("[ERROR] first_name, last_name and email are required.")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"[ERROR] Could not add student: {e}")
    finally:
        if conn:
            conn.close()
    return None


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------
def updateStudentEmail(student_id, new_email):
    """
    Updates the email address of the student with the given student_id.
    Returns True if a row was updated, False otherwise.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE students SET email = %s WHERE student_id = %s;",
                (new_email, student_id),
            )
            updated = cur.rowcount  # number of rows changed
        conn.commit()

        if updated == 0:
            print(f"[INFO] No student found with student_id = {student_id}. Nothing updated.")
            return False
        print(f"[OK] Email for student_id = {student_id} updated to '{new_email}'.")
        return True

    except errors.UniqueViolation:
        if conn:
            conn.rollback()
        print(f"[ERROR] The email '{new_email}' is already used by another student.")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"[ERROR] Could not update email: {e}")
    finally:
        if conn:
            conn.close()
    return False



# DELETE
def deleteStudent(student_id):
    """
    Deletes the record of the student with the given student_id.
    Returns True if a row was deleted, False otherwise.
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM students WHERE student_id = %s;", (student_id,))
            deleted = cur.rowcount
        conn.commit()

        if deleted == 0:
            print(f"[INFO] No student found with student_id = {student_id}. Nothing deleted.")
            return False
        print(f"[OK] Student with student_id = {student_id} deleted.")
        return True

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"[ERROR] Could not delete student: {e}")
    finally:
        if conn:
            conn.close()
    return False


# Input helpers (validate user input before it reaches the database)
def ask_required(prompt):
    """Keeps asking until the user types a non-empty value."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  This field cannot be empty.")


def ask_int(prompt):
    """Keeps asking until the user types a whole number (used for IDs)."""
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            return int(value)
        print("  Please enter a valid whole number.")


def ask_date(prompt):
    """
    Asks for a date in YYYY-MM-DD format. Pressing Enter leaves it empty,
    which stores NULL (enrollment_date is optional in the schema).
    """
    while True:
        value = input(prompt).strip()
        if value == "":
            return None
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("  Invalid date. Use the format YYYY-MM-DD (e.g. 2023-09-01).")


# Main menu
def main():
    """Shows the menu and calls the chosen CRUD function in a loop."""
    # Ask for the password once if it was not given as an environment variable.
    if DB_CONFIG["password"] is None:
        DB_CONFIG["password"] = getpass(f"PostgreSQL password for user '{DB_CONFIG['user']}': ")

    # Test the connection once at startup so a wrong setting is reported clearly.
    try:
        get_connection().close()
        print(f"Connected to database '{DB_CONFIG['dbname']}' on {DB_CONFIG['host']}:{DB_CONFIG['port']}.")
    except psycopg2.Error as e:
        print(f"[ERROR] Could not connect to the database: {e}")
        sys.exit(1)

    menu = """
========== Students Database ==========
1. getAllStudents()      - Show all students
2. addStudent()          - Add a new student
3. updateStudentEmail()  - Update a student's email
4. deleteStudent()       - Delete a student
5. Exit
======================================="""

    while True:
        print(menu)
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            getAllStudents()

        elif choice == "2":
            first_name = ask_required("First name: ")
            last_name = ask_required("Last name: ")
            email = ask_required("Email: ")
            enrollment_date = ask_date("Enrollment date (YYYY-MM-DD, Enter to leave empty): ")
            addStudent(first_name, last_name, email, enrollment_date)

        elif choice == "3":
            student_id = ask_int("student_id to update: ")
            new_email = ask_required("New email: ")
            updateStudentEmail(student_id, new_email)

        elif choice == "4":
            student_id = ask_int("student_id to delete: ")
            deleteStudent(student_id)

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


# Run the menu only when this file is executed directly
if __name__ == "__main__":
    main()
