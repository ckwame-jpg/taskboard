from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.auth import get_current_user
from app.routes.boards import require_role
from app.ws import manager

router = APIRouter(prefix="/boards/{board_id}/columns", tags=["Columns"])


@router.post("/", response_model=schemas.ColumnOut)
async def create_column(board_id: int, col: schemas.ColumnCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_role(db, board_id, current_user.id, ["owner", "editor"])

    max_pos = db.query(models.BoardColumn).filter(
        models.BoardColumn.board_id == board_id
    ).count()

    new_col = models.BoardColumn(board_id=board_id, title=col.title, position=max_pos)
    db.add(new_col)
    db.commit()
    db.refresh(new_col)

    await manager.broadcast(board_id, {
        "type": "column_created",
        "data": {"id": new_col.id, "title": new_col.title, "position": new_col.position},
    })
    return new_col


@router.put("/{column_id}", response_model=schemas.ColumnOut)
async def update_column(board_id: int, column_id: int, update: schemas.ColumnUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_role(db, board_id, current_user.id, ["owner", "editor"])

    col = db.query(models.BoardColumn).filter(
        models.BoardColumn.id == column_id,
        models.BoardColumn.board_id == board_id,
    ).first()
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    if update.title is not None:
        col.title = update.title
    if update.position is not None:
        col.position = update.position
    db.commit()
    db.refresh(col)

    await manager.broadcast(board_id, {
        "type": "column_updated",
        "data": {"id": col.id, "title": col.title, "position": col.position},
    })
    return col


@router.delete("/{column_id}")
async def delete_column(board_id: int, column_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_role(db, board_id, current_user.id, ["owner", "editor"])

    col = db.query(models.BoardColumn).filter(
        models.BoardColumn.id == column_id,
        models.BoardColumn.board_id == board_id,
    ).first()
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")

    db.delete(col)
    db.commit()

    await manager.broadcast(board_id, {
        "type": "column_deleted",
        "data": {"column_id": column_id},
    })
    return {"detail": "Column deleted"}
