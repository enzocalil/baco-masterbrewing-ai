import sys
import os
import time
import json
import subprocess
import urllib.request
import urllib.error

def test_api():
    print("🔹 Iniciando teste da API de Chat...")
    
    # Define o comando para rodar a API (via uvicorn)
    # Assume que o script é rodado da raiz do projeto
    cmd = [sys.executable, "-m", "uvicorn", "src.interface.api:app", "--port", "8000", "--log-level", "warning"]
    
    # Inicia o servidor em background
    print("⏳ Iniciando servidor Uvicorn...")
    server_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    try:
        # Aguarda o servidor subir
        server_ready = False
        for _ in range(10):  # Tenta por 10 segundos
            time.sleep(1)
            try:
                with urllib.request.urlopen("http://localhost:8000/health") as response:
                    if response.getcode() == 200:
                        server_ready = True
                        print("✅ Servidor Online!")
                        break
            except urllib.error.URLError:
                continue
        
        if not server_ready:
            print("❌ Erro: Servidor não ficou pronto a tempo.")
            return

        # Teste do Endpoint /chat
        print("📤 Enviando mensagem de teste: 'Qual a melhor temperatura para IPA?'")
        payload = {
            "user_id": "test_user_01",
            "message": "Qual a melhor temperatura para IPA?"
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request("http://localhost:8000/chat", data=data, headers={'Content-Type': 'application/json'})
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.load(response)
                print("\n📩 Resposta recebida:")
                print("-" * 30)
                print(result.get("response"))
                print("-" * 30)
                print("✅ Teste de Chat concluído com SUCESSO.")
        except urllib.error.HTTPError as e:
            print(f"❌ Erro na requisição de Chat: {e.code} - {e.read().decode()}")

    finally:
        # Garante que o servidor seja encerrado
        print("🛑 Encerrando servidor...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_api()
