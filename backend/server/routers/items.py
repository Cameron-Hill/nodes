from fastapi import APIRouter, Depends
from server import crud, schemas
from server.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
