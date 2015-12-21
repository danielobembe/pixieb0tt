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


    def selectOverUnders(self, eventMarkets):
        over_under_markets = []
        for market in eventMarkets:
            marketName = market['marketName']
            #print(marketName)
            marketNameToList = marketName.split(' ')
            if(marketNameToList[0]=="Over/Under"):
                over_under_markets.append(market)
        return over_under_markets


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


    def encapsulatePrices_0(self, market_book_result, eventMarkets):
        #if(market_book_result is not None):
        mbr = m_b_r.MarketBookResult()             #create new marketBookResult object
        for marketBook in market_book_result:
            _marketbook = m_b_r.MarketBook()       #create new marketBook object
            marketId = marketBook["marketId"]
            marketName = None
            for market in eventMarkets:
                if(marketId == market["marketId"]):
                    marketName = market["marketName"]
            _marketbook.name = marketName         #marketBook.name = marketName
            #print(marketName)
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

    def encapsulatePrices(self, market_book_result, eventMarkets):
        mbr = m_b_r.MarketBookResult()          #create new MarketBookResult object to hold both marketbooks
        for marketBook in market_book_result:   #for each marketbook in passed in market_book_results array
            _marketbook = m_b_r.MarketBook()    #create new MarketBook object to store in MarketBookResult
            marketId = marketBook["marketId"]   #get marketbook's id
            marketName = None                   #initialize variable to hold marketbook's name
            for market in eventMarkets:         #get name from eventMarkets
                if(marketId == market["marketId"]):
                    marketName = market["marketName"]
            _marketbook.marketId    = marketId   #store id in marketbook object
            _marketbook.name        = marketName #store name in marketbook object
            #print("Adding Book: " + _marketbook.name)
            self.addInRunners(_marketbook, marketBook['runners'], eventMarkets)
            #print(len(mbr.marketBooks))
            #mbr.marketBooks[len(mbr.marketBooks)] = _marketbook
            mbr.addIn(_marketbook)
        return mbr

    def addInRunners(self, marketbook, runners, eventMarkets):
        for runner in runners:
            _runner = m_b_r.Runner()
            selectionId = runner['selectionId']
            runnerName = None
            for market in eventMarkets:
                for run in market['runners']:
                    if(run['selectionId']==selectionId):
                        runnerName = run['runnerName']
                        #print("Adding Runner: " + runnerName)
            _runner.runnerName = runnerName
            _runner.selectionId = selectionId
            marketbook.append_to_runners(_runner)



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
            eventTypeId = self.selectEventType()    #e.g select Sport
            eventId = self.selectEvent(eventTypeId) #e.g select Match
            eventMarkets = self.getMarkets(eventId) #all markets for selected Match
            #self.prettyPrint(eventMarkets)
            over_unders = self.selectOverUnders(eventMarkets) #subset of eventMarkets i.e only Over/Under x.5's
            print('\nList of Over/Under x.5 markets: ')
            for market in over_unders:
                print(market["marketName"])         #print list of available Over/Under x.5's
            illiquidChoice = input("Select arbitrage-market from list: \n")
            illiquidMarketId = self.selectMarkets(illiquidChoice, eventMarkets) #select appropriate x.5 market
            #print("IlliquidMarketId: "+ str(illiquidMarketId))
            liquidMarketId = self.selectMarkets('Correct Score', eventMarkets)  #Correct Score market, automatically selected
            if (liquidMarketId == []):
                print("Correct Score Market not available for this event. Please select another: ")
                continue
            #else: print("Liquid Market Id: " + str(liquidMarketId))
            marketIds = self.combineMarkets(liquidMarketId, illiquidMarketId)
            # print("\nAcquired choice Ids: ")
            # for each in marketIds:
            #     print(each)
            lockIn = True
            while lockIn:
                marketBooks = self.getMarketPrices(marketIds) #returns marketbooks for selected markets
                #self.prettyPrint(marketBooks)
                #self.printPrices(marketBooks)
                #import pdb; pdb.set_trace()
                encapsulatedBook = self.encapsulatePrices(marketBooks, eventMarkets)
                #encapsulatedBook.printBooks()
                encapsulatedBook.printBooks()
                #encapsulatedBook.callArbitrage()
                lockIn = False
            self.session = False
        if not self.session:
            msg = 'SESSION TIMEOUT'
            print(msg)
            #raise Exception(msg)
