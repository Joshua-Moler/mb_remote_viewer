import socketio

mgr = socketio.RedisManager('redis://')
sio = socketio.Server()


@sio.event
def connect(sid, environ, auth):
    print('connect ', sid)


@sio.on("test")
def testEvent(sid, data):
    print(sid, data)
