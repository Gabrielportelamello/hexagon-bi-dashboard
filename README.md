Streamlit Sales Dashboard — AdventureWorks

Mini painel de vendas feito com Streamlit + Plotly + Pandas usando o banco AdventureWorks no SQL Server.
Permite filtrar por período, categoria e região, mostra KPIs e visualizações interativas (receita por dia/produto, nº de vendas por dia/categoria, receita por região e por mês), além de um detalhe tabular dos dados filtrados.

✅ O que foi entregue (critérios do teste)

Consulta SQL otimizada (queries.sql) juntando SalesOrderHeader/Detail, Product, Category, Address/Region.

Manipulação com Pandas (agregações, cálculo de YearMonth, filtros reativos).

Visualizações úteis (linhas, barras horizontais com scroll, área), em pt-BR.

Usabilidade: KPIs em “caixas”, seções colapsáveis, filtros práticos e responsivos.

Entrega: repositório com código-fonte + instruções claras para rodar.

Requisitos

Docker e Docker Compose

Python 3.11+ (para o app)

ODBC 18 para SQL Server (no host, se usar Linux/WSL):

sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc unixodbc-dev g++

Como rodar
1) Subir o SQL Server (Docker)
docker compose -f docker/mssql-compose.yml up -d


O compose já mapeia a pasta ./backups para /var/opt/mssql/backups dentro do container.

(Se precisar) Baixar o .BAK do AdventureWorks
curl -L -o backups/AdventureWorks2022.bak \
  https://github.com/Microsoft/sql-server-samples/releases/download/adventureworks/AdventureWorks2022.bak

2) Restaurar o .BAK no SQL Server

O repositório inclui o script docker/restore_bak.sql. Execute:

docker exec -it mssql2022 bash -lc "/opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P '<SUA_SENHA_SA>' -C \
  -i /var/opt/mssql/restore_bak.sql \
  || /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P '<SUA_SENHA_SA>' -i /var/opt/mssql/restore_bak.sql"


Importante: a senha do usuário sa é definida no docker/mssql-compose.yml (SA_PASSWORD). Substitua <SUA_SENHA_SA> pela que estiver no compose.

3) Preparar o ambiente Python
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt

4) Segredos do Streamlit

Crie o arquivo .streamlit/secrets.toml (ou copie o exemplo e edite a senha):

mkdir -p .streamlit
cat > .streamlit/secrets.toml << 'EOF'
[mssql]
server = "localhost,1433"
database = "salesDB"
username = "sa"
password = "<SUA_SENHA_SA>"
driver = "ODBC Driver 18 for SQL Server"
trust_server_certificate = "yes"
EOF


Não comite sua senha real. Use o modelo secrets.example.toml para compartilhar.

5) Rodar o app
streamlit run app.py


Acesse: http://localhost:8501

Estrutura do projeto
.
├─ app.py                   # App Streamlit (UI, gráficos, KPIs)
├─ db.py                    # Conexão com SQL Server (SQLAlchemy/pyodbc)
├─ queries.sql              # Consulta SQL principal (joins e filtros)
├─ requirements.txt         # Dependências Python
├─ README.md
├─ .streamlit/
│  ├─ secrets.toml          # (local, não versionar)
│  └─ secrets.example.toml  # modelo sem senha
└─ docker/
   ├─ mssql-compose.yml     # SQL Server + volumes
   └─ restore_bak.sql       # Script de restore do .bak


A pasta backups/ é mapeada no compose para o restore do .bak. Não suba .bak no Git.

Como usar o painel

Filtros: período inicial/final, seleção de categorias e regiões (ShipTo).

KPIs (em caixas):

Pedidos (qtde) → nº de pedidos distintos

Unidades vendidas → soma de quantidades

Receita (itens) → soma de UnitPrice * Qty * (1 - Discount)

Seções em “caixas”:

Visão geral (aberta por padrão)

Receita por dia (linha)

Receita por produto (barras horizontais com scroll)

Número de vendas (colapsada por padrão)

Nº de vendas por dia (linha)

Vendas por categoria (barras)

Análises adicionais (colapsada por padrão)

Receita por região (barras horizontais)

Receita por mês (área)

Tabela detalhada com colunas em pt-BR:
Categoria, Valor, Data do pedido, ID do produto, Produto,
Quantidade, Região, ID do pedido, Total faturado, Ano-Mês.

Decisões técnicas

SQL: queries.sql retorna as colunas necessárias para as análises (datas, valores, produto, categoria, região e IDs).

Pandas: agregações para séries (por dia, mês), rankings (produto, categoria, região) e KPIs.

Plotly:

Barras horizontais de produto com scroll (evita “estourar” a coluna).

Eixos e rótulos em pt-BR (formato R$ 1.234,56).

UX/Streamlit:

Sidebar colapsada ao iniciar (botão “☰ Filtros” exibe/esconde).

Seções colapsáveis para manter a página organizada.

KPIs em caixas para leitura rápida.

Problemas comuns

ODBC Driver ausente (Linux/WSL): instale com:

sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc unixodbc-dev g++


Senha incorreta do sa: confira docker/mssql-compose.yml e .streamlit/secrets.toml.

backups/AdventureWorks2022.bak não encontrado: baixe com o curl acima.

Scripts úteis

Se preferir automatizar, há um script setup_project.sh (Linux) que instala ODBC 18 e cria venv. Execute com:

chmod +x setup_project.sh
./setup_project.sh


Ajuste conforme seu ambiente; no Windows, use o PowerShell para a venv.

Licença

Projeto de demonstração para avaliação técnica.