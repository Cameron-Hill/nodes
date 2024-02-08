from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from . import models
from .database import engine
from .routers import users, nodes, items, workflows
from pydantic import ValidationError
import json

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


app.include_router(nodes.router)
app.include_router(users.router)
app.include_router(items.router)
app.include_router(workflows.router)
