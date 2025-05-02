# main.py
from fastapi import FastAPI, Request
from automacao_retorno_obra_api import BootRetornoObra
import os

app = FastAPI()

@app.post("/run_ln")
async def run_script(request: Request):
    try:
        # Recebendo JSON com login/senha
        data = await request.json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"status": "erro", "mensagem": "Credenciais ausentes"}

        bot = BootRetornoObra(username, password)
        resultado = bot.automate_ln()

        return {"status": "sucesso", "message": resultado}

    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}
