# ============================================
# ARM64 Docker Image Build Script
# Marine Equipment QR System
# Target: Synology DS223 NAS
# ============================================

param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$CleanBuilder,
    [string]$OutputDir = "docker-images"
)

$ErrorActionPreference = "Stop"

# Color output functions
function Write-Status($message) {
    Write-Host "[INFO] $message" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "[OK] $message" -ForegroundColor Green
}

function Write-ErrorMsg($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# Get project root directory (parent of scripts folder)
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host " Marine Equipment QR System" -ForegroundColor Yellow
Write-Host " ARM64 Docker Image Builder" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""

# ----------------------------------------
# Step 1: Check Docker Installation
# ----------------------------------------
Write-Status "Checking Docker installation..."

try {
    $dockerVersion = docker --version
    Write-Success "Docker installed: $dockerVersion"
} catch {
    Write-ErrorMsg "Docker is not installed or not running"
    Write-Host ""
    Write-Host "Please install Docker Desktop:" -ForegroundColor Yellow
    Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Verify Docker is running
try {
    docker info | Out-Null
    Write-Success "Docker is running"
} catch {
    Write-ErrorMsg "Docker Desktop is not started. Please start Docker Desktop first."
    exit 1
}

# ----------------------------------------
# Step 2: Setup Buildx
# ----------------------------------------
Write-Status "Setting up Docker Buildx for multi-architecture support..."

$builderName = "marine-arm64-builder"
$existingBuilder = docker buildx ls 2>&1 | Select-String $builderName

if (-not $existingBuilder) {
    Write-Status "Creating new Buildx builder: $builderName"
    docker buildx create --name $builderName --driver docker-container --use
    docker buildx inspect --bootstrap
} else {
    Write-Status "Using existing builder: $builderName"
    docker buildx use $builderName
}

Write-Success "Buildx setup complete"

# ----------------------------------------
# Step 3: Create Output Directory
# ----------------------------------------
$OutputPath = Join-Path $ProjectRoot $OutputDir

if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    Write-Status "Created output directory: $OutputPath"
} else {
    Write-Status "Using existing output directory: $OutputPath"
}

# ----------------------------------------
# Step 4: Build Backend Image
# ----------------------------------------
if (-not $SkipBackend) {
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host " Building Backend Image (ARM64)" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow

    $backendTar = Join-Path $OutputPath "backend-arm64.tar"

    Write-Status "Starting backend image build..."
    Write-Status "This may take 5-10 minutes (first build)..."

    $startTime = Get-Date

    docker buildx build `
        --platform linux/arm64 `
        --tag marine-equipment-backend:arm64 `
        --output "type=docker,dest=$backendTar" `
        --file backend/Dockerfile `
        --progress=plain `
        backend

    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Backend image build failed"
        exit 1
    }

    $duration = (Get-Date) - $startTime
    $fileSize = [math]::Round((Get-Item $backendTar).Length / 1MB, 2)

    Write-Success "Backend image build complete"
    Write-Host "  - File: $backendTar" -ForegroundColor Gray
    Write-Host "  - Size: $fileSize MB" -ForegroundColor Gray
    Write-Host "  - Duration: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor Gray
} else {
    Write-Status "Skipping backend image build (-SkipBackend)"
}

# ----------------------------------------
# Step 5: Build Frontend Image
# ----------------------------------------
if (-not $SkipFrontend) {
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host " Building Frontend Image (ARM64)" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow

    $frontendTar = Join-Path $OutputPath "frontend-arm64.tar"

    Write-Status "Starting frontend image build..."
    Write-Status "This may take 3-5 minutes (first build)..."

    $startTime = Get-Date

    docker buildx build `
        --platform linux/arm64 `
        --tag marine-equipment-frontend:arm64 `
        --output "type=docker,dest=$frontendTar" `
        --file frontend/Dockerfile `
        --progress=plain `
        frontend

    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Frontend image build failed"
        exit 1
    }

    $duration = (Get-Date) - $startTime
    $fileSize = [math]::Round((Get-Item $frontendTar).Length / 1MB, 2)

    Write-Success "Frontend image build complete"
    Write-Host "  - File: $frontendTar" -ForegroundColor Gray
    Write-Host "  - Size: $fileSize MB" -ForegroundColor Gray
    Write-Host "  - Duration: $($duration.Minutes)m $($duration.Seconds)s" -ForegroundColor Gray
} else {
    Write-Status "Skipping frontend image build (-SkipFrontend)"
}

# ----------------------------------------
# Step 6: Cleanup (Optional)
# ----------------------------------------
if ($CleanBuilder) {
    Write-Host ""
    Write-Status "Cleaning up Buildx builder..."
    docker buildx rm $builderName
    Write-Success "Builder removed"
}

# ----------------------------------------
# Build Summary
# ----------------------------------------
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " Build Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output files:" -ForegroundColor Yellow

Get-ChildItem $OutputPath -Filter "*.tar" | ForEach-Object {
    $fileSize = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  - $($_.Name) ($fileSize MB)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Upload tar files to NAS via DSM File Station" -ForegroundColor White
Write-Host "  2. Import images in Container Manager" -ForegroundColor White
Write-Host "  3. Create project and start containers" -ForegroundColor White
Write-Host ""
Write-Host "See scripts/DEPLOY.md for detailed instructions" -ForegroundColor Gray
Write-Host ""
