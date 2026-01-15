"""
VanVani AI - Setup and Run Guide

This script helps you set up and run the VanVani AI system.
"""

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "VanVani AI - Setup Script" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python not found. Please install Python 3.10 or higher." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""

# Create .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file. Please edit it with your API keys." -ForegroundColor Green
    Write-Host ""
    Write-Host "Required API keys:" -ForegroundColor Cyan
    Write-Host "  1. OPENAI_API_KEY - Get from https://platform.openai.com/" -ForegroundColor White
    Write-Host "  2. TWILIO_ACCOUNT_SID & TWILIO_AUTH_TOKEN - Get from https://www.twilio.com/" -ForegroundColor White
    Write-Host "  3. SARVAM_API_KEY (optional) - Get from https://www.sarvam.ai/" -ForegroundColor White
    Write-Host ""
    Write-Host "Press any key after you've edited the .env file..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

Write-Host ""

# Create data directories
Write-Host "Creating data directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data\raw_pdfs" | Out-Null
New-Item -ItemType Directory -Force -Path "data\processed" | Out-Null
New-Item -ItemType Directory -Force -Path "data\vector_store" | Out-Null
Write-Host "Data directories created." -ForegroundColor Green

Write-Host ""

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Yellow
python -m app.database.init_db

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "To expose local server (for Twilio webhooks):" -ForegroundColor Cyan
Write-Host "  ngrok http 8000" -ForegroundColor White
Write-Host ""
