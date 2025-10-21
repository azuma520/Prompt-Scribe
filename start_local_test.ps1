# Start Local Test Environment
# This script starts both backend and frontend for GPT-5 testing
#
# IMPORTANT: Run setup_env_local.ps1 first to configure API keys!

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting Prompt-Scribe Local Test Environment" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify backend environment variables
Write-Host "[1/4] Verifying backend environment..." -ForegroundColor Yellow

# Check if environment variables are set
if (-not $env:OPENAI_API_KEY) {
    Write-Host ""
    Write-Host "    ERROR: OPENAI_API_KEY not set!" -ForegroundColor Red
    Write-Host "    Please run: .\setup_env_local.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

if (-not $env:SUPABASE_URL) {
    Write-Host ""
    Write-Host "    ERROR: SUPABASE_URL not set!" -ForegroundColor Red  
    Write-Host "    Please run: .\setup_env_local.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Set defaults if not configured
if (-not $env:OPENAI_MODEL) { $env:OPENAI_MODEL = "gpt-5-mini" }
if (-not $env:ENABLE_OPENAI_INTEGRATION) { $env:ENABLE_OPENAI_INTEGRATION = "true" }
if (-not $env:DEBUG) { $env:DEBUG = "false" }
if (-not $env:LOG_LEVEL) { $env:LOG_LEVEL = "INFO" }

Write-Host "    Backend environment verified" -ForegroundColor Green
Write-Host "    - OpenAI Model: $env:OPENAI_MODEL" -ForegroundColor Gray
Write-Host "    - Integration Enabled: $env:ENABLE_OPENAI_INTEGRATION" -ForegroundColor Gray

# Step 2: Configure frontend
Write-Host ""
Write-Host "[2/4] Configuring frontend for local API..." -ForegroundColor Yellow

$frontendEnv = @"
# Prompt-Scribe Web Frontend - Local Testing
# Using local backend API with GPT-5

# Local API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# API Timeout (milliseconds)
NEXT_PUBLIC_API_TIMEOUT=30000

# Environment
NEXT_PUBLIC_ENV=development

# Debug mode
NEXT_PUBLIC_DEBUG=true
"@

$frontendEnv | Out-File -FilePath "prompt-scribe-web\.env.local" -Encoding utf8 -Force
Write-Host "    Frontend configured for http://localhost:8000" -ForegroundColor Green

# Step 3: Backend instructions
Write-Host ""
Write-Host "[3/4] Starting Backend API..." -ForegroundColor Yellow
Write-Host "    Open a NEW terminal and run:" -ForegroundColor Cyan
Write-Host "    cd D:\Prompt-Scribe" -ForegroundColor White
Write-Host "    python run_server.py" -ForegroundColor White
Write-Host ""
Write-Host "    Wait for: 'Uvicorn running on http://0.0.0.0:8000'" -ForegroundColor Gray

# Step 4: Frontend instructions
Write-Host ""
Write-Host "[4/4] Starting Frontend Dev Server..." -ForegroundColor Yellow
Write-Host "    Open another NEW terminal and run:" -ForegroundColor Cyan
Write-Host "    cd D:\Prompt-Scribe\prompt-scribe-web" -ForegroundColor White
Write-Host "    npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "    Wait for: 'Local: http://localhost:3000'" -ForegroundColor Gray

# Summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Start backend in terminal 1" -ForegroundColor White
Write-Host "  2. Start frontend in terminal 2" -ForegroundColor White
Write-Host "  3. Open: http://localhost:3000" -ForegroundColor White
Write-Host "  4. Test Inspire with GPT-5!" -ForegroundColor White
Write-Host ""
Write-Host "Test Examples:" -ForegroundColor Cyan
Write-Host "  - '1girl'" -ForegroundColor Gray
Write-Host "  - 'a girl with long blue hair'" -ForegroundColor Gray
Write-Host "  - 'sunset on the beach'" -ForegroundColor Gray
Write-Host ""
