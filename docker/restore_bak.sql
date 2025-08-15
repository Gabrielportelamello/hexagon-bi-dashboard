/* 1) Conferir nomes lógicos do backup */
RESTORE FILELISTONLY 
FROM DISK = N'/var/opt/mssql/backups/AdventureWorks2022.bak';
GO

/* 2) Restaurar o banco com novos nomes físicos */
USE master;
GO

IF DB_ID(N'SalesDB') IS NOT NULL
BEGIN
    ALTER DATABASE [SalesDB] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE [SalesDB];
END
GO

RESTORE DATABASE [SalesDB]
FROM DISK = N'/var/opt/mssql/backups/AdventureWorks2022.bak'
WITH 
    MOVE N'AdventureWorks2022'     TO N'/var/opt/mssql/data/SalesDB.mdf',
    MOVE N'AdventureWorks2022_log' TO N'/var/opt/mssql/log/SalesDB_log.ldf',
    REPLACE, RECOVERY, STATS = 5;
GO
