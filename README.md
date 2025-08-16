# Instruções para rodar o projeto

## 1 Clonar o repositório
git clone https://github.com/Gabrielportelamello/hexagon-bi-dashboard.git
cd hexagon-bi-dashboard

## 2 Baixar o arquivo .bak do AdventureWorks

### Windows PowerShell (recomendado):

Invoke-WebRequest `
  -Uri https://github.com/Microsoft/sql-server-samples/releases/download/adventureworks/AdventureWorks2022.bak `
  -OutFile .\backups\AdventureWorks2022.bak


### Windows CMD:

curl.exe -L -o backups\AdventureWorks2022.bak ^
  https://github.com/Microsoft/sql-server-samples/releases/download/adventureworks/AdventureWorks2022.bak


### Linux/macOS:

curl -L -o backups/AdventureWorks2022.bak \
  https://github.com/Microsoft/sql-server-samples/releases/download/adventureworks/AdventureWorks2022.bak

## 3️ Subir o container do SQL Server

### Windows (PowerShell/CMD):

docker compose -f docker\mssql-compose.yml up -d --build


### Linux/macOS:

docker compose -f docker/mssql-compose.yml up -d --build

## 4️ Copiar o .bak para dentro do container
docker cp .\backups\AdventureWorks2022.bak mssql2022:/var/opt/mssql/backups/



⚠ Importante: O nome mssql deve ser igual ao container_name configurado no docker-compose.yml.
Para confirmar, rode:

docker ps

## 5️ Restaurar o banco SalesDB

docker compose -f docker\mssql-compose.yml exec mssql /opt/mssql-tools18/bin/sqlcmd `
  -S localhost -U sa -P 'SenhaForte123' -C -Q "
RESTORE DATABASE [SalesDB]
FROM DISK = N'/var/opt/mssql/backups/AdventureWorks2022.bak'
WITH
    MOVE N'AdventureWorks2022'     TO N'/var/opt/mssql/data/SalesDB.mdf',
    MOVE N'AdventureWorks2022_log' TO N'/var/opt/mssql/data/SalesDB_log.ldf',
    REPLACE, RECOVERY, STATS = 5;"

## 6️ Conferir se o banco foi restaurado

docker compose -f docker\mssql-compose.yml exec mssql /opt/mssql-tools18/bin/sqlcmd `
  -S localhost -U sa -P 'SenhaForte123' -C -Q "SELECT name FROM sys.databases"


Você deve ver SalesDB na lista.

## 7️ Abrir o app no navegador

Depois que o banco estiver restaurado, acesse:

http://localhost:8501