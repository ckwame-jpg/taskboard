"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import type { BoardData } from "@/lib/board-types";

export function useBoardData(boardId?: string) {
  const router = useRouter();
  const [board, setBoard] = useState<BoardData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchBoard = useCallback(async () => {
    if (!boardId) {
      setLoading(false);
      return;
    }

    try {
      const data = await apiFetch(`/boards/${boardId}`);
      setBoard(data as BoardData);
    } catch {
      router.push("/boards");
    } finally {
      setLoading(false);
    }
  }, [boardId, router]);

  useEffect(() => {
    if (!boardId) {
      router.push("/boards");
      return;
    }

    if (!localStorage.getItem("token")) {
      router.push("/");
      return;
    }

    fetchBoard();
  }, [boardId, fetchBoard, router]);

  const addColumn = useCallback(
    async (title: string) => {
      if (!boardId) {
        return;
      }

      await apiFetch(`/boards/${boardId}/columns/`, {
        method: "POST",
        body: JSON.stringify({ title }),
      });
      await fetchBoard();
    },
    [boardId, fetchBoard],
  );

  const deleteColumn = useCallback(
    async (columnId: number) => {
      if (!boardId) {
        return;
      }

      await apiFetch(`/boards/${boardId}/columns/${columnId}`, { method: "DELETE" });
      await fetchBoard();
    },
    [boardId, fetchBoard],
  );

  const addCard = useCallback(
    async (columnId: number, title: string) => {
      if (!boardId) {
        return;
      }

      await apiFetch(`/boards/${boardId}/cards/`, {
        method: "POST",
        body: JSON.stringify({ title, column_id: columnId }),
      });
      await fetchBoard();
    },
    [boardId, fetchBoard],
  );

  const deleteCard = useCallback(
    async (cardId: number) => {
      if (!boardId) {
        return;
      }

      await apiFetch(`/boards/${boardId}/cards/${cardId}`, { method: "DELETE" });
      await fetchBoard();
    },
    [boardId, fetchBoard],
  );

  const moveCard = useCallback(
    async (cardId: number, columnId: number, position: number) => {
      if (!boardId) {
        return;
      }

      await apiFetch(`/boards/${boardId}/cards/${cardId}/move`, {
        method: "PUT",
        body: JSON.stringify({ column_id: columnId, position }),
      });
      await fetchBoard();
    },
    [boardId, fetchBoard],
  );

  return {
    board,
    loading,
    fetchBoard,
    addColumn,
    deleteColumn,
    addCard,
    deleteCard,
    moveCard,
  };
}
