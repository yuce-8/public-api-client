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
    
    
    def get_latest_signal(self, symbol='BTCUSD'):
        URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-' + symbol + '.json'
        signal = json.loads(requests.get(URL).text)
        return signal

    
    def get_latest_forecast_v2(self, symbol, interval):
        return self.get_historical_forecast_v2(symbol, interval, 1)

    
    def get_latest_quotes_v2(self, symbol, interval):
        return self.get_historical_quotes_v2(symbol, interval, 1)

    def get_historical_quotes_v2(self, symbol, interval, history):
        resource = f'public-interval-quotes-{symbol}-{interval}--{history}.json'
        SIG = f'get_historical_quotes_v2({symbol}/{interval}/{history}) | '
        
        self.debug_out(SIG, f'requesting @ {resource}')
        success, data = get_ressource(self.CLIENT_ID, resource)
        self.debug_out(SIG, f'request successful? {success}')
        if success:
            j = json.loads(data)
            df = pd.DataFrame.from_records(j['rows'])
            df.Date_ = pd.to_datetime(df.Date_orig)
            return df
        else:
            return None

        
    def get_historical_forecast_v2(self, symbol, interval, history):
        F_NAME = f'public-f_0-{symbol}-{interval}--{history}.json'
        SIG = f'get_historical_forecast({symbol}/{interval}/{history}) | '
        self.debug_out(SIG, f'requesting @ {F_NAME}')
        
        success, data = get_ressource(self.CLIENT_ID, F_NAME)
        self.debug_out(SIG, f'request successful? {success}')
        if success:
            f_0 = json.loads(data)
            f_0 = run_bug_fixes_for_this_release(f_0)
            return f_0
        else:
            return None

    
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
    
#------------------------------ UTILITIES:

