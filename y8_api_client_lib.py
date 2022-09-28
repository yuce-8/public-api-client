from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import traceback
import pytz
import json
import requests
import time
import concurrent.futures


class Y8_API_CLIENT:

    BTCUSD = 'BTCUSD'
    ETHUSD = 'ETHUSD'
    INTERVAL_30MIN = '30min'
    INTERVAL_4HOURS = '4hour'
        
    
    def __init__(self, CLIENT_ID, EVENT_LISTENER, PARALLEL_EXECUTOR) -> None:
        self.CLIENT_ID = CLIENT_ID
        self.EVENT_LISTENER = EVENT_LISTENER
        self.stop = False
        self.PARALLEL_EXECUTOR = PARALLEL_EXECUTOR
        pass


    def get_latest_forecast(self, symbol='BTCUSD', interval='30min'):
        URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-' + symbol + '-' + interval + '.json'
        f_0 = json.loads(requests.get(URL).text)
        return f_0
    
    
    def get_latest_signal(self, symbol='BTCUSD'):
        URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-' + symbol + '.json'
        signal = json.loads(requests.get(URL).text)
        return signal
    
    
    
