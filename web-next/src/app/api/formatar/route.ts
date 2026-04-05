import { NextRequest, NextResponse } from "next/server";

const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";
const GROQ_MODEL = "llama-3.3-70b-versatile";
const GROQ_MODEL_FAST = "llama-3.1-8b-instant";

async function chamarGroq(prompt: string, apiKey: string, system: string, modelo = GROQ_MODEL): Promise<string | null> {
  const messages = [
    { role: "system", content: system },
    { role: "user", content: prompt },
  ];

  const resp = await fetch(GROQ_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({ model: modelo, messages, temperature: 0.2, max_tokens: 4096 }),
  });

  if (!resp.ok) {
    if (resp.status === 401) return "__INVALID_KEY__";
    if (resp.status === 429) {
      const err = await resp.json().catch(() => ({}));
      const msg = err?.error?.message || "";
      if ((msg.includes("tokens per day") || msg.includes("TPD")) && modelo === GROQ_MODEL) {
        return chamarGroq(prompt, apiKey, system, GROQ_MODEL_FAST);
      }
      return "__DAILY_LIMIT__";
    }
    throw new Error(`Groq ${resp.status}`);
  }

  const data = await resp.json();
  return data.choices?.[0]?.message?.content?.trim() || null;
}

export async function POST(req: NextRequest) {
  try {
    const { texto, apiKey, system } = await req.json();
    if (!texto) return NextResponse.json({ erro: "Nenhum texto enviado." }, { status: 400 });
    if (!apiKey) return NextResponse.json({ erro: "API key nao configurada." }, { status: 400 });
    if (!system) return NextResponse.json({ erro: "System prompt nao enviado." }, { status: 400 });

    const resultado = await chamarGroq(texto, apiKey, system);

    if (resultado === "__INVALID_KEY__") return NextResponse.json({ erro: "API key do Groq invalida." }, { status: 401 });
    if (resultado === "__DAILY_LIMIT__") return NextResponse.json({ erro: "Limite diario de tokens atingido. Tente novamente em algumas horas." }, { status: 429 });
    if (!resultado) return NextResponse.json({ erro: "O modelo nao retornou texto." }, { status: 500 });

    return NextResponse.json({ resultado });
  } catch (e) {
    return NextResponse.json({ erro: `Erro: ${e instanceof Error ? e.message : e}` }, { status: 500 });
  }
}
