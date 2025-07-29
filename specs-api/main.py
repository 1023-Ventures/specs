from fastapi import FastAPI
from app.api.api import api_router
import uvicorn

app = FastAPI(
    title="ECS Auth API",
    description="Simple Authentication API with SQLite - Clean Architecture",
    version="1.0.0"
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Add a root endpoint for health check
@app.get("/")
async def root():
    return {
        "message": "ECS Auth API is running!",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api/v1"
    }

def main():
    print("Starting ECS Auth API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
