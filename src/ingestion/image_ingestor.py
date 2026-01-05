import os
import base64
import logging
from groq import Groq
from dotenv import load_dotenv
from src.storage.database import BeerDatabase
from src.ingestion.pdf_handler import BeerDocReader
from src.agent.orchestrator import BrewerAgent

load_dotenv()
db = BeerDatabase()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
pdf_reader = BeerDocReader()
agent = BrewerAgent()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def universal_ingest(base_directory):
    img_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    
    for root, dirs, files in os.walk(base_directory):
        folder_context = os.path.basename(root)
        
        for filename in files:
            path = os.path.join(root, filename)
            
            # SE FOR IMAGEM
            if filename.lower().endswith(img_extensions):
                logger.info(f"📸 Estudando imagem: {filename} em {folder_context}")
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                
                res = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": f"Descreva tecnicamente esta imagem da pasta {folder_context}."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]}]
                )
                db.save_image_analysis(f"{folder_context}/{filename}", res.choices[0].message.content)

            # SE FOR PDF (PERGAMINHO)
            elif filename.lower().endswith('.pdf'):
                logger.info(f"📜 Lendo pergaminho: {filename} em {folder_context}")
                try:
                    markdown = pdf_reader.extract_recipe_data(path)
                    recipe = agent.parse_recipe_with_ai(markdown)
                    db.save_recipe(recipe)
                    # Também guarda uma nota no conhecimento de imagem para o RAG achar fácil
                    db.save_image_analysis(filename, f"Receita técnica de {recipe.name} encontrada na pasta {folder_context}")
                except Exception as e:
                    logger.error(f"Erro no PDF {filename}: {e}")

if __name__ == "__main__":
    caminho = "data/raw_images"
    print(f"🚀 Iniciando ingestão universal em: {caminho}")
    universal_ingest(caminho)
    print("✅ O Ancião terminou de estudar todas as pastas!")