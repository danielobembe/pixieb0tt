__version__ = 0.01

import os
import pickle
import settings
from logger import Logger
from time import time, sleep
from betfair.api_ng import API
from datetime import datetime, timedelta
import json
import urllib, urllib.request, urllib.error

class Pixie(object):
    """betfair laying bot - lays the field using settings.py parameters"""
    def __init__(self):
        self.username = '' # set by run() function at startup
        self.logger = None # set by run() function at startup
        self.api = None # set by run() function at startup
        self.abs_path = os.path.abspath(os.path.dirname(__file__))
        self.ignores_path = '%s/ignores.pkl' % self.abs_path
        self.ignores = self.unpickle_data(self.ignores_path, []) # list of market ids
        self.betcount_path = '%s/betcount.pkl' % self.abs_path
        self.betcount = self.unpickle_data(self.betcount_path, {}) # keys = hours, vals = market ids
        self.throttle = {
            'next': time(), # time we can send next request. auto-updated in do_throttle()
            'wait': 1.0, # time in seconds between requests
            'keep_alive': time(), # auto-updated in keep_alive()
            'update_closed': time() # auto-updated in update_ignores()
        }
        self.session = False

    def pickle_data(self, filepath = '', data = None):
        """pickle object to file"""
        f = open(filepath, 'wb')
        pickle.dump(data, f)
        f.close()

    def unpickle_data(self, filepath = '', default_object = None):
        """unpickle file to object. returns object"""
        if os.path.exists(filepath):
            f = open(filepath, 'rb')
            data = pickle.load(f)
            f.close()
            return data
        return default_object # return default object (empty)

    def do_throttle(self):
        """return when it's safe to continue"""
        now = time()
        if now < self.throttle['next']:
            wait = self.throttle['next'] - now
            sleep(wait)
        self.throttle['next'] = time() + self.throttle['wait']
        return

    def do_login(self, username = '', password = ''):
        """login to betfair & set session status"""
        self.session = False
        resp = self.api.login(username, password)
        if resp == 'SUCCESS':
            self.session = True
        else:
            self.session = False # failed login
            msg = 'api.login() resp = %s' % resp
            raise Exception(msg)

    def keep_alive(self):
        """refresh login session. sessions expire after 20 mins.
        NOTE: betfair throttle = 1 req every 7 mins
        """
        now = time()
        if now > self.throttle['keep_alive']:
            # refresh
            self.session = False
            resp = self.api.keep_alive()
            if resp == 'SUCCESS':
                self.throttle['keep_alive'] = now + (15 * 60) # add 15 mins
                self.session = True
            else:
                self.session = False
                msg = 'api.keep_alive() resp = %s' % resp
                raise Exception(msg)

    #funct: print json dicts in a readable format
    def prettyPrint(self, json_dict):
        print(json.dumps(json_dict,sort_keys=True,indent=4,separators=(',',': ')))

    #funct: asks for eventType and returns eventType's id
    def selectEventType(self):
        eventTypes = self.api.get_event_types()
        print('Here are the types of events available: ')
        for eventType in eventTypes:
            eventTypeName = eventType['eventType']['name']
            print(eventTypeName)
        eventTypeChoice = input('Please input an option from the above list: ')
        eventTypeId = None
        for eventType in eventTypes:
            eventTypeName = eventType['eventType']['name']
            if (eventTypeName == eventTypeChoice):
                eventTypeId = eventType['eventType']['id']
            else: continue
            return eventTypeId

    #funct: asks for events (given a particular eventType), and returns event id
    def selectEvent(self, eventTypeId):
        filter = {'eventTypeIds':[eventTypeId]}
        events = self.api.get_events(filter)
        print('\n\nEVENTS ON OFFER:')
        for event in events:
            eventName = event["event"]["name"]
            print(eventName)
        eventChoice = input('Please input an option from the above list: ')
        eventId = None
        for event in events:
            eventName = event["event"]["name"]
            if (eventName == eventChoice):
                eventId = event["event"]["id"]
            else: continue
            return eventId
        #self.prettyPrint(events)

    def run(self, username = '', password = '', app_key = '', aus = False):
        # create the API object
        self.username = username
        self.api = API(aus, ssl_prefix = username)
        self.api.app_key = app_key
        self.logger = Logger(aus)
        self.logger.bot_version = __version__
        # login to betfair api-ng
        self.do_login(username, password)
        while self.session:
            self.do_throttle()
            self.keep_alive()
            eventTypeId = self.selectEventType()
            eventId = self.selectEvent(eventTypeId)
            print(eventId)
            self.session = False
        if not self.session:
            msg = 'SESSION TIMEOUT'
            print(msg)
            #raise Exception(msg)
