$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Get-Command python -ErrorAction SilentlyContinue
$pythonPath = if ($python) { $python.Source } else {
  $bundled = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
  if (Test-Path -LiteralPath $bundled) { $bundled } else { $null }
}
if (-not $pythonPath) {
  Write-Host "Python 3.11+ is required. Install it from https://www.python.org/downloads/windows/ and enable Add Python to PATH." -ForegroundColor Yellow
  exit 1
}
Set-Location $workspace
& $pythonPath "$workspace\backend\gateway.py"
