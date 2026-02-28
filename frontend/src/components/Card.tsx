"use client";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

interface CardData {
  id: number;
  title: string;
  description: string | null;
  column_id: number;
  position: number;
}

interface SortableCardProps {
  card: CardData;
  onDelete: (cardId: number) => void;
}

export function SortableCard({ card, onDelete }: SortableCardProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: `card-${card.id}`,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="bg-gray-800 border border-gray-700 rounded-md p-3 cursor-grab active:cursor-grabbing hover:border-gray-600 transition group"
    >
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-medium text-gray-200">{card.title}</p>
        <button
          type="button"
          onPointerDown={(e) => e.stopPropagation()}
          onClick={() => onDelete(card.id)}
          className="text-gray-600 hover:text-red-400 transition opacity-0 group-hover:opacity-100 shrink-0"
          aria-label="Delete card"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
        </button>
      </div>
      {card.description && (
        <p className="text-xs text-gray-500 mt-1 line-clamp-2">{card.description}</p>
      )}
    </div>
  );
}
