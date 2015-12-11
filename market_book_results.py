
class propertyDescriptor(object):
    """Descriptor object to access/modify class properties"""
    def __init__(self, default):
        self._name = default

    def __set__(self, instance, name_):
        self._name = name_

    def __get__(self, instance, owner):
        return self._name

    def __delete__(self, instance):
         del self._name


class MarketBookResult(object):
    """Collection of marketbooks."""
    marketBooks = propertyDescriptor([])

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


class MarketBook(object):
    """Class representation of a marketbook, with built-in useful behaviors"""
    marketId = propertyDescriptor(0)
    name = propertyDescriptor('')
    runners = propertyDescriptor([])



class Runner(object):
    """Class representation of a runner"""
    selectionId = propertyDescriptor(0)
    runnerName = propertyDescriptor('')
    availableToBack = propertyDescriptor([])
    availableToLay = propertyDescriptor([])
    active = propertyDescriptor(False)
