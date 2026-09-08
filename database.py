import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

class PostgresTaskRepository:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        print(f"-> Connecting to Database URL: {self.db_url}", flush=True)
        self.init_db()

    def get_db_connection(self):
        for i in range(5):
            try:
                conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
                print("-> Database connection successful!", flush=True)
                return conn
            except psycopg2.OperationalError as e:
                print(f"-> DB connection attempt {i+1} failed: {e}. Retrying in 2s...", flush=True)
                if i < 4:
                    time.sleep(2)
                else:
                    raise

    def init_db(self):
        print("-> Initializing database tables...", flush=True)
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        done BOOLEAN DEFAULT FALSE
                    )
                """)
                cursor.execute("SELECT COUNT(*) FROM tasks")
                count = cursor.fetchone()['count']
                
                if count == 0:
                    print("-> Seeding initial tasks...", flush=True)
                    cursor.execute("INSERT INTO tasks (title, done) VALUES ('Buy groceries', false)")
                    cursor.execute("INSERT INTO tasks (title, done) VALUES ('Read a book', true)")
                    cursor.execute("INSERT INTO tasks (title, done) VALUES ('Write backend code', false)")
                conn.commit()
        print("-> Database initialization complete!", flush=True)

    def get_all_tasks(self):
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM tasks")
                return cursor.fetchall()

    def get_task(self, task_id):
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
                return cursor.fetchone()

    def create_task(self, title):
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, false) RETURNING id, title, done", 
                    (title,)
                )
                new_task = cursor.fetchone()
            conn.commit()
            return new_task

    def update_task(self, task_id, title, done):
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
                    (title, done, task_id)
                )
                updated_task = cursor.fetchone()
            conn.commit()
            return updated_task

    def delete_task(self, task_id):
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            conn.commit()