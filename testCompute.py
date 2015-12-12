"""Test file - shows usage of runner and marketbook classes"""

import market_book_results
from market_book_results import Runner
from market_book_results import MarketBook

one_zero = Runner()
one_one = Runner()
one_two = Runner()
two_zero = Runner()
two_one = Runner()
three_zero = Runner()

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

print('\n')

under_35 = Runner()
under_35.availableToBack = 1.45
under_35.availableToLay = 1.46
under_35.runnerName = "Under 35 Goals"
mbk_ = MarketBook()
mbk_.runners = [under_35]
for runner in mbk_.runners:
    print (runner.runnerName + ' back price: '+ str(runner.availableToBack))
print('\n')
print("Synthetic Back: " + str(mbk_.computeSyntheticBack()))
print("Synthetic Lay: " + str(mbk_.computeSyntheticLay()))
