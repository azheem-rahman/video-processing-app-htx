from fastapi import FastAPI
from upload_service.handlers import router

app = FastAPI(title="Upload Service")
app.include_router(router)