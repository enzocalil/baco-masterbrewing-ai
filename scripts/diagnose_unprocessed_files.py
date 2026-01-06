#!/usr/bin/env python3
"""
Script para diagnosticar quais arquivos em raw_images não estão sendo processados.
Mostra todos os arquivos encontrados e indica quais seriam ignorados pelo ingestor atual.
"""

import os
from pathlib import Path

def diagnose_raw_images(base_directory="data/raw_images"):
    """Analisa todos os arquivos e mostra quais não seriam processados."""
    
    # Extensões que o ingestor atual processa
    img_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    pdf_extensions = ('.pdf',)
    
    processed_files = []
    skipped_files = []
    
    print("=" * 80)
    print("🔍 DIAGNÓSTICO DE ARQUIVOS EM raw_images")
    print("=" * 80)
    
    for root, dirs, files in os.walk(base_directory):
        folder_name = os.path.basename(root)
        
        if files:
            print(f"\n📁 Pasta: {folder_name}")
            print("-" * 80)
            
            for filename in files:
                filepath = os.path.join(root, filename)
                file_lower = filename.lower()
                
                # Verifica se seria processado
                if file_lower.endswith(img_extensions):
                    status = "✅ IMAGEM (processada)"
                    processed_files.append(filepath)
                elif file_lower.endswith(pdf_extensions):
                    # PDFs são processados, mas vamos categorizar por nome
                    if 'foto' in file_lower or 'photo' in file_lower:
                        status = "📸 PDF FOTO (processado como receita, não como imagem)"
                    elif 'pergaminho' in file_lower:
                        status = "📜 PDF PERGAMINHO (processado)"
                    elif 'receita' in file_lower:
                        status = "📋 PDF RECEITA (processado)"
                    else:
                        status = "📄 PDF GENÉRICO (processado)"
                    processed_files.append(filepath)
                elif file_lower == '.ds_store':
                    status = "🗑️  ARQUIVO SISTEMA (ignorado)"
                    continue  # Não conta como skipped
                else:
                    status = "❌ NÃO PROCESSADO"
                    skipped_files.append(filepath)
                
                # Mostra tamanho do arquivo
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"  {status:50} | {filename:40} | {size_mb:6.2f} MB")
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📊 RESUMO")
    print("=" * 80)
    print(f"Total de arquivos processados: {len(processed_files)}")
    print(f"Total de arquivos NÃO processados: {len(skipped_files)}")
    
    if skipped_files:
        print("\n⚠️  ARQUIVOS QUE NÃO SERÃO PROCESSADOS:")
        for f in skipped_files:
            print(f"  - {f}")
    
    # Problema específico: PDFs de fotos
    print("\n" + "=" * 80)
    print("🔧 PROBLEMA IDENTIFICADO")
    print("=" * 80)
    print("Os arquivos 'foto.pdf' são PDFs contendo imagens, mas o ingestor atual")
    print("os trata como receitas (extrai texto), não como imagens para análise visual.")
    print("\nSOLUÇÃO: Atualizar image_ingestor.py para:")
    print("  1. Detectar PDFs com 'foto' no nome")
    print("  2. Extrair imagens do PDF")
    print("  3. Enviar para análise visual com Groq Vision")
    
    return processed_files, skipped_files

if __name__ == "__main__":
    diagnose_raw_images()
