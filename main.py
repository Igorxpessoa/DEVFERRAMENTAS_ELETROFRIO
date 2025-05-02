from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.post("/run_ln")
def run_script():
    try:
        # Executa o script como subprocesso
        subprocess.run(["python", "automacao_retorno_obra_api.py"], check=True)
        return {"status": "Script executado com sucesso!"}
    except subprocess.CalledProcessError as e:
        return {"status": "Erro ao executar o script", "detalhes": str(e)}
