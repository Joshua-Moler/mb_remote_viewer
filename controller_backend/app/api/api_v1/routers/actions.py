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
from app.core.action_config import execute_action
from app.core.Pressures import *


actions_router = r = APIRouter()

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

@r.websocket("/actions/ws/pressure")
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
    "/actions/{action_name}"
)

# # /actions/cool_down
# # /actions/cool_down_action
# # /actions/pump_down


async def exec_action(
    request: Request,
    action_name: str,
    db=Depends(get_db),
    rdb=Depends(get_rdb),
    current_user=Depends(get_current_active_user)
):
    """
    Execute actions
    """
    return execute_action(action_name, current_user)
    # read yaml file
    # eexecute the action as specified
    # leak check is only for admin
    # return action_name


# @r.get(
#     "/actions/leak_check"
# )


# async def leak_check_action (
#     request: Request,
#     db=Depends(get_db),
#     current_user=Depends(get_current_active_superuser)
# ):
#     """
#     Execute actions
#     """
#     # read yaml file
#     # eexecute the action as specified
#     action_name = 'leak_check'
#     return None


# @r.get(
#     "/actions/pump_down"
# )


# async def pump_down_action (
#     request: Request,
#     db=Depends(get_db),
#     current_user=Depends(get_current_active_user)
# ):
#     """
#     Execute actions
#     """
#     # read yaml file
#     # eexecute the action as specified
#     action_name = 'pump_down'
#     exectute_action(action_name, current_user)
#     return None

