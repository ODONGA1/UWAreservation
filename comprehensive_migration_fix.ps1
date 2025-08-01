# PowerShell script to fix all Django migration issues

Write-Host "🔧 Comprehensive Django Migration Fix" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow

# Step 1: Remove problematic accounts migration
$problematicFile = "accounts\migrations\0002_notificationsettings_wishlist.py"
if (Test-Path $problematicFile) {
    Remove-Item $problematicFile -Force
    Write-Host "✅ Removed problematic accounts migration" -ForegroundColor Green
}

# Step 2: Clean up all migration cache
$cacheDirs = @(
    "accounts\migrations\__pycache__",
    "tours\migrations\__pycache__"
)

foreach ($cacheDir in $cacheDirs) {
    if (Test-Path $cacheDir) {
        Remove-Item $cacheDir -Recurse -Force
        Write-Host "✅ Cleaned cache: $cacheDir" -ForegroundColor Green
    }
}

# Step 3: Show current migration structure
Write-Host "`n📁 Current Migration Structure:" -ForegroundColor Cyan

Write-Host "`nAccounts migrations:" -ForegroundColor White
Get-ChildItem "accounts\migrations\*.py" | Where-Object { $_.Name -ne "__init__.py" } | Sort-Object Name | ForEach-Object {
    Write-Host "   - $($_.Name)" -ForegroundColor Gray
}

Write-Host "`nTours migrations:" -ForegroundColor White
Get-ChildItem "tours\migrations\*.py" | Where-Object { $_.Name -ne "__init__.py" } | Sort-Object Name | ForEach-Object {
    Write-Host "   - $($_.Name)" -ForegroundColor Gray
}

Write-Host "`n🎯 Next Steps (run these commands):" -ForegroundColor Cyan
Write-Host "1. python manage.py migrate tours --fake 0002_park_image_tour_image_tour_max_participants_and_more" -ForegroundColor White
Write-Host "2. python manage.py migrate accounts --fake 0002_enhanced_profile" -ForegroundColor White
Write-Host "3. python manage.py migrate" -ForegroundColor White
Write-Host "4. python manage.py makemigrations" -ForegroundColor White

Write-Host "`n✨ Migration structure fixed!" -ForegroundColor Green
Write-Host "The above commands will:" -ForegroundColor Yellow
Write-Host "- Mark existing migrations as applied without running them" -ForegroundColor Yellow
Write-Host "- Apply any pending migrations" -ForegroundColor Yellow
Write-Host "- Allow future makemigrations to work properly" -ForegroundColor Yellow
