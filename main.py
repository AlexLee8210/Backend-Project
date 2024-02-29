from fastapi import FastAPI
from routers import users, products, auth

app = FastAPI()

app.include_router(users.router)
app.include_router(products.router)
app.include_router(auth.router)
