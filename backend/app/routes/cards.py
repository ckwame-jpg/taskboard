from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db
from app.services.boards import require_role
from app.ws import manager

router = APIRouter(prefix="/boards/{board_id}/cards", tags=["Cards"])


@router.post("/", response_model=schemas.CardOut)
async def create_card(
    board_id: int,
    card: schemas.CardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_role(db, board_id, current_user.id, ["owner", "editor"])

    column = (
        db.query(models.BoardColumn)
        .filter(models.BoardColumn.id == card.column_id, models.BoardColumn.board_id == board_id)
        .first()
    )
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")

    max_position = db.query(models.Card).filter(models.Card.column_id == card.column_id).count()

    new_card = models.Card(
        column_id=card.column_id,
        title=card.title,
        description=card.description,
        position=max_position,
        created_by=current_user.id,
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)

    await manager.broadcast(
        board_id,
        {
            "type": "card_created",
            "data": schemas.CardOut.model_validate(new_card).model_dump(),
        },
    )
    return new_card


@router.put("/{card_id}", response_model=schemas.CardOut)
async def update_card(
    board_id: int,
    card_id: int,
    update: schemas.CardUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_role(db, board_id, current_user.id, ["owner", "editor"])

    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    column = (
        db.query(models.BoardColumn)
        .filter(models.BoardColumn.id == card.column_id, models.BoardColumn.board_id == board_id)
        .first()
    )
    if not column:
        raise HTTPException(status_code=404, detail="Card not found in this board")

    if update.title is not None:
        card.title = update.title
    if update.description is not None:
        card.description = update.description

    db.commit()
    db.refresh(card)

    await manager.broadcast(
        board_id,
        {
            "type": "card_updated",
            "data": schemas.CardOut.model_validate(card).model_dump(),
        },
    )
    return card


@router.put("/{card_id}/move", response_model=schemas.CardOut)
async def move_card(
    board_id: int,
    card_id: int,
    move: schemas.CardMove,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_role(db, board_id, current_user.id, ["owner", "editor"])

    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    target_column = (
        db.query(models.BoardColumn)
        .filter(models.BoardColumn.id == move.column_id, models.BoardColumn.board_id == board_id)
        .first()
    )
    if not target_column:
        raise HTTPException(status_code=404, detail="Target column not found")

    old_column_id = card.column_id
    card.column_id = move.column_id
    card.position = move.position
    db.commit()
    db.refresh(card)

    await manager.broadcast(
        board_id,
        {
            "type": "card_moved",
            "data": {
                "card_id": card.id,
                "from_column": old_column_id,
                "to_column": move.column_id,
                "position": move.position,
            },
        },
    )
    return card


@router.delete("/{card_id}")
async def delete_card(
    board_id: int,
    card_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_role(db, board_id, current_user.id, ["owner", "editor"])

    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    column = (
        db.query(models.BoardColumn)
        .filter(models.BoardColumn.id == card.column_id, models.BoardColumn.board_id == board_id)
        .first()
    )
    if not column:
        raise HTTPException(status_code=404, detail="Card not found in this board")

    db.delete(card)
    db.commit()

    await manager.broadcast(
        board_id,
        {
            "type": "card_deleted",
            "data": {"card_id": card_id},
        },
    )
    return {"detail": "Card deleted"}
