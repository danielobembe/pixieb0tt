__version__ = 0.01

import os
import pickle
import settings
import json
from betfair.api_ng import API 
from time import time, sleep
from datetime import datetime, timedelta



#Class: Executes Betfair operations.
class Pixie(object):
    
    #Function: Initialzes Pixie object.
    def __init__(self):
        self.username = ''
        self.api = None
        self.ignores = None
        self.session = False
        #self.abs_path = os.path.abspath(os.path.dirname(__file__))
        #self.ignores_path = '%s/ignores.pkl' % self.abs_path
        #self.ignores = self.unpickle_data(self.ignores_path, [])


        
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

    """Funct:returns paths matching filters in settings.menu_filters."""
    """@menu_paths: dict of menu paths. Keys=marketIds,vals=menu_paths """
    def filter_menu_path(self, menu_paths= None ):
        keepers = {}
        for market_id in menu_paths:
            market_path = menu_paths[market_id]
            path_texts = market_path.split('/')
            for filter_index, filter in enumerate(settings.menu_filters):
                matched_all = False
                for text in filter:
                    if text in path_texts:
                        matched_all = True
                    else:
                        matched_all = False
                        break
                if matched_all:
                    keepers[market_id] = {
                        'bets_index': filter_index,
                        'market_path': market_path
                        }
        return keepers
        
    #
    def run(self, username='', password='', app_key='', aus = False):
        #Create an API object
        self.username = username
        self.api = API(aus, ssl_prefix=username)
        self.api.app_key = app_key
        self.do_login(username, password)

        #Get Navigation Menu and Menu paths 
        all_menu_paths = self.api.get_menu_paths() 
        try:
            all_menu_paths = self.api.get_menu_paths()
        except:
            raise Exception
        #Filter navigation menu accoring to settings.py filters
        market_paths = self.filter_menu_path(all_menu_paths)
        print(json.dumps(market_paths,sort_keys=True, indent =4,
                         separators=(',',': ')))
        sleep(10)
        self.do_logout()
        
