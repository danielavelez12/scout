from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="API Service", description="A basic API service")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello")
async def hello():
    return {"message": "Hello"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
