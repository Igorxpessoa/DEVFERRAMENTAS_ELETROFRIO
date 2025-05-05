import os
import time
import warnings
from datetime import datetime
from fastapi import FastAPI, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

app = FastAPI(title="LN Automation API")

@app.get("/")
def read_root():
    return {"mensagem": "🚀 API de retorno da obra ativa com sucesso!"}

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

        download_dir = os.path.join(os.path.expanduser("~"), ".fastapi_downloads", self.username)
        os.makedirs(download_dir, exist_ok=True)

        options = ChromeOptions()
        options.use_chromium = True
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "directory_upgrade": True,
        }
        options.add_experimental_option("prefs", prefs)

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        try:
            success = self.acessar_ln(driver)
            if not success:
                raise RuntimeError("❌ Falha no login LN. Verifique usuário/senha ou disponibilidade da URL.")
            return {"status": "ok", "download_dir": download_dir}
        finally:
            driver.quit()

    def acessar_ln(self, driver, tentativas_acess_ln=0, max_tentativas_acess_ln=8):
        url = "https://mingle-portal.inforcloudsuite.com/ELETROFRIO_PRD/a8841f8a-7964-4977-b108-14edbb6ddb4f"

        while tentativas_acess_ln < max_tentativas_acess_ln:
            try:
                driver.get(url)
                time.sleep(2)

                campo_login = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                campo_senha = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "pass"))
                )
                campo_login.send_keys(self.username)
                campo_senha.send_keys(self.password)
                campo_senha.send_keys(Keys.ENTER)

                time.sleep(10)  # aguarda página carregar
                return True

            except WebDriverException as e:
                tentativas_acess_ln += 1
                print(f"⚠️ Tentativa {tentativas_acess_ln}/{max_tentativas_acess_ln} falhou: {str(e)}")
                time.sleep(5)

        print("❌ Número máximo de tentativas atingido. Não foi possível acessar o LN.")
        return False

@app.post("/run_ln")
def run_ln():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 🚀 Requisição recebida para executar o robô LN")

    try:
        username = os.environ.get("LN_USERNAME")
        password = os.environ.get("LN_PASSWORD")

        if not username or not password:
            print(f"[{timestamp}] ❌ Credenciais não encontradas")
            raise HTTPException(status_code=400, detail="Credenciais LN não configuradas nas variáveis de ambiente.")

        bot = BootRetornoObra(username, password)
        result = bot.automate_ln()

        print(f"[{timestamp}] ✅ Automação finalizada com sucesso!")
        return {"message": "Automação concluída com sucesso!", **result}

    except Exception as e:
        print(f"[{timestamp}] ❌ Erro durante a automação: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
