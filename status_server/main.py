from statusServer import app
from flask_socketio import SocketIO
from flask_socketio import ConnectionRefusedError
from flask import request

socketio = SocketIO(app)


@socketio.on('connect')
def test_connect(auth):
    print('')
    print(auth, request.sid)
    print('')


if __name__ == '__main__':
    socketio.run(app)
