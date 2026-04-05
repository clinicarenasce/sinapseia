"use client";
import { useEffect, useState } from "react";

interface ToastProps {
  mensagem: string;
  tipo?: "success" | "warn" | "error";
  onClose: () => void;
}

export function Toast({ mensagem, tipo = "success", onClose }: ToastProps) {
  const [visible, setVisible] = useState(true);
  useEffect(() => {
    const t = setTimeout(() => { setVisible(false); setTimeout(onClose, 300); }, 3000);
    return () => clearTimeout(t);
  }, [onClose]);

  const cores = {
    success: "bg-green-600",
    warn: "bg-yellow-600",
    error: "bg-red-600",
  };

  return (
    <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg text-white text-sm shadow-lg transition-opacity duration-300 ${cores[tipo]} ${visible ? "opacity-100" : "opacity-0"}`}>
      {mensagem}
    </div>
  );
}
