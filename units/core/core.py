
from units.unit import Unit
from units.core.task_mgr import TaskMgr
from units.core.message_mgr import MessageMgr

from units.http import HTTP
from units.event_mgr import EventMgr
from units.json_iface import JSONIface
from units.dictionary_mgr import DictionaryMgr


class Core(Unit):

    name = 'core'

    def __init__(self):
        super(Core, self).__init__()
        self._task_mgr    = TaskMgr(self)
        self._message_mgr = MessageMgr(self)

        ''' TODO: It is better if we take the list of
            modules to load from a config file or something
            like that (do not hardcode them).
        '''
        self.units = {}
        self.units[JSONIface.name] = JSONIface(self)
        self.units[HTTP.name] = HTTP(self)

    ''' ############################################
        Core Unit Commands
        ############################################
    '''
    def _sync_halt(self, message):
        print('[i] Halting units...')
        for unit in self.units.values():
            unit.halt()
        print('[i] Halting Message Manager...')
        self._message_mgr.halt()

    ''' ############################################
    '''
    def forward(self, message):
        if message['dst'] in self.units:
            self.units[message['dst']].dispatch(message)
        # TODO: We could generate a error here, informing that
        #       the dst module does not exist.

    def dispatch(self, message):
        self._message_mgr.push(message)

    ''' ############################################
    '''
    def start(self):
        
        self.sync_commands['halt'] = self._sync_halt

        print('[i] Starting all standard modules...')
        for unit in self.units.values():
            unit.start()

        self._task_mgr.start()
        self._message_mgr.start()
