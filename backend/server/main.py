from fastapi import FastAPI
from . import models
from .database import engine
from .routers import users, nodes, items

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(nodes.router)
app.include_router(users.router)
app.include_router(items.router)
