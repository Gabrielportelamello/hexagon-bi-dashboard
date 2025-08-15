#!/bin/bash
set -e

echo "🧹 Limpando possíveis conflitos de repositório Microsoft..."
sudo rm -f /etc/apt/sources.list.d/mssql-release.list /etc/apt/sources.list.d/microsoft-prod.list || true
sudo rm -f /etc/apt/trusted.gpg.d/microsoft.gpg /etc/apt/trusted.gpg.d/packages.microsoft.gpg || true

echo "📦 Atualizando pacotes..."
sudo apt-get update

echo "📦 Instalando dependências do unixODBC..."
sudo apt-get install -y unixodbc unixodbc-dev g++

echo "🔑 Instalando chave Microsoft (gpg dearmor)..."
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/microsoft.gpg

echo "📝 Criando fonte do repositório Microsoft..."
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/microsoft.gpg] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" | sudo tee /etc/apt/sources.list.d/microsoft-prod.list

echo "📦 Atualizando pacotes (com repositório MS)..."
sudo apt-get update

echo "📦 Instalando driver ODBC 18..."
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18

echo "🐍 Criando ambiente virtual Python..."
python3 -m venv .venv

echo "📂 Ativando ambiente virtual..."
source .venv/bin/activate

echo "📦 Instalando dependências do Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup concluído! Ative depois com: source .venv/bin/activate"
