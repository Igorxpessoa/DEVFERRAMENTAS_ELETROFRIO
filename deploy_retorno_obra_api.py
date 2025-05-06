import logging
from fastapi import FastAPI
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deploy_retorno_obra_api")

class RunRequest(BaseModel):
    tipo: str

@app.get("/")
async def root():
    return {"status": "API Online"}

@app.post("/run_ln")
async def run_script(request: RunRequest):
    logger.info("[{}] Iniciando automação LN".format(time.strftime("%Y-%m-%d %H:%M:%S")))

    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.get("https://mingle-portal.inforcloudsuite.com/ELETROFRIO_PRD/a8841f8a-7964-4977-b108-14edbb6ddb4f")
        time.sleep(2)
        driver.quit()

        return {"status": "Concluído com sucesso"}

    except Exception as e:
        logger.error("[{}] Erro: {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), str(e)))
        return {"status": "Erro", "detalhes": str(e)}
