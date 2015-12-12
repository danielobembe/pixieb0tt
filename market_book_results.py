from weakref import WeakKeyDictionary

#
# class propertyDescriptor(object):
#     """Descriptor object to access/modify class properties"""
#     def __init__(self, default):
#         self._name = default
#
#     def __set__(self, instance, name_):
#         self._name = name_
#
#     def __get__(self, instance, owner):
#         return self._name
#
#     def __delete__(self, instance):
#          del self._name

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

    def printBooks(self):
        print('Please find Best three available prices for the runners: ')
        for marketBook in self.marketBooks:
            print(("===="* 5)+"Market Name: " + marketBook.name + ("===="* 5))  #Print market
            for runner in marketBook.runners:
                print("Runner Name:   | "+runner.runnerName+" |")
                if (runner.active == True):
                    print ('Available to back price :' + str(runner.availableToBack))
                    print ('Available to lay price :' + str(runner.availableToLay))
                else:
                    print ('This runner is not active')
        return


    def callArbitrage(self):
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
            inverted.append(1/float(runner.availableToBack))
        invertedSum = sum(inverted)
        print("Sum of inverted Back Prices: " + str(invertedSum))
        syntheticBack = float(1/invertedSum)
        return syntheticBack

    def computeSyntheticLay(self):
        inverted = []
        for runner in self.runners:
            inverted.append(1/float(runner.availableToLay))
        invertedSum = sum(inverted)
        print("Sum of inverted Lay Prices: " + str(invertedSum))
        syntheticLay = float(1/invertedSum)
        return syntheticLay


class Runner(object):
    """Class representation of a runner"""
    selectionId = propertyDescriptor(0)
    runnerName = propertyDescriptor('')
    availableToBack = propertyDescriptor([])
    availableToLay = propertyDescriptor([])
    active = propertyDescriptor(False)
