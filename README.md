# Masterbrew AI - Baco Bot

This is the official repository for **Masterbrew AI**, home of **Baco**, a grumpy (but wise) guardian of brewing formulas.

The system uses **RAG (Retrieval-Augmented Generation)** to answer technical questions about beer production by consulting a knowledge base of recipes ("The Scriptures of Clóvis").

## Technologies

- **Python 3.10+**
- **LangChain / RAG Logic** (Custom implementation)
- **Groq API** (Llama 3.1 8B Instant & Llama 3.2 11B Vision) for fast inference.
- **OpenAI API** (Text Embedding 3 Small) for embeddings.
- **Telegram Bot API** for the user interface.
- **SQLite** for history and recipe storage.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/masterbrew_ai.git
   cd masterbrew_ai
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy the example file:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file and add your API keys:
     - `GROQ_API_KEY`: Groq Cloud API Key.
     - `OPENAI_API_KEY`: OpenAI API Key.
     - `TELEGRAM_TOKEN`: Your Telegram bot token (obtained via BotFather).

## Usage

To start the bot:

```bash
python src/interface/telegram_bot.py
```

## Project Structure

- `src/agent/`: Agent logic and orchestration.
- `src/ingestion/`: Data ingestion scripts (PDFs, Images).
- `src/interface/`: User interfaces (Telegram, CLI).
- `src/rag/`: RAG modules (Embedder, Retriever).
- `src/storage/`: Models and Database connection.
- `data/`: Local storage (SQLite, indexes).

## Contribution

Feel free to submit Pull Requests or open Issues.
