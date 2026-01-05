from openai import OpenAI
import os

class BeerEmbedder:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_embedding(self, text: str):
        """Gera o vetor numérico para o texto sensorial."""
        text = text.replace("\n", " ")
        return self.client.embeddings.create(
            input=[text], 
            model="text-embedding-3-small"
        ).data[0].embedding