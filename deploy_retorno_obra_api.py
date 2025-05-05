import os
import time
import warnings
from io import BytesIO
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env, se existir
load_dotenv()

# --- Inicializa FastAPI
app = FastAPI(title="LN Automation API")

# ✅ Rota raiz para evitar erro 404
@app.get("/")
def read_root():
    return {"mensagem": "🚀 API de retorno da obra ativa com sucesso!"}

# --- Classe de automação com Selenium
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
        
        options.binary_location = "/usr/bin/chromium"  # ou "/usr/bin/google-chrome" se estiver usando o .deb
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)


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

    def acessar_ln(self,driver,tentativas_acess_ln=0,max_tentativas_acess_ln=8):

        try:
        
            driver.get("https://mingle-portal.inforcloudsuite.com/ELETROFRIO_PRD/a8841f8a-7964-4977-b108-14edbb6ddb4f")

        except WebDriverException as e:
            driver.quit()
            self.atualizacao.destroy()
            print("Informação", "Erro ao acessar a página. Verifique sua conexão com a internet e tente novamente.")


        while tentativas_acess_ln < max_tentativas_acess_ln:

              
            try:
                time.sleep(2)
                campo_login = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "username")))
                campo_senha = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "pass")))
                campo_login.send_keys(self.username)
                campo_senha.send_keys(self.password)
                campo_senha.send_keys(Keys.ENTER)
                time.sleep(10) 
                return True
        
            except WebDriverException as e:
                tentativas_acess_ln += 1
                print("Tentando logar no LN. Tentativa {}/{}".format(tentativas_acess_ln, max_tentativas_acess_ln))
                driver.get("https://mingle-portal.inforcloudsuite.com/ELETROFRIO_PRD/a8841f8a-7964-4977-b108-14edbb6ddb4f")
                time.sleep(5)

        print("Número máximo de tentativas atingido.Não foi possivel acessar a pagina do LN")
        driver.quit()
        print("Informação", "Não foi possivel acessar a page do LN. Verifique sua conexão e tente novamente mais tarde!")
        return False

# --- Endpoint para disparar automação
@app.post("/run_ln")
def run_ln():
    """
    Executa o robô de retorno de obra no LN.
    Usa credenciais das variáveis de ambiente:
    USERNAME e PASSWORD.
    """
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
        return {"message": "Automação concluída", **result}

    except Exception as e:
        print(f"[{timestamp}] ❌ Erro durante a automação: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
