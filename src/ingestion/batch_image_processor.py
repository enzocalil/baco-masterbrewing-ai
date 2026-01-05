import os
import zipfile
import base64
import logging
from groq import Groq
from dotenv import load_dotenv
from src.storage.database import BeerDatabase

load_dotenv()
db = BeerDatabase()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

logging.basicConfig(level=logging.INFO)

def process_zip_images(zip_path):
    extract_to = "data/temp_extraction"
    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(root, file)
                print(f"🧐 Ancião analisando: {file}...")
                
                with open(img_path, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode('utf-8')

                try:
                    # O Ancião descreve a foto para a memória RAG
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Descreva tecnicamente esta imagem de cerveja ou processo para um banco de dados. Foco em cor, insumos visíveis e equipamentos."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}}
                            ]
                        }]
                    )
                    descricao = response.choices[0].message.content
                    
                    # Salvamos como uma "Receita Visual" ou Nota Técnica
                    # (Aqui adaptamos para salvar no seu banco de dados existente)
                    print(f"✅ Descrição salva: {descricao[:50]}...")
                    # db.save_image_context(file, descricao) <-- Criaríamos essa função no database.py
                except Exception as e:
                    print(f"❌ Erro ao analisar {file}: {e}")

if __name__ == "__main__":
    # Coloque o caminho do seu Thoth.zip aqui
    process_zip_images("caminho/para/seu/Thoth.zip")