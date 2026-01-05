import os
import sys
sys.path.append(os.getcwd())

from src.ingestion.pdf_handler import BeerDocReader
from src.agent.orchestrator import BrewerAgent
from src.domain.calculators import BrewMath
from src.storage.database import BeerDatabase
from src.rag.embedder import BeerEmbedder
from src.rag.vector_engine import BeerVectorStore

def main():
    print("\n🍺 MASTERBREW AI - PIPELINE COMPLETO 🍺\n")
    
    # Inicialização dos componentes
    reader = BeerDocReader()
    agent = BrewerAgent()
    db = BeerDatabase()
    embedder = BeerEmbedder()
    vector_store = BeerVectorStore(dimension=1536) # Dimensão do 'text-embedding-3-small'

    # 1. Ingestão (Busca o PDF)
    pdf_path = "data/pdfs/sua_receita.pdf" # <-- AJUSTE O NOME DO SEU PDF AQUI
    if not os.path.exists(pdf_path):
        print(f"❌ Coloque o PDF em {pdf_path}")
        return

    # 2. Parsing com IA
    markdown_text = reader.extract_recipe_data(pdf_path)
    recipe = agent.parse_recipe_with_ai(markdown_text)
    print(f"✅ IA extraiu a receita: {recipe.name} ({recipe.style})")

    # 3. Validação de Domínio
    if BrewMath.is_plausible(recipe):
        print(f"✔️ Validação Técnica: OK (ABV: {recipe.abv}%)")
        
        # 4. Salvando no Banco SQL
        db.save_recipe(recipe)
        
        # 5. Indexando no RAG (Busca Semântica)
        sensory_text = ", ".join(recipe.sensory_profile)
        vector = embedder.get_embedding(sensory_text)
        vector_store.add_recipe_to_index(recipe_id=1, sensory_text=sensory_text, embedding=vector)
        
        print("\n🚀 PROCESSO FINALIZADO: Dados estruturados e prontos para consulta!")
    else:
        print("⚠️ Alerta: A IA extraiu dados que não batem matematicamente.")

if __name__ == "__main__":
    main()