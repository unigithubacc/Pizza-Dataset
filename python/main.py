from fastapi import FastAPI
from .routers import stores, products, customers, locations, homepage

app = FastAPI()

app.include_router(stores.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(locations.router)
app.include_router(homepage.router)