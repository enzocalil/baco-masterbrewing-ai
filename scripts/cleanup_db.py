import sqlite3
import os

DB_PATH = "data/brew_knowledge.db"

def cleanup_duplicates():
    if not os.path.exists(DB_PATH):
        print("Banco de dados não encontrado.")
        return

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            print("--- Limpando Tabela Recipes ---")
            # Deleta todos os registros que NÃO SÃO o MAX(id) para cada nome
            cursor.execute("""
                DELETE FROM recipes 
                WHERE id NOT IN (
                    SELECT MAX(id) 
                    FROM recipes 
                    GROUP BY name
                )
            """)
            print(f"Receitas removidas: {cursor.rowcount}")

            print("--- Limpando Tabela Image Knowledge ---")
            # Deleta todos os registros que NÃO SÃO o MAX(id) para cada image_name
            cursor.execute("""
                DELETE FROM image_knowledge 
                WHERE id NOT IN (
                    SELECT MAX(id) 
                    FROM image_knowledge 
                    GROUP BY image_name
                )
            """)
            print(f"Imagens removidas: {cursor.rowcount}")
            
            conn.commit()
            print("Limpeza concluída com sucesso.")

    except Exception as e:
        print(f"Erro durante a limpeza: {e}")

if __name__ == "__main__":
    cleanup_duplicates()
