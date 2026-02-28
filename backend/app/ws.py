from fastapi import WebSocket
from typing import Dict, Set


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, board_id: int):
        await websocket.accept()
        if board_id not in self.active_connections:
            self.active_connections[board_id] = set()
        self.active_connections[board_id].add(websocket)

    def disconnect(self, websocket: WebSocket, board_id: int):
        if board_id in self.active_connections:
            self.active_connections[board_id].discard(websocket)
            if not self.active_connections[board_id]:
                del self.active_connections[board_id]

    async def broadcast(self, board_id: int, message: dict, exclude: WebSocket = None):
        if board_id not in self.active_connections:
            return
        for connection in self.active_connections[board_id].copy():
            if connection != exclude:
                try:
                    await connection.send_json(message)
                except Exception:
                    self.active_connections[board_id].discard(connection)


manager = ConnectionManager()
