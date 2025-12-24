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

echo -e "${YELLOW}=== Lambrk Compression Service Startup ===${NC}\n"

# Check if Python 3 is installed
echo -e "${YELLOW}Checking Python 3...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python 3 found: $PYTHON_VERSION${NC}"

# Check if pip is installed
echo -e "${YELLOW}Checking pip...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}✗ pip3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip3 found${NC}"

# Check if virtual environment exists, create if not
echo -e "${YELLOW}Checking virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip --quiet

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Failed to install dependencies${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

# Check if FFmpeg is installed
echo -e "${YELLOW}Checking FFmpeg...${NC}"
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}✗ FFmpeg is not installed${NC}"
    echo -e "${YELLOW}Please install FFmpeg: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)${NC}"
    exit 1
fi

FFMPEG_VERSION=$(ffmpeg -version | head -n 1 | awk '{print $3}')
echo -e "${GREEN}✓ FFmpeg found: $FFMPEG_VERSION${NC}"

# Check if ffprobe is installed
if ! command -v ffprobe &> /dev/null; then
    echo -e "${RED}✗ ffprobe is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ ffprobe found${NC}"

# Check PostgreSQL connection
echo -e "${YELLOW}Checking PostgreSQL connection...${NC}"
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-debarunlahiri}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-}
POSTGRES_DB=${POSTGRES_DB:-lambrk}

if [ -n "$POSTGRES_PASSWORD" ]; then
    export PGPASSWORD="$POSTGRES_PASSWORD"
fi

if psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; then
    echo -e "${GREEN}✓ PostgreSQL connection successful${NC}"
else
    echo -e "${YELLOW}⚠ Cannot connect to PostgreSQL, but continuing...${NC}"
    echo -e "${YELLOW}Please ensure PostgreSQL is running and credentials are correct${NC}"
fi

unset PGPASSWORD

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python3 scripts/migrate.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠ Database migrations had issues, but continuing...${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
PENDING_DIR=${PENDING_DIR:-/Volumes/Expansion/Lambrk/pending}
COMPLETED_DIR=${COMPLETED_DIR:-/Volumes/Expansion/Lambrk/completed}

mkdir -p "$PENDING_DIR"
mkdir -p "$COMPLETED_DIR"
echo -e "${GREEN}✓ Directories created${NC}"

# Check if process is already running
echo -e "${YELLOW}Checking if service is already running...${NC}"
if [ -f "compression_service.pid" ]; then
    OLD_PID=$(cat compression_service.pid)
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Service is already running with PID: $OLD_PID${NC}"
        echo -e "${YELLOW}Use ./stop.sh to stop it first${NC}"
        exit 1
    else
        rm -f compression_service.pid
    fi
fi

# Start the service
echo -e "${YELLOW}Starting compression service...${NC}"
API_HOST=${API_HOST:-0.0.0.0}
API_PORT=${API_PORT:-8000}

nohup uvicorn app.main:app --host "$API_HOST" --port "$API_PORT" > compression_service.log 2>&1 &
SERVICE_PID=$!

echo $SERVICE_PID > compression_service.pid

sleep 2

# Check if service started successfully
if ps -p "$SERVICE_PID" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Compression service started successfully${NC}"
    echo -e "${GREEN}  PID: $SERVICE_PID${NC}"
    echo -e "${GREEN}  URL: http://$API_HOST:$API_PORT${NC}"
    echo -e "${GREEN}  Docs: http://$API_HOST:$API_PORT/docs${NC}"
    echo -e "${GREEN}  Logs: compression_service.log${NC}"
else
    echo -e "${RED}✗ Failed to start compression service${NC}"
    echo -e "${YELLOW}Check compression_service.log for details${NC}"
    rm -f compression_service.pid
    exit 1
fi

echo -e "\n${GREEN}=== Service is running ===${NC}"

