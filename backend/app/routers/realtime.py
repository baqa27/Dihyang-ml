"""
DITA Realtime WebSocket Router
Push notifikasi cuaca realtime ke frontend.
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from datetime import datetime

router = APIRouter()

# Connection manager untuk broadcast ke semua client
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] Client connected - Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WebSocket] Client disconnected - Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message ke semua connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        # Cleanup disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

# Managers untuk berbagai channel
weather_manager = ConnectionManager()
predictions_manager = ConnectionManager()
dashboard_manager = ConnectionManager()


@router.websocket("/ws/weather")
async def weather_websocket(websocket: WebSocket):
    """WebSocket untuk weather updates saja."""
    await weather_manager.connect(websocket)
    
    try:
        from ..services.realtime_scheduler import get_scheduler
        scheduler = get_scheduler()
        
        # Send initial data
        latest = scheduler.get_latest_data()
        if latest:
            await websocket.send_json({
                "type": "weather_initial",
                "timestamp": datetime.now().isoformat(),
                "data": latest.get("current", {}),
            })
        
        # Keep-alive loop
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data == "get_latest":
                    latest = scheduler.get_latest_data()
                    if latest:
                        await websocket.send_json({
                            "type": "weather_update",
                            "timestamp": datetime.now().isoformat(),
                            "data": latest.get("current", {}),
                        })
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        weather_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket Weather] Error: {e}")
        weather_manager.disconnect(websocket)


@router.websocket("/ws/predictions")
async def predictions_websocket(websocket: WebSocket):
    """WebSocket untuk ML predictions updates."""
    await predictions_manager.connect(websocket)
    
    try:
        from ..models.predict import get_predictor
        predictor = get_predictor()
        
        # Send initial predictions
        from ..routers.predictions import _run_predictions
        _, current_temp, live, _, temp_pred, rain_pred, risk_pred = await _run_predictions()
        
        await websocket.send_json({
            "type": "predictions_initial",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "temperature": temp_pred,
                "rain": rain_pred,
                "risk": risk_pred,
            }
        })
        
        # Keep-alive loop
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data == "get_latest":
                    _, current_temp, live, _, temp_pred, rain_pred, risk_pred = await _run_predictions()
                    await websocket.send_json({
                        "type": "predictions_update",
                        "timestamp": datetime.now().isoformat(),
                        "data": {
                            "temperature": temp_pred,
                            "rain": rain_pred,
                            "risk": risk_pred,
                        }
                    })
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        predictions_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket Predictions] Error: {e}")
        predictions_manager.disconnect(websocket)


@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """WebSocket untuk dashboard - kombinasi weather + predictions."""
    await dashboard_manager.connect(websocket)
    
    try:
        # Send initial dashboard data
        from ..routers.predictions import _run_predictions
        now, current_temp, live, predictor, temp_pred, rain_pred, risk_pred = await _run_predictions()
        
        await websocket.send_json({
            "type": "dashboard_initial",
            "timestamp": now.isoformat(),
            "data": {
                "current": {
                    "temperature": current_temp,
                    "precipitation": live["precipitation"],
                    "humidity": live["humidity"],
                    "visibility_km": live["visibility_km"],
                    "windspeed": live["windspeed"],
                },
                "predictions": {
                    "temperature": temp_pred,
                    "rain": rain_pred,
                    "risk": risk_pred,
                }
            }
        })
        
        # Keep-alive loop dengan auto-update setiap 5 menit
        last_update = datetime.now()
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data == "get_latest":
                    now, current_temp, live, predictor, temp_pred, rain_pred, risk_pred = await _run_predictions()
                    await websocket.send_json({
                        "type": "dashboard_update",
                        "timestamp": now.isoformat(),
                        "data": {
                            "current": {
                                "temperature": current_temp,
                                "precipitation": live["precipitation"],
                                "humidity": live["humidity"],
                                "visibility_km": live["visibility_km"],
                                "windspeed": live["windspeed"],
                            },
                            "predictions": {
                                "temperature": temp_pred,
                                "rain": rain_pred,
                                "risk": risk_pred,
                            }
                        }
                    })
                    last_update = datetime.now()
            except asyncio.TimeoutError:
                # Auto-update setiap 5 menit
                if (datetime.now() - last_update).seconds >= 300:
                    now, current_temp, live, predictor, temp_pred, rain_pred, risk_pred = await _run_predictions()
                    await websocket.send_json({
                        "type": "dashboard_update",
                        "timestamp": now.isoformat(),
                        "data": {
                            "current": {
                                "temperature": current_temp,
                                "precipitation": live["precipitation"],
                                "humidity": live["humidity"],
                                "visibility_km": live["visibility_km"],
                                "windspeed": live["windspeed"],
                            },
                            "predictions": {
                                "temperature": temp_pred,
                                "rain": rain_pred,
                                "risk": risk_pred,
                            }
                        }
                    })
                    last_update = datetime.now()
                else:
                    await websocket.send_json({"type": "ping"})
                
    except WebSocketDisconnect:
        dashboard_manager.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket Dashboard] Error: {e}")
        dashboard_manager.disconnect(websocket)


@router.get("/status")
async def get_realtime_status():
    """Status realtime monitoring system."""
    from ..services.realtime_scheduler import get_scheduler
    from ..services.auto_retrain import get_retrainer
    
    scheduler = get_scheduler()
    retrainer = get_retrainer()
    
    return {
        "scheduler": scheduler.get_status(),
        "auto_retrain": retrainer.get_status(),
        "connected_clients": {
            "weather": len(weather_manager.active_connections),
            "predictions": len(predictions_manager.active_connections),
            "dashboard": len(dashboard_manager.active_connections),
            "total": len(weather_manager.active_connections) + 
                    len(predictions_manager.active_connections) + 
                    len(dashboard_manager.active_connections),
        },
        "websocket_endpoints": {
            "weather": "/api/realtime/ws/weather",
            "predictions": "/api/realtime/ws/predictions",
            "dashboard": "/api/realtime/ws/dashboard",
        }
    }


@router.post("/retrain")
async def trigger_retrain():
    """
    Trigger manual retrain model dengan data terbaru.
    PERHATIAN: Proses ini bisa memakan waktu 5-10 menit.
    """
    from ..services.auto_retrain import get_retrainer
    import asyncio
    
    retrainer = get_retrainer()
    
    # Run retrain di background
    async def run_retrain():
        return retrainer.run_full_retrain()
    
    # Start background task
    asyncio.create_task(run_retrain())
    
    return {
        "message": "Retrain pipeline started in background",
        "status": "running",
        "estimated_time": "5-10 minutes",
        "check_status": "/api/realtime/status"
    }


async def broadcast_weather_update(data: dict):
    """Broadcast weather update ke semua weather clients."""
    await weather_manager.broadcast({
        "type": "weather_update",
        "timestamp": datetime.now().isoformat(),
        "data": data,
    })


async def broadcast_predictions_update(predictions: dict):
    """Broadcast predictions update ke semua predictions clients."""
    await predictions_manager.broadcast({
        "type": "predictions_update",
        "timestamp": datetime.now().isoformat(),
        "data": predictions,
    })


async def broadcast_dashboard_update(dashboard_data: dict):
    """Broadcast dashboard update ke semua dashboard clients."""
    await dashboard_manager.broadcast({
        "type": "dashboard_update",
        "timestamp": datetime.now().isoformat(),
        "data": dashboard_data,
    })
