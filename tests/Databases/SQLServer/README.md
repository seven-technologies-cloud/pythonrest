To test this database, run the command below on the docker-compose.yml file:
```
docker-compose up
```
This pattern of message appears on the terminal when the database is ready to accept connections and run the creation of the tables:
```
2024-07-25 17:35:05.68 spid26s     Recovery is complete. This 
is an informational message only. No user action is required. 
2024-07-25 17:35:05.70 spid35s     The default language (LCID 
0) has been set for engine and full-text services.
2024-07-25 17:35:06.12 spid35s     The tempdb database has 8 data file(s).
```

To create all of the tables on the database, run the command below on the terminal:
powershell:
```
docker exec -it sql-server-database-mapper /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P '24ad0a77-c59b-4479-b508-72b83615f8ed' -d master -i /docker-entrypoint-initdb.d/1.sql
```

cmd:
```
docker exec -it sql-server-database-mapper /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 24ad0a77-c59b-4479-b508-72b83615f8ed -d master -i docker-entrypoint-initdb.d/1.sql
```

The pythonrest command to generate the API for this database is:
```
pythonrest generate --sqlserver-connection-string mssql://sa:24ad0a77-c59b-4479-b508-72b83615f8ed@locahost:1433/database_mapper_sqlserver
```
