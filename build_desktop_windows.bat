@echo off
setlocal
cd /d %~dp0
echo Building Aurevia Desktop for Windows...
if not exist node_modules (
  npm install
)
npm run build
echo.
echo Done. Check the dist folder.
pause
