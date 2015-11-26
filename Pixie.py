__version__ = 0.01

from betfair.api_ng import API 
from time import time, sleep
from datetime import datetime, timedelta

#Class: Executes Betfair operations.
class Pixie(object):
    
    #Function: Initialzes Pixie object.
    def __init__(self):
        self.username = ''
        self.api = None
        self.session = False


    #Function: performs non-interactive betfair login. 
    def do_login(self, username='', password=''):
        self.session = False
        resp = self.api.login(username, password)
        if (resp == 'SUCCESS'):
            self.session = True
            print(resp)
        else:
            self.session = False
            msg = 'api.login() resp = %s' % resp
            print(msg)
            raise Exception (msg)


    #Function: performs betfair logout.
    def do_logout(self):
        if (self.session == True):
            resp = self.api.logout()
            if (resp == 'SUCCESS'):
                self.session = False
                print(resp)
            else:
                print(resp)
        else:
            print('Not in session')
        
    #
    def run(self, username='', password='', app_key='', aus = False):
        #Create an API object
        self.username = username
        self.api = API(aus, ssl_prefix=username)
        self.api.app_key = app_key
        self.do_login(username, password)
        sleep(10)
        self.do_logout()
        
