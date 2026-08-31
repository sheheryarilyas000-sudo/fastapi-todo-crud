import sqlite3

conn = sqlite3.connect("tasks.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# ---------------------------------------------------
print("--- ALL TASKS ---")
cursor.execute("SELECT * FROM tasks")
for row in cursor.fetchall():
    print(dict(row))

print("\n--- INCOMPLETE TASKS ---")
cursor.execute("SELECT * FROM tasks WHERE done = 0")
for row in cursor.fetchall():
    print(dict(row))

print("\n--- TOTAL TASK COUNT ---")
cursor.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]
print(f"Total tasks: {count}")

cursor.execute("UPDATE tasks SET done = 1")
conn.commit()
print("1. All tasks marked as completed (done = 1)")

cursor.execute("DELETE FROM tasks WHERE done = 1")
conn.commit()
print("2. All completed tasks deleted")
# ---------------------------------------------------

cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Task from SQL direct", 0))
conn.commit()

print(f"New task created with ID: {cursor.lastrowid}")
conn.close()