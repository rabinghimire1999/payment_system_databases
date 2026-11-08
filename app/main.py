"""Main entry point for the fps Database API.

This module configures the FastAPI application, including CORS middleware,
global exception handling, and routing. It also handles database connection
verification on startup.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Verify database connection on startup.

    Attempts to connect to the database and execute a simple query to ensure
    connectivity. Includes a small retry loop for Docker environments.
    """
    import time
    max_retries = 5
    for i in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection verified successfully.")
            return
        except Exception as e:
            if i < max_retries - 1:
                logger.warning(f"Database not ready (attempt {i+1}/{max_retries}). Retrying in 2s...")
                time.sleep(2)
            else:
                logger.critical(f"Could not connect to database after {max_retries} attempts: {e}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to catch unhandled errors.

    Logs the exception with stack trace and returns a standardized JSON 500 response.

    Args:
        request: The incoming FastAPI Request object.
        exc: The raised Exception.

    Returns:
        JSONResponse: A 500 status response with a generic error message.
    """
    logger.error(f"Unhandled exception occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please contact the administrator."},
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint returning basic API metadata.

    Useful for UI to verify API connection.

    Returns:
        dict: A dictionary containing project name, version, documentation path, and status.
    """
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Simple health check endpoint for monitoring.

    Returns:
        dict: A dictionary indicating the service status is 'ok'.
    """
    return {"status": "ok"}
