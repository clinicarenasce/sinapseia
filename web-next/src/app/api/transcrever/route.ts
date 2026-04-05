import { NextRequest, NextResponse } from "next/server";

const GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions";
const WHISPER_MODEL = "whisper-large-v3-turbo";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const audio = formData.get("audio") as File | null;
    const apiKey = formData.get("apiKey") as string | null;

    if (!audio) return NextResponse.json({ erro: "Nenhum audio enviado." }, { status: 400 });
    if (!apiKey) return NextResponse.json({ erro: "API key nao configurada." }, { status: 400 });

    const groqForm = new FormData();
    groqForm.append("file", audio, audio.name || "audio.webm");
    groqForm.append("model", WHISPER_MODEL);
    groqForm.append("response_format", "verbose_json");

    const resp = await fetch(GROQ_URL, {
      method: "POST",
      headers: { Authorization: `Bearer ${apiKey}` },
      body: groqForm,
    });

    if (!resp.ok) {
      if (resp.status === 401) return NextResponse.json({ erro: "API key do Groq invalida." }, { status: 401 });
      if (resp.status === 429) return NextResponse.json({ erro: "Limite de requisicoes atingido. Tente novamente em alguns minutos." }, { status: 429 });
      return NextResponse.json({ erro: `Erro na transcricao: ${resp.status}` }, { status: resp.status });
    }

    const data = await resp.json();
    return NextResponse.json({
      texto: data.text || "",
      idioma: data.language || "",
    });
  } catch (e) {
    return NextResponse.json({ erro: `Erro: ${e instanceof Error ? e.message : e}` }, { status: 500 });
  }
}
