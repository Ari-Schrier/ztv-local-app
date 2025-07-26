@echo off
cd "%USERPROFILE%\Desktop\ztv-local-app" || (
    echo Error: ztv-local-app directory not found on Desktop.
    exit /b 1
)

:: Pull the latest updates from the Git repository
git pull || (
    echo Error: Failed to pull the latest changes from the git repository.
    exit /b 1
)

:: Activate the virtual environment
call .venv\Scripts\activate.bat || (
    echo Error: Failed to activate virtual environment.
    exit /b 1
)

:: Run the application
python -m daily_chronicle.main || (
    echo Error: Failed to start the Daily Chronicle program.
    exit /b 1
)

echo ✅ Daily Chronicle started successfully.

:: Uncomment the line below if the window is closing too fast and you want to see error messages
:: pause
