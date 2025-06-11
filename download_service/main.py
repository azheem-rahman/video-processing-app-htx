from fastapi import FastAPI
from download_service.handlers import router

app = FastAPI(title="Download Service")
app.include_router(router)
