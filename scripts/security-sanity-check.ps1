$ErrorActionPreference = "Stop"

param(
  [Parameter(Mandatory=$true)]
  [string]$Domain
)

function Assert-Contains([string]$Text, [string]$Needle, [string]$Msg) {
  if ($Text -notmatch [Regex]::Escape($Needle)) {
    throw $Msg
  }
}

$https = "https://$Domain/"
$http  = "http://$Domain/"

Write-Host "== Redirect http -> https"
$h = (curl.exe -sSIL $http) -join "`n"
Assert-Contains $h "Location: https://$Domain/" "Expected redirect to https://$Domain/"

Write-Host "== Headers (security + no double Server)"
$hh = (curl.exe -sSI $https) -join "`n"

# Server header: ideally none; if present, should not be duplicated.
$serverCount = ([regex]::Matches($hh, "^(?im)server:\s")).Count
if ($serverCount -gt 1) { throw "Found $serverCount Server headers (expected 0 or 1)" }

Assert-Contains $hh "strict-transport-security" "Missing HSTS"
Assert-Contains $hh "content-security-policy" "Missing CSP"
Assert-Contains $hh "x-content-type-options" "Missing nosniff"

Write-Host "== API reachable"
$api = (curl.exe -sSI "https://$Domain/api/") -join "`n"
Write-Host $api

Write-Host "== PDF worker reachable (optional)"
$pdfw = (curl.exe -sSI "https://$Domain/pdf.worker.min.mjs") -join "`n"
Write-Host $pdfw

Write-Host "OK"

