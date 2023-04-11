from threading import Thread
from threading import enumerate as threnum
from time import sleep


def test():
    try:
        raise ValueError
    except:
        pass
    sleep(3)


T = Thread(target=test, daemon=True)
T.start()
print(T.is_alive())

sleep(2)

print(T.is_alive())
