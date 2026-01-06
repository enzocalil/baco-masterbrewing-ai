#!/usr/bin/env python3
"""
Script para limpar formatação markdown das mensagens antigas no banco de dados.
Remove **, *, _, ` das mensagens do assistente no chat_memory.
"""

import sqlite3
import re

def strip_markdown(text: str) -> str:
    """Remove formatação markdown (**, *, _, etc.) do texto."""
    # Remove bold (**texto**)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    # Remove italic (*texto* ou _texto_)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    # Remove code (`texto`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    return text

def clean_chat_history(db_path="data/brew_knowledge.db"):
    """Remove markdown de todas as mensagens do assistente no histórico."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Busca todas as mensagens do assistente
    cursor.execute("SELECT id, content FROM chat_memory WHERE role = 'assistant'")
    messages = cursor.fetchall()
    
    print(f"🔍 Encontradas {len(messages)} mensagens do assistente para limpar")
    
    cleaned_count = 0
    for msg_id, content in messages:
        # Verifica se tem markdown
        if '**' in content or '*' in content or '_' in content or '`' in content:
            cleaned_content = strip_markdown(content)
            cursor.execute("UPDATE chat_memory SET content = ? WHERE id = ?", (cleaned_content, msg_id))
            cleaned_count += 1
            
            if cleaned_count <= 3:  # Mostra os primeiros 3 exemplos
                print(f"\n📝 Exemplo {cleaned_count}:")
                print(f"ANTES: {content[:150]}...")
                print(f"DEPOIS: {cleaned_content[:150]}...")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Limpeza concluída! {cleaned_count} mensagens foram atualizadas.")
    print(f"📊 {len(messages) - cleaned_count} mensagens já estavam limpas.")

if __name__ == "__main__":
    print("🧹 Iniciando limpeza de formatação markdown no histórico de chat...")
    clean_chat_history()
