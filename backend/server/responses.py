from pydantic import BaseModel

class InfoSchema(BaseModel):
    name: str = "Workflow Engine"
    version: str = "0.1.0"
    description: str = "A workflow engine for running workflows"


class ErrorResponse(BaseModel):
    detail: str

Error404 = {"description": "The requested resource was not found", "model": ErrorResponse}
Error500 = {"description": "Internal Server Error", "model": ErrorResponse}