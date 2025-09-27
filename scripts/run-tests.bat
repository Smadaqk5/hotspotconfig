@echo off
REM MikroTik Hotspot Ticketing System - Test Runner (Windows)
REM Comprehensive test execution script

setlocal enabledelayedexpansion

REM Colors for output (Windows doesn't support colors in batch, so we'll use echo)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM Function to print status
:print_status
echo %INFO% %~1
goto :eof

:print_success
echo %SUCCESS% %~1
goto :eof

:print_warning
echo %WARNING% %~1
goto :eof

:print_error
echo %ERROR% %~1
goto :eof

REM Function to check if command exists
:command_exists
where %1 >nul 2>&1
if %errorlevel% equ 0 (
    set "command_exists_result=true"
) else (
    set "command_exists_result=false"
)
goto :eof

REM Function to setup environment
:setup_environment
call :print_status "Setting up test environment..."

REM Check if Node.js is installed
call :command_exists node
if "%command_exists_result%"=="false" (
    call :print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit /b 1
)

REM Check if Python is installed
call :command_exists python
if "%command_exists_result%"=="false" (
    call :print_error "Python is not installed. Please install Python 3.11+ first."
    exit /b 1
)

call :print_success "Environment check passed"
goto :eof

REM Function to install dependencies
:install_dependencies
call :print_status "Installing dependencies..."

REM Install Node.js dependencies
if not exist "node_modules" (
    call :print_status "Installing Node.js dependencies..."
    npm install
) else (
    call :print_status "Node.js dependencies already installed"
)

REM Install Playwright browsers
call :print_status "Installing Playwright browsers..."
npx playwright install --with-deps

REM Install Python dependencies
if not exist "venv" (
    call :print_status "Creating Python virtual environment..."
    python -m venv venv
)

call :print_status "Activating Python virtual environment..."
call venv\Scripts\activate.bat

call :print_status "Installing Python dependencies..."
pip install -r requirements.txt

call :print_success "Dependencies installed successfully"
goto :eof

REM Function to setup database
:setup_database
call :print_status "Setting up test database..."

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run migrations
call :print_status "Running database migrations..."
python manage.py migrate

REM Load test data
call :print_status "Loading test data..."
python manage.py loaddata tests\fixtures\test-data.json

call :print_success "Database setup complete"
goto :eof

REM Function to start Django server
:start_server
call :print_status "Starting Django development server..."

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start server in background
start /b python manage.py runserver 8000

REM Wait for server to start
call :print_status "Waiting for server to start..."
timeout /t 10 /nobreak >nul

REM Check if server is running
curl -s http://localhost:8000 >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Django server started successfully"
) else (
    call :print_error "Failed to start Django server"
    exit /b 1
)
goto :eof

REM Function to stop Django server
:stop_server
call :print_status "Stopping Django server..."
taskkill /f /im python.exe >nul 2>&1
call :print_success "Django server stopped"
goto :eof

REM Function to run tests
:run_tests
set "test_type=%~1"
set "browser=%~2"
set "headed=%~3"

call :print_status "Running %test_type% tests..."

REM Build test command
set "test_cmd=npx playwright test"

if not "%test_type%"=="all" (
    set "test_cmd=%test_cmd% tests\%test_type%.spec.ts"
)

if not "%browser%"=="all" (
    set "test_cmd=%test_cmd% --project=%browser%"
)

if "%headed%"=="true" (
    set "test_cmd=%test_cmd% --headed"
)

REM Run tests
call :print_status "Executing: %test_cmd%"
%test_cmd%

if %errorlevel% equ 0 (
    call :print_success "%test_type% tests passed"
) else (
    call :print_error "%test_type% tests failed"
    exit /b 1
)
goto :eof

REM Function to generate report
:generate_report
call :print_status "Generating test report..."

REM Generate HTML report
start /b npx playwright show-report --host 0.0.0.0 --port 9323

call :print_success "Test report available at http://localhost:9323"
call :print_status "Press any key to stop the report server"
pause >nul
goto :eof

REM Function to cleanup
:cleanup
call :print_status "Cleaning up..."

