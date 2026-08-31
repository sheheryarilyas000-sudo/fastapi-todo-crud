from contextlib import asynccontextmanager
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

DB_NAME = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES ('Buy groceries', 0)")
        cursor.execute("INSERT INTO tasks (title, done) VALUES ('Read a book', 1)")
        cursor.execute("INSERT INTO tasks (title, done) VALUES ('Write backend code', 0)")
        conn.commit()
        
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Pydantic Schemas
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/tasks")
def get_all_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    
    conn.close()  
    
    return [dict(row) for row in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    
    conn.close()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return dict(task)

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    cleaned_title = task_data.title.strip()
    if not cleaned_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, 0)", (cleaned_title,)
    )

    conn.commit()
    
    new_id = cursor.lastrowid

    conn.close()
    
    return {
        "id": new_id,
        "title": cleaned_title,
        "done": False
    }

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    current_task = cursor.fetchone()
    
    if current_task is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    new_title = current_task["title"]
    if task_data.title is not None:
        cleaned_title = task_data.title.strip()
        if not cleaned_title:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty"
            )
        new_title = cleaned_title
        
    new_done = current_task["done"]
    if task_data.done is not None:
        new_done = 1 if task_data.done else 0
        
    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id)
    )
    conn.commit()
    conn.close()
    
    return {
        "id": task_id,
        "title": new_title,
        "done": bool(new_done)
    }


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    
    if task is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
        
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    
    return None
