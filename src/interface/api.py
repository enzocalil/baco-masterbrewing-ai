from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.interface.chat_service import ChatService
import logging

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MasterBrew AI Chat API", description="API para conversar com o Baco", version="1.0.0")

# Instancia o serviço (Singleton simples para este caso de uso)
try:
    chat_service = ChatService()
    logger.info("ChatService inicializado com sucesso.")
except Exception as e:
    logger.error(f"Erro ao inicializar ChatService: {e}")
    chat_service = None

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/health")
async def health_check():
    if chat_service:
        return {"status": "ok", "service": "ready"}
    return {"status": "error", "service": "unavailable"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not chat_service:
        raise HTTPException(status_code=503, detail="Chat service not available")
    
    try:
        response_text = chat_service.get_response(request.user_id, request.message)
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Erro no processamento da requisição: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
