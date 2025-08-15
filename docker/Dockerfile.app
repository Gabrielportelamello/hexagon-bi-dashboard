# docker/Dockerfile.app
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# ODBC 18 para SQL Server + deps (modo compatível com Debian 12: sem apt-key)
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl gnupg ca-certificates apt-transport-https unixodbc unixodbc-dev g++ \
  && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
     | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
  && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
     > /etc/apt/sources.list.d/microsoft-prod.list \
  && apt-get update \
  && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código do app
COPY . .

# Entry: gera secrets.toml a partir de variáveis de ambiente e inicia Streamlit
RUN mkdir -p .streamlit && \
    printf '#!/bin/bash\nset -e\nmkdir -p /app/.streamlit\ncat > /app/.streamlit/secrets.toml <<EOF\n[mssql]\nserver = \"${MSSQL_SERVER}\"\ndatabase = \"${MSSQL_DATABASE}\"\nusername = \"${MSSQL_USERNAME}\"\npassword = \"${MSSQL_PASSWORD}\"\ndriver = \"ODBC Driver 18 for SQL Server\"\ntrust_server_certificate = \"yes\"\nEOF\nexec streamlit run app.py --server.port=8501 --server.address=0.0.0.0\n' \
    > /usr/local/bin/start-app.sh && chmod +x /usr/local/bin/start-app.sh

EXPOSE 8501
ENTRYPOINT ["/usr/local/bin/start-app.sh"]
