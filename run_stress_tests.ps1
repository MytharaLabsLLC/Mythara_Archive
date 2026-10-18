# Mythara Engine - Comprehensive Stress Test Runner
# Copyright © 2026 Mythara Labs LLC. All rights reserved.

Write-Host "==> Mythara Engine - Comprehensive Stress Test Suite" -ForegroundColor Cyan
Write-Host "Started: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss'))Z`n" -ForegroundColor Gray

# Ensure output directory exists
$outputDir = "tests\output"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Find Python executable (try multiple common locations)
$pythonPaths = @(
    "py",
    "python",
    "python3",
    "C:\Python311\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Program Files\Python311\python.exe"
)

$pythonCmd = $null
foreach ($path in $pythonPaths) {
    try {
        $version = & $path --version 2>&1
        if ($version -match "Python 3\.11") {
            $pythonCmd = $path
            Write-Host "[OK] Found Python: $version using '$path'" -ForegroundColor Green
            break
        }
    } catch {
        # Continue to next path
    }
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] Python 3.11 not found. Please ensure Python 3.11.9 is in PATH." -ForegroundColor Red
    Write-Host "You mentioned Python is running in VS Code. Please run this from VS Code terminal." -ForegroundColor Yellow
    exit 1
}

$results = @{}

# Function to run a test
function Run-Test {
    param(
        [string]$Script,
        [string]$Args,
        [string]$Description
    )
    
    Write-Host "`n$('=' * 60)" -ForegroundColor Cyan
    Write-Host "[STRESS TEST] $Description" -ForegroundColor Yellow
    Write-Host "$('=' * 60)`n" -ForegroundColor Cyan
    
    $startTime = Get-Date
    try {
        $process = Start-Process -FilePath $pythonCmd -ArgumentList "$Script $Args" -NoNewWindow -Wait -PassThru
        $exitCode = $process.ExitCode
        $duration = ((Get-Date) - $startTime).TotalSeconds
        
        Write-Host "[Duration: $([math]::Round($duration, 2))s] " -NoNewline -ForegroundColor Gray
        if ($exitCode -eq 0) {
            Write-Host "[PASS]" -ForegroundColor Green
            return $true
        } else {
            Write-Host "[FAIL] Exit code: $exitCode" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "[ERROR] $_" -ForegroundColor Red
        return $false
    }
}

# Run all stress tests with high-load parameters
Write-Host "`n[Phase 1] Determinism & Reproducibility Tests (100 iterations)" -ForegroundColor Magenta
$results['determinism'] = Run-Test "tests\run_determinism_test.py" "--iterations 100" "Determinism Tests (High Load)"

Write-Host "`n[Phase 2] Security & Leakage Probe Tests (10,000 probes)" -ForegroundColor Magenta
$results['security'] = Run-Test "tests\run_leakage_probes.py" "--count 10000" "Leakage Probe Tests (High Load)"

Write-Host "`n[Phase 3] SSIP Integrity Audit" -ForegroundColor Magenta
$results['ssip'] = Run-Test "tests\run_ssip_audit.py" "--interval 24h" "SSIP Audit"

Write-Host "`n[Phase 4] Accessibility Token Delivery Tests (1,000 tokens)" -ForegroundColor Magenta
$results['accessibility'] = Run-Test "tests\test_accessibility_delivery.py" "--count 1000" "Accessibility Tests (High Load)"

Write-Host "`n[Phase 5] Adversarial Attack & Hardening Tests (5,000 attacks)" -ForegroundColor Magenta
$results['adversarial'] = Run-Test "tests\run_adversarial_tests.py" "--count 5000" "Adversarial Tests (High Load)"

# Summary
Write-Host "`n$('=' * 60)" -ForegroundColor Cyan
Write-Host "STRESS TEST SUITE SUMMARY" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "$('=' * 60)`n" -ForegroundColor Cyan

Write-Host "Test Results:" -ForegroundColor White
foreach ($test in $results.Keys | Sort-Object) {
    $status = if ($results[$test]) { "[PASS]" } else { "[FAIL]" }
    $color = if ($results[$test]) { "Green" } else { "Red" }
    Write-Host ("  {0,-20} {1}" -f ($test + ":"), $status) -ForegroundColor $color
}

$allPassed = ($results.Values | Where-Object { -not $_ }).Count -eq 0
$passCount = ($results.Values | Where-Object { $_ }).Count
$totalCount = $results.Count

Write-Host "`nOverall: $passCount/$totalCount tests passed" -ForegroundColor $(if ($allPassed) { "Green" } else { "Yellow" })
Write-Host "Status: $(if ($allPassed) { '[ALL TESTS PASSED]' } else { '[SOME TESTS FAILED]' })" -ForegroundColor $(if ($allPassed) { "Green" } else { "Red" })
Write-Host "`nCompleted: $((Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss'))Z" -ForegroundColor Gray

Write-Host "`nResults saved to: $outputDir\" -ForegroundColor Cyan
Write-Host "   - determinism_report.txt"
Write-Host "   - leakage_probe_log.csv"
Write-Host "   - ssip_audit_report.md"
Write-Host "   - accessibility_delivery_report.csv"
Write-Host "   - adversarial_test_summary.txt"

exit $(if ($allPassed) { 0 } else { 1 })
