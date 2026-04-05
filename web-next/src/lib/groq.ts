const GROQ_URL = "https://api.groq.com/openai/v1";
const GROQ_MODEL = "llama-3.3-70b-versatile";
const GROQ_MODEL_FAST = "llama-3.1-8b-instant";
const WHISPER_MODEL = "whisper-large-v3-turbo";

export async function transcreverAudio(
  audioFile: File | Blob,
  apiKey: string
): Promise<{ texto: string; idioma: string }> {
  const formData = new FormData();
  formData.append("file", audioFile, "audio.webm");
  formData.append("model", WHISPER_MODEL);
  formData.append("response_format", "verbose_json");

  const resp = await fetch(`${GROQ_URL}/audio/transcriptions`, {
    method: "POST",
    headers: { Authorization: `Bearer ${apiKey}` },
    body: formData,
  });

  if (!resp.ok) {
    if (resp.status === 401) throw new Error("API key do Groq invalida.");
    if (resp.status === 429) throw new Error("Limite de requisicoes atingido. Tente novamente em alguns minutos.");
    throw new Error(`Erro na transcricao: ${resp.status}`);
  }

  const data = await resp.json();
  return {
    texto: data.text || "",
    idioma: data.language || "",
  };
}

export async function groqGerar(
  prompt: string,
  apiKey: string,
  options: { maxTokens?: number; system?: string; modelo?: string } = {}
): Promise<string | null> {
  const { maxTokens = 4096, system, modelo = GROQ_MODEL } = options;

  const messages: { role: string; content: string }[] = [];
  if (system) messages.push({ role: "system", content: system });
  messages.push({ role: "user", content: prompt });

  const resp = await fetch(`${GROQ_URL}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: modelo,
      messages,
      temperature: 0.2,
      max_tokens: maxTokens,
    }),
  });

  if (!resp.ok) {
    if (resp.status === 401) return "__INVALID_KEY__";
    if (resp.status === 429) {
      const err = await resp.json().catch(() => ({}));
      const msg = err?.error?.message || "";
      if (msg.includes("tokens per day") || msg.includes("TPD")) {
        if (modelo === GROQ_MODEL) {
          return groqGerar(prompt, apiKey, { ...options, modelo: GROQ_MODEL_FAST });
        }
        return "__DAILY_LIMIT__";
      }
      throw new Error("Rate limit. Tente novamente em alguns segundos.");
    }
    throw new Error(`Erro Groq: ${resp.status}`);
  }

  const data = await resp.json();
  return data.choices?.[0]?.message?.content?.trim() || null;
}

export const PROMPT_OBSIDIAN = `Voce e um assistente que formata transcricoes e textos para notas no Obsidian.

Primeiro, identifique o tipo de conteudo:
- AULA: conteudo educacional, curso, modulo
- REUNIAO: discussao, decisoes, action items
- PALESTRA: apresentacao, talk, keynote
- PODCAST: conversa, entrevista
- TEXTO: artigo, anotacao, conteudo geral

Estrutura da nota:
1. YAML frontmatter:
---
date: {data de hoje no formato YYYY-MM-DD}
type: {tipo identificado acima em minusculo}
tags: [tag1, tag2, tag3]
---

2. Titulo: # Titulo claro baseado no conteudo

3. Secao ## Resumo com 2-3 frases

4. Conteudo estruturado:
   - Use ## e ### para headers
   - Use bullet points para conceitos
   - Destaque termos com **negrito**
   - Crie [[wikilinks]] para conceitos importantes que merecem nota propria
   - Para REUNIAO: adicione secao "## Decisoes" e "## Proximos passos"
   - Para AULA: adicione secao "## Exemplos" se houver

5. Secao ## Conceitos-chave no final com lista de [[wikilinks]]

Regras importantes:
- Mantenha fidelidade ao conteudo original, NAO invente informacoes
- [[wikilinks]] devem ser para conceitos reais mencionados, nao genericos
- Tags devem ser especificas: #marketing-digital em vez de #marketing
- Responda APENAS com o markdown formatado, sem explicacoes

Conteudo:
`;

export const IDIOMAS: Record<string, string> = {
  pt: "Portugues", en: "English", es: "Espanol",
  zh: "Mandarim", hi: "Hindi", ar: "Arabe", fr: "Francais",
  de: "Deutsch", ja: "Japones", ko: "Coreano", it: "Italiano", ru: "Russo",
};
