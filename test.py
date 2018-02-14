import threading
import time

def t1():
    while True:
        print('11111111')
        time.sleep(10)

def t2():
    while True:
        print('22222222')
        time.sleep(10)

if __name__ == '__main__':
    a1 = threading.Thread(target=t1)
    a2 = threading.Thread(target=t2)
    a2.setDaemon(True)
    a1.start()
    a2.start()
    a1.join()
    a2.join()