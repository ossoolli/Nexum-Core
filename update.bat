@echo off
cd c:\Users\Administrator\Downloads\Mutaz-dev-master\Nexum-Core
git pull origin main
REM Adjust the path below if your venv is named differently
call .venv\Scripts\activate.bat
pip install -r requirements.txt
pm2 restart all
echo "NEXUM UPDATED SUCCESSFULLY"
