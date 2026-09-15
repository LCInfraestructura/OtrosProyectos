$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
dotnet publish (Join-Path $projectRoot 'src/Loteria/Loteria.csproj') -c Release -r win-x64 --self-contained true -o (Join-Path $projectRoot 'dist/Loteria') --nologo
if ($LASTEXITCODE -ne 0) { throw 'Falló la publicación.' }
Copy-Item -LiteralPath (Join-Path $projectRoot 'README.md') -Destination (Join-Path $projectRoot 'dist/Loteria/LEEME.md')
Write-Host 'Listo: dist/Loteria/Loteria.exe. Conserva la carpeta completa.'
