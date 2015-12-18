__version__ = 0.01

#General version of pixy. Other version being tailored to focus on soccer#
import os
import pickle
import settings
from logger import Logger
from time import time, sleep
from betfair.api_ng import API
from datetime import datetime, timedelta
import json
import urllib, urllib.request, urllib.error
import market_book_results as m_b_r

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

    #Function: Prompts user to select from a list of EventTypes (i.e Soccer, Golf, ...)
    #that was pulled down from Betfair site. Converts selection into, and returns id of
    #EventType as "eventTypeId"
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
            #print(eventTypeId)
            return eventTypeId

    #Function: Prompts user to select from a list of events e.g ('Man-U vs Arsenal').
    #Converts selection into eventID.
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
            #print(eventId)
            return eventId
        #self.prettyPrint(events)

    #funct: shows markets on offer for event representd by eventId
    def getMarkets(self, eventId):
        filter = {'eventIds':[eventId]}
        params = { 'filter':filter,
                   'marketProjection':['RUNNER_METADATA','RUNNER_DESCRIPTION'],
                   'maxResults': 50 }
        markets = self.api.get_markets(params)
        #self.prettyPrint(markets)
        return markets


    #funct: return marketIds for a selected set of markets
    def selectMarkets(self, choices, eventMarkets):
        liquidMarkets = map(str,choices.split(',') )
        liquidMarketIds = []
        for market in liquidMarkets:
            for eventMarket in eventMarkets:
                if (market == eventMarket['marketName']):
                    liquidMarketIds.append(eventMarket['marketId'])
        return liquidMarketIds

    #combine 2 sets of marketIds into 1 which is suitable for passing to api call
    def combineMarkets(self,liquidSet, illiquidSet):
        marketSet = []
        for each in liquidSet:
            marketSet.append(each)
        for each in illiquidSet:
            marketSet.append(each)
        return marketSet


    def getMarketPrices(self, marketIds):
        marketBook = self.api.get_market_books(market_ids=marketIds,price_data=['EX_BEST_OFFERS'])
        #self.prettyPrint(marketBook)
        return marketBook


    def printPrices(self, market_book_result):
        if(market_book_result is not None):
            print ('Please find Best three available prices for the runners')
            for marketBook in market_book_result:
                runners = marketBook['runners']
                for runner in runners:
                    print ('Selection id is ' + str(runner['selectionId']))
                    if (runner['status'] == 'ACTIVE'):
                        print ('Available to back price :' + str(runner['ex']['availableToBack']))
                        print ('Available to lay price :' + str(runner['ex']['availableToLay']))
                    else:
                        print ('This runner is not active')
                print("****"*10)

    def printPrices_2(self, market_book_result):
        if(market_book_result is not None):
            self.prettyPrint(market_book_result)


    def encapsulatePrices(self, market_book_result, eventMarkets):
        if(market_book_result is not None):
            mbr = m_b_r.MarketBookResult()             #create new marketBookResult object
            for marketBook in market_book_result:
                _marketbook = m_b_r.MarketBook()       #create new marketBook object
                marketId = marketBook["marketId"]
                marketName = None
                for market in eventMarkets:
                    if(marketId == market["marketId"]):
                        marketName = market["marketName"]
                _marketbook.name = marketName         #marketBook.name = marketName
                _marketbook.marketId = marketId       #marketBook.marketId = marketId
                runners = marketBook['runners']
                for runner in runners:
                    _runner = m_b_r.Runner()          #create new Runner object
                    selectionId = runner["selectionId"]
                    runnerName = None
                    for market in eventMarkets:
                        for run in market["runners"]:
                            if(run['selectionId']==selectionId):
                                runnerName = run["runnerName"]
                    _runner.runnerName = runnerName   #Runner.runnerName = runnerName
                    _runner.selectionId = selectionId #Runner.selectionId = selectionId
                    if (runner['status'] == 'ACTIVE'):
                        _runner.availableToBack = runner['ex']['availableToBack']
                        _runner.availableToLay = runner['ex']['availableToLay']
                        _runner.active = True   #else: active==False
                    _marketbook.runners.append(_runner)
                mbr.addIn(_marketbook)
            return mbr


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
            eventTypeId = self.selectEventType()    #e.g returns 1 for Soccer
            eventId = self.selectEvent(eventTypeId) #e.g return 27632951 for Lucena CF v Coria CF
            eventMarkets = self.getMarkets(eventId) #returns all markets for a given event
            #self.prettyPrint(eventMarkets)
            # --------------- #
            #At this point we need to jump directly into selecting arb-choices
            # --------------- #
            for market in eventMarkets:
                print(market["marketName"])
            liquidChoices = input("Input liquid markets. Note: max = 2. Separate using ',' and no spaces between choices:\n")
            liquidMarketIds = self.selectMarkets(liquidChoices, eventMarkets)
            illiquidChoices = input("Input Non-liquid markets. Note: max = 2. Separate using ',' and no spaces between choices:\n")
            illiquidMarketIds = self.selectMarkets(illiquidChoices, eventMarkets)
            marketIds = self.combineMarkets(liquidMarketIds, illiquidMarketIds)
            print("\nAcquired choice Ids: ")
            for each in marketIds:
                print(each)
            lockIn = True
            while lockIn:
                marketBooks = self.getMarketPrices(marketIds) #returns array of marketbooks for each selected market
                #self.prettyPrint(marketBooks)
                #self.printPrices(marketBooks)
                encapsulatedBook = self.encapsulatePrices(marketBooks, eventMarkets)
                #encapsulatedBook.printBooks()
                encapsulatedBook.callArbitrage()
                #lockIn = False
            #self.session = False
        if not self.session:
            msg = 'SESSION TIMEOUT'
            print(msg)
            #raise Exception(msg)

    ##############################################
    #Correct Score Arbitrage Functions:
    def correctScoreArbitrage(eventMarkets):
        liquidMarkets = self.selectMarkets('Correct Score', eventMarkets)

    ###############################################



    def soccer_run(self, username = '', password = '', app_key = '', aus = False):
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
            eventTypeId = 1          #Soccer
            eventId = self.selectEvent(eventTypeId)
            eventMarkets = self.showMarkets(eventId) #returns all markets for a given event
            for market in eventMarkets:
                print(market["marketName"])
            liquidMarkets = self.selectMarkets('Correct Score', eventMarkets)
            print("Correct Score market has been set as Liquid market. Select Choice of Over-Under:\n")
            illiquidChoices = input("Input Non-liquid markets. Note: max = 2. Separate using ',' and no spaces between choices:\n")
            illiquidMarketIds = self.selectMarkets(illiquidChoices, eventMarkets)
            marketIds = self.combineMarkets(liquidMarketIds, illiquidMarketIds)
            print("\nAcquired choice Ids: ")
            for each in marketIds:
                print(each)
            lockIn = True
            while lockIn:
                marketBooks = self.getMarketPrices(marketIds) #returns array of marketbooks for each selected market
                #self.prettyPrint(marketBooks)
                #self.printPrices(marketBooks)
                encapsulatedBook = self.encapsulatePrices(marketBooks, eventMarkets)
                #encapsulatedBook.printBooks()
                encapsulatedBook.callArbitrage()
                #lockIn = False
            #self.session = False
        if not self.session:
            msg = 'SESSION TIMEOUT'
            print(msg)
            #raise Exception(msg)
