# Função para logar mensagens com timestamp
function Write-Log {
    param($Message)
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
}

# Sair ao primeiro erro
$ErrorActionPreference = "Stop"

# Função para desativar o venv PythonREST ao sair
function Cleanup-PythonRESTVenv {
    if ($script:PYTHONREST_VENV_ACTIVATED) {
        Write-Log "Desativando o ambiente virtual PythonREST devido à saída do script..."
        deactivate
        Write-Log "Ambiente virtual PythonREST desativado."
        $script:PYTHONREST_VENV_ACTIVATED = $false
    }
}

# Registrar cleanup para rodar ao sair
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Cleanup-PythonRESTVenv }

# 0. Determinar diretórios
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Resolve-Path (Join-Path $SCRIPT_DIR "..\..\..\") | ForEach-Object { $_.Path }
Write-Log "Script directory: $SCRIPT_DIR"
Write-Log "Project root: $PROJECT_ROOT"

# Mudar para o diretório raiz do projeto
Set-Location $PROJECT_ROOT
Write-Log "Changed directory to project root: $(Get-Location)"

# 1. Início
Write-Log "Starting SQL Server integration test script."

# 2. Subir container SQL Server
Write-Log "Starting SQL Server Docker container..."
Set-Location $SCRIPT_DIR
Write-Log "Changed directory to script location for Docker operations: $(Get-Location)"
docker-compose down --remove-orphans
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Log "ERROR: Failed to start SQL Server Docker container."
    Write-Log "Checking docker-compose logs:"
    docker-compose logs
    exit 1
}
Write-Log "SQL Server Docker container started."

# 3. Esperar container ficar healthy
$SQLSERVER_CONTAINER_NAME = "sql-server-database-mapper"
Write-Log "Waiting for SQL Server container ($SQLSERVER_CONTAINER_NAME) to be healthy..."

# Função para verificar se o SQL Server está pronto
function Test-SQLServerReady {
    try {
        $logs = docker logs $SQLSERVER_CONTAINER_NAME
        if ($logs -match "Recovery is complete. This is an informational message only. No user action is required.") {
            return $true
        }
        return $false
    }
    catch {
        return $false
    }
}

$TIMEOUT_SECONDS = 120
$SECONDS_WAITED = 0
$MAX_RETRIES = 3
$retryCount = 0

while ($true) {
    if (Test-SQLServerReady) {
        Write-Log "SQL Server container is ready and accepting connections."
        break
    }

    if ($SECONDS_WAITED -ge $TIMEOUT_SECONDS) {
        if ($retryCount -lt $MAX_RETRIES) {
            Write-Log "Timeout reached. Attempting to restart container (Attempt $($retryCount + 1) of $MAX_RETRIES)..."
            docker-compose restart
            $SECONDS_WAITED = 0
            $retryCount++
            continue
        }
        
        Write-Log "ERROR: SQL Server container failed to become ready after $MAX_RETRIES attempts."
        Write-Log "Container logs:"
        docker-compose logs
        Write-Log "Container details:"
        docker inspect $SQLSERVER_CONTAINER_NAME
        docker-compose down
        exit 1
    }

    Write-Log "Waiting for SQL Server to be ready... ($SECONDS_WAITED/$TIMEOUT_SECONDS seconds)"
    Start-Sleep -Seconds 5
    $SECONDS_WAITED += 5
    Write-Log "Still waiting for SQL Server container... ($SECONDS_WAITED/$TIMEOUT_SECONDS seconds)"
}

Write-Log "SQL Server container is ready and healthy."

