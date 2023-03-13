import json
from typing import List
from fastapi import FastAPI, Depends, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket
from fastapi.middleware.cors import CORSMiddleware

from starlette.requests import Request
import uvicorn
import logging

from app.api.api_v1.routers.users import users_router
from app.api.api_v1.routers.valves import valves_router
from app.api.api_v1.routers.auth import auth_router
from app.api.api_v1.routers.actions import actions_router
from app.api.api_v1.routers.logs import logs_router
from app.core import config
from app.db.session import SessionLocal
from app.core.auth import get_current_active_user
from app.core.celery_app import celery_app
from app import tasks
from app.getComPorts import getDeviceMap
import asyncio

from app.core.Valves import init as ValveInit

deviceMap = getDeviceMap()
print(deviceMap)
if "Valves" in deviceMap:
    ValveInit(deviceMap["Valves"])

app = FastAPI(
    title=config.PROJECT_NAME, docs_url="/api/docs", openapi_url="/api"
)

origins = [
    "http://bramkascloud01:9005/",
    "http://bramkascloud01:9005",
    "https://ui.apps.3slokas.com",
    "https://ui.apps.3slokas.com/",
    "https://api.apps.3slokas.com/",
    "https://api.apps.3slokas.com",
    "http://localhost"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can alter with time
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.DEBUG)   # add this line
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger("foo")


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    request.state.db.close()
    return response


@app.get("/api/v1")
async def root():
    return {"message": "Hello World"}


@app.get("/api/v1/task")
async def example_task():
    celery_app.send_task("app.tasks.example_task", args=["Hello World"])

    return {"message": "success"}

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://bramkascloud01:8888/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


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


@app.get("/api/test")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"{data}")
            # await asyncio.sleep(0.1)
            # payload = 1
            # await websocket.send_json(payload)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Routers
app.include_router(
    users_router,
    prefix="/api/v1",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)],
)
app.include_router(
    valves_router,
    prefix="/api/v1",
    tags=["valves"],
    dependencies=[Depends(get_current_active_user)],
)
app.include_router(
    actions_router,
    prefix="/api/v1",
    tags=["actions"],
    dependencies=[Depends(get_current_active_user)],
)

app.include_router(
    logs_router,
    prefix="/api/v1",
    tags=["logs"],
    dependencies=[Depends(get_current_active_user)],
)


app.include_router(auth_router, prefix="/api", tags=["auth"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0",
                debug=False, reload=True, port=8888)
