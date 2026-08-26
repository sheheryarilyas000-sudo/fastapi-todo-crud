from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Pydantic Schema: Yeh client ke aane wale data ka rule set karta hai
class TaskCreate(BaseModel):
    title: str

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

# Stage 3: Naya task create karna (POST)
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate):
    # Rule validation: Title khali ya sirf spaces na ho
    cleaned_title = task_data.title.strip()
    if not cleaned_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )
    
    # Nayi auto-incremented ID generate karna
    next_id = max([t["id"] for t in tasks], default=0) + 1
    
    new_task = {
        "id": next_id,
        "title": cleaned_title,
        "done": False
    }
    
    tasks.append(new_task)
    return new_task