#!/usr/bin/env bash

# Atualiza pacotes e instala dependências necessárias
apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    fonts-liberation \
    xdg-utils \
    chromium-driver \
    --no-install-recommends

# Instala o Chromium
apt-get install -y chromium

# Baixa a versão compatível do ChromeDriver com o Chromium
CHROMIUM_VERSION=$(chromium --version | grep -oP '\d+\.\d+\.\d+' | head -1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROMIUM_VERSION")
curl -s -o chromedriver_linux64.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip

# Adiciona o chromedriver ao PATH
export PATH=$PATH:/usr/local/bin

# Instala dependências Python
pip install --upgrade pip
pip install -r requirements.txt
