from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app import models, schemas


def get_membership(db: Session, board_id: int, user_id: int) -> models.BoardMember:
    membership = (
        db.query(models.BoardMember)
        .filter(models.BoardMember.board_id == board_id, models.BoardMember.user_id == user_id)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this board")
    return membership


def require_role(db: Session, board_id: int, user_id: int, allowed_roles: list[str]) -> models.BoardMember:
    membership = get_membership(db, board_id, user_id)
    if membership.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return membership


def get_board_or_404(db: Session, board_id: int) -> models.Board:
    board = (
        db.query(models.Board)
        .options(
            selectinload(models.Board.board_columns).selectinload(models.BoardColumn.cards),
            selectinload(models.Board.members).selectinload(models.BoardMember.user),
        )
        .filter(models.Board.id == board_id)
        .first()
    )
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


def to_member_output(member: models.BoardMember) -> schemas.BoardMemberOut:
    return schemas.BoardMemberOut(
        user_id=member.user_id,
        role=member.role,
        display_name=member.user.display_name if member.user else "",
    )


def build_board_detail(board: models.Board) -> schemas.BoardDetail:
    columns = [
        schemas.ColumnWithCards(
            id=column.id,
            title=column.title,
            position=column.position,
            cards=[schemas.CardOut.model_validate(card) for card in column.cards],
        )
        for column in board.board_columns
    ]

    members = [to_member_output(member) for member in board.members]

    return schemas.BoardDetail(
        id=board.id,
        title=board.title,
        owner_id=board.owner_id,
        created_at=board.created_at,
        columns=columns,
        members=members,
    )
