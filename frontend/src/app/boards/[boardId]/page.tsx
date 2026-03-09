"use client";

import { useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { DndContext, type DragEndEvent, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import Column from "@/components/Column";
import { useBoardSocket } from "@/hooks/useBoardSocket";
import { useBoardData } from "@/hooks/useBoardData";
import { resolveDropTarget } from "@/lib/board-drag";

export default function BoardPage() {
  const params = useParams();
  const router = useRouter();
  const boardIdParam = params.boardId;
  const boardId = Array.isArray(boardIdParam) ? boardIdParam[0] : boardIdParam;

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  const { board, loading, fetchBoard, addColumn, deleteColumn, addCard, deleteCard, moveCard } = useBoardData(
    boardId,
  );

  const handleWsMessage = useCallback(() => {
    fetchBoard();
  }, [fetchBoard]);

  useBoardSocket(boardId, handleWsMessage);

  const handleAddColumn = async () => {
    const title = prompt("Column title:");
    if (!title?.trim()) {
      return;
    }
    await addColumn(title.trim());
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    if (!board || !event.over) {
      return;
    }

    const activeId = String(event.active.id);
    if (!activeId.startsWith("card-")) {
      return;
    }

    const cardId = Number(activeId.replace("card-", ""));
    const target = resolveDropTarget(board, String(event.over.id));

    if (!target) {
      return;
    }

    await moveCard(cardId, target.columnId, target.position);
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
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 className="text-xl font-bold">{board.title}</h1>
        <div className="flex items-center gap-1 ml-4">
          {board.members.map((member) => (
            <span
              key={member.user_id}
              className="w-7 h-7 rounded-full bg-gray-700 flex items-center justify-center text-xs font-medium"
              title={`${member.display_name} (${member.role})`}
            >
              {member.display_name.charAt(0).toUpperCase()}
            </span>
          ))}
        </div>
      </div>

      <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
        <div className="flex gap-4 overflow-x-auto pb-4">
          {board.columns.map((column) => (
            <Column
              key={column.id}
              id={column.id}
              title={column.title}
              cards={column.cards}
              onAddCard={addCard}
              onDeleteColumn={deleteColumn}
              onDeleteCard={deleteCard}
            />
          ))}

          <button
            type="button"
            onClick={handleAddColumn}
            className="min-w-[280px] h-12 bg-gray-900/50 border border-dashed border-gray-700 rounded-lg text-gray-500 hover:text-gray-300 hover:border-gray-600 transition flex items-center justify-center"
          >
            + Add column
          </button>
        </div>
      </DndContext>
    </div>
  );
}
