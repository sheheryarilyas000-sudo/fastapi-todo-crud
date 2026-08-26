from fastapi import FastAPI, HTTPException, status

app = FastAPI()

# In-memory dummy data (Shelves)
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

# Stage 2: Sab tasks ki list mangwana
@app.get("/tasks")
def get_all_tasks():
    return tasks

# Stage 2: Specific task dhoondna ID ke zariye
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    # Agar task na mile toh 404 error throw karna
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )