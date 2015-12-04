__version__ = 0.00

menu_filters = [
    #['Soccer']
    ['Soccer', 'Fixtures 30 November']       # filter No. 0
]

market_filters = { #Note: input filters from top-down
    'inPlayOnly': True,
    'eventIds': ['27614715'], # <== taken from print(events)
    'marketId': ['1.122072553']
}

event_to_market_filter = {
    
}



#Under 2.5s: 0-0,0-1,0-2,1-0,
market_ids = [

]


market_types = [
    'MATCH_ODDS'
]

market_bets = [
    [   # bets for filter No. 0
        {'side': 'LAY', 'price': 1.01, 'stake': 2.00},
        {'side': 'LAY', 'price': 1.02, 'stake': 2.00}
    ],
    [   # bets for filter No. 1
        {'side': 'LAY', 'price': 1.01, 'stake': 2.00},
        {'side': 'LAY', 'price': 1.02, 'stake': 2.00}
    ]
]

max_transactions = 250
