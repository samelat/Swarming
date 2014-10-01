
from multiprocessing import Process

from units.modules import tools
from units.modules.unit import Unit
from units.modules.messenger import Messenger

from units.brain.knowledge import Knowledge


class Brain(Unit):

    name = 'brain'

    def __init__(self, core):
        super(Brain, self).__init__(core)
        self._messenger = Messenger(self)
        self._knowledge = Knowledge(self)

    ''' ############################################

    '''
    def start(self):
        print('[brain] Staring')
        self.add_cmd_handler('get', self._knowledge.get)
        self.add_cmd_handler('set', self._knowledge.set)
        self._messenger.start()

    def dispatch(self, message):
        self._messenger.push(message)

    ''' ############################################
        Command Handlers
    '''
    def halt(self, message):
        self._messenger.halt()