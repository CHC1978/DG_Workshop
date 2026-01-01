# ============================================
# ARM64 Docker 映像構建腳本
# Marine Equipment QR System
# 適用於 Synology DS223 NAS
# ============================================

param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$CleanBuilder,
    [string]$OutputDir = "docker-images"
)

$ErrorActionPreference = "Stop"

# 顏色輸出函式
function Write-Status($message) {
    Write-Host "[INFO] $message" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "[OK] $message" -ForegroundColor Green
}

function Write-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# 取得腳本所在目錄的父目錄（專案根目錄）
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host " Marine Equipment QR System" -ForegroundColor Yellow
Write-Host " ARM64 Docker Image Builder" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""

# ----------------------------------------
# 步驟 1: 檢查 Docker
# ----------------------------------------
Write-Status "檢查 Docker 安裝狀態..."

try {
    $dockerVersion = docker --version
    Write-Success "Docker 已安裝: $dockerVersion"
} catch {
    Write-Error "Docker 未安裝或未啟動"
    Write-Host ""
    Write-Host "請安裝 Docker Desktop:" -ForegroundColor Yellow
    Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# 確認 Docker 正在運行
try {
    docker info | Out-Null
    Write-Success "Docker 正在運行"
} catch {
    Write-Error "Docker Desktop 未啟動，請先啟動 Docker Desktop"
    exit 1
}

# ----------------------------------------
# 步驟 2: 設定 Buildx
# ----------------------------------------
Write-Status "設定 Docker Buildx 多架構支援..."

$builderName = "marine-arm64-builder"
$existingBuilder = docker buildx ls 2>&1 | Select-String $builderName

if (-not $existingBuilder) {
    Write-Status "建立新的 Buildx builder: $builderName"
    docker buildx create --name $builderName --driver docker-container --use
    docker buildx inspect --bootstrap
} else {
    Write-Status "使用現有的 builder: $builderName"
    docker buildx use $builderName
}

Write-Success "Buildx 設定完成"

# ----------------------------------------
# 步驟 3: 建立輸出目錄
# ----------------------------------------
$OutputPath = Join-Path $ProjectRoot $OutputDir

if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    Write-Status "已建立輸出目錄: $OutputPath"
} else {
    Write-Status "使用現有輸出目錄: $OutputPath"
}

# ----------------------------------------
# 步驟 4: 構建後端映像
# ----------------------------------------
if (-not $SkipBackend) {
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host " 構建後端映像 (ARM64)" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow

    $backendTar = Join-Path $OutputPath "backend-arm64.tar"

    Write-Status "開始構建後端映像..."
    Write-Status "這可能需要 5-10 分鐘（首次構建）..."

    $startTime = Get-Date

    docker buildx build `
        --platform linux/arm64 `
        --tag marine-equipment-backend:arm64 `
        --output "type=docker,dest=$backendTar" `
        --file backend/Dockerfile `
        --progress=plain `
        backend

    if ($LASTEXITCODE -ne 0) {
        Write-Error "後端映像構建失敗"
        exit 1
    }

    $duration = (Get-Date) - $startTime
    $size = [math]::Round((Get-Item $backendTar).Length / 1MB, 2)

    Write-Success "後端映像構建完成"
    Write-Host "  - 檔案: $backendTar" -ForegroundColor Gray
    Write-Host "  - 大小: ${size} MB" -ForegroundColor Gray
    Write-Host "  - 耗時: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor Gray
} else {
    Write-Status "跳過後端映像構建 (-SkipBackend)"
}

# ----------------------------------------
# 步驟 5: 構建前端映像
# ----------------------------------------
if (-not $SkipFrontend) {
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host " 構建前端映像 (ARM64)" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow

    $frontendTar = Join-Path $OutputPath "frontend-arm64.tar"

    Write-Status "開始構建前端映像..."
    Write-Status "這可能需要 3-5 分鐘（首次構建）..."

    $startTime = Get-Date

    docker buildx build `
        --platform linux/arm64 `
        --tag marine-equipment-frontend:arm64 `
        --output "type=docker,dest=$frontendTar" `
        --file frontend/Dockerfile `
        --progress=plain `
        frontend

    if ($LASTEXITCODE -ne 0) {
        Write-Error "前端映像構建失敗"
        exit 1
    }

    $duration = (Get-Date) - $startTime
    $size = [math]::Round((Get-Item $frontendTar).Length / 1MB, 2)

    Write-Success "前端映像構建完成"
    Write-Host "  - 檔案: $frontendTar" -ForegroundColor Gray
    Write-Host "  - 大小: ${size} MB" -ForegroundColor Gray
    Write-Host "  - 耗時: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor Gray
} else {
    Write-Status "跳過前端映像構建 (-SkipFrontend)"
}

# ----------------------------------------
# 步驟 6: 清理（可選）
# ----------------------------------------
if ($CleanBuilder) {
    Write-Host ""
    Write-Status "清理 Buildx builder..."
    docker buildx rm $builderName
    Write-Success "Builder 已清理"
}

# ----------------------------------------
# 完成摘要
# ----------------------------------------
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " 構建完成！" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "輸出檔案:" -ForegroundColor Yellow

Get-ChildItem $OutputPath -Filter "*.tar" | ForEach-Object {
    $size = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  - $($_.Name) (${size} MB)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "下一步驟:" -ForegroundColor Yellow
Write-Host "  1. 透過 DSM File Station 上傳 tar 檔案至 NAS" -ForegroundColor White
Write-Host "  2. 在 Container Manager 匯入映像" -ForegroundColor White
Write-Host "  3. 建立專案並啟動容器" -ForegroundColor White
Write-Host ""
Write-Host "詳細說明請參閱專案文件" -ForegroundColor Gray
Write-Host ""
