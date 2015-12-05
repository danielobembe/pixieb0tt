"""betfair bot manager"""
from time import sleep
import traceback
from sys import argv, exit
from login_config import login_info

### USER INFO ###
USERNAME = login_info['username']
PASSWORD = login_info['password']
APP_KEY =  login_info['app_key_delay']

### EXCHANGE INFO ###
# NOTE: launch bot using 'python gubber_ng/manager.py --aus' to use AUS exchange
AUS = False # default to UK exchange
if '--aus' in argv: AUS = True

EXIT_ON_ERROR = True # set to False when bot is ready to run 24/7

while True: # loop forever
    try:
        from Pixie_2 import Pixie
        from logger import Logger
        log = Logger(AUS)
        log.xprint('STARTING BOT...')
        # start bot
        pixiebot = Pixie()
        pixiebot.run(USERNAME, PASSWORD, APP_KEY, AUS)
    except Exception as exc:
        from logger import Logger
        log = Logger()
        msg = traceback.format_exc()
        http_err = 'ConnectionError:'
        if http_err in msg:
            msg = '%s%s' % (http_err, msg.rpartition(http_err)[2])
        msg = '#### BOT CRASH ####\n%s' % msg
        log.xprint(msg, err = True)
        if EXIT_ON_ERROR: exit()
    sleep(60) # wait for betfair errors to clear
