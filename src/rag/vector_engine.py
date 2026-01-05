import faiss
import numpy as np
from typing import List

class BeerVectorStore:
    def __init__(self, dimension: int = 1536): # 1536 é o padrão da OpenAI
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata = []

    def add_recipe_to_index(self, recipe_id: int, sensory_text: str, embedding: List[float]):
        """Adiciona o vetor sensorial ao índice FAISS."""
        vector = np.array([embedding]).astype('float32')
        self.index.add(vector)
        self.metadata.append({"recipe_id": recipe_id, "text": sensory_text})
        print(f"🧠 Perfil sensorial indexado para busca semântica.")

    def search_similar(self, query_embedding: List[float], k: int = 3):
        """Busca as receitas mais próximas ao perfil desejado."""
        vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(vector, k)
        return [self.metadata[i] for i in indices[0] if i != -1]