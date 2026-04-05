"use client";
import { useRecorder } from "@/hooks/useRecorder";

function formatTempo(s: number) {
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
}

interface GravadorProps {
  onAudioPronto: (blob: Blob) => void;
  disabled?: boolean;
}

export function Gravador({ onAudioPronto, disabled }: GravadorProps) {
  const { gravando, pausado, tempo, nivel, iniciar, pausar, parar, cancelar } = useRecorder();

  const handleParar = async () => {
    const blob = await parar();
    if (blob && blob.size > 0) onAudioPronto(blob);
  };

  if (!gravando) {
    return (
      <button
        onClick={iniciar}
        disabled={disabled}
        className="w-full py-4 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white font-semibold text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
      >
        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
        Gravar Audio
      </button>
    );
  }

  return (
    <div className="w-full p-4 rounded-xl bg-gray-800/50 border border-gray-700 space-y-4">
      {/* Nivel de audio */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-3 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-green-500 to-violet-500 rounded-full transition-all duration-100"
            style={{ width: `${nivel * 100}%` }}
          />
        </div>
        <span className="text-white font-mono text-lg min-w-[60px] text-right">
          {formatTempo(tempo)}
        </span>
      </div>

      {/* Indicador */}
      <div className="flex items-center justify-center gap-2 text-sm">
        <span className={`w-3 h-3 rounded-full ${pausado ? "bg-yellow-500" : "bg-red-500 animate-pulse"}`} />
        <span className="text-gray-300">{pausado ? "Pausado" : "Gravando..."}</span>
      </div>

      {/* Botoes */}
      <div className="flex gap-3">
        <button
          onClick={pausar}
          className="flex-1 py-2.5 rounded-lg bg-yellow-600 hover:bg-yellow-500 text-white font-medium transition-colors"
        >
          {pausado ? "Retomar" : "Pausar"}
        </button>
        <button
          onClick={handleParar}
          className="flex-1 py-2.5 rounded-lg bg-green-600 hover:bg-green-500 text-white font-medium transition-colors"
        >
          Parar
        </button>
        <button
          onClick={cancelar}
          className="py-2.5 px-4 rounded-lg bg-gray-600 hover:bg-gray-500 text-white font-medium transition-colors"
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}
