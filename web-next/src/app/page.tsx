"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { Gravador } from "@/components/Gravador";
import { Editor } from "@/components/Editor";
import { Historico } from "@/components/Historico";
import { Config } from "@/components/Config";
import { Onboarding } from "@/components/Onboarding";
import { Toast } from "@/components/Toast";
import { carregarConfig, getGroqKey, temGroqKey } from "@/lib/storage";
import type { HistoricoItem } from "@/lib/storage";

type ToastData = { msg: string; tipo: "success" | "warn" | "error" };

export default function Home() {
  const [texto, setTexto] = useState("");
  const [idioma, setIdioma] = useState("");
  const [transcrevendo, setTranscrevendo] = useState(false);
  const [progresso, setProgresso] = useState("");
  const [showHistorico, setShowHistorico] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [toast, setToast] = useState<ToastData | null>(null);
  const [textoLivre, setTextoLivre] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const config = carregarConfig();
    if (!config.onboarding_done) setShowOnboarding(true);
  }, []);

  const showToast = useCallback((msg: string, tipo: "success" | "warn" | "error" = "success") => {
    setToast({ msg, tipo });
  }, []);

  const transcreverAudio = async (blob: Blob) => {
    const apiKey = getGroqKey();
    if (!apiKey) { showToast("Configure sua API key primeiro.", "warn"); setShowConfig(true); return; }

    setTranscrevendo(true);
    setProgresso("Enviando audio para transcricao...");
    try {
      const formData = new FormData();
      formData.append("audio", blob, "audio.webm");
      formData.append("apiKey", apiKey);

      const resp = await fetch("/api/transcrever", { method: "POST", body: formData });
      const data = await resp.json();

      if (data.erro) { showToast(data.erro, "error"); return; }

      setTexto(data.texto);
      setIdioma(data.idioma || "");
      showToast("Transcricao concluida!", "success");
    } catch (e) {
      showToast(`Erro: ${e instanceof Error ? e.message : e}`, "error");
    } finally {
      setTranscrevendo(false);
      setProgresso("");
    }
  };

  const handleArquivo = async () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "audio/*,video/*,.srt,.vtt,.txt";
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;

      // Texto/legenda: ler direto
      if (file.name.match(/\.(txt|srt|vtt|ass|ssa|sub|sbv)$/i)) {
        const text = await file.text();
        setTexto(text);
        showToast("Arquivo carregado!", "success");
        return;
      }

      // Audio/video: transcrever
      await transcreverAudio(file);
    };
    input.click();
  };

  const handleColarTexto = () => {
    setTextoLivre(true);
    setTexto("");
    setTimeout(() => textareaRef.current?.focus(), 100);
  };

  const handleTextoLivreSubmit = () => {
    const val = textareaRef.current?.value || "";
    if (!val.trim()) { showToast("Cole ou digite um texto.", "warn"); return; }
    setTexto(val);
    setTextoLivre(false);
  };

  const handleHistoricoAbrir = (item: HistoricoItem) => {
    setTexto(item.conteudo);
    setTextoLivre(false);
  };

  const limpar = () => {
    setTexto("");
    setIdioma("");
    setTextoLivre(false);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="SinapseIA" className="w-8 h-8 rounded-lg" />
          <h1 className="text-lg font-bold bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text text-transparent">
            SinapseIA
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setShowHistorico(true)} className="p-2 text-gray-400 hover:text-white transition-colors" title="Historico">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </button>
          <button onClick={() => setShowConfig(true)} className="p-2 text-gray-400 hover:text-white transition-colors" title="Configuracoes">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
          </button>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 flex flex-col items-center px-4 py-6 max-w-2xl mx-auto w-full">
        {/* Transcrevendo */}
        {transcrevendo && (
          <div className="w-full text-center space-y-4 py-12">
            <div className="w-12 h-12 mx-auto border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-violet-400 animate-pulse">{progresso}</p>
          </div>
        )}

        {/* Texto livre */}
        {textoLivre && !texto && !transcrevendo && (
          <div className="w-full space-y-4">
            <h2 className="text-lg font-semibold text-white">Cole ou digite seu texto</h2>
            <textarea
              ref={textareaRef}
              className="w-full min-h-[300px] p-4 bg-gray-800/50 border border-gray-700 rounded-xl text-gray-200 text-sm leading-relaxed resize-y focus:outline-none focus:border-violet-500"
              placeholder="Cole seu texto aqui..."
            />
            <div className="flex gap-3">
              <button onClick={handleTextoLivreSubmit} className="flex-1 py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-medium transition-colors">
                Processar Texto
              </button>
              <button onClick={() => setTextoLivre(false)} className="py-2.5 px-4 rounded-lg bg-gray-700 hover:bg-gray-600 text-white font-medium transition-colors">
                Voltar
              </button>
            </div>
          </div>
        )}

        {/* Editor de resultado */}
        {texto && !transcrevendo && (
          <div className="w-full">
            <Editor
              texto={texto}
              idioma={idioma}
              apiKey={getGroqKey()}
              onToast={showToast}
              onLimpar={limpar}
            />
          </div>
        )}

        {/* Tela inicial */}
        {!texto && !transcrevendo && !textoLivre && (
          <div className="w-full space-y-6 py-8">
            <div className="text-center space-y-2 mb-8">
              <img src="/logo.png" alt="SinapseIA" className="w-16 h-16 mx-auto rounded-2xl animate-pulse-glow" />
              <h2 className="text-xl font-bold text-white">O que voce quer fazer?</h2>
              <p className="text-gray-400 text-sm">Escolha uma opcao para comecar</p>
            </div>

            {/* Gravador */}
            <Gravador onAudioPronto={transcreverAudio} disabled={!temGroqKey()} />

            {/* Outras opcoes */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleArquivo}
                disabled={!temGroqKey()}
                className="py-4 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-violet-500/50 text-white font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex flex-col items-center gap-2"
              >
                <svg className="w-6 h-6 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                <span className="text-sm">Enviar Arquivo</span>
              </button>
              <button
                onClick={handleColarTexto}
                className="py-4 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-violet-500/50 text-white font-medium transition-all flex flex-col items-center gap-2"
              >
                <svg className="w-6 h-6 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                <span className="text-sm">Colar Texto</span>
              </button>
            </div>

            {!temGroqKey() && (
              <button onClick={() => setShowConfig(true)} className="w-full py-3 rounded-xl border-2 border-dashed border-violet-500/50 text-violet-400 hover:text-violet-300 hover:border-violet-400 font-medium transition-all">
                Configure sua API Key para comecar
              </button>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center text-xs text-gray-600 py-3 border-t border-gray-800">
        SinapseIA — Transforme audio em conhecimento
      </footer>

      {/* Modais */}
      <Historico aberto={showHistorico} onFechar={() => setShowHistorico(false)} onAbrir={handleHistoricoAbrir} />
      <Config aberto={showConfig} onFechar={() => setShowConfig(false)} onToast={showToast} />
      {showOnboarding && <Onboarding onConcluir={() => setShowOnboarding(false)} />}
      {toast && <Toast mensagem={toast.msg} tipo={toast.tipo} onClose={() => setToast(null)} />}
    </div>
  );
}
