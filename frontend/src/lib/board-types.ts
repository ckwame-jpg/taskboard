export interface CardData {
  id: number;
  title: string;
  description: string | null;
  column_id: number;
  position: number;
  assigned_to: number | null;
  created_by: number | null;
}

export interface ColumnData {
  id: number;
  title: string;
  position: number;
  cards: CardData[];
}

export interface BoardMember {
  user_id: number;
  role: string;
  display_name: string;
}

export interface BoardData {
  id: number;
  title: string;
  owner_id: number;
  columns: ColumnData[];
  members: BoardMember[];
}
