import os
import sys
from groq import Groq
from dotenv import load_dotenv

# Garante que o Python encontre os módulos locais no Mac
sys.path.append(os.getcwd())

from src.rag.retriever import RecipeRetriever

load_dotenv()

def chat():
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    retriever = RecipeRetriever()
    
    print("\n🍺 MESTRE CERVEJEIRO (INTERFACE GROQ) 🍺")
    print("Digite 'sair' para encerrar.\n")

    while True:
        user_input = input("Você: ")
        if user_input.lower() in ["sair", "exit"]: break

        context = retriever.get_all_recipes_context()
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Você é um Mestre Cervejeiro. Contexto do usuário: {context}"},
                {"role": "user", "content": user_input}
            ]
        )
        print(f"\nMestre: {response.choices[0].message.content}\n")

if __name__ == "__main__":
    chat()