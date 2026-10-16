@echo off
echo ===================================================
echo Pushing Project to GitHub: Final-Project
echo ===================================================

git remote remove origin >nul 2>&1
git remote add origin https://github.com/patelsoham1304/Final-Project.git

echo 1. Staging files...
git add .

echo 2. Committing changes...
git commit -m "feat: complete education path generator project with rich UI and database"

echo 3. Renaming branch to main...
git branch -M main

echo 4. Pushing to GitHub...
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Push failed or requires force push. Trying push with force...
    git push -u origin main --force
)

echo.
echo ===================================================
echo Done! Please check your repository on GitHub.
echo ===================================================
pause
