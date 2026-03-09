import type { BoardData } from "@/lib/board-types";

export interface DropTarget {
  columnId: number;
  position: number;
}

function parseId(raw: string, prefix: "column-" | "card-") {
  if (!raw.startsWith(prefix)) {
    return null;
  }
  const parsed = Number(raw.replace(prefix, ""));
  return Number.isFinite(parsed) ? parsed : null;
}

export function resolveDropTarget(board: BoardData, overId: string): DropTarget | null {
  const columnId = parseId(overId, "column-");
  if (columnId !== null) {
    const column = board.columns.find((candidate) => candidate.id === columnId);
    return { columnId, position: column ? column.cards.length : 0 };
  }

  const overCardId = parseId(overId, "card-");
  if (overCardId === null) {
    return null;
  }

  for (const column of board.columns) {
    const cardIndex = column.cards.findIndex((card) => card.id === overCardId);
    if (cardIndex !== -1) {
      return { columnId: column.id, position: cardIndex };
    }
  }

  return null;
}
