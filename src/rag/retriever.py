import sqlite3
import json
import os
import re

class RecipeRetriever:
    def __init__(self, db_path="data/brew_knowledge.db"):
        self.db_path = db_path

    def get_relevant_context(self, query: str) -> str:
        """Busca o conhecimento nas escrituras de Clóvis sem perder detalhes técnicos."""
        if not os.path.exists(self.db_path):
            return "As escrituras estão em branco, nenhum conhecimento foi catalogado por Clóvis."

        # Extrai palavras-chave para busca (Ignora palavras muito curtas)
        keywords = [word for word in query.split() if len(word) > 2]
        query_lower = query.lower()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                results = []

                # --- 1. LÓGICA DE ÍNDICE (Para listar nomes) ---
                if any(k in query_lower for k in ["lista", "todas", "quais", "quais receitas", "inventário"]):
                    cursor.execute("SELECT DISTINCT name FROM recipes")
                    db_names = {row[0].strip() for row in cursor.fetchall() if row[0]}
                    
                    cursor.execute("SELECT DISTINCT image_name FROM image_knowledge")
                    file_names = {row[0] for row in cursor.fetchall() if row[0]}
                    
                    # Logic to clean filenames preserving complexity
                    # e.g. "Grã Pindurama foto.pdf" -> "Grã Pindurama"
                    cleaned_files = set()
                    for fn in file_names:
                        # Remove extension
                        name = fn.rsplit('.', 1)[0]
                        # Remove common suffixes usually present (case insensitive)
                        name = re.sub(r'\s+(foto|receita|pergaminho|doc|pdf)$', '', name, flags=re.IGNORECASE).strip()
                        cleaned_files.add(name)
                    
                    # Merge sets
                    final_set = db_names.union(cleaned_files)
                    
                    # Intelligent Dedup (Merge "IPA" and "Ipa")
                    deduped_map = {}
                    for name in final_set:
                        key = name.lower()
                        if key not in deduped_map:
                            deduped_map[key] = name
                        else:
                            # Keep the one with more capital letters (e.g. IPA > Ipa)
                            curr = deduped_map[key]
                            if sum(1 for c in name if c.isupper()) > sum(1 for c in curr if c.isupper()):
                                deduped_map[key] = name
                    
                    final_list = sorted(deduped_map.values())
                    
                    summary = "=== ESCRITURAS DE CLÓVIS: LISTA COMPLETA E EXAUSTIVA ===\n"
                    summary += f"Total de receitas catalogadas: {len(final_list)}\n\n"
                    summary += "RECEITAS EXISTENTES (NÃO INVENTE OUTRAS):\n"
                    for i, recipe in enumerate(final_list, 1):
                        summary += f"{i}. {recipe}\n"
                    summary += "\n⚠️ ESTA É A LISTA COMPLETA. NÃO EXISTEM OUTRAS RECEITAS.\n"
                    results.append(summary)

                # --- 2. BUSCA DE CONTEÚDO (Para ler maltes/lúpulos) ---
                # Se o usuário perguntou por algo específico ou se pediu 'todas', 
                # buscamos o CONTEÚDO real dos registros.
                search_terms = keywords if keywords else ["%"] # Fallback para trazer algo se query for vazia
                
                seen_content = set() # Avoid identical content blocks

                for word in search_terms:
                    # Limpa a palavra para a busca SQL
                    clean_word = f"%{word.replace(',', '').replace('.', '')}%"

                    # Busca em 'image_knowledge'
                    cursor.execute("""
                        SELECT DISTINCT image_name, description FROM image_knowledge 
                        WHERE description LIKE ? OR image_name LIKE ?
                    """, (clean_word, clean_word))
                    for row in cursor.fetchall():
                        # Use hash of content to dedup
                        content_hash = hash(row[1])
                        if content_hash not in seen_content:
                            entry = f"REGISTRO DE CLÓVIS [{row[0]}]:\n{row[1]}"
                            results.append(entry)
                            seen_content.add(content_hash)
                    
                    # Busca em 'recipes'
                    cursor.execute("SELECT DISTINCT name, full_data FROM recipes WHERE name LIKE ?", (clean_word,))
                    for row in cursor.fetchall():
                        content_hash = hash(row[1])
                        if content_hash not in seen_content:
                            entry = f"RECEITA ESTRUTURADA [{row[0]}]:\n{row[1]}"
                            results.append(entry)
                            seen_content.add(content_hash)

                if not results:
                    return "Não encontrei detalhes específicos para sua dúvida nas notas de Clóvis."
                
                # Retorna os resultados (limite de 50 para aproveitar seus 500k de tokens)
                return "\n\n".join(results[:50])
                
        except Exception as e:
            return f"Erro ao consultar as memórias: {e}"

    def get_all_recipes_context(self) -> str:
        """Dump geral de todas as receitas."""
        return self.get_relevant_context("todas as receitas")