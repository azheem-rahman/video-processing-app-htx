from fastapi import FastAPI
from handlers import router

app = FastAPI(title="Upload Service")
app.include_router(router)