
from units.engine.orm import *


class Knowledge:

    def __init__(self, engine):
        self._engine = engine
        self._db_mgr = ORM()
        print('[KKKKKKKKKKK] {0}'.format(self._db_mgr.session_lock))

    ''' ############################################
        These set and get methods are just to keep an abstract
        implementation of the database manager. This allow us
        to change to mongodb (for example) in the future if we
        want to.
    '''
    def set(self, message):
        print('[knowledge] "set" message - {0}'.format(message['params']))

        errors = 0
        results_list = []
        self._db_mgr.session_lock.acquire()
        for rows in message['params']:
            results = {}
            for table, row in rows.items():
                result = self._db_mgr.set(table, row)
                results[table] = result
                if result['status'] < 0:
                    errors += 1
            results_list.append(results)
        self._db_mgr.session_lock.release()

        print('[knowledge] saliendo de "set" - {1} - {0}'.format(results_list, errors))

        return {'status':errors, 'results':results_list}


    def get(self, message):
        #print('[knowledge] "get" message - {0}'.format(params))

        results = []
        self._db_mgr.session_lock.acquire()
        for query in message['params']:
            values = {}
            for table, _values in params.items():
                rows = self._db_mgr.get(table, _values)
                values[table] = {table:rows}
            results.append(values)
        self._db_mgr.session_lock.release()

        return {'status':0, 'results':results}

