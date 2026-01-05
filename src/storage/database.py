import sqlite3
import json
import os
from src.storage.models import BeerRecipe

class BeerDatabase:
    def __init__(self, db_path="data/brew_knowledge.db"):
        self.db_path = db_path
        # Garante que a pasta data exista
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Conexão segura para multi-threading com o Telegram
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Cria as escrituras (tabelas) necessárias para o conhecimento do Baco."""
        # Tabela de Receitas Técnicas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                style TEXT,
                abv REAL,
                ibu INTEGER,
                og REAL,
                fg REAL,
                full_data TEXT
            )
        """)
        
        # Tabela de Conhecimento Visual (RAG de Imagens)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_name TEXT,
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # NOVO: Tabela de Memória de Longo Prazo por Usuário
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def save_recipe(self, recipe: BeerRecipe):
        """Salva uma receita técnica no banco de dados."""
        recipe_dict = recipe.model_dump()
        self.cursor.execute("""
            INSERT INTO recipes (name, style, abv, ibu, og, fg, full_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            recipe.name,
            recipe.style,
            recipe.abv,
            recipe.ibu,
            recipe.target_og,
            recipe.target_fg,
            json.dumps(recipe_dict)
        ))
        self.conn.commit()

    def save_image_analysis(self, image_name: str, description: str):
        """Guarda a análise visual extraída pelo Ancião."""
        self.cursor.execute("""
            INSERT INTO image_knowledge (image_name, description)
            VALUES (?, ?)
        """, (image_name, description))
        self.conn.commit()

    def save_chat_message(self, user_id, role, content):
        """Registra a conversa para que o Baco nunca esqueça."""
        self.cursor.execute(
            "INSERT INTO chat_memory (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        self.conn.commit()

    def get_chat_history(self, user_id, limit=6):
        """Busca as últimas mensagens para dar contexto ao Ancião."""
        self.cursor.execute("""
            SELECT role, content FROM chat_memory 
            WHERE user_id = ? 
            ORDER BY timestamp DESC LIMIT ?
        """, (user_id, limit))
        rows = self.cursor.fetchall()
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

    def get_all_recipes(self):
        self.cursor.execute("SELECT full_data FROM recipes")
        rows = self.cursor.fetchall()
        return [json.loads(row[0]) for row in rows]

    def close(self):
        self.conn.close()