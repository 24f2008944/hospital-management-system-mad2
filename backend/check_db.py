#!/usr/bin/env python3
"""
Quick script to check database content
"""
import sqlite3
import os

# Path to the database file
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hospital.db')

print("=== DATABASE CONTENT CHECK ===")
print(f"Database file: {db_path}")

if not os.path.exists(db_path):
    print("Database file does not exist!")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check users
    cursor.execute("SELECT COUNT(*) FROM user")
    user_count = cursor.fetchone()[0]
    print(f"\nUsers: {user_count}")
    
    if user_count > 0:
        cursor.execute("SELECT id, username, email FROM user LIMIT 10")
        users = cursor.fetchall()
        for user in users:
            print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
    
    # Check departments
    cursor.execute("SELECT COUNT(*) FROM department")
    dept_count = cursor.fetchone()[0]
    print(f"\nDepartments: {dept_count}")
    
    if dept_count > 0:
        cursor.execute("SELECT id, name, description FROM department")
        departments = cursor.fetchall()
        for dept in departments:
            print(f"  - ID: {dept[0]}, Name: {dept[1]}, Description: {dept[2]}")
    
    # Check doctors
    cursor.execute("SELECT COUNT(*) FROM doctor")
    doctor_count = cursor.fetchone()[0]
    print(f"\nDoctors: {doctor_count}")
    
    if doctor_count > 0:
        cursor.execute("""
            SELECT d.id, d.user_id, d.department_id, d.specialization, u.username 
            FROM doctor d 
            LEFT JOIN user u ON d.user_id = u.id 
            LIMIT 10
        """)
        doctors = cursor.fetchall()
        for doctor in doctors:
            print(f"  - ID: {doctor[0]}, User ID: {doctor[1]}, Username: {doctor[4]}, Dept ID: {doctor[2]}, Specialization: {doctor[3]}")
    
    # Check patients
    cursor.execute("SELECT COUNT(*) FROM patient")
    patient_count = cursor.fetchone()[0]
    print(f"\nPatients: {patient_count}")
    
    if patient_count > 0:
        cursor.execute("""
            SELECT p.id, p.user_id, p.first_name, p.last_name, u.username 
            FROM patient p 
            LEFT JOIN user u ON p.user_id = u.id 
            LIMIT 10
        """)
        patients = cursor.fetchall()
        for patient in patients:
            print(f"  - ID: {patient[0]}, User ID: {patient[1]}, Username: {patient[4]}, Name: {patient[2]} {patient[3]}")
    
    conn.close()
    print("\n=== END ===")
    
except Exception as e:
    print(f"Error: {e}")
    exit(1)