def plot_forecast(df, forecast):
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import datetime
    import warnings
    warnings.filterwarnings('ignore')
    
    def to_datetime(x):
        x = str(x).replace('T', ' ')
        if len(x) > 19:
          x = x[:19]
        elif len(x) == 10:
          x = x + '00:00:00'
        return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")

    dpi = 96
    width = 1400
    height = 800 # 800
    mpl.rcParams.update(mpl.rcParamsDefault)
    fig = plt.figure(figsize=(width/dpi, height/dpi), dpi=dpi)
    plt.rcParams["axes.grid"] = False
    plt.style.use("seaborn-bright")
    plt.rcParams['axes.facecolor'] = 'white'
    fig.patch.set_facecolor('white')
    future_dates = []  
    all_indizes = []
    fill_colors = ['darkorange', 'mediumspringgreen', 'midnightblue']
    color_counter = -1  
    level_1 = forecast['level_1']
    level_2 = forecast['level_2']
    model_name = forecast['model_name']
    training_date = forecast['training_date']
    last_date_of_forecast = forecast['last_date']
    last_quote_of_forecast = forecast['last_quote']
    forecasted_values = forecast['forecast']
    sl_before, sl_after = forecast['next_support'], forecast['next_resistance'] 
    is_negative = forecast['is_negative']
    confidence_extended_1 = forecast['confidence_extended_1']
    confidence_extended_2 = forecast['confidence_extended_2']
    forecasted_future_prices_top = forecast['quotes_forecast_top_incl_vola']
    forecasted_future_prices_bottom = forecast['quotes_forecast_bottom_incl_vola']

    all_quotes_until_forecast = df.loc[df.Date_ <= last_date_of_forecast]
    all_quotes_after_forecast = df.loc[df.Date_ > last_date_of_forecast]  
    
    history = len(all_quotes_after_forecast)
    all_dates_of_prediction = all_quotes_until_forecast.Date_.values
    true_date_interval = (to_datetime(all_dates_of_prediction[-1]) - to_datetime(all_dates_of_prediction[-2])).total_seconds() // 60
    
    df = df if history == 0 else all_quotes_until_forecast
    if len(all_quotes_after_forecast) > 0:
        true_highs = all_quotes_after_forecast.High.head(len(forecasted_future_prices_top)).values
        true_lows = all_quotes_after_forecast.Low.head(len(forecasted_future_prices_top)).values
        true_closings = all_quotes_after_forecast.Close.head(len(forecasted_future_prices_top)).values
        true_dates = [to_datetime(d) for d in all_quotes_after_forecast.Date_.head(len(forecasted_future_prices_top)).values]
        future_dates = [true_dates[-1] + datetime.timedelta(minutes=true_date_interval * i) for i in range(1, len(forecasted_future_prices_top) + 1)]
        history = 1
    plot_history = len(forecasted_values)
    
    last_quotes = df['Close'].tail(plot_history).values
    last_highs = df['High'].tail(plot_history).values
    last_lows = df['Low'].tail(plot_history).values
    indizes = df['Close'].tail(plot_history).index
    indizes_2 = []

    last_quote = df['Close'].tail(1).values[0]
    indizes_forecast = range(indizes[-1] + 1, indizes[-1]+len(forecasted_values) + 1)
    
    bridge_indizes = [indizes[-1], indizes_forecast[0]]
    bridge_values_1 = [last_quote, forecasted_future_prices_top[0]]
    bridge_values_2 = [last_quote, forecasted_future_prices_bottom[0]]

    
    if history > 0:
        shoting_factor = 0 #if history_size < len(predicted_labels_orig) + 3 else len(predicted_labels_orig) + 5
        last_quotes_2 = true_closings.tolist()
        indizes_2 = list(range(list(indizes_forecast)[0], list(indizes_forecast)[0] + len(true_closings)))
        last_quotes_2.insert(0, last_quote_of_forecast)
        indizes_2.insert(0, indizes[-1])
        last_quotes_2 = last_quotes_2[:plot_history+1]
        indizes_2 = indizes_2[:plot_history+1]
        plt.plot(indizes_2, last_quotes_2, ':', color='midnightblue', label='Real Close', alpha=0.3)
        plt.plot(indizes_2[-1 * len(true_highs):], true_highs, '--', color='black', alpha=0.15)
        plt.plot(indizes_2[-1 * len(true_highs):], true_lows, '--', color='black', alpha=0.15)


    plt.axhline(y=last_quotes[-1], color='grey', linestyle='-')
    plt.plot(indizes, last_quotes, color='black', label='Close')
    plt.plot(indizes, last_lows, '--', alpha=0.3, color='black', label='High')
    plt.plot(indizes, last_highs, '--', alpha=0.3, color='black', label='High')

    
    a = 0.3
    redyellow = 'yellow' if not is_negative else 'red'
    plt.fill_between(indizes_forecast, confidence_extended_1, confidence_extended_2, color='green', alpha=0.2)
    plt.fill_between(indizes_forecast, forecasted_future_prices_top, forecasted_future_prices_bottom, color=redyellow, alpha=0.5)

    plt.plot(indizes[-1], last_quotes[-1], 'bo', label='Forecast', alpha=a, color='navy')
    plt.plot(indizes_forecast, forecasted_future_prices_top, 'bo', label='Forecast', alpha=a, color='navy')
    plt.plot(indizes_forecast, forecasted_future_prices_top, 'bo', label='Forecast', alpha=a, color='navy')
    

    if sl_before != -1 and sl_before > last_quote_of_forecast * 0.9:
        plt.axhline(sl_before, ls=':', color='orange')
    if sl_after != 9999999999 and sl_after < last_quote_of_forecast * 1.1:
        plt.axhline(sl_after, ls=':', color='orange')  
        
    trend_1 = forecast['trendline_extended_1'] # extend_trendline(trend_lines[0], iterations=len(indizes_forecast))
    trend_2 = forecast['trendline_extended_2'] # extend_trendline(
    plt.plot(indizes_forecast, trend_1, color='blue', alpha=0.5)
    plt.plot(indizes_forecast, trend_2, color='blue', alpha=0.5)
      
      

    default_distance = (indizes_forecast[1] - indizes_forecast[0]) // 2
    plt.plot(bridge_indizes, bridge_values_1, '--', color='lavender', alpha=a)
    plt.plot(bridge_indizes, bridge_values_2, '--', color='lavender', alpha=a)
    all_indizes = [*all_indizes, *indizes, *indizes_2]


    
    plt.title(forecast['symbol'] + ' / ' + forecast['interval'])
    all_indizes = list(set(all_indizes))[::2]
    
    all_indizes = [*indizes, *indizes_2]
    all_indizes = all_indizes[::2]
      # printd('** all_indizes: ', all_indizes)
    
    last_date_of_forecast = to_datetime(last_date_of_forecast)
    new_future_dates = [last_date_of_forecast + datetime.timedelta(minutes=true_date_interval * i) for i in range(1, len(forecasted_future_prices_top) + 1, 2)]
    date_array = [last_date_of_forecast - datetime.timedelta(minutes=true_date_interval * i) for i in range(len(last_quotes) - 2, 0, -2)] + [last_date_of_forecast] + new_future_dates

    if len(all_indizes) < len(date_array):
        all_indizes = all_indizes[:len(all_indizes)-1]
        date_array = date_array[:len(all_indizes)]
    
    plt.xticks(all_indizes, date_array, rotation=30, ha='right')
    plt.show()
    
