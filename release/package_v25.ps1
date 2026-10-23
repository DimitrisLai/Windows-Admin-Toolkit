$ErrorActionPreference = 'Stop'
$releaseDir = Join-Path (Get-Location) 'release-output'
$packageRoot = Join-Path $releaseDir 'WindowsAdminToolkit'
New-Item -ItemType Directory -Force -Path $packageRoot | Out-Null
Copy-Item 'dist/WindowsAdminToolkit.exe' $packageRoot
Copy-Item 'LICENSE' $packageRoot
Copy-Item 'docs/Windows_Admin_Toolkit_Detailed_Guide.pdf' (Join-Path $packageRoot 'Windows_Admin_Toolkit_Detailed_Guide.pdf')
$instructions = @'
Windows Admin Toolkit v2.5.0 - Public Beta
Created by Dimitris Laidis - MIT License

1. Extract this ZIP to a local folder.
2. Open WindowsAdminToolkit.exe (Python not required).
3. Review every command's details and warnings. Some commands can modify Windows.
4. Expert Mode suppresses only the post-launch informational popup; safety confirmations remain.

IMPORTANT: UNSIGNED PUBLIC BETA
The executable was compiled by GitHub Actions, but its real-world maintenance commands,
Windows UAC flow, and compatibility have NOT been fully verified on physical PCs.
Do not bypass SmartScreen, Microsoft Defender, or company policies.
Confirm you trust the publisher before using. Back up important data.
See the included PDF and project repository for additional details.
https://github.com/DimitrisLai/Windows-Admin-Toolkit
'@
Set-Content -Path (Join-Path $packageRoot 'README_FIRST.txt') -Value $instructions -Encoding UTF8
$windowsZip = Join-Path $releaseDir 'Windows-Admin-Toolkit-v2.5.0-Windows.zip'
Compress-Archive -Path (Join-Path $packageRoot '*') -DestinationPath $windowsZip -CompressionLevel Optimal
# Archive the exact source commit, including code, documentation, tests and assets.
$sourceZip = Join-Path $releaseDir 'Windows-Admin-Toolkit-v2.5.0-Source.zip'
& git archive --format=zip --output="$sourceZip" HEAD
if ($LASTEXITCODE -ne 0) { throw 'git archive source packaging failed' }
$pdf = Join-Path $releaseDir 'Windows-Admin-Toolkit-v2.5.0-User-Manual.pdf'
Copy-Item 'docs/Windows_Admin_Toolkit_Detailed_Guide.pdf' $pdf
$assets = @($windowsZip, $sourceZip, $pdf)
foreach ($item in $assets) {
  if (-not (Test-Path $item) -or ((Get-Item $item).Length -lt 1024)) { throw "Missing or empty release asset: $item" }
}
$sumPath = Join-Path $releaseDir 'SHA256SUMS.txt'
$lines = foreach ($asset in $assets) {
  $hash = Get-FileHash -LiteralPath $asset -Algorithm SHA256
  "$($hash.Hash.ToLowerInvariant())  $(Split-Path $asset -Leaf)"
}
$lines | Set-Content -LiteralPath $sumPath -Encoding ASCII
Remove-Item $packageRoot -Recurse -Force
Get-ChildItem $releaseDir -File | Select-Object Name, Length | Format-Table -AutoSize
