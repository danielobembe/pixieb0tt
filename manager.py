from login_config import login_info
from sys import argv, exit

#User Information
USERNAME = login_info['username']
PASSWORD = login_info['password']
APP_KEY  = login_info['app_key_live']

#Exchange interaction settings
AUS = False           #default = UK exchange
if '--aus' in argv:   #commandline: switch to australian exchange
    AUS = True
EXIT_ON_ERROR = True  #Set to False to run 24/7


try:
    from Pixie import Pixie
    print('Testing Bot.')
    pixie = Pixie()
    pixie.run(USERNAME, PASSWORD, APP_KEY, AUS)
except Exception as exc:
    print(exc)
