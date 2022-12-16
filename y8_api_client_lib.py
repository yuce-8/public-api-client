from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import traceback
import pytz
import json
import requests
import time
import pandas as pd


class Y8_API_CLIENT:

    BTCUSD = 'BTC-USD'
    ETHUSD = 'ETH-USD'
    INTERVAL_30MIN = '30min'
    INTERVAL_4HOURS = '4hour'
    INTERVAL_1D = '1d'
     
    
    def __init__(self, CLIENT_ID, debug_output=False) -> None:
        self.CLIENT_ID = CLIENT_ID
        self.debug_output = debug_output
        
    def debug_out(*args, **kwargs):
        if self.debug_output:
            print(args, kwargs)

    def get_latest_forecast(self, symbol='BTCUSD', interval='30min'):
        URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-' + symbol + '-' + interval + '.json'
        f_0 = json.loads(requests.get(URL).text)
        run_bug_fixes_for_this_release(f_0)
        return f_0
    
    
    def get_latest_signal(self, symbol='BTCUSD'):
        URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-' + symbol + '.json'
        signal = json.loads(requests.get(URL).text)
        return signal
    
    def get_historical_quotes(self, symbol='BTCUSD', interval='30min'):
        SIG = f'get_historical_quotes({symbol}/{interval}) | '
        URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-quotes-' + symbol + '-' + interval + '-quotes.json'
        self.debug_out(SIG, f'requesting URL = {URL}') 
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
        
    
 
#------------

def run_bug_fixes_for_this_release(f_0):
    def convert_to_float(attribute, is_array=False):
        nonlocal f_0
        if not is_array and attribute in f_0:
            f_0[attribute] = float(f_0[attribute])
    
    # convert some elements to float...
    convert_to_float('last_quote')
    convert_to_float('next_resistance')
    convert_to_float('next_support')
    
    
