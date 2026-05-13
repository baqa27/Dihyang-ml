import os
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import weather, chat, itinerary, destinations, predictions, realtime
from .services.realtime_scheduler import get_scheduler

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

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development. In prod, use specific origins.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(itinerary.router, prefix="/api/itinerary", tags=["Itinerary"])
app.include_router(destinations.router, prefix="/api/destinations", tags=["Destinations"])
app.include_router(predictions.router, prefix="/api/ml", tags=["ML Predictions"])
app.include_router(realtime.router, prefix="/api/realtime", tags=["Realtime"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Dihyang Web API v2.0 with Realtime Features",
        "docs": "/docs",
        "websocket_endpoints": {
            "weather": "ws://localhost:8000/api/realtime/ws/weather",
            "predictions": "ws://localhost:8000/api/realtime/ws/predictions",
            "dashboard": "ws://localhost:8000/api/realtime/ws/dashboard"
        },
        "realtime_status": "/api/realtime/status"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0", "features": ["realtime", "websocket", "ml"]}
