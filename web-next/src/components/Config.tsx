"use client";
import { useState } from "react";
import { salvarConfig, getGroqKey } from "@/lib/storage";

interface ConfigProps {
  aberto: boolean;
  onFechar: () => void;
  onToast: (msg: string, tipo?: "success" | "warn" | "error") => void;
}

export function Config({ aberto, onFechar, onToast }: ConfigProps) {
  const [key, setKey] = useState(() => getGroqKey());

  const salvar = () => {
    const trimmed = key.trim();
    if (!trimmed) { onToast("Insira uma API key.", "warn"); return; }
    salvarConfig("groq_api_key", trimmed);
    onToast("API key salva!", "success");
    onFechar();
  };

  if (!aberto) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60" onClick={onFechar} />
      <div className="relative bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-md space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Configuracoes</h2>
          <button onClick={onFechar} className="text-gray-400 hover:text-white text-2xl">&times;</button>
        </div>

        <div className="space-y-2">
          <label className="text-sm text-gray-300">API Key do Groq</label>
          <input
            type="password"
            value={key}
            onChange={(e) => setKey(e.target.value)}
            placeholder="gsk_..."
            className="w-full px-3 py-2.5 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500"
          />
          <p className="text-xs text-gray-500">
            Obtenha sua key gratuita em{" "}
            <a href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer" className="text-violet-400 hover:underline">
              console.groq.com
            </a>
          </p>
        </div>

        <button onClick={salvar} className="w-full py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-medium transition-colors">
          Salvar
        </button>
      </div>
    </div>
  );
}
