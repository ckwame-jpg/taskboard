from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db
from app.services.boards import require_role
from app.ws import manager

router = APIRouter(prefix="/boards/{board_id}/columns", tags=["Columns"])


@router.post("/", response_model=schemas.ColumnOut)
async def create_column(
    board_id: int,
    column: schemas.ColumnCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_role(db, board_id, current_user.id, ["owner", "editor"])

    max_position = db.query(models.BoardColumn).filter(models.BoardColumn.board_id == board_id).count()

    new_column = models.BoardColumn(board_id=board_id, title=column.title, position=max_position)
    db.add(new_column)
    db.commit()
    db.refresh(new_column)

    await manager.broadcast(
        board_id,
        {
            "type": "column_created",
            "data": {"id": new_column.id, "title": new_column.title, "position": new_column.position},
        },
    )
    return new_column


@router.put("/{column_id}", response_model=schemas.ColumnOut)
async def update_column(
    board_id: int,
    column_id: int,
    update: schemas.ColumnUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_role(db, board_id, current_user.id, ["owner", "editor"])

    column = (
        db.query(models.BoardColumn)
        .filter(models.BoardColumn.id == column_id, models.BoardColumn.board_id == board_id)
        .first()
    )
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")

    if update.title is not None:
        column.title = update.title
    if update.position is not None:
        column.position = update.position

    db.commit()
    db.refresh(column)

    await manager.broadcast(
        board_id,
        {
            "type": "column_updated",
            "data": {"id": column.id, "title": column.title, "position": column.position},
        },
    )
    return column


@router.delete("/{column_id}")
async def delete_column(
    board_id: int,
    column_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_role(db, board_id, current_user.id, ["owner", "editor"])

    column = (
        db.query(models.BoardColumn)
        .filter(models.BoardColumn.id == column_id, models.BoardColumn.board_id == board_id)
        .first()
    )
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")

    db.delete(column)
    db.commit()

    await manager.broadcast(
        board_id,
        {
            "type": "column_deleted",
            "data": {"column_id": column_id},
        },
    )
    return {"detail": "Column deleted"}
