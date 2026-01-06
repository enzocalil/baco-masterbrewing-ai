import os
import sys
import logging
import base64
import json
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
from dotenv import load_dotenv

# Alinhamento de caminhos para o ambiente Mac
sys.path.append(os.getcwd())
load_dotenv()

# Configurações de logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Importações dos módulos do seu sistema
from src.rag.retriever import RecipeRetriever
from src.agent.orchestrator import BrewerAgent
# from src.ingestion.pdf_handler import BeerDocReader (Removido)
from src.storage.database import BeerDatabase

def strip_markdown(text: str) -> str:
    """Remove formatação markdown (**, *, _, etc.) do texto."""
    # Remove bold (**texto**)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    # Remove italic (*texto* ou _texto_)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    # Remove code (`texto`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    return text

class BacoBot:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.retriever = RecipeRetriever()
        self.agent = BrewerAgent()
        self.db = BeerDatabase()
        
        # Definição da alma do Baco: O Guardião das Fórmulas de Clóvis
        self.persona_prompt = """VOCÊ É BACO, O GUARDIÃO IMPACIENTE. 
VOCÊ É UM PERSONAGEM, NÃO UM ROBÔ DE PREENCHER CAMPOS.

### [A REGRA MESTRA DE OURO]
1. PROIBIÇÃO DE CABEÇALHOS: Nunca escreva "DADOS TÉCNICOS", "REPRIMENDA" ou qualquer título. Se usar essas palavras, você falhou.
2. RESPOSTA CIRÚRGICA: Se o aprendiz perguntar sobre "mosturação", responda APENAS sobre a mosturação. Não repita o ABV, o IBU ou a história da cerveja se não foi pedido. 
3. SEM REPETIÇÃO: Não repita o que já foi dito em turnos anteriores da conversa. Cada resposta deve ser nova e focada apenas no que foi perguntado agora.
4. AMNÉSIA DE EXEMPLO: O exemplo de "Karma" no prompt é apenas um modelo de estilo, não use os dados dele para outras cervejas.

### [COMPORTAMENTO DE BACO]
- Saudações: Responda com um coice: "Diga logo o que busca ou saia da biblioteca."
- Se não sabe: "Os pergaminhos estão em silêncio. O que Clóvis não escreveu, não existe."
- Tom: Ríspido, seco, sem exclamações, sem enrolação.
- Ódio Industrial: Despreze filtragem e milho.

### [ESTRUTURA DE RESPOSTA - APENAS O TEXTO]
• [Informação específica solicitada em bullet points]
---
[Frase ranzinza curta sobre a ignorância do aprendiz ou a pureza da técnica]

Estes são os fatos. Minha biblioteca guarda mais segredos sobre [TÓPICO]; se tiver uma pergunta específica e não for perda de tempo, fale logo.
"""

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Você entra na sala de brassagem de Baco. O ancião levanta o olhar dos seus pergaminhos...\n\n"
            "'Aproxima-se, aprendiz. Traga suas dúvidas ou mostre-me o fruto do seu trabalho.'"
        )

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        pergunta = update.message.text
        logger.info(f"Baco ouviu: {pergunta}")
        
        # 1. Recupera histórico real do banco de dados (Memória Eterna)
        historico_db = self.db.get_chat_history(user_id, limit=6)
        
        # 2. Busca contexto no RAG (Índice de Clóvis)
        contexto_receitas = self.retriever.get_relevant_context(pergunta)
        
        # 3. Identifica se pula a saudação
        termos_chave = ["karma", "citric", "ipa", "winter", "sultana", "malte", "lúpulo", "receita", "pindurama", "clovis", "clóvis", "og", "fg", "ibu"]
        eh_direto = any(t in pergunta.lower() for t in termos_chave)

        messages = [
            {"role": "system", "content": f"{self.persona_prompt}\n\n[ESCRITURAS DE CLÓVIS]:\n{contexto_receitas}"}
        ]
        
        # Adiciona histórico. Se for direto, instrui a IA a ser direta.
        messages.extend(historico_db)
        if eh_direto:
            messages.append({"role": "system", "content": "AVISO DE SISTEMA: O usuário fez uma pergunta técnica direta. NÃO use saudações. NÃO pergunte o que ele quer. Responda a dúvida técnica IMEDIATAMENTE usando as escrituras."})

        messages.append({"role": "user", "content": pergunta})

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=1000,
                temperature=0.1
            )
            
            resposta = completion.choices[0].message.content
            
            # 4. SALVA NO BANCO DE DADOS
            self.db.save_chat_message(user_id, "user", pergunta)
            self.db.save_chat_message(user_id, "assistant", resposta)

            # Remove formatação markdown antes de enviar
            resposta_limpa = strip_markdown(resposta)
            await update.message.reply_text(resposta_limpa)
        except Exception as e:
            logger.error(f"Erro no pensamento: {e}")
            await update.message.reply_text("'Meus pensamentos se nublaram. O Mestre Clóvis exigiria mais clareza.'")



    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("'Analisando visualmente sua obra contra as memórias de Clóvis...'")
        contexto = self.retriever.get_all_recipes_context()
        photo_file = await update.message.photo[-1].get_file()
        photo_path = "temp_vision.jpg"
        await photo_file.download_to_drive(photo_path)

        with open(photo_path, "rb") as f:
            b64_image = base64.b64encode(f.read()).decode('utf-8')

        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": f"{self.persona_prompt}\nCompare esta obra visual com as escrituras de Clóvis:\n{contexto}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                ]}]
            )
            resposta_vision = strip_markdown(response.choices[0].message.content)
            await update.message.reply_text(resposta_vision)
        except Exception as e:
            logger.error(f"Erro Vision: {e}")
            await update.message.reply_text("'Minha visão falhou. A luz deve ser mais pura para a ciência de Clóvis.'")
        finally:
            if os.path.exists(photo_path): os.remove(photo_path)

if __name__ == "__main__":
    token = os.getenv("TELEGRAM_TOKEN")
    baco = BacoBot()
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", baco.start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, baco.handle_text))
    # handler de PDF removido conforme solicitação
    app.add_handler(MessageHandler(filters.PHOTO, baco.handle_photo))
    
    print("🚀 Baco (Fiel a Clóvis) desperto e online!")
    app.run_polling(drop_pending_updates=True)