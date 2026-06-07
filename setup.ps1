# ZAMON MARKET — bir buyruqli o'rnatish (Windows / PowerShell)
# Ishlatish:  ./setup.ps1
# Bu skript: .venv yaratadi, paketlarni o'rnatadi, bazani migrate qiladi va
# 105 ta demo mahsulot bilan to'ldiradi. Boshqa kompyuterga ko'chirganda ham
# shu bitta buyruq yetarli.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

# 1) Python topish (py launcher yoki python)
$py = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $py = "py" }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $py = "python" }
else { Write-Error "Python topilmadi. python.org dan Python 3.12+ o'rnating."; exit 1 }

# 2) venv yaratish (agar yo'q bo'lsa)
$venvPy = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "[1/4] .venv yaratilmoqda..." -ForegroundColor Cyan
    & $py -m venv .venv
}

# 3) Paketlar
Write-Host "[2/4] Paketlar o'rnatilmoqda..." -ForegroundColor Cyan
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install -r backend\requirements.txt --quiet

# 4) Migrate + seed
Write-Host "[3/4] Baza migratsiyasi..." -ForegroundColor Cyan
& $venvPy backend\manage.py migrate

Write-Host "[4/4] Demo ma'lumot (105 mahsulot)..." -ForegroundColor Cyan
& $venvPy backend\manage.py seed_data

Write-Host ""
Write-Host "Tayyor! Ishga tushirish:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\python.exe backend\manage.py runserver 8000"
Write-Host "Brauzerda:  http://localhost:8000"
Write-Host "Admin: admin@zamon.uz / admin12345"
