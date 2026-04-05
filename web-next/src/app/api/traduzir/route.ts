import { NextRequest, NextResponse } from "next/server";

const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";
const GROQ_MODEL = "llama-3.3-70b-versatile";

const IDIOMAS: Record<string, string> = {
  pt: "Portugues", en: "English", es: "Espanol",
  zh: "Mandarim", hi: "Hindi", ar: "Arabe", fr: "Francais",
  de: "Deutsch", ja: "Japones", ko: "Coreano", it: "Italiano", ru: "Russo",
};

export async function POST(req: NextRequest) {
  try {
    const { texto, idioma, apiKey } = await req.json();
    if (!texto || !idioma || !apiKey) {
      return NextResponse.json({ erro: "Campos obrigatorios faltando." }, { status: 400 });
    }

    const nome = IDIOMAS[idioma] || idioma;
    const system = `You are a professional translator. Translate the following text into ${nome}. Preserve the original meaning, tone, and any formatting. Reply ONLY with the translated text, no explanations.`;

    const resp = await fetch(GROQ_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: GROQ_MODEL,
        messages: [
          { role: "system", content: system },
          { role: "user", content: texto },
        ],
        temperature: 0.2,
        max_tokens: 4096,
      }),
    });

    if (!resp.ok) {
      if (resp.status === 401) return NextResponse.json({ erro: "API key invalida." }, { status: 401 });
      return NextResponse.json({ erro: `Erro: ${resp.status}` }, { status: resp.status });
    }

    const data = await resp.json();
    const resultado = data.choices?.[0]?.message?.content?.trim();
    return NextResponse.json({ resultado: resultado || null });
  } catch (e) {
    return NextResponse.json({ erro: `Erro: ${e instanceof Error ? e.message : e}` }, { status: 500 });
  }
}
