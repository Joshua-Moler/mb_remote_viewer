from fastapi import APIRouter, Request, Depends, Response, encoders
from fastapi import FastAPI, Depends, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket
import typing as t
import asyncio
from app.db.session import get_db, get_rdb
# from app.db.crud import (
#     get_actions,
#     get_valve,
#     create_valve,
#     delete_valve,
#     edit_valve,
# )
# from app.db.schemas import ValveCreate, ValveEdit, Valve, ValveOut
from app.core.auth import get_current_active_user, get_current_active_superuser
from app.core.Pressures import *
from app.db.crud import (
    get_logs_data_by_id,
    get_logs_data
)



logs_router = r = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@r.websocket("/logs/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # data = await websocket.receive_text()
            # await websocket.send_text(f"Message text was : {data}")
            # await asyncio.sleep(0.1)
            payload = {
                'pressure' : check_pressure()
            }
            await websocket.send_json({'Ok': 1})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@r.get(
    "/logs/{run_id}"
)

# # /actions/cool_down
# # /actions/cool_down_action
# # /actions/pump_down


async def get_logs_by_id (
    request: Request,
    run_id: str,
    db=Depends(get_db),
    rdb=Depends(get_rdb),
    current_user=Depends(get_current_active_user)
):
    """
    Get Logs by RUN_ID
    """
    return get_logs_data_by_id (run_id, current_user)


@r.get(
    "/logs"
)


async def get_logs(
    request: Request,
    db=Depends(get_db),
    rdb=Depends(get_rdb),
    current_user=Depends(get_current_active_user)
):
    """
    Get Logs
    """

    print ("Getting Logs")

    return get_logs_data (current_user)



