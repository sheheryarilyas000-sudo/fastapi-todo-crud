from contextlib import asynccontextmanager
from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, HTTPException, status, Request, Header
from pydantic import BaseModel
from database import PostgresTaskRepository
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
security = HTTPBearer()

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

class UserCredentials(BaseModel):
    email: str
    password: str

@app.get("/")
def get_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks", "/auth/signup", "/auth/login"]}

@app.get("/health")
def get_health():
    return {"status": "ok"}

# Public Route
@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

# Protected Route with Real Token Verification (Pro Level)
@app.get("/protected/profile")
def protected_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials 

    try:
        user_response = supabase.auth.get_user(token)
        return {
            "message": "Token successfully verified by Supabase!",
            "user_email": user_response.user.email,
            "user_id": user_response.user.id
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Sign Up Route
@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCredentials):
    if not user.email or not user.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Log In Route
@app.post("/auth/login", status_code=status.HTTP_200_OK)
def login(user: UserCredentials):
    if not user.email or not user.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

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