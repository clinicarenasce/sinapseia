"use client";
import { useState, useRef, useEffect } from "react";
import { PROMPT_OBSIDIAN, IDIOMAS } from "@/lib/groq";
import { salvarHistorico } from "@/lib/storage";

interface EditorProps {
  texto: string;
  idioma: string;
  apiKey: string;
  onToast: (msg: string, tipo?: "success" | "warn" | "error") => void;
  onLimpar: () => void;
}

export function Editor({ texto, idioma, apiKey, onToast, onLimpar }: EditorProps) {
  const [conteudo, setConteudo] = useState(texto);
  const [editando, setEditando] = useState(false);
  const [processando, setProcessando] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => { setConteudo(texto); }, [texto]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
    }
  }, [conteudo]);

  const copiar = async () => {
    await navigator.clipboard.writeText(conteudo);
    onToast("Copiado!", "success");
  };

  const salvarTxt = () => {
    const nome = `SinapseIA_${new Date().toISOString().slice(0, 16).replace(/[:-]/g, "")}`;
    salvarHistorico({ nome, tipo: "txt", conteudo });
    const blob = new Blob([conteudo], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `${nome}.txt`; a.click();
    URL.revokeObjectURL(url);
    onToast("Texto salvo!", "success");
  };

  const formatarObsidian = async () => {
    setProcessando(true);
    setStatusMsg("Formatando com IA...");
    try {
      const resp = await fetch("/api/formatar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: conteudo, apiKey, system: PROMPT_OBSIDIAN }),
      });
      const data = await resp.json();
      if (data.erro) { onToast(data.erro, "error"); return; }
      setConteudo(data.resultado);
      onToast("Formatado para Obsidian!", "success");
    } catch (e) {
      onToast(`Erro: ${e instanceof Error ? e.message : e}`, "error");
    } finally {
      setProcessando(false);
      setStatusMsg("");
    }
  };

  const salvarObsidian = () => {
    const nome = `SinapseIA_${new Date().toISOString().slice(0, 16).replace(/[:-]/g, "")}`;
    salvarHistorico({ nome, tipo: "obsidian", conteudo });
    const blob = new Blob([conteudo], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = `${nome}.md`; a.click();
    URL.revokeObjectURL(url);
    onToast("Nota Obsidian baixada!", "success");
  };

  const traduzir = async (idiomaAlvo: string) => {
    setProcessando(true);
    setStatusMsg(`Traduzindo para ${IDIOMAS[idiomaAlvo] || idiomaAlvo}...`);
    try {
      const resp = await fetch("/api/traduzir", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: conteudo, idioma: idiomaAlvo, apiKey }),
      });
      const data = await resp.json();
      if (data.erro) { onToast(data.erro, "error"); return; }
      if (data.resultado) {
        setConteudo(data.resultado);
        onToast("Traduzido!", "success");
      }
    } catch (e) {
      onToast(`Erro: ${e instanceof Error ? e.message : e}`, "error");
    } finally {
      setProcessando(false);
      setStatusMsg("");
    }
  };

  return (
    <div className="space-y-4">
      {/* Status */}
      {statusMsg && (
        <div className="text-center text-violet-400 text-sm animate-pulse">{statusMsg}</div>
      )}

      {/* Textarea */}
      <textarea
        ref={textareaRef}
        value={conteudo}
        onChange={(e) => { setConteudo(e.target.value); setEditando(true); }}
        className="w-full min-h-[200px] p-4 bg-gray-800/50 border border-gray-700 rounded-xl text-gray-200 text-sm leading-relaxed resize-y focus:outline-none focus:border-violet-500 transition-colors"
        placeholder="Texto transcrito aparecera aqui..."
      />

      {/* Botoes principais */}
      {!editando && (
        <div className="grid grid-cols-2 gap-3">
          <button onClick={copiar} disabled={processando} className="py-2.5 rounded-lg bg-gray-700 hover:bg-gray-600 text-white text-sm font-medium transition-colors disabled:opacity-50">
            Copiar
          </button>
          <button onClick={salvarTxt} disabled={processando} className="py-2.5 rounded-lg bg-gray-700 hover:bg-gray-600 text-white text-sm font-medium transition-colors disabled:opacity-50">
            Salvar .txt
          </button>
          <button onClick={formatarObsidian} disabled={processando} className="py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors disabled:opacity-50">
            {processando ? "Processando..." : "Formatar Obsidian"}
          </button>
          <button onClick={salvarObsidian} disabled={processando} className="py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors disabled:opacity-50">
            Baixar .md
          </button>
        </div>
      )}

      {/* Botoes de edicao */}
      {editando && (
        <div className="flex gap-3">
          <button onClick={() => { setEditando(false); onToast("Alteracoes salvas!", "success"); }} className="flex-1 py-2.5 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm font-medium transition-colors">
            Salvar Edicao
          </button>
          <button onClick={() => { setConteudo(texto); setEditando(false); }} className="py-2.5 px-4 rounded-lg bg-gray-600 hover:bg-gray-500 text-white text-sm font-medium transition-colors">
            Cancelar
          </button>
        </div>
      )}

      {/* Traducao */}
      {idioma && idioma !== "pt" && !editando && (
        <button onClick={() => traduzir("pt")} disabled={processando} className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-colors disabled:opacity-50">
          Traduzir para Portugues
        </button>
      )}

      {/* Limpar */}
      {!editando && (
        <button onClick={onLimpar} className="w-full py-2 rounded-lg text-gray-400 hover:text-white text-sm transition-colors">
          Nova transcricao
        </button>
      )}
    </div>
  );
}
