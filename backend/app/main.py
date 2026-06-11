import os
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings
from .routers import weather, chat, itinerary, destinations, predictions, realtime
from .services.realtime_scheduler import get_scheduler

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.is_production() else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager untuk startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start realtime scheduler
    scheduler = get_scheduler(interval_seconds=300)  # 5 menit untuk realtime monitoring
    scheduler_task = asyncio.create_task(scheduler.start())
    print("[App] Realtime scheduler started (interval: 5 menit)")
    
    yield
    
    # Shutdown: Stop scheduler
    scheduler.stop()
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass
    print("[App] Realtime scheduler stopped")

app = FastAPI(
    title="Dihyang API",
    description="Backend API for Dihyang Web - Smart Tourism Dieng with Realtime Features",
    version="2.0.0",
    lifespan=lifespan
)

# Rate Limiter Setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration (Secure)
logger.info(f"🌍 CORS allowed origins: {settings.ALLOWED_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # ✅ Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # ✅ Specific methods
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],  # ✅ Specific headers
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"📨 Request: {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"📤 Response: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.error(f"❌ Error processing request: {str(e)}", exc_info=True)
        raise

# Custom Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "validation_error",
            "message": "Data yang dikirim tidak valid",
            "details": exc.errors() if settings.is_development() else None
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "internal_server_error",
            "message": "Terjadi kesalahan pada server",
            "details": str(exc) if settings.is_development() else None
        },
    )

# Include routers
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(itinerary.router, prefix="/api/itinerary", tags=["Itinerary"])
app.include_router(destinations.router, prefix="/api/destinations", tags=["Destinations"])
app.include_router(predictions.router, prefix="/api/ml", tags=["ML Predictions"])
app.include_router(realtime.router, prefix="/api/realtime", tags=["Realtime"])

@app.get("/")
def read_root(request: Request):
    base_url = str(request.base_url).rstrip("/")
    ws_scheme = "wss" if request.url.scheme == "https" else "ws"
    ws_host = request.url.netloc
    return {
        "message": "Welcome to Dihyang Web API v2.0 with Realtime Features",
        "docs": "/docs",
        "websocket_endpoints": {
            "weather": f"{ws_scheme}://{ws_host}/api/realtime/ws/weather",
            "predictions": f"{ws_scheme}://{ws_host}/api/realtime/ws/predictions",
            "dashboard": f"{ws_scheme}://{ws_host}/api/realtime/ws/dashboard"
        },
        "realtime_status": f"{base_url}/api/realtime/status"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "features": ["realtime", "websocket", "ml"],
        "security": {
            "cors_enabled": True,
            "rate_limiting": True,
            "api_keys_configured": bool(settings.GEMINI_API_KEY)
        }
    }
