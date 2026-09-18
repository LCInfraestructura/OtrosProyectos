$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
dotnet publish (Join-Path $projectRoot 'src/Loteria/Loteria.csproj') -c Release -r win-x64 --self-contained true -o (Join-Path $projectRoot 'dist/Loteria') --nologo
if ($LASTEXITCODE -ne 0) { throw 'Falló la publicación.' }
Remove-Item -LiteralPath (Join-Path $projectRoot 'dist/Loteria/assets/loteria/radioteca-downloads.json') -ErrorAction SilentlyContinue
$assetRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot 'dist/Loteria/assets/loteria'))
$cards = Get-Content -LiteralPath (Join-Path $assetRoot 'manifest.json') -Raw | ConvertFrom-Json
foreach ($card in $cards) {
    foreach ($voice in @('generated-es', 'generated-en', 'generated-verses-es')) {
        $relative = $card.audio.$voice
        if ([IO.Path]::GetExtension($relative) -eq '.wav') {
            $obsolete = [IO.Path]::GetFullPath((Join-Path $assetRoot ([IO.Path]::ChangeExtension($relative, '.mp3'))))
            if (-not $obsolete.StartsWith($assetRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Ruta de limpieza fuera del paquete.' }
            if (Test-Path -LiteralPath $obsolete) { Remove-Item -LiteralPath $obsolete }
        }
    }
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'README.md') -Destination (Join-Path $projectRoot 'dist/Loteria/LEEME.md')
Write-Host 'Listo: dist/Loteria/Loteria.exe. Conserva la carpeta completa.'
