# ==============================================================================
# MINH AN AI AGENT - UNIVERSAL LOCALHOST SERVER (PORT 8000)
# ==============================================================================

$port = 8000
$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $workspace

function Test-RealPython($cmd) {
    try {
        $result = & $cmd -c "print('PY_OK')" 2>$null
        return ($result -match "PY_OK")
    } catch {
        return $false
    }
}

$pythonExe = $null

# 1. Kiem tra cac duong dan Python thuc thu (bo qua Windows Store dummy stub)
$candidates = @(
    "py",
    "python",
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "$env:ProgramFiles\Python312\python.exe",
    "$env:ProgramFiles\Python311\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe"
)

foreach ($c in $candidates) {
    if (Get-Command $c -ErrorAction SilentlyContinue) {
        if (Test-RealPython $c) {
            $pythonExe = $c
            break
        }
    } elseif (Test-Path $c) {
        if (Test-RealPython $c) {
            $pythonExe = $c
            break
        }
    }
}

if ($pythonExe) {
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Phat hien Python thuc thu: $pythonExe" -ForegroundColor Green
    Write-Host "Dang khoi dong Minh An Backend tai http://localhost:$port" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Start-Process "http://localhost:$port"
    & $pythonExe app.py
    exit
}

# 2. Neu may chua cai Python: Chay ngay bang Built-in .NET HttpListener (Luon luon thanh cong!)
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "KHOI DONG MAY CHU MINH AN (BUILT-IN ENGINE) TAI CONG $port" -ForegroundColor Green
Write-Host "Dang lang nghe tai: http://localhost:$port/" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Yellow

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Start()

Write-Host "May chu da san sang! Dang mo trinh duyet..." -ForegroundColor Green
Start-Process "http://localhost:$port/"

$staticDir = Join-Path $workspace "static"
$indexPath = Join-Path $staticDir "index.html"

while ($listener.IsListening) {
    $context = $listener.GetContext()
    $request = $context.Request
    $response = $context.Response
    
    $localPath = $request.Url.LocalPath
    
    $content = $null
    if ($localPath -eq "/" -or $localPath -eq "/index.html") {
        $content = [System.IO.File]::ReadAllBytes($indexPath)
        $response.ContentType = "text/html; charset=utf-8"
    } else {
        $filePath = Join-Path $staticDir ($localPath.TrimStart('/'))
        if (Test-Path $filePath) {
            $content = [System.IO.File]::ReadAllBytes($filePath)
            if ($filePath.EndsWith(".css")) { $response.ContentType = "text/css" }
            elseif ($filePath.EndsWith(".js")) { $response.ContentType = "application/javascript" }
        } else {
            $content = [System.IO.File]::ReadAllBytes($indexPath)
            $response.ContentType = "text/html; charset=utf-8"
        }
    }
    
    $response.Headers.Add("Access-Control-Allow-Origin", "*")
    $response.ContentLength64 = $content.Length
    $response.OutputStream.Write($content, 0, $content.Length)
    $response.OutputStream.Close()
}
