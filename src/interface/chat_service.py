import os
import logging
import re
import json
from typing import List, Dict, Optional
from groq import Groq
from dotenv import load_dotenv

# Import domain components
from src.rag.retriever import RecipeRetriever
from src.agent.orchestrator import BrewerAgent
from src.storage.database import BeerDatabase

load_dotenv()
logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.retriever = RecipeRetriever()
        self.agent = BrewerAgent()
        self.db = BeerDatabase()
        
        # Persona: O Guardião das Fórmulas de Clóvis
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

    def _strip_markdown(self, text: str) -> str:
        """Remove formatação markdown (**, *, _, etc.) do texto."""
        # Remove bold (**texto**)
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        # Remove italic (*texto* ou _texto_)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        # Remove code (`texto`)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        return text

    def get_response(self, user_id: str, message: str) -> str:
        """Processa uma mensagem do usuário e retorna a resposta do Baco."""
        logger.info(f"Baco (API) ouviu de {user_id}: {message}")
        
        # 1. Recupera histórico real do banco de dados
        # Nota: O user_id no Telegram é int, mas aqui trataremos como str para flexibilidade
        historico_db = self.db.get_chat_history(user_id, limit=6)
        
        # 2. Busca contexto no RAG
        contexto_receitas = self.retriever.get_relevant_context(message)
        
        # 3. Identifica se pula a saudação (lógica 'eh_direto')
        termos_chave = ["karma", "citric", "ipa", "winter", "sultana", "malte", "lúpulo", "receita", "pindurama", "clovis", "clóvis", "og", "fg", "ibu"]
        eh_direto = any(t in message.lower() for t in termos_chave)

        messages = [
            {"role": "system", "content": f"{self.persona_prompt}\n\n[ESCRITURAS DE CLÓVIS]:\n{contexto_receitas}"}
        ]
        
        # Adiciona histórico
        messages.extend(historico_db)
        
        if eh_direto:
            messages.append({"role": "system", "content": "AVISO DE SISTEMA: O usuário fez uma pergunta técnica direta. NÃO use saudações. NÃO pergunte o que ele quer. Responda a dúvida técnica IMEDIATAMENTE usando as escrituras."})

        messages.append({"role": "user", "content": message})

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=1000,
                temperature=0.1
            )
            
            resposta = completion.choices[0].message.content
            
            # 4. Salva no Banco de Dados
            self.db.save_chat_message(user_id, "user", message)
            self.db.save_chat_message(user_id, "assistant", resposta)

            # Limpa e retorna
            return self._strip_markdown(resposta)

        except Exception as e:
            logger.error(f"Erro no pensamento do Baco: {e}")
            return "Meus pensamentos se nublaram. O Mestre Clóvis exigiria mais clareza. (Erro interno)"
