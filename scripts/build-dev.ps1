# ============================================
# Windows x64 Development Docker Build Script
# Marine Equipment QR System
# ============================================

param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$Up,
    [switch]$Down,
    [switch]$Rebuild
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

# Get project root directory
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host ""
Write-Host "============================================" -ForegroundColor Yellow
Write-Host " Marine Equipment QR System" -ForegroundColor Yellow
Write-Host " Windows x64 Development Build" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Yellow
Write-Host ""

# ----------------------------------------
# Step 1: Check Docker
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
    exit 1
}

try {
    docker info | Out-Null
    Write-Success "Docker is running"
} catch {
    Write-ErrorMsg "Docker Desktop is not started. Please start Docker Desktop first."
    exit 1
}

# ----------------------------------------
# Handle -Down flag
# ----------------------------------------
if ($Down) {
    Write-Status "Stopping development containers..."
    docker compose -f docker-compose.dev.yml down
    Write-Success "Containers stopped"
    exit 0
}

# ----------------------------------------
# Handle -Rebuild flag
# ----------------------------------------
if ($Rebuild) {
    Write-Status "Rebuilding and restarting containers..."
    docker compose -f docker-compose.dev.yml down
    docker compose -f docker-compose.dev.yml build --no-cache
    docker compose -f docker-compose.dev.yml up -d
    Write-Success "Containers rebuilt and started"
    Write-Host ""
    Write-Host "Services available at:" -ForegroundColor Yellow
    Write-Host "  - Frontend: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    exit 0
}

# ----------------------------------------
# Step 2: Create data directories
# ----------------------------------------
Write-Status "Creating data directories..."

$dataDir = Join-Path $ProjectRoot "backend\data"
$uploadsDir = Join-Path $ProjectRoot "backend\uploads"

if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
    Write-Status "Created: $dataDir"
}

if (-not (Test-Path $uploadsDir)) {
    New-Item -ItemType Directory -Path $uploadsDir -Force | Out-Null
    Write-Status "Created: $uploadsDir"
}

# ----------------------------------------
# Step 3: Build Images
# ----------------------------------------
if (-not $SkipBackend) {
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host " Building Backend Image (x64)" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow

    $startTime = Get-Date

    docker build -t marine-equipment-backend:dev ./backend

    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Backend image build failed"
        exit 1
    }

    $duration = (Get-Date) - $startTime
    Write-Success "Backend image built in $($duration.Minutes)m $($duration.Seconds)s"
} else {
    Write-Status "Skipping backend build (-SkipBackend)"
}

if (-not $SkipFrontend) {
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host " Building Frontend Image (x64)" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow

    $startTime = Get-Date

    docker build -t marine-equipment-frontend:dev ./frontend

    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Frontend image build failed"
        exit 1
    }

    $duration = (Get-Date) - $startTime
    Write-Success "Frontend image built in $($duration.Minutes)m $($duration.Seconds)s"
} else {
    Write-Status "Skipping frontend build (-SkipFrontend)"
}

# ----------------------------------------
# Step 4: Start Containers (if -Up flag)
# ----------------------------------------
if ($Up) {
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host " Starting Development Containers" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow

    docker compose -f docker-compose.dev.yml up -d

    if ($LASTEXITCODE -ne 0) {
        Write-ErrorMsg "Failed to start containers"
        exit 1
    }

    Write-Success "Containers started"
    Write-Host ""
    Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5

    # Check health
    Write-Status "Checking service health..."
    docker compose -f docker-compose.dev.yml ps
}

# ----------------------------------------
# Summary
# ----------------------------------------
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host " Build Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

if ($Up) {
    Write-Host "Services running at:" -ForegroundColor Yellow
    Write-Host "  - Frontend: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
} else {
    Write-Host "To start the development environment:" -ForegroundColor Yellow
    Write-Host "  .\scripts\build-dev.ps1 -Up" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or use docker compose directly:" -ForegroundColor Yellow
    Write-Host "  docker compose -f docker-compose.dev.yml up -d" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Other commands:" -ForegroundColor Yellow
Write-Host "  .\scripts\build-dev.ps1 -Down      # Stop containers" -ForegroundColor Gray
Write-Host "  .\scripts\build-dev.ps1 -Rebuild   # Rebuild and restart" -ForegroundColor Gray
Write-Host "  .\scripts\build-dev.ps1 -Up        # Build and start" -ForegroundColor Gray
Write-Host ""
