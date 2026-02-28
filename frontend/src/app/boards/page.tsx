"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, logout } from "@/lib/api";

interface Board {
  id: number;
  title: string;
  owner_id: number;
}

export default function BoardsPage() {
  const [boards, setBoards] = useState<Board[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/");
      return;
    }
    apiFetch("/boards/")
      .then(setBoards)
      .catch(() => { logout(); router.push("/"); })
      .finally(() => setLoading(false));
  }, [router]);

  const createBoard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    const board = await apiFetch("/boards/", {
      method: "POST",
      body: JSON.stringify({ title: newTitle }),
    });
    setBoards([...boards, board]);
    setNewTitle("");
  };

  const deleteBoard = async (id: number) => {
    await apiFetch(`/boards/${id}`, { method: "DELETE" });
    setBoards(boards.filter((b) => b.id !== id));
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading...</div>;
  }

  return (
    <div className="min-h-screen p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Your Boards</h1>
        <button
          type="button"
          onClick={() => { logout(); router.push("/"); }}
          className="text-sm text-gray-400 hover:text-gray-200 transition"
        >
          Log out
        </button>
      </div>

      <form onSubmit={createBoard} className="flex gap-3 mb-8">
        <input
          type="text"
          placeholder="New board name..."
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          className="flex-1 px-4 py-2 bg-gray-900 border border-gray-800 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500 transition"
        />
        <button
          type="submit"
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition"
        >
          Create
        </button>
      </form>

      {boards.length === 0 ? (
        <p className="text-gray-500 text-center py-12">No boards yet. Create one to get started.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {boards.map((board) => (
            <div
              key={board.id}
              className="bg-gray-900 border border-gray-800 rounded-lg p-5 hover:border-gray-700 transition cursor-pointer group"
              onClick={() => router.push(`/boards/${board.id}`)}
            >
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-lg">{board.title}</h3>
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); deleteBoard(board.id); }}
                  className="text-gray-600 hover:text-red-400 transition opacity-0 group-hover:opacity-100"
                  aria-label="Delete board"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" /></svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
