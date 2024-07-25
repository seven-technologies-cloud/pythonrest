To test this database, run the command below on the docker-compose.yml file:
```
docker-compose up
```

The pythonrest command to generate the API for this database is:
```
pythonrest generate --mysql-connection-string mysql://admin:adminuserdb@localhost:3306/database_mapper_mysql
```
