To test this database, run the command below on the docker-compose.yml file:
```
docker-compose up
```

The pythonrest command to generate the API for this database is:
```
pythonrest generate --postgres-connection-string postgresql://postgres:postgres@localhost:5432/database_mapper_postgresql?options=-c%20search_path=database_mapper_postgresql,public
```