# Executar script SQL para criar o banco e as tabelas
Write-Log "Executing SQL script to create database and tables..."
$SQLCMD_LOG = "$env:TEMP\sqlcmd_output_sqlserver.log"
docker exec $SQLSERVER_CONTAINER_NAME /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U SA -P '24ad0a77-c59b-4479-b508-72b83615f8ed' -d master -i /docker-entrypoint-initdb.d/database_mapper_sqlserver.sql > $SQLCMD_LOG 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Log "ERROR: Failed to execute SQL script. See $SQLCMD_LOG for details."
    Get-Content $SQLCMD_LOG
    docker-compose down
    exit 1
}
Write-Log "SQL script executed successfully. Output logged to $SQLCMD_LOG."
Start-Sleep -Seconds 10 # Delay for schema changes and database to be fully ready

# 4. Ativar venv PythonREST
$VENV_ACTIVATE = Join-Path $PROJECT_ROOT "venv\Scripts\Activate.ps1"
Write-Log "Activating shared PythonREST virtual environment: $VENV_ACTIVATE"
if (-not (Test-Path $VENV_ACTIVATE)) {
    Write-Log "ERROR: PythonREST venv activate script not found at $VENV_ACTIVATE"
    docker-compose down
    exit 1
}
. $VENV_ACTIVATE
$script:PYTHONREST_VENV_ACTIVATED = $true
Write-Log "Shared PythonREST virtual environment activated."

# 5. Rodar geração PythonREST
Write-Log "Running PythonREST generation using $PROJECT_ROOT\pythonrest.py..."
Set-Location $PROJECT_ROOT
Write-Log "Changed directory to project root for PythonREST generation: $(Get-Location)"

python "$PROJECT_ROOT\pythonrest.py" generate --sqlserver-connection-string mssql://sa:24ad0a77-c59b-4479-b508-72b83615f8ed@localhost:1433/database_mapper_sqlserver

$GENERATION_STATUS = $LASTEXITCODE

if ($GENERATION_STATUS -ne 0) {
    Write-Log "ERROR: PythonREST generation failed."
    Set-Location $SCRIPT_DIR
    docker-compose down
    exit 1
}

Write-Log "PythonREST generation completed successfully."

# 6. Checar pasta PythonRestAPI
$GENERATED_API_PATH = Join-Path $PROJECT_ROOT "PythonRestAPI"
Write-Log "Checking for generated API at: $GENERATED_API_PATH"
if (-not (Test-Path $GENERATED_API_PATH)) {
    Write-Log "ERROR: 'PythonRestAPI' folder not found at $GENERATED_API_PATH after PythonREST generation."
    Set-Location $SCRIPT_DIR
    docker-compose down
    exit 1
}
Write-Log "PythonREST generation successful. 'PythonRestAPI' folder found at $GENERATED_API_PATH."

# 7. Ir para PythonRestAPI
Set-Location $GENERATED_API_PATH
Write-Log "Changed directory to $(Get-Location)."

# 8. Criar venv para API gerada
Write-Log "Creating Python virtual environment for generated API..."
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Log "ERROR: Failed to create Python virtual environment for generated API."
    Set-Location $SCRIPT_DIR
    docker-compose down
    exit 1
}
Write-Log "Python virtual environment for generated API created."

# 9. Ativar venv da API gerada
$GENERATED_VENV_ACTIVATE = Join-Path (Get-Location) "venv\Scripts\Activate.ps1"
Write-Log "Activating virtual environment for generated API..."
. $GENERATED_VENV_ACTIVATE
Write-Log "Virtual environment for generated API activated."

# 10. Instalar dependências
$PIP_LOG = "$env:TEMP\pip_install_sqlserver_api.log"
Write-Log "Installing dependencies from requirements.txt for generated API..."

Write-Log "Installing packages from requirements.txt"
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    $logContent = Get-Content $PIP_LOG -Raw
    if ($logContent -match "ERROR" -or $logContent -match "failed") {
        Write-Host "pip install failed with exit code $LASTEXITCODE"
        throw "pip install failed"
    } else {
        Write-Host "pip install exited with code $LASTEXITCODE but no errors found in log."
    }
}

Write-Log "Dependencies for generated API installed successfully. Output logged to $PIP_LOG"

