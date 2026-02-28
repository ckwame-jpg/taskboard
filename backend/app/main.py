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


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
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
