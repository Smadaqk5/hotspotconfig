#!/bin/bash

# MikroTik Hotspot Ticketing System - Test Runner
# Comprehensive test execution script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup environment
setup_environment() {
    print_status "Setting up test environment..."
    
    # Check if Node.js is installed
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    # Check if Python is installed
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        exit 1
    fi
    
    # Check Node.js version
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18+ is required. Current version: $(node -v)"
        exit 1
    fi
    
    print_success "Environment check passed"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Install Node.js dependencies
    if [ ! -d "node_modules" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    else
        print_status "Node.js dependencies already installed"
    fi
    
    # Install Playwright browsers
    print_status "Installing Playwright browsers..."
    npx playwright install --with-deps
    
    # Install Python dependencies
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    print_status "Activating Python virtual environment..."
    source venv/bin/activate
    
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Dependencies installed successfully"
}

# Function to setup database
setup_database() {
    print_status "Setting up test database..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run migrations
    print_status "Running database migrations..."
    python manage.py migrate
    
    # Load test data
    print_status "Loading test data..."
    python manage.py loaddata tests/fixtures/test-data.json
    
    print_success "Database setup complete"
}

# Function to start Django server
start_server() {
    print_status "Starting Django development server..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start server in background
    python manage.py runserver 8000 &
    SERVER_PID=$!
    
    # Wait for server to start
    print_status "Waiting for server to start..."
    sleep 10
    
    # Check if server is running
    if curl -s http://localhost:8000 > /dev/null; then
        print_success "Django server started successfully (PID: $SERVER_PID)"
    else
        print_error "Failed to start Django server"
        exit 1
    fi
}

# Function to stop Django server
stop_server() {
    if [ ! -z "$SERVER_PID" ]; then
        print_status "Stopping Django server (PID: $SERVER_PID)..."
        kill $SERVER_PID 2>/dev/null || true
        print_success "Django server stopped"
    fi
}

# Function to run tests
run_tests() {
    local test_type="$1"
    local browser="$2"
    local headed="$3"
    
    print_status "Running $test_type tests..."
    
    # Build test command
    local test_cmd="npx playwright test"
    
    if [ "$test_type" != "all" ]; then
        test_cmd="$test_cmd tests/$test_type.spec.ts"
    fi
    
    if [ "$browser" != "all" ]; then
        test_cmd="$test_cmd --project=$browser"
    fi
    
    if [ "$headed" = "true" ]; then
        test_cmd="$test_cmd --headed"
    fi
    
    # Run tests
    print_status "Executing: $test_cmd"
    eval $test_cmd
    
    if [ $? -eq 0 ]; then
        print_success "$test_type tests passed"
    else
        print_error "$test_type tests failed"
        return 1
    fi
}

# Function to generate report
generate_report() {
    print_status "Generating test report..."
    
    # Generate HTML report
    npx playwright show-report --host 0.0.0.0 --port 9323 &
    REPORT_PID=$!
    
    print_success "Test report available at http://localhost:9323"
    print_status "Press Ctrl+C to stop the report server"
    
    # Wait for user to stop
    wait $REPORT_PID
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    
    # Stop server
    stop_server
    
    # Kill report server if running
    if [ ! -z "$REPORT_PID" ]; then
        kill $REPORT_PID 2>/dev/null || true
    fi
    
    print_success "Cleanup complete"
}

# Function to show help
show_help() {
    echo "MikroTik Hotspot Ticketing System - Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup           Setup test environment"
    echo "  test            Run all tests"
    echo "  test-specific   Run specific test suite"
    echo "  test-browser    Run tests for specific browser"
    echo "  test-headed    Run tests in headed mode"
    echo "  report          Generate and view test report"
    echo "  clean           Clean up test environment"
    echo ""
    echo "Options:"
    echo "  --browser=BROWSER    Browser to test (chromium, firefox, webkit, all)"
    echo "  --headed             Run tests in headed mode"
    echo "  --suite=SUITE        Test suite to run (landing-page, authentication, etc.)"
    echo "  --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 test"
    echo "  $0 test --browser=chromium --headed"
    echo "  $0 test --suite=authentication"
    echo "  $0 report"
}

# Main execution
main() {
    # Parse arguments
    local command=""
    local browser="all"
    local headed="false"
    local suite=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --browser=*)
                browser="${1#*=}"
                shift
                ;;
            --headed)
                headed="true"
                shift
                ;;
            --suite=*)
                suite="${1#*=}"
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                command="$1"
                shift
                ;;
        esac
    done
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Execute command
    case $command in
        setup)
            setup_environment
            install_dependencies
            setup_database
            print_success "Test environment setup complete!"
            ;;
        test)
            setup_environment
            install_dependencies
            setup_database
            start_server
            if [ -n "$suite" ]; then
                run_tests "$suite" "$browser" "$headed"
            else
                run_tests "all" "$browser" "$headed"
            fi
            ;;
        test-specific)
            if [ -z "$suite" ]; then
                print_error "Suite not specified. Use --suite=SUITE"
                exit 1
            fi
            setup_environment
            install_dependencies
            setup_database
            start_server
            run_tests "$suite" "$browser" "$headed"
            ;;
        test-browser)
            if [ "$browser" = "all" ]; then
                print_error "Browser not specified. Use --browser=BROWSER"
                exit 1
            fi
            setup_environment
            install_dependencies
            setup_database
            start_server
            run_tests "all" "$browser" "$headed"
            ;;
        test-headed)
            setup_environment
            install_dependencies
            setup_database
            start_server
            run_tests "all" "$browser" "true"
            ;;
        report)
            generate_report
            ;;
        clean)
            cleanup
            print_success "Test environment cleaned up"
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
