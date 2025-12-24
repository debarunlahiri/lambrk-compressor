#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR" || exit 1

echo -e "${YELLOW}=== Stopping Lambrk Compression Service ===${NC}\n"

# Check if PID file exists
if [ ! -f "compression_service.pid" ]; then
    echo -e "${YELLOW}⚠ PID file not found. Service may not be running.${NC}"
    
    # Try to find the process by port
    API_PORT=${API_PORT:-8000}
    PID_BY_PORT=$(lsof -ti:$API_PORT 2>/dev/null)
    
    if [ -n "$PID_BY_PORT" ]; then
        echo -e "${YELLOW}Found process on port $API_PORT: $PID_BY_PORT${NC}"
        read -p "Kill this process? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill "$PID_BY_PORT"
            echo -e "${GREEN}✓ Process $PID_BY_PORT killed${NC}"
        fi
    else
        echo -e "${YELLOW}No process found running on port $API_PORT${NC}"
    fi
    exit 0
fi

PID=$(cat compression_service.pid)

# Check if process is still running
if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}Stopping service with PID: $PID${NC}"
    kill "$PID"
    
    # Wait for process to stop
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Service stopped successfully${NC}"
            rm -f compression_service.pid
            exit 0
        fi
        sleep 1
    done
    
    # If still running, force kill
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}Service did not stop gracefully, force killing...${NC}"
        kill -9 "$PID"
        sleep 1
        
        if ! ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Service force stopped${NC}"
            rm -f compression_service.pid
        else
            echo -e "${RED}✗ Failed to stop service${NC}"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠ Process $PID is not running${NC}"
    rm -f compression_service.pid
    echo -e "${GREEN}✓ Cleaned up PID file${NC}"
fi

echo -e "\n${GREEN}=== Service stopped ===${NC}"

