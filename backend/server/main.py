from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from . import models
from .database import engine
from .routers import users, nodes, items, workflows
from pydantic import ValidationError, BaseModel
import json
import os
import logging


LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "OFF"]

level = os.environ.get("LOG_LEVEL", "DEBUG").upper().strip()
if level not in LOG_LEVELS:
    raise ValueError(f"Invalid log level {level}, must be one of{LOG_LEVELS}")

logging.basicConfig(level=level)

logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.exception_handler(ValidationError)
def handle_pydantic_validation_errors(
    request: Request, exc: ValidationError
) -> JSONResponse:
    detail = {}
    detail["error"] = json.loads(exc.json())
    for error in detail["error"]:
        if isinstance(error, dict):
            error.pop("url", None)
            error.pop("ctx", None)
    detail["extra"] = []
    for note in getattr(exc, "__notes__", []):
        try:
            detail["extra"].append(json.loads(note))
        except Exception:
            detail["extra"].append({"msg": note})
    return JSONResponse(content=detail, status_code=422)

class InfoSchema(BaseModel):
    name: str = "Workflow Engine"
    version: str = "0.1.0"
    description: str = "A workflow engine for running workflows"

@app.get("/info")
def info() -> InfoSchema:
    return InfoSchema()

app.include_router(nodes.router)
app.include_router(users.router)
app.include_router(items.router)
app.include_router(workflows.router)
