# TaskBoard

A real-time collaborative task board built with FastAPI and Next.js. Multiple users can view and manage the same board simultaneously — card moves, column changes, and new tasks show up instantly for everyone via WebSockets.

## Tech Stack

**Backend:** FastAPI, PostgreSQL, SQLAlchemy, WebSockets, JWT auth
**Frontend:** Next.js 15, TypeScript, Tailwind CSS, @dnd-kit
**Infra:** Docker Compose

## Features

- **Real-time sync** — WebSocket broadcasts every mutation (card created, moved, deleted, etc.) to all connected clients
- **Drag and drop** — Move cards between columns with @dnd-kit, with optimistic UI updates
- **Role-based access** — Three roles per board:
  - **Owner** — full control, can invite members and delete the board
  - **Editor** — create, update, delete cards and columns
  - **Viewer** — read-only access
- **JWT authentication** — register/login flow with secure password hashing
- **Board invitations** — invite users by email with a specific role

## Quick Start

```bash
docker compose up
```

That's it. This spins up:
- **PostgreSQL** on port 5432
- **Backend API** on http://localhost:8000
- **Frontend** on http://localhost:3000

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Create a new account |
| POST | `/login` | Get a JWT access token |

### Boards
| Method | Path | Description |
|--------|------|-------------|
| POST | `/boards/` | Create a board |
| GET | `/boards/` | List your boards |
| GET | `/boards/{id}` | Get board with columns, cards, and members |
| PUT | `/boards/{id}` | Rename a board |
| DELETE | `/boards/{id}` | Delete a board (owner only) |
| POST | `/boards/{id}/invite` | Invite a user by email |
| GET | `/boards/{id}/members` | List board members |

### Columns
| Method | Path | Description |
|--------|------|-------------|
| POST | `/boards/{id}/columns/` | Add a column |
| PUT | `/boards/{id}/columns/{col_id}` | Rename or reorder a column |
| DELETE | `/boards/{id}/columns/{col_id}` | Delete a column |

### Cards
| Method | Path | Description |
|--------|------|-------------|
| POST | `/boards/{id}/cards/` | Create a card |
| PUT | `/boards/{id}/cards/{card_id}` | Update a card |
| PUT | `/boards/{id}/cards/{card_id}/move` | Move a card to a different column |
| DELETE | `/boards/{id}/cards/{card_id}` | Delete a card |

### WebSocket
Connect to `ws://localhost:8000/ws/{board_id}?token={jwt}` to receive real-time events:
`card_created`, `card_moved`, `card_updated`, `card_deleted`, `column_created`, `column_updated`, `column_deleted`

## Project Structure

```
taskboard/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, WebSocket endpoint
│   │   ├── auth.py           # JWT auth, password hashing
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── database.py       # DB engine and session
│   │   ├── ws.py             # WebSocket connection manager
│   │   └── routes/
│   │       ├── boards.py     # Board CRUD + RBAC helpers
│   │       ├── columns.py    # Column CRUD
│   │       ├── cards.py      # Card CRUD + move
│   │       └── users.py      # Registration
│   ├── tests/                # pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages (login, boards, board detail)
│   │   ├── components/       # Column and Card components
│   │   ├── hooks/            # useAuth, useBoardSocket
│   │   └── lib/api.ts        # Fetch wrapper with auth
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest
```
