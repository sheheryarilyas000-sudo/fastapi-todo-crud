from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Pydantic Schemas
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# In-memory dummy data
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Write backend code", "done": False}
]

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
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    cleaned_title = task_data.title.strip()
    if not cleaned_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )
    
    next_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {
        "id": next_id,
        "title": cleaned_title,
        "done": False
    }
    tasks.append(new_task)
    return new_task

# Stage 4: Task update karna (PUT)
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            # Agar title provide kiya gaya hai toh check karein khali na ho
            if task_data.title is not None:
                cleaned_title = task_data.title.strip()
                if not cleaned_title:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Title cannot be empty"
                    )
                task["title"] = cleaned_title
            
            # Agar done status provide kiya gaya hai toh update karein
            if task_data.done is not None:
                task["done"] = task_data.done
                
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )

# Stage 4: Task delete karna (DELETE)
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(index)
            return None  # 204 No Content returns empty body
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )