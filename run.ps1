"""
Quick start script to run VanVani AI server.
"""

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Starting VanVani AI Server" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "Error: Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "Error: .env file not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Start the server
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "API documentation will be available at http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
