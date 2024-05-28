from fastapi import FastAPI
from .routers import stores 

app = FastAPI()

app.include_router(stores.router)