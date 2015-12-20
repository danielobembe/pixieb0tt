from weakref import WeakKeyDictionary
import json

class propertyDescriptor(object):
    def __init__(self, default):
        self.default = default
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        #we get here when someone calls x.d, and d is a
        #NonNegative instance.
        #instance = x, owner = type(x)
        return self.data.get(instance,self.default)

    def __set__(self, instance, value):
        #we get here when someone calls x.d = val, and d is a
        #NonNegative instance.
        #instance = x, value = val
        self.data[instance] = value


class MarketBookResult(object):
    """Collection of marketbooks."""
    marketBooks = propertyDescriptor([])
    liquidity = {
        'liquidMarket':'',
        'illiquidMarket':''
    }

    def addIn(self, mbk):
        self.marketBooks.append(mbk)
        if (self.liquidity['liquidMarket']==''):
            self.liquidity['liquidMarket']= mbk.name
            mbk.liquidity = 'liquidMarket'
        else:
            self.liquidity['illiquidMarket'] = mbk.name
            mbk.liquidity = 'illiquidMarket'

    # def printBooks(self):
    #     print('Please find Best three available prices for the runners: ')
    #     for marketBook in self.marketBooks:
    #         print(("===="* 5)+"Market Name: " + marketBook.name + ("===="* 5))  #Print market
    #         for runner in marketBook.runners:
    #             print("Runner Name:   | "+runner.runnerName+" | ...: "+ marketBook.name )
    #             if (runner.active == True):
    #                 print ('Available to back price :' + str(runner.availableToBack))
    #                 print ('Available to lay price :' + str(runner.availableToLay))
    #             else:
    #                 print ('This runner is not active')
    #     return

    def printBooks(self):
        print('\n')
        itern = 0
        for marketBook in self.marketBooks:
            itern += 1
            print(str(itern) + " ===" * 5)
            print(marketBook.name)
            # for runner in marketBook.runners:
            #     print("Runner Name: "+ runner.runnerName)
            #     #THis has indicated very clearly
            #     #that encapsulatedBook is faulty.
            #     #TODO: rewrite encapsulatePrices.
        print("==="*5)

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
    runners = propertyDescriptor([])
    liquidity = propertyDescriptor('')

    def computeSyntheticBack(self):
        inverted = []
        for runner in self.runners:
            #print("Name: "+ str(runner.runnerName) + " | Back-price: " + str(runner.availableToBack))
            """would need to generalize to the entire returned marketprices (right now only computing on best Price)."""
            inverted.append(1/float(runner.availableToBack[0]['price']))
        #print("List of inverted Back Prices: " + str(inverted))
        invertedSum = sum(inverted)
        #print("Sum of inverted Back Prices: " + str(invertedSum))
        syntheticBack = float(1/invertedSum)
        #print("Price of synthetic Back: " + str(syntheticBack))
        return syntheticBack

    def computeSyntheticLay(self):
        inverted = []
        for runner in self.runners:
            #print("Name: "+ str(runner.runnerName) + " | Back-price: " + str(runner.availableToLay))
            """would need to generalize to the entire returned marketprices (right now only computing on best Price)."""
            inverted.append(1/float(runner.availableToLay[0]['price']))
        #print("List of inverted Lay Prices: " + str(inverted))
        invertedSum = sum(inverted)
        #print("Sum of inverted Lay Prices: " + str(invertedSum))
        syntheticLay = float(1/invertedSum)
        #print("Price of synthetic Lay: " + str(syntheticLay))
        return syntheticLay


class Runner(object):
    """Class representation of a runner"""
    selectionId = propertyDescriptor(0)
    runnerName = propertyDescriptor('')
    availableToBack = propertyDescriptor([])
    availableToLay = propertyDescriptor([])
    active = propertyDescriptor(False)
