# Copyright © 2026 Mythara Labs LLC. All rights reserved.

# Mythara Archives - Quick GitHub Push Script
# Run this after closing and reopening PowerShell (so Git is in PATH)

Write-Host "=" * 80
Write-Host "MYTHARA ARCHIVES - GITHUB PUSH"
Write-Host "=" * 80

# Configure Git
Write-Host "`n[1/6] Configuring Git..." -ForegroundColor Cyan
git config --global user.name "Herbert Velez Jr"
git config --global user.email "herbievelezjr@gmail.com"
Write-Host "[OK] Git configured" -ForegroundColor Green

# Initialize repository
Write-Host "`n[2/6] Initializing repository..." -ForegroundColor Cyan
git init
Write-Host "[OK] Repository initialized" -ForegroundColor Green

# Create .gitignore
Write-Host "`n[3/6] Creating .gitignore..." -ForegroundColor Cyan
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/
ENV/
*.egg-info/
dist/
build/

# Databases (contain sensitive data)
*.db
*.sqlite
*.sqlite3

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Sensitive
*_private.py
*_secrets.py
*.key
*.pem
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
Write-Host "[OK] .gitignore created" -ForegroundColor Green

# Add files
Write-Host "`n[4/6] Adding files..." -ForegroundColor Cyan
git add .
Write-Host "[OK] Files staged" -ForegroundColor Green

# Commit
Write-Host "`n[5/6] Creating commit..." -ForegroundColor Cyan
git commit -m "Initial commit: Mythara Archives - 15 autonomous bots, SSIP compliance, $9.45M grant pipeline"
Write-Host "[OK] Commit created" -ForegroundColor Green

# Push to GitHub
Write-Host "`n[6/6] Pushing to GitHub..." -ForegroundColor Cyan
git remote add origin https://github.com/herbievelezjr/Mythara_Archives.git
git branch -M main
git push -u origin main
Write-Host "[OK] Pushed to GitHub!" -ForegroundColor Green

Write-Host "`n" + "=" * 80
Write-Host "SUCCESS! Your code is now on GitHub:" -ForegroundColor Green
Write-Host "https://github.com/herbievelezjr/Mythara_Archives" -ForegroundColor Cyan
Write-Host "=" * 80
