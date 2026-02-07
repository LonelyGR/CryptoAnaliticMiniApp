$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "[deploy] git pull (if configured)"
try { git pull --ff-only } catch { }

Write-Host "[deploy] docker compose up (prod)"
docker compose -f docker-compose.prod.yml up -d --build

Write-Host "[deploy] done"

