"""Test file - shows usage of runner and marketbook classes"""

import market_book_results
from market_book_results import Runner
from market_book_results import MarketBook

one_zero = Runner(0)
one_one = Runner(0)
one_two = Runner(0)
two_zero = Runner(0)
two_one = Runner(0)
three_zero = Runner(0)

one_zero.availableToBack = 6.6
one_zero.availableToLay = 7.4
one_zero.runnerName = "One-Zero"
one_one.availableToBack = 7
one_one.availableToLay = 7.6
one_one.runnerName = "One-One"
one_two.availableToBack = 15.5
one_two.availableToLay = 18.5
one_two.runnerName = "One-Two"
two_zero.availableToBack = 6.4
two_zero.availableToLay = 7.4
two_zero.runnerName = "Two-Zero"
two_one.availableToBack = 6.8
two_one.availableToLay = 7.8
two_one.runnerName = "Two-One"
three_zero.availableToBack = 12
three_zero.availableToLay = 14
three_zero.runnerName = "Three-Zero"

mbk = MarketBook()
mbk.runners = [one_zero, one_one, one_two, two_zero, two_one, three_zero]
for runner in mbk.runners:
    print (runner.runnerName + ' back price: '+ str(runner.availableToBack))
print('\n')
print("Synthetic Back: " + str(mbk.computeSyntheticBack()))
print("Synthetic Lay: " + str(mbk.computeSyntheticLay()))
