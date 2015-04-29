import multiprocessing
import time
import sys

def one(x):
    p = multiprocessing.current_process()
    print 'Starting:', p.name, p.pid
    print x
    time.sleep(5)
    sys.stdout.flush()
    print 'Exiting :', p.name, p.pid
    sys.stdout.flush()


if __name__ == '__main__':
    for x in range(1, 3, 1):
        #print x
        n1 = multiprocessing.Process(name='one', target=one, args=(x,))
        n1.daemon = False
        n1.start()


