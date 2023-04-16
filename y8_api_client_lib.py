from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import traceback
import pytz
import json
import requests
import time
import pandas as pd
from io import StringIO


class Y8_API_CLIENT:

    BTCUSD = 'BTC-USD'
    ETHUSD = 'ETH-USD'
    INTERVAL_30MIN = '30min'
    INTERVAL_4HOURS = '4hour'
    INTERVAL_1D = '1d'
     
    
    def __init__(self, CLIENT_ID, debug_output=False) -> None:
        self.CLIENT_ID = CLIENT_ID
        self.debug_output = debug_output
        
    def debug_out(self, *args, **kwargs):
        if self.debug_output:
            print(args, kwargs)

    def get_latest_forecast(self, symbol='BTCUSD', interval='30min'):
        URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-' + symbol + '-' + interval + '.json'
        SIG = f'get_latest_forecast({symbol}/{interval}) | '
        self.debug_out(SIG, f'requesting @ {URL}')
        f_0 = json.loads(requests.get(URL).text)
        f_0 = run_bug_fixes_for_this_release(f_0)
        return f_0
    
    
    def get_latest_forecast_v2(self, symbol='BTC-USD', interval='1d'):
        F_NAME = f'public-f_0-{symbol}-{interval}--1.json'
        SIG = f'get_latest_forecast({symbol}/{interval}) | '
        self.debug_out(SIG, f'requesting @ {F_NAME}')
        
        success, data = get_ressource(self.CLIENT_ID, F_NAME)
        self.debug_out(SIG, f'request successful? {success}')
        if success:
            f_0 = json.loads(data)
            f_0 = run_bug_fixes_for_this_release(f_0)
            return f_0
        else:
            return None
    
    
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
            SIG = f'get_historical_forecasts({symbol}/{interval}) | '
            URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-all-history-' + symbol + '-' + interval + '.json'
            self.debug_out(SIG, f'requesting URL = {URL}') 
            f_0_history = json.loads(requests.get(URL).text)
            # bug fixes
            _ = []
            for f_0 in f_0_history:
                new_f_0 = run_bug_fixes_for_this_release(f_0)
                _.append(new_f_0)
            f_0_history = _
            #------- end of bug fixes
            
            return f_0_history
        except:
            return []

#------------

def get_ressource(email, resource):
  resp = requests.post('https://europe-west2-yuce-8-v1.cloudfunctions.net/website_dynamix_large', json={
    'action': 'access_resource',
    'email': email,
    'requested_ressource': resource
  })

  if resp.status_code == 200:
    x = resp.json()
    if x['status'] == 'failed':
      print('failure: ', x['data'])
      return False, x['data']
    elif x['status'] == 'success':
      print(len(str(x['data'])), ' bytes received')
      return True, x['data']
  else:
    print('general failure: ', resp.text)
    return False, resp.text


def get_btc_test_data(email, interval):
    resource = f'test_dataset_BTCUSD_{interval}.csv'
    success, data = get_ressource(email, resource)
    if success:
      csvStringIO = StringIO(data)
      df = pd.read_csv(csvStringIO)
      df.Date_ = pd.to_datetime(df.Date_)
      return df
    else:
      return None

def get_btc_test_forecasts(email):
  resource = 'test_dataset_BTCUSD-4hours_forecasts.json'
  success, data = get_ressource(email, resource)
  if success:
    return json.loads(data)
  else:
    return None


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
    return f_0
    
    
