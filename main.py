from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from database import PostgresTaskRepository

repo: Optional[PostgresTaskRepository] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global repo

    repo = PostgresTaskRepository()
    yield

app = FastAPI(lifespan=lifespan)

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/")
def get_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/tasks")
def get_all_tasks():
    return repo.get_all_tasks()

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")
    return dict(task)

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    cleaned_title = task_data.title.strip()
    if not cleaned_title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty")
    return dict(repo.create_task(cleaned_title))

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):
    current_task = repo.get_task(task_id)
    if not current_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")
    
    new_title = task_data.title.strip() if task_data.title is not None else current_task["title"]
    if not new_title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty")
        
    new_done = task_data.done if task_data.done is not None else current_task["done"]
    return dict(repo.update_task(task_id, new_title, new_done))

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    task = repo.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")
    repo.delete_task(task_id)
    return None