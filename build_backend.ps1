Write-Host "Installing dependencies..."
.\backend\venv\Scripts\pip.exe install pyinstaller
.\backend\venv\Scripts\pip.exe install -r requirements.txt

Write-Host "Cleaning previous builds..."
Remove-Item -Recurse -Force .\build -ErrorAction Ignore
Remove-Item -Recurse -Force .\backend\dist -ErrorAction Ignore
Remove-Item -Force .\backend.spec -ErrorAction Ignore

Write-Host "Building backend with PyInstaller..."
.\backend\venv\Scripts\pyinstaller.exe `
    --name backend `
    --onefile `
    --hidden-import uvicorn `
    --hidden-import fastapi `
    --hidden-import pydantic `
    --hidden-import starlette `
    --hidden-import anyio `
    --hidden-import scapy `
    --hidden-import scapy.layers.ipsec `
    --hidden-import scapy.layers.inet `
    --hidden-import sklearn `
    --hidden-import xgboost `
    --hidden-import pandas `
    --hidden-import joblib `
    --hidden-import fpdf `
    --hidden-import sqlite3 `
    --hidden-import passlib `
    --hidden-import win32timezone `
    --hidden-import win32serviceutil `
    --hidden-import win32service `
    --hidden-import win32event `
    --hidden-import servicemanager `
    --add-data "backend/templates;backend/templates" `
    --add-data "ml/model;ml/model" `
    --distpath .\backend\dist `
    --clean `
    .\windows_service.py

Write-Host "Done! Executable is at backend\dist\backend.exe"
