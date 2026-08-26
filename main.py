from fastapi import FastAPI

app = FastAPI()

# Stage 1: Root endpoint jo API ka intro deta hai
@app.get("/")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

# Stage 1: Health check endpoint
@app.get("/health")
def get_health():
    return {"status": "ok"}