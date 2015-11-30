__version__ 0.01

import os
import pickle
from time import time, sleep
from datetime import datetime, timedelta

"""Class: records market bet/lay data at a given instance in time"""
class Snapshot(object):

    def __init__(self, correct_scores, unders):
        self.nil_nil    = correct_scores[0]
        self.nil_one    = correct_scores[1]
        self.nil_two    = correct_scores[2]
        self.nil_three  = correct_scores[3]
        self.one_nil    = correct_scores[4]
        self.one_one    = correct_scores[5]
        self.one_two    = correct_scores[6]
        self.two_nil    = correct_scores[7]
        self.two_one    = correct_scores[8]
        self.three_nil  = correct_scores[9]

        self.under_15 = unders[0]
        self.under_25 = unders[1]
        self.under_35 = unders[2]

        self.backLay_synthetic, self.backLay_35, self.backLay_25, self.backLay_15 = []
        self.market_key = {'back_price': 0,
                           'back_stake': 1,
                           'lay_price' : 2,
                           'lay_stake' : 3
        }
        
