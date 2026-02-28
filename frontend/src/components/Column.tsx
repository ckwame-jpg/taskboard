"use client";
import { useDroppable } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { SortableCard } from "./Card";

interface CardData {
  id: number;
  title: string;
  description: string | null;
  column_id: number;
  position: number;
}

interface ColumnProps {
  id: number;
  title: string;
  cards: CardData[];
  onAddCard: (columnId: number, title: string) => void;
  onDeleteColumn: (columnId: number) => void;
  onDeleteCard: (cardId: number) => void;
}

export default function Column({ id, title, cards, onAddCard, onDeleteColumn, onDeleteCard }: ColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id: `column-${id}` });

  const handleAddCard = () => {
    const cardTitle = prompt("Card title:");
    if (cardTitle?.trim()) {
      onAddCard(id, cardTitle.trim());
    }
  };

  return (
    <div
      className={`bg-gray-900 rounded-lg border ${isOver ? "border-blue-500" : "border-gray-800"} p-3 min-w-[280px] max-w-[280px] flex flex-col max-h-[calc(100vh-180px)] transition-colors`}
    >
      <div className="flex items-center justify-between mb-3 px-1">
        <h3 className="font-semibold text-sm text-gray-300 uppercase tracking-wider">{title}</h3>
        <div className="flex items-center gap-1">
          <span className="text-xs text-gray-500">{cards.length}</span>
          <button
            type="button"
            onClick={() => onDeleteColumn(id)}
            className="text-gray-600 hover:text-red-400 transition p-0.5"
            aria-label="Delete column"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
          </button>
        </div>
      </div>

      <div ref={setNodeRef} className="flex-1 overflow-y-auto space-y-2 min-h-[40px]">
        <SortableContext items={cards.map((c) => `card-${c.id}`)} strategy={verticalListSortingStrategy}>
          {cards.map((card) => (
            <SortableCard key={card.id} card={card} onDelete={onDeleteCard} />
          ))}
        </SortableContext>
      </div>

      <button
        type="button"
        onClick={handleAddCard}
        className="mt-2 w-full py-1.5 text-sm text-gray-500 hover:text-gray-300 hover:bg-gray-800 rounded transition"
      >
        + Add card
      </button>
    </div>
  );
}
