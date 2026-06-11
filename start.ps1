# TaskFlow — start all services
$venv = "$PSScriptRoot\.venv\bin"
$env:PYTHONPATH = "$PSScriptRoot\src"

Write-Host "Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Cyan
$api = Start-Process -FilePath "$venv\python.exe" `
  -ArgumentList "-m","uvicorn","taskflow.presentation.api.app:create_app","--factory","--host","0.0.0.0","--port","8000","--reload" `
  -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru
$api.Id | Out-File "$PSScriptRoot\.pids" -Encoding utf8

Write-Host "Starting Streamlit UI on http://localhost:8501 ..." -ForegroundColor Cyan
$ui = Start-Process -FilePath "$venv\streamlit.exe" `
  -ArgumentList "run","ui.py","--server.port","8501","--server.headless","true","--browser.gatherUsageStats","false" `
  -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru
$api.Id, $ui.Id | Out-File "$PSScriptRoot\.pids" -Encoding utf8

Write-Host ""
Write-Host "  UI  →  http://localhost:8501" -ForegroundColor Green
Write-Host "  API →  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Network → http://$(
    (Get-NetIPAddress -AddressFamily IPv4 |
     Where-Object { $_.InterfaceAlias -match 'Wi-Fi|Ethernet' } |
     Select-Object -First 1).IPAddress):8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "Run .\stop.ps1 to shut everything down." -ForegroundColor DarkGray
