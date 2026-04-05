export interface HistoricoItem {
  nome: string;
  tipo: "txt" | "obsidian" | "logseq" | "notion";
  data: string;
  conteudo: string;
  id: string;
}

const HISTORICO_KEY = "sinapseia_historico";
const CONFIG_KEY = "sinapseia_config";
const MAX_ITEMS = 50;

export function carregarHistorico(): HistoricoItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(HISTORICO_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function salvarHistorico(item: Omit<HistoricoItem, "id" | "data">): HistoricoItem {
  const historico = carregarHistorico();
  const entry: HistoricoItem = {
    ...item,
    id: crypto.randomUUID(),
    data: new Date().toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }),
  };
  historico.unshift(entry);
  localStorage.setItem(HISTORICO_KEY, JSON.stringify(historico.slice(0, MAX_ITEMS)));
  return entry;
}

export function excluirHistorico(id: string) {
  const historico = carregarHistorico().filter((h) => h.id !== id);
  localStorage.setItem(HISTORICO_KEY, JSON.stringify(historico));
}

export function atualizarHistorico(id: string, conteudo: string) {
  const historico = carregarHistorico();
  const item = historico.find((h) => h.id === id);
  if (item) {
    item.conteudo = conteudo;
    localStorage.setItem(HISTORICO_KEY, JSON.stringify(historico));
  }
}

export interface AppConfig {
  groq_api_key?: string;
  onboarding_done?: boolean;
}

export function carregarConfig(): AppConfig {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(CONFIG_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function salvarConfig(chave: string, valor: unknown) {
  const config = carregarConfig();
  (config as Record<string, unknown>)[chave] = valor;
  localStorage.setItem(CONFIG_KEY, JSON.stringify(config));
}

export function temGroqKey(): boolean {
  return !!carregarConfig().groq_api_key;
}

export function getGroqKey(): string {
  return carregarConfig().groq_api_key || "";
}
