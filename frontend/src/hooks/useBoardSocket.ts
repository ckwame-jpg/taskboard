"use client";
import { useEffect, useRef } from "react";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export function useBoardSocket(boardId: string | undefined, onMessage: (msg: Record<string, unknown>) => void) {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!boardId) {
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      return;
    }

    const url = `${WS_URL}/ws/${boardId}?token=${token}`;
    ws.current = new WebSocket(url);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    return () => {
      ws.current?.close();
      ws.current = null;
    };
  }, [boardId, onMessage]);
}
