
from threading import Lock
from multiprocessing import Process

from units.engine.orm import ORM
from units.modules.unit import Unit
from units.modules.messenger import Messenger

from units.uiapi.uiapi import UIApi
from units.engine.tasker import Tasker
from units.engine.knowledge import Knowledge


class Engine(Unit):

    name = 'engine'

    def __init__(self, core):
        super(Engine, self).__init__(core)
        self._messenger = Messenger(self)

        self.knowledge = None
        self.tasker = None
        self.uiapi = None


    def clean(self):
        self.knowledge = None
        self.tasker = None
        self.uiapi = None


    ''' ############################################

    '''
    def start(self):
        print('[engine] Starting')
        lock = Lock()
        self.knowledge = Knowledge(self, ORM(lock))
        self.logic = Tasker(self, ORM(lock))
        self.uiapi = UIApi(self)
        self.uiapi.start()

        self.add_cmd_handler('get', self.knowledge.get)
        self.add_cmd_handler('set', self.knowledge.set)
        self.add_cmd_handler('schedule', self.schedule)

        self._messenger.start()

        # Create 3 executor layers
        message = {'dst':'core', 'src':'engine', 'cmd':'control',
                   'params':{'action':'load', 'unit':'executor'}}
        for i in range(0, 3):
            result = self.core.dispatch(message)
            print('[engine.start] Starting executor, result: {0}'.format(result))

        # Load HTTP in the 3 layers
        message = {'dst':'core', 'src':'engine', 'cmd':'control',
                   'params':{'action':'load', 'unit':'http'}}
        for lid in range(1, 4):
            message['layer'] = lid
            result = self.core.dispatch(message)
            print('[engine.start] Starting http, result: {0}'.format(result))
            response = self.get_response(result['channel'], True)
            print('[engine.start] Unit http, ready: {0}'.format(response))

        # Register HTTP Unit (Just the unit knows its protocols)
        message = {'dst':'http', 'src':'engine', 'cmd':'register', 'params':{}, 'async':False}
        result = self.core.dispatch(message)
        response = self.get_response(result['channel'], True)

        print('[core.start] Unit Register Response: {0}'.format(response))


    def dispatch(self, message):
        result = self._messenger.push(message)
        return result

    ''' ############################################
        Command Handlers
    '''
    def halt(self, message):
        self.halt = True
        self._messenger.halt()


    def schedule(self, message):
        #print('[core.schedule] message: {0}'.format(message))
        
        ''' This is called, for example when a layer should be
            discharged, to flush all the pending messages to
            lower layers.
        '''
        self.core.dispatch(message['params'])

        return result