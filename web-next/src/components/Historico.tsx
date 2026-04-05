"use client";
import { useState, useEffect } from "react";
import { carregarHistorico, excluirHistorico, type HistoricoItem } from "@/lib/storage";

interface HistoricoProps {
  aberto: boolean;
  onFechar: () => void;
  onAbrir: (item: HistoricoItem) => void;
}

export function Historico({ aberto, onFechar, onAbrir }: HistoricoProps) {
  const [items, setItems] = useState<HistoricoItem[]>([]);

  useEffect(() => {
    if (aberto) setItems(carregarHistorico());
  }, [aberto]);

  const excluir = (id: string) => {
    excluirHistorico(id);
    setItems((prev) => prev.filter((h) => h.id !== id));
  };

  if (!aberto) return null;

  return (
    <div className="fixed inset-0 z-40 flex">
      <div className="absolute inset-0 bg-black/60" onClick={onFechar} />
      <div className="relative ml-auto w-full max-w-sm bg-gray-900 border-l border-gray-700 h-full overflow-y-auto p-4 space-y-3">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Historico</h2>
          <button onClick={onFechar} className="text-gray-400 hover:text-white text-2xl">&times;</button>
        </div>

        {items.length === 0 && (
          <p className="text-gray-500 text-sm text-center py-8">Nenhuma nota ainda.</p>
        )}

        {items.map((item) => (
          <div
            key={item.id}
            className="p-3 bg-gray-800 rounded-lg border border-gray-700 hover:border-violet-500/50 transition-colors cursor-pointer group"
            onClick={() => { onAbrir(item); onFechar(); }}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-white truncate">{item.nome}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs px-1.5 py-0.5 rounded bg-violet-600/30 text-violet-300">{item.tipo}</span>
                  <span className="text-xs text-gray-500">{item.data}</span>
                </div>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); excluir(item.id); }}
                className="text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-2 line-clamp-2">{item.conteudo.slice(0, 120)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
