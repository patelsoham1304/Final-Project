Set-Location "C:\Users\LENOVO\copilot-worktrees\Python\patelsoham1304-automatic-telegram"

# 1. Update app.py in worktree to completely remove Create Student
$appFile = "C:\Users\LENOVO\copilot-worktrees\Python\patelsoham1304-automatic-telegram\app.py"
if (Test-Path $appFile) {
    Copy-Item "C:\Users\LENOVO\Desktop\Python\app.py" $appFile -Force
}

# 2. Update ui folder in worktree
$uiFolder = "C:\Users\LENOVO\copilot-worktrees\Python\patelsoham1304-automatic-telegram\ui"
if (Test-Path $uiFolder) {
    Copy-Item "C:\Users\LENOVO\Desktop\Python\ui\*" $uiFolder -Recurse -Force
}

# 3. Stop old streamlit and run fresh
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
streamlit run app.py
