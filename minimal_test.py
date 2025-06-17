"""
Minimal FastAPI test application to diagnose routing issues.
"""
from fastapi import FastAPI

# Create a minimal FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/test")
async def test():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
