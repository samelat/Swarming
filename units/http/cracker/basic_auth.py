
import time
import requests

from units.modules.dictionary import Dictionary


class BasicAuth:

    def __init__(self, unit):
        self.unit = unit

    def crack(self, dictionaries):

        request = {'method':'get', 'url':self.unit.url}
        request.update(self.unit.complements)

        for dictionary in dictionaries:
            for username, password in Dictionary(**dictionary).pairs():
                print('[http] Forcing Username: {0} - Password: {1}'.format(username, password))
                request['auth'] = (username, password)

                response = requests.request(**request)
                if response.status_code == 200:
                    self.unit.success({'username':username, 'password':password},
                                      {'auth':[username, password]})

        return {'status':0}