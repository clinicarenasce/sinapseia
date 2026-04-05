# 🧠 Sinapse&IA

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203-F55036?style=flat-square)
![Whisper](https://img.shields.io/badge/Whisper-large--v3--turbo-412991?style=flat-square)
![Eel](https://img.shields.io/badge/UI-Eel%2FChrome-4285F4?style=flat-square&logo=googlechrome&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?style=flat-square&logo=windows&logoColor=white)
![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-22c55e?style=flat-square)

> **Transcreva qualquer áudio e transforme o resultado em uma nota estruturada para o seu segundo cérebro — com um único clique.**

---

## O que é

**Sinapse&IA** é uma aplicação desktop para Windows que combina três tecnologias em um fluxo contínuo:

1. **Captura de áudio** — grave o som do sistema (loopback) ou carregue um arquivo existente
2. **Transcrição** — converte fala em texto usando o modelo Whisper `large-v3-turbo`, rodando 100% local
3. **Formatação inteligente** — envia a transcrição para a API Groq (LLaMA 3) e recebe de volta uma nota Markdown completa, com YAML frontmatter, resumo, seções hierárquicas, `[[wikilinks]]` e tags contextuais

O resultado pode ser salvo diretamente no **Obsidian**, **Logseq** ou **Notion**, ou exportado como `.txt`/`.md` para qualquer destino. A interface roda dentro do Chrome como uma mini-janela (750 × 780 px), sem instalador nem servidor externo.

---

## Interface

```
┌─────────────────────────────────────┐
│         🧠  Sinapse&IA              │
│  Fortaleça as conexões do seu       │
│        segundo cérebro              │
│                                     │
│  ┌─────────┐ ┌────────┐ ┌────────┐  │
│  │ Arquivo │ │ Gravar │ │ Texto  │  │
│  │  Audio  │ │ do PC  │ │ Colar  │  │
│  └─────────┘ └────────┘ └────────┘  │
│                                     │
│  [ Área de transcrição em tempo     │
│    real, segmento por segmento ]    │
│                                     │
│  [ Resultado formatado em Markdown ]│
│                                     │
│  ┌────────┐ ┌────────┐ ┌─────────┐  │
│  │Obsidian│ │Logseq  │ │ Notion  │  │
│  └────────┘ └────────┘ └─────────┘  │
└─────────────────────────────────────┘
```

A janela usa um tema escuro (deep navy) com acentos em azul e dourado. Cada etapa do fluxo — seleção, transcrição, formatação e salvamento — acontece na mesma tela, sem trocas de janela.

---

## Funcionalidades

### Entrada de conteúdo
- 🎙️ **Gravação loopback** — captura o áudio que está sendo reproduzido pelo PC (reuniões, aulas online, podcasts) sem necessidade de cabo ou mixer externo
- ⏸️ **Pausar e retomar** a gravação a qualquer momento
- 📁 **Importar arquivo** — suporte a `.mp3`, `.mp4`, `.m4a`, `.wav`, `.ogg`, `.mkv`
- 📄 **Legendas e texto** — importa `.srt`, `.vtt`, `.ass`, `.ssa`, `.sbv`, `.sub` e `.txt` com limpeza automática de timestamps e tags de formatação
- ✏️ **Texto direto** — cole qualquer texto e formate sem precisar transcrever

### Transcrição
- 🤖 **Whisper `large-v3-turbo`** rodando localmente via `faster-whisper` (quantização `int8`)
- 🌍 **Detecção automática de idioma** — funciona com português, inglês, espanhol e dezenas de outros idiomas
- 📡 **Progresso em tempo real** — cada segmento aparece na tela conforme é processado
- 🔤 **Tradução** — traduz a transcrição para pt, en, es, zh, hi, ar, fr, de, ja, ko, it ou ru via Groq

### Formatação com IA
- ✨ **Classificação automática** do tipo de conteúdo: aula, reunião, palestra, podcast ou texto
- 📝 **Nota Markdown completa** com YAML frontmatter (`date`, `type`, `tags`), título, resumo e seções hierárquicas (`##`, `###`)
- 🔗 **`[[wikilinks]]` inteligentes** para os conceitos mais relevantes do conteúdo
- 🏷️ **Tags contextuais** — lê as tags já existentes no vault/graph e prioriza reutilizá-las antes de criar novas
- 🗓️ **Revisão semanal** — gera automaticamente uma nota de síntese das últimas notas salvas, com conexões temáticas e insights

### Nome inteligente
- 🏷️ O arquivo recebe um nome gerado pela IA baseado no conteúdo (ex: `Marketing Digital - Módulo 2 - Aula 5 - Funis de Venda`)
- Leva em conta os nomes recentes para detectar sequências (ex: `Aula 1`, `Aula 2` → sugere `Aula 3`)

### Integrações
| Plataforma | Status | O que faz |
|---|---|---|
| **Obsidian** | ✅ Completo | Detecta vaults automaticamente; salva `.md` com criação de stubs para wikilinks |
| **Logseq** | ✅ Completo | Detecta graphs automaticamente; salva em `pages/` |
| **Notion** | ✅ Completo | Cria página via API com conversão Markdown → blocos Notion (paginação automática) |
| **Roam Research** | 🚧 Em breve | Placeholder ativo, implementação pendente |

### Histórico
- 📜 Mantém os últimos 50 arquivos salvos (nome, caminho/URL, tipo, data)
- Permite reabrir, editar ou excluir qualquer registro do histórico

---

## Requisitos

| Componente | Versão mínima | Observação |
|---|---|---|
| **Python** | 3.10+ | Testado com 3.11 e 3.12 |
| **Google Chrome** | qualquer recente | Usado como janela da interface (via Eel) |
| **Windows** | 10 ou 11 | `winsound` e `soundcard` são exclusivos para Windows |
| **RAM** | 4 GB+ | O modelo `large-v3-turbo` usa ~1,5 GB na primeira carga |
| **Chave API Groq** | gratuita | Obtida em [console.groq.com](https://console.groq.com) |

> **ffmpeg** não é necessário para os formatos nativamente suportados pelo `soundfile`. Para arquivos `.mkv` ou outros containers menos comuns, instale o ffmpeg e adicione ao PATH.

---

## Instalação

### 1. Clone ou baixe o projeto

```bash
git clone https://github.com/seu-usuario/sinapseia.git
cd sinapseia
```

Ou baixe o ZIP e extraia em uma pasta de sua escolha.

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

O `requirements.txt` contém:

```
Eel>=0.16
faster-whisper>=1.0
SoundCard>=0.4
soundfile>=0.12
numpy>=2.0
```

> Na primeira execução, o `faster-whisper` vai baixar o modelo `large-v3-turbo` (~800 MB). Isso acontece uma única vez e o modelo fica em cache local.

### 4. Execute

```bash
python app.py
```

O Chrome abrirá automaticamente com a interface do Sinapse&IA.

---

## Como usar

### Fluxo principal: áudio → nota no Obsidian

```
1. Clique em "Arquivo" e selecione um .mp3, .mp4, .wav etc.
   (ou arraste o arquivo para a área de drop)

2. Clique em "Transcrever"
   → Os segmentos aparecem em tempo real

3. Clique em "Formatar para Obsidian"
   → A IA gera a nota Markdown completa

4. (Opcional) Edite o conteúdo formatado diretamente na tela

5. Clique em "Salvar no Obsidian"
   → O arquivo .md é criado no seu vault com stubs para os wikilinks
```

### Fluxo: gravação do PC

```
1. Clique em "Gravar"
2. Selecione a fonte de áudio (dispositivo de saída do sistema)
3. Clique em "Iniciar gravação"
   → Inicie a aula/reunião/podcast no PC
4. Clique em "Parar"
   → O arquivo .wav é salvo na Área de Trabalho
5. Continue com o fluxo normal de transcrição e formatação
```

### Fluxo: colar texto direto

```
1. Clique em "Texto"
2. Cole seu texto na área de entrada
3. Clique em "Formatar"
   → Sem transcrição, vai direto para a formatação com IA
```

---

## Configuração

### API Key do Groq

1. Acesse [console.groq.com](https://console.groq.com) e crie uma conta gratuita
2. Gere uma API key no painel
3. Na primeira abertura do Sinapse&IA, uma tela de onboarding pedirá a key
4. Ou acesse o ícone de Configurações (engrenagem) a qualquer momento

A key é salva localmente em `~/.sinapseia_config.json`.

### Vault do Obsidian

Na tela de Configurações, o app escaneia automaticamente os seguintes locais em busca de pastas com `.obsidian/`:

- Desktop, Documentos, OneDrive, pasta home
- Drives D:, E:, F: (se existirem)

Selecione o vault desejado na lista ou navegue manualmente até a pasta.

### Graph do Logseq

Funciona da mesma forma: o app detecta pastas com subdiretório `logseq/` nos mesmos locais acima.

### Notion

Em Configurações → Notion:
1. Crie uma integração em [notion.so/my-integrations](https://www.notion.so/my-integrations) e copie o **Internal Integration Token**
2. Abra a página do Notion onde as notas serão criadas → clique em `...` → `Add connections` → selecione sua integração
3. Copie o **ID da página** (os 32 caracteres no final da URL)
4. Insira o token e o ID na tela de Configurações do app

---

## Modelos de IA

### Transcrição (local)

| Modelo | Tamanho | Dispositivo | Quantização |
|---|---|---|---|
| `faster-whisper/large-v3-turbo` | ~800 MB | CPU | int8 |

Roda completamente offline após o download inicial. Nenhum áudio é enviado para servidores externos.

### Formatação e nomeação (API Groq)

| Modelo principal | Fallback automático | Quando o fallback é ativado |
|---|---|---|
| `llama-3.3-70b-versatile` | `llama-3.1-8b-instant` | Limite diário de tokens do plano gratuito atingido |

O sistema tenta o modelo maior primeiro. Se receber erro `429` por limite diário (`tokens per day`), troca automaticamente para o modelo menor sem interromper o fluxo. Em caso de rate limit por minuto, faz retry com backoff exponencial (até 3 tentativas).

---

## Estrutura do projeto

```
sinapseia/
│
├── app.py                  # Ponto de entrada; expõe funções Python ao JavaScript via Eel
│
├── core/
│   ├── ai.py               # Integração com a API Groq (geração, tradução, prompts)
│   ├── config.py           # Leitura/escrita de ~/.sinapseia_config.json; validação Pro
│   ├── transcriber.py      # Whisper large-v3-turbo via faster-whisper; detecção de idioma
│   ├── recorder.py         # Gravação loopback via soundcard; VU meter em tempo real
│   ├── naming.py           # Geração de nome inteligente de arquivo via Groq
│   ├── storage.py          # Histórico local (~/.transcritor_historico.json)
│   └── wikilinks.py        # Extração de [[wikilinks]], criação de stubs, leitura de tags do vault
│
├── integrations/
│   ├── obsidian.py         # Detecção de vaults, formatação e salvamento de .md; stubs de wikilinks
│   ├── logseq.py           # Detecção de graphs, salvamento em pages/
│   ├── notion.py           # API Notion v1: criação de página, conversão MD→blocos, paginação
│   └── roam.py             # Placeholder (em desenvolvimento)
│
├── web/
│   ├── index.html          # Interface completa (HTML + Tailwind CSS + JS inline)
│   ├── logo.png            # Ícone do neurônio
│   └── favicon.ico
│
├── requirements.txt
└── README.md
```

---

## Armazenamento local

O app não usa banco de dados. Dois arquivos JSON são criados na pasta home do usuário (`C:\Users\<nome>\`):

| Arquivo | Conteúdo |
|---|---|
| `~/.sinapseia_config.json` | API key Groq, vault Obsidian, graph Logseq, token Notion, status Pro |
| `~/.transcritor_historico.json` | Últimas 50 entradas do histórico (nome, caminho, tipo, data) |

Nenhum dado é enviado a servidores terceiros, exceto:
- O **texto da transcrição** enviado à **API Groq** para formatação (sujeito à política de privacidade da Groq)
- A **chave de licença Pro** validada via endpoint próprio (`validar-sinapseia.clinicarenasce.workers.dev`)

---

## Versão Pro

O Sinapse&IA possui um plano Pro com funcionalidades adicionais. Para ativar:

1. Acesse Configurações → Pro
2. Insira sua chave no formato `SINAPSE-XXXX-XXXX-XXXX`
3. A validação é feita online em tempo real

---

## Licença

MIT License — veja abaixo.

```
MIT License

Copyright (c) 2025 Sinapse&IA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
