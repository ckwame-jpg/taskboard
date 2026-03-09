from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db
from app.services.boards import (
    build_board_detail,
    get_board_or_404,
    get_membership,
    require_role,
    to_member_output,
)

router = APIRouter(prefix="/boards", tags=["Boards"])


@router.post("/", response_model=schemas.BoardOut)
def create_board(
    board: schemas.BoardCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_board = models.Board(title=board.title, owner_id=current_user.id)
    db.add(new_board)
    db.flush()

    owner_membership = models.BoardMember(board_id=new_board.id, user_id=current_user.id, role="owner")
    db.add(owner_membership)

    db.commit()
    db.refresh(new_board)
    return new_board


@router.get("/", response_model=list[schemas.BoardOut])
def list_boards(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return (
        db.query(models.Board)
        .join(models.BoardMember, models.BoardMember.board_id == models.Board.id)
        .filter(models.BoardMember.user_id == current_user.id)
        .order_by(models.Board.created_at.desc())
        .all()
    )


@router.get("/{board_id}", response_model=schemas.BoardDetail)
def get_board(board_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    get_membership(db, board_id, current_user.id)
    board = get_board_or_404(db, board_id)
    return build_board_detail(board)


@router.put("/{board_id}", response_model=schemas.BoardOut)
def update_board(
    board_id: int,
    update: schemas.BoardUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_role(db, board_id, current_user.id, ["owner"])
    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    board.title = update.title
    db.commit()
    db.refresh(board)
    return board


@router.delete("/{board_id}")
def delete_board(board_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_role(db, board_id, current_user.id, ["owner"])
    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    db.delete(board)
    db.commit()
    return {"detail": "Board deleted"}


@router.post("/{board_id}/invite", response_model=schemas.BoardMemberOut)
def invite_member(
    board_id: int,
    invite: schemas.InviteRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_role(db, board_id, current_user.id, ["owner"])

    if invite.role not in ("editor", "viewer"):
        raise HTTPException(status_code=400, detail="Role must be 'editor' or 'viewer'")

    user = db.query(models.User).filter(models.User.email == invite.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = (
        db.query(models.BoardMember)
        .filter(models.BoardMember.board_id == board_id, models.BoardMember.user_id == user.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")

    member = models.BoardMember(board_id=board_id, user_id=user.id, role=invite.role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return schemas.BoardMemberOut(user_id=user.id, role=invite.role, display_name=user.display_name)


@router.get("/{board_id}/members", response_model=list[schemas.BoardMemberOut])
def list_members(board_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    get_membership(db, board_id, current_user.id)
    board = get_board_or_404(db, board_id)
    return [to_member_output(member) for member in board.members]
