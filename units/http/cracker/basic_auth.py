
import requests

from units.modules.dictionary import Dictionary


class BasicAuth:

    def __init__(self, unit):
        self.unit = unit

    def crack(self, resource, dictionaries):

        #resource = message['params']['task']['resource']

        print('[<#########>] {0}'.format(resource))

        for dictionary in dictionaries:
            for username, password in Dictionary(**dictionary).pairs():
                print('[http] Forcing Username: {0} - Password: {1}'.format(username, password))

        return {'status':0}