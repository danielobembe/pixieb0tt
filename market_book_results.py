from weakref import WeakKeyDictionary
import json

class propertyDescriptor(object):
    def __init__(self, default):
        self.default = default
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        #Origin  : x.d
        #d       = propertyDescriptor instance
        #x       = instance,
        #type(x) = owner
        return self.data.get(instance,self.default)

    def __set__(self, instance, value):
        #Origin : x.d = val,
        #d      = propertyDescriptor instance
        #x      = instance
        #val    = value
        self.data[instance] = value


class MarketBookResult(object):
    """Collection of marketbooks."""


    def __init__(self):
        self.marketBooks = []
        self.liquidity = {
            'liquidMarket':'',
            'illiquidMarket':''
        }

    def print_liquidities(self):
        print('Liquid Market: ' + self.liquidity['liquidMarket'])
        print('Illiquid Market: '+ self.liquidity['illiquidMarket'])


    def addIn(self, mbk):
        self.marketBooks.append(mbk)
        if (mbk.name == 'Correct Score'):
            self.liquidity['liquidMarket'] = mbk.name
            mbk.liquidity = 'liquidMarket'
        else:
            self.liquidity['illiquidMarket'] = mbk.name
            mbk.liquidity = 'illiquidMarket'

    def printBooks(self):
        print('Please find Best three available prices for the runners: ')
        for marketBook in self.marketBooks:
            print(("===="* 5)+"Market Name: " + marketBook.name + ("===="* 5))  #Print market
            for runner in marketBook.runners:
                print("Runner Name:   | "+runner.runnerName+" | ")
                if (runner.active == True):
                    print ('Available to back price :' + str(runner.get_availableToBack()))
                    print ('Available to lay price :' + str(runner.get_availableToLay()))
                else:
                    print ('This runner is not active')
        return


    def printBook_0(self):
        print('\n\n')
        marketBook = self.marketBooks[0]
        print(marketBook.name)
        marketBook.printRunners()

    def getLiquidMarket(self):
        liquid = None
        for mbk in self.marketBooks:
            if (mbk.liquidity == 'liquidMarket'):
                liquid = mbk
        return liquid

    def getIlliquidMarket(self):
        illiquid = None
        for mbk in self.marketBooks:
            if (mbk.liquidity == 'illiquidMarket'):
                illiquid = mbk
        return illiquid


    def callArbitrage(self):
        liquid = self.getLiquidMarket()
        illiquid = self.getIlliquidMarket()
        #print('Liquid Market: '+ liquid.name)
        #print('Illiquid Market: '+ illiquid.name)
        liquidBack = liquid.computeSyntheticBack()#<====
        liquidLay  = liquid.computeSyntheticLay()
        illiquidBack = illiquid.computeSyntheticBack()
        illiquidLay = illiquid.computeSyntheticLay()
        #conditions:
        if (liquidBack >= illiquidLay):
            print('Arbitrage, profit: '+ (liquidBack - illiquidLay))
        if (liquidLay <= illiquidBack):
            print('Arbitrage, profit: '+ (liquidLay - illiquidBack))
        if (liquidBack < illiquidLay or liquidLay > illiquidBack ):
            print('No-Arb condition holding.') #<=======
        return


class MarketBook(object):
    """Class representation of a marketbook, with built-in useful behaviors"""
    marketId = propertyDescriptor(0)
    name = propertyDescriptor('')
    liquidity = propertyDescriptor('')

    def __init__(self):
        self.runners = []
        self.user_runnerChoices = []

    def get_runners(self):
        return self.runners

    def set_runners(self, value):
        self.runners = value

    def append_to_runners(self,value):
        self.runners.append(value)

    def computeSyntheticBack(self):
        inverted = []
        choices = []
        if(self.user_runnerChoices == 0):#i.e if it is the illiquid market, because in the liquid market - the user picks the runners (see pixie.py after inputList under while LockIn)
            choices = self.runners
        else: choices = self.user_runnerChoices #i.e otherwise we are in the liquid market. user_runnerChoices set in self.selectRunners()
        for runner in choices:
            """would need to generalize to the entire returned marketprices (right now only computing on best Price)."""
            inverted.append(1/float(runner.availableToBack[0]['price']))
        invertedSum = sum(inverted)
        syntheticBack = float(1/invertedSum)
        return syntheticBack

    def computeSyntheticLay(self):
        inverted = []
        choices = []
        if(self.user_runnerChoices == 0):
            choices = self.runners
        else: choices = self.user_runnerChoices
        for runner in choices:
            """would need to generalize to the entire returned marketprices (right now only computing on best Price)."""
            inverted.append(1/float(runner.availableToLay[0]['price']))
        invertedSum = sum(inverted)
        syntheticLay = float(1/invertedSum)
        return syntheticLay

    def printRunners(self):
        print("Number of runners: "+ str(len(self.runners)))
        for runner in self.runners:
            print(runner.runnerName)


    def selectRunners(self, inputList):
        print('\n')
        userChoices = inputList.split(',')
        for choice in userChoices:
            for runner in self.runners:
                if (str(choice)==runner.runnerName):
                    self.user_runnerChoices.append(runner)
                    print(str(choice))
        return



class Runner(object):
    """Class representation of a runner"""
    selectionId = propertyDescriptor(0)
    runnerName = propertyDescriptor('')
    active = propertyDescriptor(False)

    def __init__ (self):
        self.availableToBack = None
        self.availableToLay  = None


    def get_availableToBack(self):
        return self.availableToBack

    def set_availableToBack(self, value):
        self.availableToBack = value

    def get_availableToLay(self):
        return self.availableToLay

    def set_availableToLay(self, value):
        self.availableToLay = value
