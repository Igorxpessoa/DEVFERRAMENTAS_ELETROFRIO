from fastapi import FastAPI
from fastapi.responses import JSONResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

app = FastAPI()

class RetornoObraAutomatizado:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        # Usa ChromeDriverManager para obter o driver atualizado
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    def login(self, username, password):
        self.driver.get("https://www.ln.com.br/portal/login")
        time.sleep(2)

        self.driver.find_element(By.ID, "usuario").send_keys(username)
        self.driver.find_element(By.ID, "senha").send_keys(password)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(3)

    def close(self):
        self.driver.quit()

@app.get("/")
async def root():
    return {"status": "API online"}

@app.get("/login")
async def executar_login():
    username = os.environ.get("LN_USERNAME")
    password = os.environ.get("LN_PASSWORD")

    if not username or not password:
        return JSONResponse(content={"error": "Credenciais não configuradas corretamente."}, status_code=500)

    try:
        app_bot = RetornoObraAutomatizado()
        app_bot.login(username, password)
        app_bot.close()
        return {"status": "Login executado com sucesso."}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
