import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import weather, chat, itinerary, destinations, predictions

app = FastAPI(
    title="Dihyang API",
    description="Backend API for Dihyang Web - Smart Tourism Dieng",
    version="1.0.0"
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

@app.get("/")
def read_root():
    return {"message": "Welcome to Dihyang Web API. Visit /docs for documentation."}
