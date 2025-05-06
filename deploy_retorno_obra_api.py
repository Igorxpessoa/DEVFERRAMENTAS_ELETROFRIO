import os
import time
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis de ambiente
load_dotenv()

# Inicializa API
app = FastAPI(title="LN Automation API")

@app.get("/")
def read_root():
    return {"mensagem": "🚀 API de retorno da obra ativa com sucesso!"}

class BootRetornoObra:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def automate_ln(self):
        download_dir = "/tmp/ln_download"
        os.makedirs(download_dir, exist_ok=True)

        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--remote-debugging-port=9222")

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
        }
        options.add_experimental_option("prefs", prefs)

        service = ChromeService(executable_path="/usr/local/bin/chromedriver")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        try:
            success = self.acessar_ln(driver)
            if not success:
                raise RuntimeError("❌ Falha no login LN.")
            return {"status": "ok", "download_dir": download_dir}
        finally:
            driver.quit()

    def acessar_ln(self, driver, tentativas=0, max_tentativas=8):
        url = "https://mingle-portal.inforcloudsuite.com/ELETROFRIO_PRD/a8841f8a-7964-4977-b108-14edbb6ddb4f"
        while tentativas < max_tentativas:
            try:
                driver.get(url)
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(self.username)
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "pass"))).send_keys(self.password + Keys.ENTER)
                time.sleep(10)
                return True
            except WebDriverException:
                tentativas += 1
                logger.warning(f"Tentativa {tentativas}/{max_tentativas} de login LN")
                time.sleep(5)
        logger.error("❌ Não foi possível acessar o LN após várias tentativas.")
        return False

@app.post("/run_ln")
def run_ln():
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{timestamp}] Iniciando automação LN")

    try:
        username = os.getenv("LN_USERNAME")
        password = os.getenv("LN_PASSWORD")

        if not username or not password:
            raise HTTPException(status_code=400, detail="Credenciais não configuradas.")

        bot = BootRetornoObra(username, password)
        result = bot.automate_ln()

        logger.info(f"[{timestamp}] Automação concluída.")
        return {"message": "Automação concluída com sucesso!", **result}
    except Exception as e:
        logger.error(f"[{timestamp}] Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))