REM Stop server
call :stop_server

call :print_success "Cleanup complete"
goto :eof

REM Function to show help
:show_help
echo MikroTik Hotspot Ticketing System - Test Runner
echo.
echo Usage: %0 [OPTIONS] [COMMAND]
echo.
echo Commands:
echo   setup           Setup test environment
echo   test            Run all tests
echo   test-specific   Run specific test suite
echo   test-browser    Run tests for specific browser
echo   test-headed     Run tests in headed mode
echo   report          Generate and view test report
echo   clean           Clean up test environment
echo.
echo Options:
echo   --browser=BROWSER    Browser to test (chromium, firefox, webkit, all)
echo   --headed             Run tests in headed mode
echo   --suite=SUITE        Test suite to run (landing-page, authentication, etc.)
echo   --help               Show this help message
echo.
echo Examples:
echo   %0 setup
echo   %0 test
echo   %0 test --browser=chromium --headed
echo   %0 test --suite=authentication
echo   %0 report
goto :eof

REM Main execution
:main
set "command=%1"
set "browser=all"
set "headed=false"
set "suite="

REM Parse arguments
:parse_args
if "%~1"=="" goto :execute_command
if "%~1"=="--browser=*" (
    set "browser=%~1"
    set "browser=!browser:~10!"
    shift
    goto :parse_args
)
if "%~1"=="--headed" (
    set "headed=true"
    shift
    goto :parse_args
)
if "%~1"=="--suite=*" (
    set "suite=%~1"
    set "suite=!suite:~8!"
    shift
    goto :parse_args
)
if "%~1"=="--help" (
    call :show_help
    exit /b 0
)
if "%~1"=="setup" (
    set "command=setup"
    shift
    goto :parse_args
)
if "%~1"=="test" (
    set "command=test"
    shift
    goto :parse_args
)
if "%~1"=="test-specific" (
    set "command=test-specific"
    shift
    goto :parse_args
)
if "%~1"=="test-browser" (
    set "command=test-browser"
    shift
    goto :parse_args
)
if "%~1"=="test-headed" (
    set "command=test-headed"
    shift
    goto :parse_args
)
if "%~1"=="report" (
    set "command=report"
    shift
    goto :parse_args
)
if "%~1"=="clean" (
    set "command=clean"
    shift
    goto :parse_args
)
shift
goto :parse_args

:execute_command
if "%command%"=="setup" (
    call :setup_environment
    call :install_dependencies
    call :setup_database
    call :print_success "Test environment setup complete!"
    goto :end
)
if "%command%"=="test" (
    call :setup_environment
    call :install_dependencies
    call :setup_database
    call :start_server
    if not "%suite%"=="" (
        call :run_tests "%suite%" "%browser%" "%headed%"
    ) else (
        call :run_tests "all" "%browser%" "%headed%"
    )
    goto :end
)
if "%command%"=="test-specific" (
    if "%suite%"=="" (
        call :print_error "Suite not specified. Use --suite=SUITE"
        exit /b 1
    )
    call :setup_environment
    call :install_dependencies
    call :setup_database
    call :start_server
    call :run_tests "%suite%" "%browser%" "%headed%"
    goto :end
)
if "%command%"=="test-browser" (
    if "%browser%"=="all" (
        call :print_error "Browser not specified. Use --browser=BROWSER"
        exit /b 1
    )
    call :setup_environment
    call :install_dependencies
    call :setup_database
    call :start_server
    call :run_tests "all" "%browser%" "%headed%"
    goto :end
)
if "%command%"=="test-headed" (
    call :setup_environment
    call :install_dependencies
    call :setup_database
    call :start_server
    call :run_tests "all" "%browser%" "true"
    goto :end
)
if "%command%"=="report" (
    call :generate_report
    goto :end
)
if "%command%"=="clean" (
    call :cleanup
    call :print_success "Test environment cleaned up"
    goto :end
)
if "%command%"=="" (
    call :show_help
    goto :end
)

call :print_error "Unknown command: %command%"
call :show_help
exit /b 1

:end
endlocal
