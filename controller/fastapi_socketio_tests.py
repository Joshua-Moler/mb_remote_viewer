import uvicorn
from fastapi import FastAPI
import socketio

sio = socketio.AsyncServer(
    async_mode='asgi', cors_allowed_origins='http://localhost:3000')
socket_app = socketio.ASGIApp(sio)

app = FastAPI()


@app.get("/test")
async def test():
    print('test')
    return "WORKS"


@app.get('/')
async def base():
    print('base')
    return 'base'

app.mount('/', socket_app)


@sio.on('connect')
async def connect(sid, env):
    print('on connect', sid, env)


@sio.on('direct')
async def direct(sid, msg):
    print(f'direct {msg}')
    await sio.emit('event_name', msg, room=sid)


@sio.on('disconnect')
async def disconnect(sid):
    print('on disconnect', sid)


@sio.on('broadcast')
async def broadcast(sid, msg):
    print(f'broadcast {msg}')
    await sio.emit('event_name', msg)

if __name__ == '__main__':
    kwargs = {'host': '0.0.0.0', 'port': 5000}
    kwargs.update({'reload': True})
    uvicorn.run('fastapi_socketio_tests:app', **kwargs)
