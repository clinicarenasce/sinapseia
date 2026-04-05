"use client";
import { useState } from "react";
import { salvarConfig } from "@/lib/storage";

interface OnboardingProps {
  onConcluir: () => void;
}

export function Onboarding({ onConcluir }: OnboardingProps) {
  const [step, setStep] = useState(0);
  const [key, setKey] = useState("");

  const salvarKey = () => {
    const trimmed = key.trim();
    if (!trimmed) return;
    salvarConfig("groq_api_key", trimmed);
    salvarConfig("onboarding_done", true);
    onConcluir();
  };

  const pular = () => {
    salvarConfig("onboarding_done", true);
    onConcluir();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl p-8 w-full max-w-lg space-y-6 text-center">
        {step === 0 && (
          <>
            <img src="/logo.png" alt="SinapseIA" className="w-20 h-20 mx-auto rounded-2xl" />
            <h1 className="text-2xl font-bold text-white">Bem-vindo ao SinapseIA</h1>
            <p className="text-gray-400">
              Transforme audio em notas inteligentes para seu segundo cerebro.
              Grave, transcreva e formate para Obsidian em segundos.
            </p>
            <div className="space-y-3 text-left text-sm text-gray-300">
              <div className="flex gap-3 items-start">
                <span className="text-violet-400 text-lg">1.</span>
                <span>Grave audio ou envie um arquivo</span>
              </div>
              <div className="flex gap-3 items-start">
                <span className="text-violet-400 text-lg">2.</span>
                <span>A IA transcreve automaticamente</span>
              </div>
              <div className="flex gap-3 items-start">
                <span className="text-violet-400 text-lg">3.</span>
                <span>Formate e exporte para Obsidian, Logseq ou Notion</span>
              </div>
            </div>
            <button onClick={() => setStep(1)} className="w-full py-3 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white font-semibold transition-all">
              Comecar
            </button>
          </>
        )}

        {step === 1 && (
          <>
            <h2 className="text-xl font-bold text-white">Configure sua API Key</h2>
            <p className="text-gray-400 text-sm">
              O SinapseIA usa o Groq para transcrever e formatar suas notas. E gratuito!
            </p>
            <div className="space-y-2 text-left">
              <label className="text-sm text-gray-300">API Key do Groq</label>
              <input
                type="text"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder="gsk_..."
                className="w-full px-3 py-2.5 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm focus:outline-none focus:border-violet-500"
              />
              <p className="text-xs text-gray-500">
                Crie sua key em{" "}
                <a href="https://console.groq.com/keys" target="_blank" rel="noopener noreferrer" className="text-violet-400 hover:underline">
                  console.groq.com/keys
                </a>
                {" "}(gratuito, leva 30 segundos)
              </p>
            </div>
            <div className="flex gap-3">
              <button onClick={pular} className="flex-1 py-2.5 rounded-lg bg-gray-700 hover:bg-gray-600 text-white font-medium transition-colors">
                Pular
              </button>
              <button onClick={salvarKey} disabled={!key.trim()} className="flex-1 py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 text-white font-medium transition-colors disabled:opacity-50">
                Pronto
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
