
import queue
from multiprocessing import Queue
from threading import Thread

from units.modules.unit import Unit


class Messenger:

    def __init__(self, owner):
        self._owner = owner
        self._halt = False
        
        self._messages = Queue()
        self._thread = None

    ''' 
    '''
    def _handler(self):
        while not self._halt:
            try:
                message = self._messages.get(timeout=1)
            except queue.Empty:
                continue
            print('[{0}] Message Manager - New message: {1}'.format(self._owner.unit_id(), message))
            if message['dst'] == self._owner.unit_id():
                self._owner.digest(message)
            else:
                self._owner.forward(message)

    def start(self):
        self._thread = Thread(target=self._handler)
        self._thread.start()

    def halt(self):
        self._halt = True

    def push(self, message):
        self._messages.put(message)
