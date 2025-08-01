# PowerShell script to fix Django migration conflicts

Write-Host "🔧 Fixing Django migration conflicts..." -ForegroundColor Yellow

# Step 1: Remove conflicting migration file
$conflictingFile = "accounts\migrations\0002_notificationsettings_wishlist.py"
if (Test-Path $conflictingFile) {
    Remove-Item $conflictingFile -Force
    Write-Host "✅ Removed conflicting migration file" -ForegroundColor Green
} else {
    Write-Host "⚠️  Conflicting migration file not found" -ForegroundColor Yellow
}

# Step 2: Clean up cache
$cacheDir = "accounts\migrations\__pycache__"
if (Test-Path $cacheDir) {
    Remove-Item $cacheDir -Recurse -Force
    Write-Host "✅ Cleaned up cache directory" -ForegroundColor Green
}

# Step 3: Show remaining files
Write-Host "`n📁 Remaining migration files:" -ForegroundColor Cyan
Get-ChildItem "accounts\migrations\*.py" | Where-Object { $_.Name -ne "__init__.py" } | Sort-Object Name | ForEach-Object {
    Write-Host "   - $($_.Name)" -ForegroundColor White
}

Write-Host "`n🎯 Next steps:" -ForegroundColor Cyan
Write-Host "1. python manage.py migrate accounts --fake 0002_enhanced_profile" -ForegroundColor White
Write-Host "2. python manage.py migrate accounts" -ForegroundColor White
Write-Host "3. python manage.py makemigrations" -ForegroundColor White

Write-Host "`n✨ Migration conflict fix complete!" -ForegroundColor Green
