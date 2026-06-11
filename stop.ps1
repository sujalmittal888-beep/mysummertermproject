# TaskFlow — stop all services
$pidsFile = "$PSScriptRoot\.pids"

if (Test-Path $pidsFile) {
    Get-Content $pidsFile | ForEach-Object {
        $id = [int]$_
        $proc = Get-Process -Id $id -ErrorAction SilentlyContinue
        if ($proc) {
            Stop-Process -Id $id -Force
            Write-Host "Stopped PID $id ($($proc.ProcessName))" -ForegroundColor Yellow
        }
    }
    Remove-Item $pidsFile
} else {
    # fallback: kill any python process on our ports
    "8000","8501" | ForEach-Object {
        $port = $_
        $pid_ = (netstat -ano | Select-String ":$port " | ForEach-Object {
            ($_ -split '\s+')[-1]
        } | Select-Object -First 1)
        if ($pid_) {
            Stop-Process -Id ([int]$pid_) -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped process on port $port (PID $pid_)" -ForegroundColor Yellow
        }
    }
}

Write-Host "All TaskFlow services stopped." -ForegroundColor Green
