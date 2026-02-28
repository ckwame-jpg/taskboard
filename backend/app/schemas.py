from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


# --- Users ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    display_name: str


class Token(BaseModel):
    access_token: str
    token_type: str


# --- Boards ---

class BoardCreate(BaseModel):
    title: str


class BoardUpdate(BaseModel):
    title: str


class BoardMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    role: str
    display_name: str = ""


class InviteRequest(BaseModel):
    email: EmailStr
    role: str = "editor"


# --- Columns ---

class ColumnCreate(BaseModel):
    title: str


class ColumnUpdate(BaseModel):
    title: Optional[str] = None
    position: Optional[int] = None


class ColumnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    position: int


# --- Cards ---

class CardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    column_id: int


class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class CardMove(BaseModel):
    column_id: int
    position: int


class CardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    column_id: int
    title: str
    description: Optional[str] = None
    position: int
    assigned_to: Optional[int] = None
    created_by: Optional[int] = None


class ColumnWithCards(ColumnOut):
    cards: list[CardOut] = []


class BoardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    owner_id: int
    created_at: Optional[datetime] = None


class BoardDetail(BoardOut):
    columns: list[ColumnWithCards] = []
    members: list[BoardMemberOut] = []
