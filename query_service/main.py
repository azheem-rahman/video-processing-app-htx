from fastapi import FastAPI
from query_service.handlers import router

app = FastAPI(title="Query Service")
app.include_router(router)