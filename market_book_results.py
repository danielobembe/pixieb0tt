class MarketBookResult:
    """Collection of marketbooks."""
    def __init__(self):
        self.marketBooks = []





class MarketBook:
    """Class representation of a marketbook, with built-in useful behaviors"""
    def __init__(self):
        self.marketId = 0
        self.name = ''
        self.runners = []




class Runners:
    """Class representation of a runner"""
    def __init__(self):
        self.selectionID = 0
        self.runnerName = ''
        self.availableToBack = []
        self.availableToLay = []
        self.active = False
