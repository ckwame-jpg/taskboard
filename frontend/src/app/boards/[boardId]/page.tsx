"use client";
import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { DndContext, DragEndEvent, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import { apiFetch } from "@/lib/api";
import { useBoardSocket } from "@/hooks/useBoardSocket";
import Column from "@/components/Column";

interface CardData {
  id: number;
  title: string;
  description: string | null;
  column_id: number;
  position: number;
  assigned_to: number | null;
  created_by: number | null;
}

interface ColumnData {
  id: number;
  title: string;
  position: number;
  cards: CardData[];
}

interface BoardData {
  id: number;
  title: string;
  owner_id: number;
  columns: ColumnData[];
  members: { user_id: number; role: string; display_name: string }[];
}

export default function BoardPage() {
  const params = useParams();
  const router = useRouter();
  const boardId = params.boardId as string;
  const [board, setBoard] = useState<BoardData | null>(null);
  const [loading, setLoading] = useState(true);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  const fetchBoard = useCallback(async () => {
    try {
      const data = await apiFetch(`/boards/${boardId}`);
      setBoard(data);
    } catch {
      router.push("/boards");
    } finally {
      setLoading(false);
    }
  }, [boardId, router]);

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/");
      return;
    }
    fetchBoard();
  }, [fetchBoard, router]);

  const handleWsMessage = useCallback((msg: Record<string, unknown>) => {
    fetchBoard();
  }, [fetchBoard]);

  useBoardSocket(boardId, handleWsMessage);

  const addColumn = async () => {
    const title = prompt("Column title:");
    if (!title?.trim()) return;
    await apiFetch(`/boards/${boardId}/columns/`, {
      method: "POST",
      body: JSON.stringify({ title: title.trim() }),
    });
    fetchBoard();
  };

  const deleteColumn = async (columnId: number) => {
    await apiFetch(`/boards/${boardId}/columns/${columnId}`, { method: "DELETE" });
    fetchBoard();
  };

  const addCard = async (columnId: number, title: string) => {
    await apiFetch(`/boards/${boardId}/cards/`, {
      method: "POST",
      body: JSON.stringify({ title, column_id: columnId }),
    });
    fetchBoard();
  };

  const deleteCard = async (cardId: number) => {
    await apiFetch(`/boards/${boardId}/cards/${cardId}`, { method: "DELETE" });
    fetchBoard();
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || !board) return;

    const cardId = Number(String(active.id).replace("card-", ""));
    const overId = String(over.id);

    let targetColumnId: number;
    let targetPosition: number;

    if (overId.startsWith("column-")) {
      targetColumnId = Number(overId.replace("column-", ""));
      const col = board.columns.find((c) => c.id === targetColumnId);
      targetPosition = col ? col.cards.length : 0;
    } else if (overId.startsWith("card-")) {
      const overCardId = Number(overId.replace("card-", ""));
      for (const col of board.columns) {
        const cardIndex = col.cards.findIndex((c) => c.id === overCardId);
        if (cardIndex !== -1) {
          targetColumnId = col.id;
          targetPosition = cardIndex;
          break;
        }
      }
      if (targetColumnId! === undefined) return;
    } else {
      return;
    }

    await apiFetch(`/boards/${boardId}/cards/${cardId}/move`, {
      method: "PUT",
      body: JSON.stringify({ column_id: targetColumnId!, position: targetPosition! }),
    });
    fetchBoard();
  };

  if (loading || !board) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading board...</div>;
  }

  return (
    <div className="min-h-screen p-6">
      <div className="flex items-center gap-4 mb-6">
        <button
          type="button"
          onClick={() => router.push("/boards")}
          className="text-gray-400 hover:text-gray-200 transition"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 12H5M12 19l-7-7 7-7" /></svg>
        </button>
        <h1 className="text-xl font-bold">{board.title}</h1>
        <div className="flex items-center gap-1 ml-4">
          {board.members.map((m) => (
            <span
              key={m.user_id}
              className="w-7 h-7 rounded-full bg-gray-700 flex items-center justify-center text-xs font-medium"
              title={`${m.display_name} (${m.role})`}
            >
              {m.display_name.charAt(0).toUpperCase()}
            </span>
          ))}
        </div>
      </div>

      <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
        <div className="flex gap-4 overflow-x-auto pb-4">
          {board.columns.map((col) => (
            <Column
              key={col.id}
              id={col.id}
              title={col.title}
              cards={col.cards}
              onAddCard={addCard}
              onDeleteColumn={deleteColumn}
              onDeleteCard={deleteCard}
            />
          ))}

          <button
            type="button"
            onClick={addColumn}
            className="min-w-[280px] h-12 bg-gray-900/50 border border-dashed border-gray-700 rounded-lg text-gray-500 hover:text-gray-300 hover:border-gray-600 transition flex items-center justify-center"
          >
            + Add column
          </button>
        </div>
      </DndContext>
    </div>
  );
}
