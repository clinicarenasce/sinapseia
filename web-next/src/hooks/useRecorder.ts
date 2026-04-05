"use client";
import { useState, useRef, useCallback, useEffect } from "react";

export interface UseRecorderReturn {
  gravando: boolean;
  pausado: boolean;
  tempo: number;
  nivel: number;
  iniciar: () => Promise<void>;
  pausar: () => void;
  parar: () => Promise<Blob | null>;
  cancelar: () => void;
}

export function useRecorder(): UseRecorderReturn {
  const [gravando, setGravando] = useState(false);
  const [pausado, setPausado] = useState(false);
  const [tempo, setTempo] = useState(0);
  const [nivel, setNivel] = useState(0);

  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const stream = useRef<MediaStream | null>(null);
  const chunks = useRef<Blob[]>([]);
  const analyser = useRef<AnalyserNode | null>(null);
  const animFrame = useRef<number>(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const resolveStop = useRef<((blob: Blob | null) => void) | null>(null);

  const cleanup = useCallback(() => {
    if (animFrame.current) cancelAnimationFrame(animFrame.current);
    if (timerRef.current) clearInterval(timerRef.current);
    stream.current?.getTracks().forEach((t) => t.stop());
    mediaRecorder.current = null;
    stream.current = null;
    analyser.current = null;
    chunks.current = [];
    setGravando(false);
    setPausado(false);
    setTempo(0);
    setNivel(0);
  }, []);

  const monitorarNivel = useCallback(() => {
    if (!analyser.current) return;
    const data = new Uint8Array(analyser.current.fftSize);
    const tick = () => {
      if (!analyser.current) return;
      analyser.current.getByteTimeDomainData(data);
      let sum = 0;
      for (let i = 0; i < data.length; i++) {
        const v = (data[i] - 128) / 128;
        sum += v * v;
      }
      const rms = Math.sqrt(sum / data.length);
      setNivel(Math.min(1, rms * 10));
      animFrame.current = requestAnimationFrame(tick);
    };
    tick();
  }, []);

  const iniciar = useCallback(async () => {
    try {
      const s = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.current = s;

      const ctx = new AudioContext();
      const source = ctx.createMediaStreamSource(s);
      const an = ctx.createAnalyser();
      an.fftSize = 256;
      source.connect(an);
      analyser.current = an;

      const mr = new MediaRecorder(s, { mimeType: "audio/webm;codecs=opus" });
      chunks.current = [];
      mr.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.current.push(e.data);
      };
      mr.onstop = () => {
        const blob = new Blob(chunks.current, { type: "audio/webm" });
        resolveStop.current?.(blob);
        resolveStop.current = null;
      };
      mr.start(250);
      mediaRecorder.current = mr;

      setGravando(true);
      setPausado(false);
      setTempo(0);
      timerRef.current = setInterval(() => setTempo((t) => t + 1), 1000);
      monitorarNivel();
    } catch {
      throw new Error("Permissao de microfone negada.");
    }
  }, [monitorarNivel]);

  const pausar = useCallback(() => {
    if (!mediaRecorder.current) return;
    if (mediaRecorder.current.state === "recording") {
      mediaRecorder.current.pause();
      setPausado(true);
      if (timerRef.current) clearInterval(timerRef.current);
    } else if (mediaRecorder.current.state === "paused") {
      mediaRecorder.current.resume();
      setPausado(false);
      timerRef.current = setInterval(() => setTempo((t) => t + 1), 1000);
    }
  }, []);

  const parar = useCallback((): Promise<Blob | null> => {
    return new Promise((resolve) => {
      if (!mediaRecorder.current || mediaRecorder.current.state === "inactive") {
        cleanup();
        resolve(null);
        return;
      }
      resolveStop.current = resolve;
      mediaRecorder.current.stop();
      if (animFrame.current) cancelAnimationFrame(animFrame.current);
      if (timerRef.current) clearInterval(timerRef.current);
      stream.current?.getTracks().forEach((t) => t.stop());
      setGravando(false);
    });
  }, [cleanup]);

  const cancelar = useCallback(() => {
    if (mediaRecorder.current && mediaRecorder.current.state !== "inactive") {
      mediaRecorder.current.onstop = null;
      mediaRecorder.current.stop();
    }
    cleanup();
  }, [cleanup]);

  useEffect(() => () => cleanup(), [cleanup]);

  return { gravando, pausado, tempo, nivel, iniciar, pausar, parar, cancelar };
}
