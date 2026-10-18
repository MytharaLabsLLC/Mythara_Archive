# Run Mythara Tutorial Video Bot
# Copyright © 2026 Mythara Labs LLC. All rights reserved.

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "🎬 MYTHARA TUTORIAL VIDEO BOT" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "✅ Tutorial audio files generated!" -ForegroundColor Green
Write-Host "📁 Location: tutorial_audio/`n" -ForegroundColor Yellow

Write-Host "Generated files:" -ForegroundColor White
Get-ChildItem tutorial_audio | ForEach-Object {
    Write-Host "  📄 $($_.Name)" -ForegroundColor Gray
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "QUICK START - Record First Video NOW" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "Option 1: EASIEST (2 minutes)" -ForegroundColor Yellow
Write-Host "  1. Press Windows + G (Xbox Game Bar)"
Write-Host "  2. Click Record button"
Write-Host "  3. Open: https://mytharaarchive-production.up.railway.app"
Write-Host "  4. Play: tutorial_audio/01_what_is_mythara.mp3"
Write-Host "  5. Navigate page while audio plays"
Write-Host "  6. Press Windows + Alt + R to stop"
Write-Host "  7. Video saved to: $env:USERPROFILE\Videos\Captures`n"

Write-Host "Option 2: Play Audio Now" -ForegroundColor Yellow
Write-Host "  Listen to the voiceover first:`n"

$choice = Read-Host "Play first tutorial audio? (y/n)"

if ($choice -eq 'y') {
    Write-Host "`n🎤 Playing: 01_what_is_mythara.mp3`n" -ForegroundColor Green
    Start-Process "tutorial_audio\01_what_is_mythara.mp3"
    Start-Sleep -Seconds 2
    Write-Host "💡 TIP: While listening, think about how you'll show the pricing page`n" -ForegroundColor Cyan
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

Write-Host "1. Read slide guides:" -ForegroundColor White
Write-Host "   - tutorial_audio/01_what_is_mythara_SLIDES.txt"
Write-Host "   - tutorial_audio/02_pilot_signup_SLIDES.txt"
Write-Host "   - tutorial_audio/03_soul_cradle_SLIDES.txt`n"

Write-Host "2. Record videos (choose easiest method)`n"

Write-Host "3. Upload to YouTube:" -ForegroundColor White
Write-Host "   - Set to 'Unlisted' (only people with link)"
Write-Host "   - Copy embed code (Share → Embed)`n"

Write-Host "4. Embed in pricing page:" -ForegroundColor White
Write-Host "   - Edit: core/static/pricing.html"
Write-Host "   - Add <iframe> embed code"
Write-Host "   - Commit and push to Railway`n"

Write-Host "5. Update chatbot:" -ForegroundColor White
Write-Host "   - Change training response to reference videos"
Write-Host "   - Add 'Watch 2-min video' quick reply button`n"

Write-Host "============================================`n" -ForegroundColor Cyan

$open = Read-Host "Open tutorial_audio folder? (y/n)"
if ($open -eq 'y') {
    explorer tutorial_audio
}

Write-Host "`n✨ You've got this! First video = 2 minutes of work.`n" -ForegroundColor Green
