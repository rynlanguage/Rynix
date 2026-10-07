param([string]$Compiler = "$PSScriptRoot/../../Ryn/target/release/ryn.exe", [switch]$Native)
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    foreach ($example in Get-ChildItem -LiteralPath examples -Directory | Sort-Object Name) {
        & $Compiler check $example.FullName
        if ($LASTEXITCODE -ne 0) { throw "check failed: $($example.Name)" }
        & $Compiler build $example.FullName --release
        if ($LASTEXITCODE -ne 0) { throw "build failed: $($example.Name)" }
    }
    foreach ($example in @('quick_start','math_check','camera_check','cpu_3d')) {
        & $Compiler run "examples/$example" --release
        if ($LASTEXITCODE -ne 0) { throw "CPU regression failed: $example" }
    }
    if ($Native) {
        foreach ($example in @('window_smoke','graphics_smoke','native_3d_smoke')) {
            & $Compiler run "examples/$example" --release
            if ($LASTEXITCODE -ne 0) { throw "native regression failed: $example" }
        }
    }
    Write-Output 'Rynix checks passed'
} finally { Pop-Location }
