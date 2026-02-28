import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from app.database import Base, engine, SessionLocal
from app import models
from app.auth import router as auth_router, SECRET_KEY, ALGORITHM
from app.routes.users import router as users_router
from app.routes.boards import router as boards_router
from app.routes.columns import router as columns_router
from app.routes.cards import router as cards_router
from app.ws import manager

load_dotenv()


DEMO_EMAIL = "demo@taskboard.dev"
DEMO_PASSWORD = "demo1234"


def seed_demo_data():
    from app.auth import hash_password
    db = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.email == DEMO_EMAIL).first()
        if existing:
            return

        user = models.User(email=DEMO_EMAIL, hashed_password=hash_password(DEMO_PASSWORD), display_name="Demo User")
        db.add(user)
        db.flush()

        board = models.Board(title="Weekend Plans", owner_id=user.id)
        db.add(board)
        db.flush()

        member = models.BoardMember(board_id=board.id, user_id=user.id, role="owner")
        db.add(member)

        cols = [
            models.BoardColumn(board_id=board.id, title="To Do", position=0),
            models.BoardColumn(board_id=board.id, title="In Progress", position=1),
            models.BoardColumn(board_id=board.id, title="Done", position=2),
        ]
        db.add_all(cols)
        db.flush()

        cards = [
            models.Card(column_id=cols[0].id, title="Make coffee", description="The good beans, not the instant stuff", position=0, created_by=user.id),
            models.Card(column_id=cols[0].id, title="Go for a run", description="At least 3km, no excuses", position=1, created_by=user.id),
            models.Card(column_id=cols[0].id, title="Call mom", position=2, created_by=user.id),
            models.Card(column_id=cols[1].id, title="Grocery shopping", description="Milk, eggs, and way too many snacks", position=0, created_by=user.id),
            models.Card(column_id=cols[2].id, title="Clean the apartment", position=0, created_by=user.id),
        ]
        db.add_all(cards)
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    yield


app = FastAPI(title="TaskBoard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(boards_router)
app.include_router(columns_router)
app.include_router(cards_router)


@app.get("/")
def read_root():
    return {"message": "TaskBoard API is running"}


@app.websocket("/ws/{board_id}")
async def websocket_endpoint(websocket: WebSocket, board_id: int, token: str = Query(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            await websocket.close(code=4001)
            return
    except JWTError:
        await websocket.close(code=4001)
        return

    db = SessionLocal()
    try:
        membership = db.query(models.BoardMember).filter(
            models.BoardMember.board_id == board_id,
            models.BoardMember.user_id == user_id,
        ).first()
        if not membership:
            await websocket.close(code=4003)
            return
    finally:
        db.close()

    await manager.connect(websocket, board_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, board_id)
