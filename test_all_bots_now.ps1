# Copyright © 2026 Mythara Labs LLC. All rights reserved.

# Test All 16 Bots - Run them all now to verify they work

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "MYTHARA - TESTING ALL 16 BOTS NOW" -ForegroundColor Yellow
Write-Host "=" * 80 -ForegroundColor Cyan

$pythonPath = "C:\Users\HVele\OneDrive\Desktop\Mythara_Archive\.venv\Scripts\python.exe"
$workingDir = "C:\Users\HVele\OneDrive\Desktop\Mythara_Archive"

cd $workingDir

# Test each bot one by one
$bots = @(
    @{Name="Finance VP"; Script="Commercial\run_finance_vp.py"},
    @{Name="Sales/Marketing VP"; Script="Commercial\run_sales_vp.py"},
    @{Name="Customer Success VP"; Script="Commercial\run_customer_success_vp.py"},
    @{Name="DevOps VP"; Script="Commercial\run_devops_vp.py"},
    @{Name="Logistics VP"; Script="Commercial\run_logistics_vp.py"},
    @{Name="Public Affairs VP"; Script="Commercial\run_public_affairs_vp.py"},
    @{Name="HR VP"; Script="run_hr_vp.py"},
    @{Name="Support Bot"; Script="run_support_bot.py"},
    @{Name="International Sales VP"; Script="run_international_sales_vp.py"},
    @{Name="DevSecOps VP"; Script="run_devsecops_vp.py"},
    @{Name="SEO Bot"; Script="run_seo_bot.py"},
    @{Name="Researcher Bot"; Script="run_researcher_bot.py"},
    @{Name="Grant Writer Bot"; Script="run_grant_writer_bot.py"},
    @{Name="SBGA Bot"; Script="run_sbga_bot.py"},
    @{Name="Accounting VP"; Script="run_accounting_vp.py"},
    @{Name="Sigma Six Blackbelt"; Script="run_sigma_six_blackbelt.py"}
)

$counter = 1
foreach ($bot in $bots) {
    Write-Host "`n[$counter/16] Running $($bot.Name)..." -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Gray
    
    & $pythonPath $bot.Script
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $($bot.Name) completed successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] $($bot.Name) failed with exit code $LASTEXITCODE" -ForegroundColor Red
    }
    
    Write-Host "=" * 80 -ForegroundColor Gray
    $counter++
}

Write-Host "`n" + "=" * 80 -ForegroundColor Cyan
Write-Host "ALL 16 BOTS TESTED!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
