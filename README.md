# FastAPI To-Do CRUD API (In-Memory)

A lightweight in-memory RESTful Task Management API built with Python, FastAPI, and Pydantic. Implements standard CRUD operations, input validation, structured HTTP status codes, and auto-generated Swagger UI documentation.

---

## 🛠️ Tech Stack
* **Framework:** FastAPI
* **Web Server:** Uvicorn (ASGI)
* **Validation:** Pydantic
* **Storage:** In-Memory List (RAM)

---

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone <YOUR-GITHUB-REPO-URL>
   cd todo-crud-api

## Install dependencies:
pip install fastapi uvicorn

## Start the development server:
uvicorn main:app --reload

## Access Endpoints:
Root API: http://127.0.0.1:8000/

Health Check: http://127.0.0.1:8000/health

Interactive Swagger UI: http://127.0.0.1:8000/docs

## 📋 API Endpoints Specification

| Method | Endpoint | Description | Success Status | Error Codes |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | API Metadata & Entry Point | `200 OK` | — |
| **GET** | `/health` | Health Check Endpoint | `200 OK` | — |
| **GET** | `/tasks` | List all tasks | `200 OK` | — |
| **GET** | `/tasks/{id}` | Retrieve a specific task by ID | `200 OK` | `404 Not Found` |
| **POST** | `/tasks` | Create a new task (validates title) | `201 Created` | `400 Bad Request` |
| **PUT** | `/tasks/{id}` | Update an existing task | `200 OK` | `400 Bad Request`, `404 Not Found` |
| **DELETE**| `/tasks/{id}` | Remove a task | `204 No Content` | `404 Not Found` |

## Sample Verification Output (curl -i)
HTTP/1.1 200 OK
date: Wed, 26 Aug 2026 00:00:00 GMT
server: uvicorn
content-length: 17
content-type: application/json

{"status":"ok"}

## The Mortality Experiment (Why In-Memory Data Wipes)
When tasks are created or deleted, data lives strictly in server memory (Python runtime heap/RAM). Restarting Uvicorn causes the memory space to be cleared and reinitialized with default seed data. This demonstrates why production backends require persistent database storage (SQL/NoSQL).

## 📸 Swagger UI Interactive Documentation

![Swagger UI Documentation](./swagger-ui.png)