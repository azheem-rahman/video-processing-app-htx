from fastapi import FastAPI
from api_gateway.handlers import router

app = FastAPI()
app.include_router(router)