# 11. Iniciar Flask API em background
Write-Log "Starting Flask API in the background..."
$API_LOG = "$env:TEMP\api_output_sqlserver.log"
$API_LOG_ERROR = "$env:TEMP\api_error_output_sqlserver.log"
Write-Log "API output will be logged to: $API_LOG"
Write-Log "API errors will be logged to: $API_LOG_ERROR"

$API_PROCESS = Start-Process python -ArgumentList "app.py" -RedirectStandardOutput $API_LOG -RedirectStandardError $API_LOG_ERROR -PassThru
Write-Log "Flask API started with PID $($API_PROCESS.Id). Output logged to $API_LOG."

# 12. Esperar API subir
Write-Log "Waiting for API to start (5 seconds)..."
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -OutFile "$env:TEMP\curl_check_sqlserver.log"
    Write-Log "API started and responding (status code $($response.StatusCode))."
} catch {
    # Se for 404 ou 400, considere sucesso (API está rodando, só não tem rota / ou requer algo)
    if ($_.Exception.Response.StatusCode.value__ -eq 404 -or $_.Exception.Response.StatusCode.value__ -eq 400) {
        Write-Log "API started and responded with $($_.Exception.Response.StatusCode) (no route '/' or bad request). This is expected for generated APIs."
    } else {
        Write-Log "ERROR: API failed to start or is not responding. Curl check failed. See $env:TEMP\curl_check_sqlserver.log."
        if (Test-Path "$env:TEMP\curl_check_sqlserver.log") {
            Get-Content "$env:TEMP\curl_check_sqlserver.log"
        } else {
            Write-Log "curl_check_sqlserver.log not found. The API did not respond or failed to start."
        }
        Write-Log "API logs ($API_LOG):"
        Get-Content $API_LOG
        Write-Log "API error logs ($API_LOG_ERROR):"
        Get-Content $API_LOG_ERROR
        if (Get-Process -Id $API_PROCESS.Id -ErrorAction SilentlyContinue) {
            Stop-Process -Id $API_PROCESS.Id -Force
        }
        deactivate
        Write-Log "Virtual environment for generated API deactivated."
        Set-Location $SCRIPT_DIR
        docker-compose down
        exit 1
    }
}
Remove-Item "$env:TEMP\curl_check_sqlserver.log" -ErrorAction SilentlyContinue

# 13. Teste GET
Write-Log "Performing sample GET request to http://localhost:5000/swagger..."
Invoke-WebRequest -Uri "http://localhost:5000/swagger" -UseBasicParsing -OutFile "$env:TEMP\curl_test_sqlserver.log"
if ($LASTEXITCODE -ne 0) {
    Write-Log "WARNING: Sample GET request failed. This might indicate an issue or no default route. See $env:TEMP\curl_test_sqlserver.log."
    Get-Content "$env:TEMP\curl_test_sqlserver.log"
} else {
    Write-Log "Sample GET request successful. Response logged to $env:TEMP\curl_test_sqlserver.log."
}

# 14. Matar API
Write-Log "Killing Flask API (PID $($API_PROCESS.Id))..."
Stop-Process -Id $API_PROCESS.Id -Force
Write-Log "Flask API process killed."

# 15. Desativar venv da API gerada
Write-Log "Deactivating virtual environment for generated API..."
deactivate
Write-Log "Virtual environment for generated API deactivated."

# 16. Voltar para $SCRIPT_DIR
Set-Location $SCRIPT_DIR
Write-Log "Changed directory to $(Get-Location)."

# 17. Desativar venv PythonREST
Write-Log "Deactivating shared PythonREST virtual environment (explicitly)..."
deactivate
$script:PYTHONREST_VENV_ACTIVATED = $false
Write-Log "Shared PythonREST virtual environment deactivated."

# 18. Parar e remover container
Write-Log "Stopping and removing SQL Server Docker container..."
docker-compose down
Write-Log "SQL Server Docker container stopped and removed."

# 19. Fim
Write-Log "SQL Server integration test script completed successfully."
exit 0 