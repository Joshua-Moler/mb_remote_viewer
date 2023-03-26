import socketio

sio = socketio.Client()


@sio.event
def connect():
    print('connected')


@sio.event
def connect_error(data):
    print(f"connection failed: {data}")


@sio.event
def disconnect():
    print("disconnected")


@sio.on('test')
def test(data):
    print(data)


sio.connect('http://localhost:5000',
            auth={"username": "asfasfasdfasdfas", "password": "asdfasdfalsjdakfalskdjfh"})
