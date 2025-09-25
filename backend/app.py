"""
Ponto de entrada principal da aplicação FastAPI.

Este módulo importa e executa a aplicação FastAPI definida no pacote app.
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    # Inicia o servidor Uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
