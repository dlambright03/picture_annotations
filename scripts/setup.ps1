#!/usr/bin/env pwsh
# Setup script for ADA Annotator development environment

Write-Host "🚀 ADA Annotator Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if uv is installed
Write-Host "Checking for uv installation..." -ForegroundColor Yellow
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "❌ uv is not installed!" -ForegroundColor Red
    Write-Host "Please install uv first:" -ForegroundColor Yellow
    Write-Host "  powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor White
    exit 1
}
Write-Host "✅ uv is installed" -ForegroundColor Green

# Check Python version
Write-Host ""
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(1[1-9]|[2-9][0-9])") {
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "⚠️  Python 3.11+ recommended, found: $pythonVersion" -ForegroundColor Yellow
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
uv venv
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment and install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check for .env file
Write-Host ""
Write-Host "Checking for .env file..." -ForegroundColor Yellow
if (!(Test-Path .env)) {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔧 IMPORTANT: Edit .env and add your API keys!" -ForegroundColor Cyan
    Write-Host "   - AZURE_OPENAI_ENDPOINT" -ForegroundColor White
    Write-Host "   - AZURE_OPENAI_API_KEY" -ForegroundColor White
    Write-Host "   - AZURE_OPENAI_DEPLOYMENT_NAME" -ForegroundColor White
} else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}

# Create temp directory
Write-Host ""
Write-Host "Creating temporary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path temp | Out-Null
Write-Host "✅ Temporary directories created" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Activate virtual environment:" -ForegroundColor White
Write-Host "     .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Configure your API keys in .env" -ForegroundColor White
Write-Host ""
Write-Host "  3. Run the Streamlit app:" -ForegroundColor White
Write-Host "     streamlit run src/ada_annotator/app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Run tests:" -ForegroundColor White
Write-Host "     pytest" -ForegroundColor Cyan
Write-Host ""
Write-Host "Happy coding! 🎉" -ForegroundColor Magenta
