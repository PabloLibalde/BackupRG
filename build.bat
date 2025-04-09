@echo off
REM Ativa o ambiente virtual (se existir)
call venv\Scripts\activate.bat

echo [*] Limpando build anterior...
rmdir /s /q build
rmdir /s /q dist
del /q *.spec

echo [*] Empacotando com PyInstaller...
pyinstaller --onefile --name backup_hqbird ^
--add-data "config.conf;." ^
main.py

echo [*] Build finalizado.
echo [*] Arquivo gerado em: dist\backup_hqbird.exe

pause
