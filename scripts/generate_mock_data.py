from faker import Faker
import sqlite3
import os

data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

conn = sqlite3.connect(f"{data_dir}/employees.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        phone TEXT,
        department TEXT,
        position TEXT,
        location TEXT,
        status TEXT,
        org_id INTEGER
    )
""")

total_records = 1000000
fake = Faker()

for i in range(total_records):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    phone = fake.phone_number() if fake.boolean(chance_of_getting_true=50) else None
    department = fake.word(ext_word_list=["HR", "Engineering", "Sales", "Marketing", "Finance"])
    position = fake.job()
    location = fake.city()
    status = fake.word(ext_word_list=["active", "not_started", "terminated"])
    org_id = fake.random_int(min=1, max=10)
    cursor.execute(
        'INSERT INTO employees (first_name, last_name, email, phone, department, position, location, status, org_id) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (first_name, last_name, email, phone, department, position, location, status, org_id)
    )

conn.commit()
conn.close()

print(f"Generated {total_records} employee records in database")
