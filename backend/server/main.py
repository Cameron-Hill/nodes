import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from . import models
from .database import engine
from .routers import users, nodes, items, workflows
from pydantic import ValidationError, BaseModel
import os
import logging
import logging.config
from yaml import safe_load

ROOT = os.path.dirname(__file__)

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "OFF"]

level = os.environ.get("LOG_LEVEL", "DEBUG").upper().strip()
if level not in LOG_LEVELS:
    raise ValueError(f"Invalid log level {level}, must be one of{LOG_LEVELS}")

config = os.environ.get("LOG_CONFIG", os.path.join(ROOT, "log_config.yaml"))

with open(config) as f:
    config = safe_load(f)
logging.config.dictConfig(config)
logging.basicConfig(level=level)

logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origin = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost:8081",
]


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.debug(f"Request: {request.method} {request.url} took {process_time:.2f}s")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.exception_handler(ValidationError)
# def handle_pydantic_validation_errors(
#     request: Request, exc: ValidationError
# ) -> JSONResponse:
#     detail = {}
#     detail["error"] = json.loads(exc.json())
#     for error in detail["error"]:
#         if isinstance(error, dict):
#             error.pop("url", None)
#             error.pop("ctx", None)
#     detail["extra"] = []
#     for note in getattr(exc, "__notes__", []):
#         try:
#             detail["extra"].append(json.loads(note))
#         except Exception:
#             detail["extra"].append({"msg": note})
#     return JSONResponse(content=detail, status_code=422)


@app.exception_handler(Exception)
def handle_internal_server_errors(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(exc)
    return JSONResponse(content={"detail": "Internal Server Error"}, status_code=500)


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
