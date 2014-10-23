
import time
from threading import Lock

from units.tasker.orm import *


class Logic:

    def __init__(self, tasker, db_mgr):
        self._tasker = tasker
        self._db_mgr = db_mgr
        self._cycle_delay = 10

    def _get_protocol_units(self):
        protocol_units = {}
        for unit in self._db_mgr.session.query(Unit).all():
            for protocol in unit.protocols:
                protocol_units[protocol.name] = unit.name
        return protocol_units

    def _get_initial_tasks(self):
        self._db_mgr.session_lock.acquire()

        resources = self._db_mgr.session.query(Resource).all()
        with_tasks = self._db_mgr.session.query(Resource.id).\
                                          filter(Task.resource_id == Resource.id).all()
        with_tasks = [rid[0] for rid in with_tasks]

        timestamp = self._db_mgr.timestamp()
        _tasks = [Task(resource=rsrc, timestamp=timestamp)
                  for rsrc in resources if rsrc.id not in with_tasks]
        if _tasks:
            self._db_mgr.session.add_all(_tasks)
            self._db_mgr.session.commit()

        tasks = [task.to_json() for task in _tasks]

        self._db_mgr.session_lock.release()

        return tasks

    def _get_login_tasks(self):
        return []

    def _get_crawling_tasks(self):
        return []

    def _get_waiting_tasks(self):
        return []

    def start(self):
        while not self._tasker.halt:
            ''' Por ahi convenga implementar actividades dictadas
                por el numero de ciclos ejecutados de la logica.
            '''
            units = self._get_protocol_units()

            tasks = self._get_initial_tasks()
            print('[tasker.tasks] {0}'.format(tasks))

            tasks.extend(self._get_login_tasks())

            # Create a message for each task to do.
            messages = []
            for task in tasks:
                protocol = task['resource']['service']['protocol']['name']
                message = {'dst':units[protocol], 'src':'tasker',
                           'cmd':'digest', 'params':{'task':task}}
                messages.append(message)

            # Create a schedule message for all pending task messages.
            if messages:
                schedule_msg = {'dst':'core', 'src':'tasker', 'cmd':'schedule', 'params':{}}
                schedule_msg['params']['messages'] = messages

                response = self._tasker.dispatch(schedule_msg)

            print('#######################################################')
            time.sleep(self._cycle_delay)
            