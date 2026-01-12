# Masterbrew AI - Baco Bot

Este é o repositório oficial do **Masterbrew AI**, lar do bot **Baco**, um guardião ranzinza (mas sábio) das fórmulas cervejeiras.

O sistema utiliza RAG (Retrieval-Augmented Generation) para responder dúvidas técnicas sobre produção de cerveja, consultando uma base de conhecimento de receitas ("Escrituras de Clóvis").

## Tecnologias

- **Python 3.10+**
- **LangChain / RAG Logic** (Custom implementation)
- **Groq API** (Llama 3.1 8B Instant & Llama 3.2 11B Vision) para inferência rápida.
- **OpenAI API** (Text Embedding 3 Small) para embeddings.
- **Telegram Bot API** para interface com usuário.
- **SQLite** para armazenamento de histórico e receitas.

## Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/masterbrew_ai.git
   cd masterbrew_ai
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   - Copie o arquivo de exemplo:
     ```bash
     cp .env.example .env
     ```
   - Edite o arquivo `.env` e adicione suas chaves de API:
     - `GROQ_API_KEY`: Chave da Groq Cloud.
     - `OPENAI_API_KEY`: Chave da OpenAI.
     - `TELEGRAM_TOKEN`: Token do seu bot no Telegram (obtido via BotFather).

## Execução

Para iniciar o bot:

```bash
python src/interface/telegram_bot.py
```

## Estrutura do Projeto

- `src/agent/`: Lógica do agente e orquestração.
- `src/ingestion/`: Scripts para ingestão de dados (PDFs, Imagens).
- `src/interface/`: Interfaces de usuário (Telegram, CLI).
- `src/rag/`: Módulos de RAG (Embedder, Retriever).
- `src/storage/`: Modelos e conexão com Banco de Dados.
- `data/`: Armazenamento local (SQLite, índices).

## Contribuição

Sinta-se livre para enviar Pull Requests ou abrir Issues.
