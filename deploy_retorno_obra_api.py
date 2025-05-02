import os
import time
import warnings
from io import BytesIO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import subprocess

# --- Configuração FastAPI
app = FastAPI(title="LN Automation API")

# Modelo para requisição (pode incluir credenciais, parâmetros etc.)
class LNRequest(BaseModel):
    username: str
    password: str

# --- Classe de automação Selenium (ajustada para headless e sem GUI)
class BootRetornoObra:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def wait_for_page_load(self, driver, timeout=30):
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

    def automate_ln(self):
        warnings.simplefilter("ignore")
        download_dir = os.path.expanduser("~/.fastapi_downloads")
        os.makedirs(download_dir, exist_ok=True)

        options = EdgeOptions()
        options.use_chromium = True
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
        }
        options.add_experimental_option("prefs", prefs)

        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)

        try:
            success = self.acessar_ln(driver)
            if not success:
                raise RuntimeError("Falha no login LN")
            
            # aqui você pode chamar outros métodos: Elemento_Dashboard, open_dashboard, etc.
            return {"status": "ok", "download_dir": download_dir}
        finally:
            driver.quit()

    def acessar_ln(self, driver, max_tentativas=5):
        url = "https://mingle-portal.inforcloudsuite.com/..."
        for attempt in range(max_tentativas):
            try:
                driver.get(url)
                self.wait_for_page_load(driver)
                campo_login = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                campo_senha = driver.find_element(By.ID, "pass")
                campo_login.send_keys(self.username)
                campo_senha.send_keys(self.password + Keys.ENTER)
                time.sleep(5)
                return True
            except Exception:
                time.sleep(2)
        return False





# --- Endpoint HTTP para disparar a automação
@app.post("/run_ln")
def run_ln(request: LNRequest):
    """
    Executa o processo de automação LN em modo headless.
    Exemplo de payload JSON:
      {"username": "igor...", "password": "senha"}
    """
    try:
        bot = BootRetornoObra(request.username, request.password)
        result = bot.automate_ln()
        return {"message": "Automação concluída", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Instruções de execução:
# Instale dependências: pip install fastapi uvicorn selenium webdriver-manager
# Rode: uvicorn deploy_selenium_api:app --host 0.0.0.0 --port 8000
# Chame via HTTP: POST http://<servidor>:8000/run_ln  com JSON {"username":"...","password":"..."}
