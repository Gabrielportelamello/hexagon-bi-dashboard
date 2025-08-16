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

git clone https://github.com/seuuser/streamlit_dashboard.git
cd streamlit_dashboard
docker compose -f docker/mssql-compose.yml up -d --build


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


