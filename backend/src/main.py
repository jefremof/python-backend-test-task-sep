from fastapi import FastAPI
from src.routers.api import router
from src.routers import organizations, buildings, activities

app = FastAPI()

app.include_router(router, prefix="/api")

@app.get("/")
async def index():
    return "Application is working\n"