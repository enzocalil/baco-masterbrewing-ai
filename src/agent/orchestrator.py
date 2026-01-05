import os
import json
import logging
from groq import Groq
from dotenv import load_dotenv
from src.storage.models import BeerRecipe

load_dotenv()
logger = logging.getLogger(__name__)

class BrewerAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def parse_recipe_with_ai(self, raw_text: str) -> BeerRecipe:
        """Converte texto do PDF em objeto estruturado com tratamento de erros robusto."""
        prompt = f"""
        Você é um especialista em extração de dados cervejeiros. 
        Extraia os dados técnicos desta receita e retorne APENAS um JSON válido.
        
        REGRAS CRÍTICAS:
        1. Se não encontrar um valor numérico (OG, FG, ABV, IBU), use null.
        2. Para ingredientes, se faltar 'amount', 'unit' ou 'step', preencha com null ou "N/A".
        3. O campo 'malts' e 'hops' devem ser sempre listas de objetos.
        4. Retorne apenas o JSON, sem explicações.

        Texto original:
        {raw_text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            
            # Tenta criar o objeto validado
            return BeerRecipe(**data)
            
        except Exception as e:
            logger.warning(f"⚠️ Falha na validação rigorosa. Aplicando modo de compatibilidade para o Ancião: {e}")
            
            # Plano B: Cria um objeto mínimo para não perder a informação do texto
            # Pega o nome do texto ou usa 'Receita Não Identificada'
            fallback_name = "Receita Recuperada"
            if 'data' in locals() and data.get("name"):
                fallback_name = data.get("name")
            
            return BeerRecipe(
                name=fallback_name,
                description=f"Nota técnica recuperada (Erro de validação: {str(e)}). Conteúdo original: {raw_text[:500]}..."
            )