from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import traceback
import pytz
import json
import requests
import time
import pandas as pd

class Y8_API_CLIENT:

    BTCUSD = 'BTCUSD'
    ETHUSD = 'ETHUSD'
    INTERVAL_30MIN = '30min'
    INTERVAL_4HOURS = '4hour'
        
    
    def __init__(self, CLIENT_ID) -> None:
        self.CLIENT_ID = CLIENT_ID


    def get_latest_forecast(self, symbol='BTCUSD', interval='30min'):
        URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-' + symbol + '-' + interval + '.json'
        f_0 = json.loads(requests.get(URL).text)
        return f_0
    
    
    def get_latest_signal(self, symbol='BTCUSD'):
        URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-' + symbol + '.json'
        signal = json.loads(requests.get(URL).text)
        return signal
    
    def get_historical_quotes(self, symbol='BTCUSD', interval='30min'):
        x_symbol = None
        if symbol == Y8_API_CLIENT.BTCUSD:
            x_symbol = 'BTC-USD'
        elif symbol == Y8_API_CLIENT.ETHUSD:
            x_symbol = 'ETH-USD'
        URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-quotes-' + x_symbol + '-' + interval + '-quotes.json'
        df = pd.read_json(requests.get(URL).text, orient='split')
        df.Date_ = pd.to_datetime(df.Date_)
        return df
    
    def get_historical_forecasts(self, symbol='BTCUSD', interval='30min'):
        try:
            URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-history-' + symbol + '-' + interval + '.json'
            f_0_history = json.loads(requests.get(URL).text)
            return f_0_history
        except:
            return []
        
    
    
    
