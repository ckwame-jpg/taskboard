from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.auth import get_current_user
from app.ws import manager

router = APIRouter(prefix="/boards", tags=["Boards"])


def get_membership(db: Session, board_id: int, user_id: int) -> models.BoardMember:
    membership = db.query(models.BoardMember).filter(
        models.BoardMember.board_id == board_id,
        models.BoardMember.user_id == user_id,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this board")
    return membership


def require_role(db: Session, board_id: int, user_id: int, allowed: list[str]):
    membership = get_membership(db, board_id, user_id)
    if membership.role not in allowed:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return membership


@router.post("/", response_model=schemas.BoardOut)
def create_board(board: schemas.BoardCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_board = models.Board(title=board.title, owner_id=current_user.id)
    db.add(new_board)
    db.flush()

    member = models.BoardMember(board_id=new_board.id, user_id=current_user.id, role="owner")
    db.add(member)
    db.commit()
    db.refresh(new_board)
    return new_board


@router.get("/", response_model=list[schemas.BoardOut])
def list_boards(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    memberships = db.query(models.BoardMember).filter(models.BoardMember.user_id == current_user.id).all()
    board_ids = [m.board_id for m in memberships]
    return db.query(models.Board).filter(models.Board.id.in_(board_ids)).all()


@router.get("/{board_id}", response_model=schemas.BoardDetail)
def get_board(board_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    get_membership(db, board_id, current_user.id)
    board = db.query(models.Board).filter(models.Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    columns = db.query(models.BoardColumn).filter(
        models.BoardColumn.board_id == board_id
    ).order_by(models.BoardColumn.position).all()

    columns_out = []
    for col in columns:
        cards = db.query(models.Card).filter(
            models.Card.column_id == col.id
        ).order_by(models.Card.position).all()
        columns_out.append(schemas.ColumnWithCards(
            id=col.id, title=col.title, position=col.position,
            cards=[schemas.CardOut.model_validate(c) for c in cards],
        ))

    members = db.query(models.BoardMember).filter(models.BoardMember.board_id == board_id).all()
    members_out = []
    for m in members:
        user = db.query(models.User).filter(models.User.id == m.user_id).first()
        members_out.append(schemas.BoardMemberOut(
            user_id=m.user_id, role=m.role, display_name=user.display_name if user else "",
        ))

    return schemas.BoardDetail(
        id=board.id, title=board.title, owner_id=board.owner_id,
        created_at=board.created_at, columns=columns_out, members=members_out,
    )


@router.put("/{board_id}", response_model=schemas.BoardOut)
def update_board(board_id: int, update: schemas.BoardUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
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
def invite_member(board_id: int, invite: schemas.InviteRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    require_role(db, board_id, current_user.id, ["owner"])

    if invite.role not in ("editor", "viewer"):
        raise HTTPException(status_code=400, detail="Role must be 'editor' or 'viewer'")

    user = db.query(models.User).filter(models.User.email == invite.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(models.BoardMember).filter(
        models.BoardMember.board_id == board_id,
        models.BoardMember.user_id == user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")

    member = models.BoardMember(board_id=board_id, user_id=user.id, role=invite.role)
    db.add(member)
    db.commit()
    return schemas.BoardMemberOut(user_id=user.id, role=invite.role, display_name=user.display_name)


@router.get("/{board_id}/members", response_model=list[schemas.BoardMemberOut])
def list_members(board_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    get_membership(db, board_id, current_user.id)
    members = db.query(models.BoardMember).filter(models.BoardMember.board_id == board_id).all()
    result = []
    for m in members:
        user = db.query(models.User).filter(models.User.id == m.user_id).first()
        result.append(schemas.BoardMemberOut(
            user_id=m.user_id, role=m.role, display_name=user.display_name if user else "",
        ))
    return result
