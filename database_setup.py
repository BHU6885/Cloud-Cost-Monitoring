import csv
import sqlite3
import os

CSV_PATH = "data/cloud_costs.csv"
DB_PATH = "cloud_costs.db"

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    service TEXT NOT NULL,
    cost REAL NOT NULL
)
""")

cursor.execute("DELETE FROM expenses")

with open(CSV_PATH, "r", newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        cursor.execute("""
        INSERT INTO expenses (date, service, cost)
        VALUES (?, ?, ?)
        """, (
            row["Date"],
            row["Service"],
            float(row["Cost"])
        ))

connection.commit()
connection.close()

print("Database created and CSV data imported successfully!")