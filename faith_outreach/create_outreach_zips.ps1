# Mythara Faith Outreach - ZIP Package Generator
# Copyright © 2026 Mythara Labs LLC. All rights reserved.
# Creates two ZIP files for the St. Jude outreach sequence

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Mythara Faith Outreach ZIP Generator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set paths
$rootPath = $PSScriptRoot
$firstEmailPath = Join-Path $rootPath "FirstEmail_Donation"
$secondEmailPath = Join-Path $rootPath "SecondEmail_FollowUp"
$outputPath = $rootPath

# Verify directories exist
if (-not (Test-Path $firstEmailPath)) {
    Write-Host "ERROR: FirstEmail_Donation folder not found at: $firstEmailPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $secondEmailPath)) {
    Write-Host "ERROR: SecondEmail_FollowUp folder not found at: $secondEmailPath" -ForegroundColor Red
    exit 1
}

# Create ZIP files
Write-Host "Creating ZIP packages..." -ForegroundColor Yellow
Write-Host ""

try {
    # Package 1: First Email (Donation)
    $zip1Name = "FirstEmail_Donation_StJude.zip"
    $zip1Path = Join-Path $outputPath $zip1Name
    
    Write-Host "Packaging: $zip1Name" -ForegroundColor Green
    Write-Host "  Source: $firstEmailPath" -ForegroundColor Gray
    Write-Host "  Output: $zip1Path" -ForegroundColor Gray
    
    # Remove existing ZIP if present
    if (Test-Path $zip1Path) {
        Remove-Item $zip1Path -Force
    }
    
    # Create ZIP using Compress-Archive
    Compress-Archive -Path "$firstEmailPath\*" -DestinationPath $zip1Path -CompressionLevel Optimal
    
    $zip1Size = (Get-Item $zip1Path).Length / 1KB
    Write-Host "  ✓ Created successfully ($([math]::Round($zip1Size, 2)) KB)" -ForegroundColor Green
    Write-Host ""
    
    # Package 2: Second Email (Follow-Up)
    $zip2Name = "SecondEmail_FollowUp_StJude.zip"
    $zip2Path = Join-Path $outputPath $zip2Name
    
    Write-Host "Packaging: $zip2Name" -ForegroundColor Green
    Write-Host "  Source: $secondEmailPath" -ForegroundColor Gray
    Write-Host "  Output: $zip2Path" -ForegroundColor Gray
    
    # Remove existing ZIP if present
    if (Test-Path $zip2Path) {
        Remove-Item $zip2Path -Force
    }
    
    # Create ZIP using Compress-Archive
    Compress-Archive -Path "$secondEmailPath\*" -DestinationPath $zip2Path -CompressionLevel Optimal
    
    $zip2Size = (Get-Item $zip2Path).Length / 1KB
    Write-Host "  ✓ Created successfully ($([math]::Round($zip2Size, 2)) KB)" -ForegroundColor Green
    Write-Host ""
    
    # Summary
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "ZIP Generation Complete!" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Two ZIP files created:" -ForegroundColor White
    Write-Host "  1. $zip1Name - Initial gift donation packet" -ForegroundColor White
    Write-Host "  2. $zip2Name - Follow-up partnership offer" -ForegroundColor White
    Write-Host ""
    Write-Host "Location: $outputPath" -ForegroundColor White
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Test both ZIPs by extracting them" -ForegroundColor Gray
    Write-Host "  2. Verify all files render correctly" -ForegroundColor Gray
    Write-Host "  3. Send FirstEmail_Donation_StJude.zip with initial outreach" -ForegroundColor Gray
    Write-Host "  4. Wait 7-14 days, then send SecondEmail_FollowUp_StJude.zip" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Package Contents:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "FirstEmail_Donation_StJude.zip:" -ForegroundColor Cyan
    Write-Host "  • CoverLetter.txt - Story-led donation offer" -ForegroundColor Gray
    Write-Host "  • BlessingScale.md - Biblical continuum framework" -ForegroundColor Gray
    Write-Host "  • SoulCradle_v1_Summary.md - Technical specification" -ForegroundColor Gray
    Write-Host "  • TieredOfferings.md - Pricing (Gift → Neurosymbolic → Mythic-Resonant)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "SecondEmail_FollowUp_StJude.zip:" -ForegroundColor Cyan
    Write-Host "  • FollowUpLetter.txt - Professional partnership inquiry" -ForegroundColor Gray
    Write-Host "  • CompensationFramework.md - Hybrid model (gift + scaffolding)" -ForegroundColor Gray
    Write-Host "  • TrainingModuleOutline.md - 4-hour workshop outline" -ForegroundColor Gray
    Write-Host "  • SpeakerNotes.md - What to say during training" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "ERROR: Failed to create ZIP files" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "✓ All operations completed successfully" -ForegroundColor Green
Write-Host ""
