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

    def update_ignores(self, market_id = ''):
        """update ignores list"""
        if market_id:
            # add market to ignores dict
            if market_id not in self.ignores:
                self.ignores.append(market_id)
                self.pickle_data(self.ignores_path, self.ignores)
        else:
            # check for closed markets (once every 2 hours)
            count = len(self.ignores)
            now = time()
            if count > 0 and now > self.throttle['update_closed']:
                secs = 2 * 60 * 60 # 2 hours
                self.throttle['update_closed'] = now + secs
                msg = 'CHECKING %s MARKETS FOR CLOSED STATUS...' % count
                self.logger.xprint(msg)
                for i in range(0, count, 5):
                    market_ids = self.ignores[i:i+5] # list of upto 5 market ids
                    self.do_throttle()
                    books = self.get_market_books(market_ids)
                    for book in books:
                        if book['status'] == 'CLOSED':
                            # remove from ignores
                            self.ignores.remove(book['marketId'])
                            self.pickle_data(self.ignores_path, self.ignores)

    def update_betcount(self, betcount = 0):
        """update bet count to avoid exceeding 1000 bets per hour"""
        hour = datetime.utcnow().hour
        if hour not in self.betcount:
            # new hour
            self.betcount[hour] = [betcount]
            # remove 'old' keys
            for key in self.betcount:
                if key != hour: self.betcount.pop(key)
        else:
            # current hour
            self.betcount[hour].append(betcount)
        # pickle
        self.pickle_data(self.betcount_path, self.betcount)

    def get_betcount(self):
        """returns bet count for current hour as integer"""
        betcount = 0
        hour = datetime.utcnow().hour
        if hour in self.betcount:
            betcount = sum(self.betcount[hour])
        return betcount

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

    def get_markets(self, market_ids = None):
        """returns a list of markets
        @market_ids: type = list. list of market ids to get info for.
        HINT: market ids can be filtered from menu paths
        """
        if market_ids:
            params = {
                'filter': {
                    'marketTypeCodes': settings.market_types,
                    'marketBettingTypes': ['ODDS'],
                    'turnInPlayEnabled': True, # will go in-play
                    'inPlayOnly': False, # market NOT currently in-play
                    'marketIds': market_ids
                },
                'marketProjection': ['RUNNER_DESCRIPTION'],
                'maxResults': 1000, # maximum allowed by betfair
                'sort': 'FIRST_TO_START'
            }
            # send the request
            markets = self.api.get_markets(params)
            if type(markets) is list:
                return markets
            else:
                msg = 'api.get_markets() resp = %s' % markets
                raise Exception(msg)

    def create_bets(self, markets = None, market_paths = None):
        """returns a dict of bets. keys = market ids, vals = list of bets"""
        market_bets = {}
        # loop through markets
        for market in markets:
            # get bet settings for this market
            market_id = market['marketId']
            if market_id in market_paths:
                bets_index = market_paths[market_id]['bets_index']
                bets = settings.market_bets[bets_index]
                # create bets for this market
                market_path = market_paths[market_id]['market_path']
                market_bets[market_id] = {'bets': [], 'market_path': market_path}
                for runner in market['runners']:
                    for bet in bets:
                        new_bet = {}
                        new_bet['selectionId'] = runner['selectionId']
                        new_bet['side'] = bet['side']
                        new_bet['orderType'] = 'LIMIT'
                        new_bet['limitOrder'] = {
                            'size': bet['stake'],
                            'price': bet['price'],
                            'persistenceType': 'PERSIST' # KEEP at in-play. Set as 'LAPSE' to cancel.
                        }
                        market_bets[market_id]['bets'].append(new_bet)
        return market_bets # max bet count = 1000

    def place_bets(self, market_bets = None):
        """loop through markets and place bets
        @market_bets: type = dict returned from create_bets()
        NOTE: market_bets will contain up to 1000 bets!
        """
        for market_id in market_bets:
            bets = market_bets[market_id]['bets']
            if bets:
                # update & check bet count
                new_betcount = len(bets)
                self.update_betcount(new_betcount)
                betcount = self.get_betcount() # total bets placed in current hour
                if betcount >= settings.max_transactions: return
                # place bets...
                market_path = market_bets[market_id]['market_path']
                msg = 'MARKET PATH: %s\n' % market_path
                msg += 'PLACING %s BETS...\n' % len(bets)
                for i, bet in enumerate(bets):
                    msg += '%s: %s\n' % (i, bet)
                self.logger.xprint(msg)
                self.do_throttle()
                resp = self.api.place_bets(market_id, bets)
                if (type(resp) is dict
                    and 'status' in resp
                    ):
                    if resp['status'] == 'SUCCESS':
                        # add to ignores
                        self.update_ignores(market_id)
                        msg = 'PLACE BETS: SUCCESS'
                        self.logger.xprint(msg)
                    else:
                        if resp['errorCode'] == 'INSUFFICIENT_FUNDS':
                            msg = 'PLACE BETS: FAIL (%s)' % resp['errorCode']
                            self.logger.xprint(msg)
                            sleep(180) # wait 3 minutes
                        else:
                            msg = 'PLACE BETS: FAIL (%s)' % resp['errorCode']
                            self.logger.xprint(msg, True) # do not raise error - allow bot to continue
                            # add to ignores
                            self.update_ignores(market_id)
                else:
                    msg = 'PLACE BETS: FAIL\n%s' % resp
                    raise Exception(msg)

    def filter_menu_path(self, menu_paths = None):
        """returns list of paths matching filters specified in settings.py
        @menu_paths: dict of menu paths. keys = market ids, vals = menu paths
        """
        keepers = {}
        # loop through all menu paths
        for market_id in menu_paths:
            market_path = menu_paths[market_id]
            path_texts = market_path.split('/')
            # check filters
            for filter_index, filter in enumerate(settings.menu_filters):
                # check if ALL search text matches this market
                matched_all = False
                for text in filter:
                    if text in path_texts:
                        matched_all = True
                    else:
                        matched_all = False
                        break
                # keep this market?
                if matched_all:
                    keepers[market_id] = {
                        'bets_index': filter_index,
                        'market_path': market_path
                    }
        return keepers

                        #My-addition
    def prettyPrint(self, json_dict):
        print(json.dumps(json_dict,sort_keys=True,indent=4,separators=(',',': ')))

    def callAping(self, jsonrpc_req): #need to abstract later
        try:
            req = urllib.request.Request("https://api.betfair.com/exchange/betting/json-rpc/v1",
                                        jsonrpc_req.encode('utf-8'),
                                        headers = {'X-Application':self.api.app_key ,
                                        'X-Authentication':self.api.session_token,
                                        'content-type': 'application/json'})
            response = urllib.request.urlopen(req)
            jsonResponse = response.read()
            return jsonResponse.decode('utf-8')
        except urllib.error.URLError as e:
            print (e.reason)
            print ('Oops no service available at ' + str(url))
            exit()
        except urllib.error.HTTPError:
            print ('Oops not a valid operation from the service ' + str(url))
            exit()

    def getMarketCatalogue(self, eventTypeID, marketName):
        #Note: a market catalogue gives all the outcomes for "sale" in a market
        if (eventTypeID is not None):
            print ('Calling listMarketCatalouge Operation to get MarketID and selectionId')
            now = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            market_catalogue_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue", "params": {"filter":{"eventTypeIds":["' + eventTypeID + '"],"marketCountries":["GB"],"marketTypeCodes":["'+marketName+ '"],'\
                                                                                                                                                                 '"marketStartTime":{"from":"' + now + '"}},"sort":"FIRST_TO_START","maxResults":"1","marketProjection":["RUNNER_METADATA"]}, "id": 1}'
            market_catalogue_response = self.callAping(market_catalogue_req)
            market_catalogue_loads = json.loads(market_catalogue_response)
            try:
                market_catalogue_results = market_catalogue_loads['result']
                return market_catalogue_results
            except:
                print ('Exception from API-NG' + str(market_catalogue_results['error']))
                exit()

    def getMarketId(self, marketCatalogueResult):
        if( marketCatalogueResult is not None):
            for market in marketCatalogueResult:
                return market['marketId']

    def getSelectionId(self, marketCatalogueResult):
        #NEED to modify so user can select (multiple) runners?
        if(marketCatalogueResult is not None):
            for market in marketCatalogueResult:
                return market['runners'][0]['selectionId']

    def getMarketBookBestOffers(self, marketId):
        print ('Calling listMarketBook to read prices for the Market with ID :' + marketId)
        market_book_req = '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketBook", "params": {"marketIds":["' + marketId + '"],"priceProjection":{"priceData":["EX_BEST_OFFERS"]}}, "id": 1}'
        market_book_response = self.callAping(market_book_req)
        market_book_loads = json.loads(market_book_response)
        try:
            market_book_result = market_book_loads['result']
            #self.prettyPrint(market_book_result)
            return market_book_result
        except:
            print ('Exception from API-NG' + str(market_book_result['error']))
            exit()

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
            #Get and display all events
            eventsList = self.api.get_event_types()

            ###user interaction
            #print(json.dumps(eventsList,sort_keys=True,indent=4,separators=(',',': ')))
            print('Here are the list of available events: ')
            for event in eventsList:
                eventName = event['eventType']['name']
                print(eventName) #eg: Soccer
            eventChoice = input('Please input an option from the above list: ')

            ###Get Id of selected event
            eventId = None
            for event in eventsList:
                eventName = event['eventType']['name']
                eventId = None
                if (eventName == eventChoice):
                    eventId = event['eventType']['id']
                else: continue
                break

            ###Display all markets for selected event
            eventMarkets = self.api.get_market_types({'eventTypeIds':[eventId]})
            for market in eventMarkets:
                print(market["marketType"]) #eg: OVER_UNDER_15
            marketChoice = input("Please select from the list of available Markets below: ")
            print("You selected "+ marketChoice)
            ###Get market-catalogue for user selected event
            marketCatalogue = self.getMarketCatalogue(eventId,marketChoice)
            print("This is the list of runners to bet on in the "+marketChoice+" market:")
            for runner in marketCatalogue[0]["runners"]:
                print(runner["runnerName"]) #eg: Under 1.5 goals

            ###Get market and selection (i.e runner) ids
            self.prettyPrint(marketCatalogue)
            market_id = self.getMarketId(marketCatalogue)
            print("Market " + marketChoice + " has id: " + market_id)
            selection_id = self.getSelectionId(marketCatalogue)
            print("selction_id: " + str(selection_id))

            ###Get Market Book - best offers only
            marketBook = self.getMarketBookBestOffers(market_id)
            self.printPrices(marketBook)
            #sign_out?
            self.session = False
        if not self.session:
            msg = 'SESSION TIMEOUT'
            print(msg)
            #raise Exception(msg)
