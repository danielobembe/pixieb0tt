__version__ = 0.00

# NOTE: ALL text in each filter must be matched. Text is case senitive!
# each filter can contain multiple texts, e.g. ['Horse Racing', 'Hcap'] will find all handicap races
menu_filters = [
    ['Horse Racing'],       # filter No. 0
    ['Greyhound Racing']    # filter No. 1
]

# NOTE: these are the marketTypeCodes for get_markets()
# the list is numerous, however the following are common examples:
# Horse Racing: 'WIN', 'PLACE', 'ANTEPOST_WIN', 'SPECIAL', 'STEWARDS'
# Greyhound Racing: 'WIN', 'PLACE', 'FORECAST', 'ANTEPOST_WIN'
# Soccer: 'MATCH_ODDS', 'CORRECT_SCORE', 'OVER_UNDER_05', 'OVER_UNDER_15',
#   'OVER_UNDER_25', 'HALF_TIME', 'NEXT_GOAL', 'TOTAL_GOALS', etc...
# MORE AVAILABLE AT: https://developer.betfair.com/visualisers/api-ng-sports-operations/
# (use listMarketTypes operation)
market_types = [
    'WIN'
]

# NOTES:
# bets correspond with menu_filters, so market_bets[0] are for menu_filters[0], etc.
# e.g. if menu_filters contains 5 filters, there MUST be 5 bets in this list.
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

# NOTE: this setting avoids transaction charges for placing 1000+ bets per hour
# DO NOT set this higher than 1000!
# the count is only for THIS bot and DOES NOT include other bets you have placed
# betfair count each single bet (where a betId is created) as one transaction
max_transactions = 250
