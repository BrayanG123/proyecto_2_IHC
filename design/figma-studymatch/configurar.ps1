param(
    [Parameter(Mandatory = $true)]
    [string] $ManifestGeneradoPorFigma
)

$ErrorActionPreference = 'Stop'
$taskGeneratedPath = (Resolve-Path -LiteralPath $ManifestGeneradoPorFigma).Path
$taskGeneratedManifest = Get-Content -LiteralPath $taskGeneratedPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $taskGeneratedManifest.id -or $taskGeneratedManifest.id -notmatch '^\d+$') {
    throw 'El manifest seleccionado no contiene un ID numérico generado por Figma.'
}

$taskTargetManifestPath = Join-Path $PSScriptRoot 'manifest.json'
$taskTargetManifest = Get-Content -LiteralPath $taskTargetManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$taskTargetManifest.id = [string] $taskGeneratedManifest.id
$taskTargetJson = $taskTargetManifest | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText($taskTargetManifestPath, $taskTargetJson, [System.Text.UTF8Encoding]::new($false))
Write-Output "Manifest configurado: $taskTargetManifestPath"
