from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from app.config import settings
from api.routes import router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lambrk Compression Service",
    description="Video compression service using FFmpeg",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Lambrk Compression Service")
    logger.info(f"Pending directory: {settings.PENDING_DIR}")
    logger.info(f"Completed directory: {settings.COMPLETED_DIR}")
    
    import os
    os.makedirs(settings.PENDING_DIR, exist_ok=True)
    os.makedirs(settings.COMPLETED_DIR, exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Lambrk Compression Service")
    from services.database import DatabaseService
    DatabaseService.close_all()


@app.get("/")
async def root():
    return {
        "service": "Lambrk Compression Service",
        "status": "running",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )

