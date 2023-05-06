from __future__ import absolute_import, division, print_function, unicode_literals
import traceback
import numpy as np
import datetime
import concurrent
import time
import threading
import pandas as pd
import uuid
import os
import sys
import traceback
import pytz

#-----------------------------------------------------------------------------------------------------------
SILENT_MODE = False
DO_NOT_INVEST = True
#------------------------------------------------------------------------------------------------------------

def printd(*a, **k):
    print(*a, **k)

if 'google.colab' in sys.modules:
    IS_COLAB_RUNTIME = True
    print('P A P E R   T R A D E   B T C   C O L A B   M O D E')
else:
    IS_COLAB_RUNTIME = False
    print('P A P E R   T R A D E   B T C   G C P   M O D E')
    

printd('READY FOR PAPERTRADES...')

IS_GCP_MODE = not IS_COLAB_RUNTIME
#IS_COLAB_RUNTIME = True

#------------------------------------------------------------------------------------------------------------

# extends the trendline for n-iterations
def extend_trendline(trend_line, iterations=13, including_last_close=False):
    m = trend_line[-1] / trend_line[-2]
    last_ = trend_line[-1]
    tl = [last_] if including_last_close else []
    for i in range(0, iterations):
        next_ = last_ * m
        last_ = next_
        tl.append(next_)
    return tl

#------------------------------------------------------------------------------------------------------------

def datetime_in_range(start, end, current_Date):
    return start <= current_Date.time() <= end

#------------------------------------------------------------------------------------------------------------

def to_datetime(x):
    try:
        x = str(x).replace('T', ' ')
        if len(x) > 19:
            x = x[:19]
        elif len(x) == 10:
            x = x + '00:00:00'
        return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    except:
        return x
    
#------------------------------------------------------------------------------------------------------------

def calculate_avg_forecast(top, bottom):
  avg_forecast = []
  for i in range(0, len(top)):
    avg_forecast.append(round(bottom[i] + (top[i] - bottom[i]) / 2, 2))
  return avg_forecast

#-----------------------------------------------------------------------------------------------------------

PRICES_COMING_FROM_TOP = '\\'    
PRICES_COMING_IN_FLAT = '-'
PRICES_COMING_FROM_BOTTOM = '/'

def describe_price_history(price_history):
    global PRICES_COMING_FROM_BOTTOM, PRICES_COMING_FROM_TOP, PRICES_COMING_IN_FLAT
    # calculate the average of the last 6 * 30 minutes while every price in history is 5 minutes
    length_of_price_history = len(price_history)
    price_history = [q['Close'] for q in price_history] 
    historical_timeframe = 6 * 30 * 5
    current_price = price_history[-1]
    if length_of_price_history >= historical_timeframe:
        look_back_snippet = price_history[-historical_timeframe:-1]
        avg_prices = np.mean(look_back_snippet)
        look_back_snippet = price_history[-historical_timeframe:-15]
        max_price_in_look_back_snippet = max(look_back_snippet)
        if avg_prices > current_price and max_price_in_look_back_snippet > current_price * 1.011:
            return PRICES_COMING_FROM_TOP
        else:
            min_price_in_look_back_snippet = min(look_back_snippet)
            if avg_prices < current_price and min_price_in_look_back_snippet < current_price * 0.989:
                return PRICES_COMING_FROM_BOTTOM

    return PRICES_COMING_IN_FLAT

#-----------------------------------------------------------------------------------------------------------


FUTURE_WILL_BE_VOLATILE_BULLISH_WITH_PEAK_IN_THE_MIDDLE = '__/^^-'
FUTURE_WILL_BE_VOLATILE_BULLISH_WITH_PEAK_AT_THE_END = '__/^'
FUTURE_IS_UNDEFINED = '?'
FUTURE_IS_NEGATIVE_WITH_A_SPIKE_OF_HOPE_IN_THE_MIDDLE = '__/\\__'
FUTURE_IS_VERY_NEGATIVE = '\\--__'
FUTURE_IS_NEGATIVE_U = '\\__//'
FUTURE_IS_NEGATIVE_WITH_HAPPY_END = '\\_|^^'
FUTURE_IS_NEGATIVE_AND_FLAT = '-------'
FUTURE_IS_POSITIVE_WITH_HAPPY_START = '/\\+'
FUTURE_IS_POSITIVE_WITH_HAPPY_START_BUT_FAILING_END = '/\\-'
FUTURE_IS_NEGATIVE_WITH_POSITIVE_START = '^/_'
FUTURE_IS_NEGATIVE_WITH_DOUBLE_DIP = '\\/\\_'
FUTURE_IS_VERY_NEGATIVE_AT_THE_END = 'oo\\_'
JUST_NEGATIVE = 'JUST NEG'     # \___
NEG_V_SHAPE = 'NEG V SHAPE'    # \\_/
SUPER_NEGATIVE = 'SUPER NEG'   # \__\\
NEG_TRUMPET = 'NEG TRUMP' # <

NEGATIVES = [JUST_NEGATIVE, NEG_V_SHAPE, SUPER_NEGATIVE, NEG_TRUMPET]

JUST_POSITIVE = 'JUST POS'     # /~~~
POS_HAT = 'POS HAT'            # /~~\
POS_HOCKEY = 'POS HOCKEY'      # ////
POS_S = 'POS S'                #__/~~
FALSE_V = 'FALSE V'            # \\_//
POS_TRUMPET = 'POS TRUMP'      # <

POSITIVES = [JUST_POSITIVE, POS_HAT, POS_HOCKEY, POS_S, FALSE_V, POS_TRUMPET]

FUTURE_SUPPORT_RESISTANCE_FLOW_NEG = '___'
FUTURE_SUPPORT_RESISTANCE_FLOW_NEG_X_ING_SUPPORT = '**_'
FUTURE_SUPPORT_RESISTANCE_FLOW_NEUTRAL = '---'
FUTURE_SUPPORT_RESISTANCE_FLOW_POS_X_ING_RESISTANCE = '**^'
FUTURE_SUPPORT_RESISTANCE_FLOW_POS = '^^^'



def describe_future_resistance_and_support(f_0):
    try:
        f_0_top, f_0_bottom = f_0['quotes_forecast_top_incl_vola'], f_0['quotes_forecast_bottom_incl_vola']
        avg_forecast = calculate_avg_forecast(f_0_top, f_0_bottom)
        has_support = f_0['next_support'] > 1
        has_resistance = f_0['next_resistance'] < 999999
        numbers = []
        if has_support:
            for i in range(0, len(avg_forecast)):
                if f_0['next_support'] >= avg_forecast[i]:
                    numbers.append(-1)
                else:
                    numbers.append(0)
        numbers2 = []
        if has_resistance:
            for i in range(0, len(avg_forecast)):
                if f_0['next_resistance'] < avg_forecast[i]:
                    numbers2.append(1)
                else:
                    numbers2.append(0)
        result = []
        for i in range(0, len(numbers)):
            if numbers2[i] == 1:
                result.append(1)
            elif numbers[i] == -1:
                result.append(-1)
            else:
                result.append(0)    
        if sum(result) == len(avg_forecast):
            return FUTURE_SUPPORT_RESISTANCE_FLOW_POS
        elif sum(result) == -1 * len(avg_forecast):
            return FUTURE_SUPPORT_RESISTANCE_FLOW_NEG
        elif -1 in result[9:]:
            return FUTURE_SUPPORT_RESISTANCE_FLOW_NEG_X_ING_SUPPORT
        elif 1 in result[9:]:
            return FUTURE_SUPPORT_RESISTANCE_FLOW_POS_X_ING_RESISTANCE
        else:
            return FUTURE_SUPPORT_RESISTANCE_FLOW_NEUTRAL
    except:
        return '?'

def describe_future_behavior(f_0):
    forecast = f_0['forecast']
    forecasted_prices_top = f_0['quotes_forecast_top_incl_vola']
    forecasted_prices_bottom = f_0['quotes_forecast_bottom_incl_vola']
    last_quote = f_0['last_quote']
    len_forecast = len(forecast)
    _2nd_half_of_forecast = forecast[4:]
    _1st_half_of_forecast = forecast[:4]

    avg_1st_half_of_forecast = np.mean(_1st_half_of_forecast)
    avg_2nd_half_of_forecast = np.mean(_2nd_half_of_forecast)
    is_last_forecast_the_maximum = max(_2nd_half_of_forecast) == _2nd_half_of_forecast[-1]
    is_last_forecast_the_minimum = min(_2nd_half_of_forecast) == _2nd_half_of_forecast[-1]
    all_positive = np.sum([1 if f < 0 else 0 for f in forecast]) == 0
        
    if avg_2nd_half_of_forecast > 4:
        # looks like it's very bullish
        if is_last_forecast_the_maximum and all_positive:
            return FUTURE_WILL_BE_VOLATILE_BULLISH_WITH_PEAK_AT_THE_END
        else:
            return FUTURE_WILL_BE_VOLATILE_BULLISH_WITH_PEAK_IN_THE_MIDDLE
    else:
        avg_1st_3 = np.mean(forecast[:3])
        avg_last_3 = np.mean(forecast[9:])
        are_1st_and_last_3_negative = avg_1st_3 < 0 and avg_last_3 < 0
        is_there_a_spike_in_the_middle = max(forecast[3:9]) >= 2
        if are_1st_and_last_3_negative and is_there_a_spike_in_the_middle:
            return FUTURE_IS_NEGATIVE_WITH_A_SPIKE_OF_HOPE_IN_THE_MIDDLE
        else:
            number_of_negatives = np.sum([1 if f < 0 else 0 for f in forecast])
            if number_of_negatives == len_forecast and avg_1st_half_of_forecast > avg_2nd_half_of_forecast and avg_2nd_half_of_forecast > -5 and max(forecasted_prices_top[-4:] + forecasted_prices_bottom[-4:]) < last_quote:
                return FUTURE_IS_VERY_NEGATIVE
            else:
                if number_of_negatives == len_forecast and avg_1st_half_of_forecast < avg_2nd_half_of_forecast:
                    return FUTURE_IS_NEGATIVE_U
                else:
                    are_the_1st_4_negative = np.sum([1 if f < 0 else 0 for f in forecast[:4]]) >= 3
                    are_the_last_4_positive = np.sum([1 if f > 0 else 0 for f in forecast[-4:]]) == 4
                    if are_the_1st_4_negative and are_the_last_4_positive:
                        return FUTURE_IS_NEGATIVE_WITH_HAPPY_END
                    else:
                        if number_of_negatives == len_forecast and min(forecast) > -5:
                            return FUTURE_IS_NEGATIVE_AND_FLAT
                        else:
                            number_of_positives = np.sum([1 if f > 0 else 0 for f in forecast])
                            if number_of_positives == len_forecast and max(forecast) == max(forecast[:6]):
                                return FUTURE_IS_POSITIVE_WITH_HAPPY_START
                            else:
                                if number_of_positives >= len_forecast - 4 and max(forecast) == max(forecast[:6]):
                                    return FUTURE_IS_POSITIVE_WITH_HAPPY_START_BUT_FAILING_END
                                else:
                                    number_of_positives = np.sum([1 if f > 0 else 0 for f in forecast[:5]])
                                    number_of_negatives = np.sum([1 if f < 0 else 0 for f in forecast[-5:]])
                                    if number_of_positives == number_of_negatives:
                                        return FUTURE_IS_NEGATIVE_WITH_POSITIVE_START
                                    else:
                                        are_the_last_4_negative = np.sum([1 if f < 0 else 0 for f in forecast[-4:]]) == 4
                                        is_1_in_between_positive = np.sum([1 if f > 0 else 0 for f in forecast[5:-5]]) > 0
                                        if are_the_1st_4_negative and are_the_last_4_negative and is_1_in_between_positive:
                                            return FUTURE_IS_NEGATIVE_WITH_DOUBLE_DIP
                                        else:
                                            if min(forecast[-5:]) < -7:
                                                return FUTURE_IS_VERY_NEGATIVE_AT_THE_END
                                        
    
    return FUTURE_IS_UNDEFINED    




#-----------------------------------------------------------------------------------------------------------

class BTC_1d_Wonder:
    def __init__(self, event_listener=None) -> None:
        self.invested = False
        self.ready_for_investment = False
        self.ready_for_investment_entry_price = 0
        self.ready_for_investment_maximum_Date_ = None
        self.ready_for_investment_entry_Date_ = None
        self.entry_price_of_investment = 0
        self.exit_price_of_investment = 0
        self.entry_date_of_investment = None
        self.exit_date_of_investment = None
        self.direction_of_investment = None
        self.f_0_description = None
        self.f_0_support_resistance_description = None
        self.take_profit_at = 0
        self.stop_loss_at = 0
        self.balance = 0
        self.status_change = False
        self.current_investment_trigger = -1
        self.investment_trigger = {
            'very-bullish': 1,
            'very-bearish': 2
        }
        self.stats = []
        self.event_listener = event_listener
        
    
    def run_quality_check(self):
        SIG = 'BTC_1d_Wonder.run_quality_check | '
        start_time = time.time()
        success = False
        try:
            printd(SIG, 'importing kraken lib...')
            from .yuce_8_kraken import SYMBOL_4_BTC
            from . import yuce_8_kraken
            kraken = yuce_8_kraken.Y8_Kraken(account=2)
      
            should_be_invested = self.invested
            is_really_invested = kraken.is_among_open_orders(SYMBOL_4_BTC) or kraken.is_among_open_positions(SYMBOL_4_BTC)
            printd(SIG, 'checking, if BTC is among open positions / orders: ', is_really_invested)
            printd(SIG, 'checking, if BTC should be invested: ', should_be_invested)
            if not should_be_invested and is_really_invested:
                printd(SIG, 'there is a mismatch... order opened manually')
                current_investment_volume, current_investment_avg_price, current_investment_direction, current_real_win_loss = kraken.calculate_current_investment(SYMBOL_4_BTC)
                printd(SIG, f'real investment = {current_investment_direction} @ {current_investment_avg_price}')
                self.invested = True
                self.ready_for_investment = False
                self.entry_price_of_investment = current_investment_avg_price
                self.entry_date_of_investment = just_now = datetime.datetime.now()
                self.status_change = True
                if not self.event_listener is None and not self.event_listener.discord is None:
                    self.event_listener.discord.post(f'detected manual order creation: {current_investment_direction} @ {current_investment_avg_price}')
            elif should_be_invested and not is_really_invested:
                printd(SIG, 'there is a mismatch... order closed manually')
                current_investment_volume, current_investment_avg_price, current_investment_direction, current_real_win_loss = kraken.calculate_current_investment(SYMBOL_4_BTC)
                printd(SIG, f'real investment = {current_investment_direction} @ {current_investment_avg_price}')
                self.invested = False
                self.ready_for_investment = False
                self.entry_price_of_investment = None
                self.entry_date_of_investment = None
                self.status_change = True
                if not self.event_listener is None and not self.event_listener.discord is None:
                    self.event_listener.discord.post(f'detected manual position close')
            success = True
        except Exception as E:
            printd(SIG, 'ERROR = ', E)
            traceback.print_exc()
        printd(SIG, f'finished after {time.time() - start_time}. success = {success}')

    
        
    def save_latest_state(self, IS_LOCAL, GCP_STORAGE_LOADER):
        SIG = 'BTC_1d_Wonder.save_latest_state | '
        success = False
        start_time = time.time()
        try:
            from . import yuce_8_json_serializer as y8_json
            serializer = y8_json.JSON_Serializer(IS_LOCAL, GCP_STORAGE_LOADER)
            serializer.serizalize({
                    'invested': self.invested,
                    'ready_for_investment': self.ready_for_investment,
                    'ready_for_investment_entry_price': self.ready_for_investment_entry_price,
                    'ready_for_investment_maximum_Date_': str(self.ready_for_investment_maximum_Date_),
                    'ready_for_investment_entry_Date_': str(self.ready_for_investment_entry_Date_),
                    'entry_price_of_investment': self.entry_price_of_investment,
                    'entry_date_of_investment': str(self.entry_date_of_investment),
                    'exit_date_of_investment': str(self.exit_date_of_investment),
                    'direction_of_investment': self.direction_of_investment,
                    'balance': self.balance,
                    'current_investment_trigger': self.current_investment_trigger,
                    'tp_at': self.take_profit_at,
                    'sl_at': self.stop_loss_at,
                    'f_0_description': self.f_0_description,
                    'f_0_support_resistance_description': self.f_0_support_resistance_description
                }, 
                'BTC_1d_Wonder-status-quo.json', 
                upload_automatically=True
            )
            success = True
            del serializer
        except Exception as E:
            printd(SIG, 'ERROR = ', E)
            traceback.print_exc()
        printd(SIG, f'finished after {time.time() - start_time}. success = {success}')
        return success
        
            
    def restore_latest_state(self, IS_LOCAL, GCP_STORAGE_LOADER):
        SIG = 'BTC_1d_Wonder.save_latest_state | '
        success = False
        start_time = time.time()
        try:
            from . import yuce_8_json_serializer as y8_json
            serializer = y8_json.JSON_Serializer(IS_LOCAL, GCP_STORAGE_LOADER)
            _ = serializer.deserizalize('BTC_1d_Wonder-status-quo.json')
            if not _ is None:
                self.invested = _['invested']
                self.ready_for_investment = _['ready_for_investment']
                self.ready_for_investment_entry_price = _['ready_for_investment_entry_price']
                self.ready_for_investment_maximum_Date_ = to_datetime(_['ready_for_investment_maximum_Date_'])
                self.ready_for_investment_entry_Date_ = to_datetime(_['ready_for_investment_entry_Date_'])                
                self.entry_date_of_investment = to_datetime(_['entry_date_of_investment'])
                self.exit_date_of_investment = to_datetime(_['exit_date_of_investment'])
                self.entry_price_of_investment = _['entry_price_of_investment']
                self.direction_of_investment = _['direction_of_investment']
                self.balance = _['balance']
                self.current_investment_trigger = _['current_investment_trigger']
                if 'tp_at' in _:
                    self.take_profit_at = _['tp_at']
                if 'sl_at' in _:
                    self.stop_loss_at = _['sl_at']
                if 'f_0_description' in _:
                    self.f_0_description = _['f_0_description']
                if 'f_0_support_resistance_description' in _:
                    self.f_0_support_resistance_description = _['f_0_support_resistance_description']
                success = True
            del serializer
        except Exception as E:
            printd(SIG, 'ERROR = ', E)
            traceback.print_exc()
        printd(SIG, f'finished after {time.time() - start_time}. success = {success}')
        return success


    def is_discord_available(self):
        return not (self.event_listener is None) and not (self.event_listener.discord is None)


    def process_1d_forecast(self, f_0):
        global IS_GCP_MODE
        SIG = "BTC_1d_Wonder.process_1d_forecast | "
        last_date = to_datetime(f_0['last_date'])#.replace(tzinfo=pytz.timezone('Europe/Berlin'))
        last_quote = float(f_0['last_quote'])
        f_0_description = describe_future_behavior(f_0)
        sup_res_description = describe_future_resistance_and_support(f_0)
        
        _ = f'f_0 ({last_date}/{last_quote}): f_0_description = {f_0_description}, sup_res_description = {sup_res_description}'
        printd(SIG, _)
        if self.is_discord_available():
            self.event_listener.discord.post(_)
            self.event_listener.discord.post(f'before: is_invested? {self.invested}, is ready for investment? {self.ready_for_investment}')
        
        if not self.invested and not self.ready_for_investment:
            if f_0_description in [FUTURE_WILL_BE_VOLATILE_BULLISH_WITH_PEAK_AT_THE_END, FUTURE_WILL_BE_VOLATILE_BULLISH_WITH_PEAK_IN_THE_MIDDLE] and sup_res_description in [FUTURE_SUPPORT_RESISTANCE_FLOW_POS_X_ING_RESISTANCE, FUTURE_SUPPORT_RESISTANCE_FLOW_POS]:
                printd(SIG, '***')
                printd(SIG, '***')
                printd(SIG, '***')
                printd(SIG, '*** W A I T I N G   4   I N V E S T I N G   L O N G ***')
                self.ready_for_investment = True
                self.direction_of_investment = 'LONG'
                self.ready_for_investment_maximum_Date_ = last_date + datetime.timedelta(days=7)
                self.ready_for_investment_entry_Date_ = last_date
                self.ready_for_investment_entry_price = last_quote * 0.975
                self.take_profit_at = 107.5
                self.stop_loss_at = 95
                self.current_investment_trigger = self.investment_trigger['very-bullish']
                self.f_0_description = f_0_description
                self.f_0_support_resistance_description = sup_res_description
                self.status_change = True
                printd(SIG, '*** trigger price = ', self.ready_for_investment_entry_price)
                printd(SIG, '***')
                printd(SIG, '***')
                
            elif f_0_description in [FUTURE_IS_NEGATIVE_WITH_POSITIVE_START, FUTURE_IS_VERY_NEGATIVE]: 
                printd(SIG, '***')
                printd(SIG, '***')
                printd(SIG, '***')
                printd(SIG, '*** W A I T I N G   4   I N V E S T I N G   S H O R T ***')
                self.ready_for_investment = True
                self.direction_of_investment = 'SHORT'
                self.ready_for_investment_maximum_Date_ = last_date + datetime.timedelta(days=6)
                self.ready_for_investment_entry_Date_ = last_date
                self.ready_for_investment_entry_price = last_quote * 1.025
                self.take_profit_at = 103
                self.stop_loss_at = 95
                self.f_0_description = f_0_description
                self.f_0_support_resistance_description = sup_res_description
                self.current_investment_trigger = self.investment_trigger['very-bearish']
                self.status_change = True
                printd(SIG, '*** trigger price = ', self.ready_for_investment_entry_price)
                printd(SIG, '***')
                printd(SIG, '***')
            
            elif self.is_discord_available():
                self.event_listener.discord.post('no investment strategy found for this setup...')
                
            if not self.event_listener is None and self.ready_for_investment:
                self.event_listener.is_ready_to_invest_event(self.direction_of_investment, self.ready_for_investment_maximum_Date_, self.ready_for_investment_entry_price)
                if self.is_discord_available():
                    self.event_listener.discord.post(f'I N V E S T   ==>  direction = {self.direction_of_investment}, now = {last_quote} / {last_date}, trigger price = {self.ready_for_investment_entry_price} before {self.ready_for_investment_maximum_Date_}')
                    
        
        
    #-------------                        
    
    def process_quote(self, Date_, Close):
        global IS_GCP_MODE
        SIG = "BTC_1d_Wonder.process_quote | "
        try:
            if IS_GCP_MODE:
                printd(SIG, f'Date = {Date_}, Close = {Close}')

            
            if self.ready_for_investment:
                if to_datetime(Date_) > self.ready_for_investment_maximum_Date_:
                    self.ready_for_investment = False
                    return 
                
                if Close <= self.ready_for_investment_entry_price and self.current_investment_trigger == self.investment_trigger['very-bullish']:
                    printd(SIG, '***')
                    printd(SIG, '***')
                    printd(SIG, '***')
                    printd(SIG, '*** I N V E S T I N G   L O N G ***')
                    printd(SIG, '*** trigger = ', self.current_investment_trigger)
                    printd(SIG, '***')
                    self.invested = True
                    self.ready_for_investment = False
                    self.entry_price_of_investment = Close
                    self.entry_date_of_investment = Date_
                    self.status_change = True

                elif Close >= self.ready_for_investment_entry_price and self.current_investment_trigger == self.investment_trigger['very-bearish']:
                    printd(SIG, '***')
                    printd(SIG, '***')
                    printd(SIG, '***')
                    printd(SIG, '*** I N V E S T I N G   S H O R T ***')
                    printd(SIG, '*** trigger = ', self.current_investment_trigger)
                    printd(SIG, '***')
                    self.invested = True
                    self.ready_for_investment = False
                    self.entry_price_of_investment = Close
                    self.entry_date_of_investment = Date_
                    self.status_change = True

                if not self.event_listener is None and self.invested:
                    self.event_listener.is_invested_event(self.direction_of_investment, self.entry_price_of_investment, self.entry_date_of_investment)



            elif self.invested:
                if self.current_investment_trigger == self.investment_trigger['very-bullish']:
                    difference = round(Close / self.entry_price_of_investment * 100, 1)
                    printd(SIG, 'difference = ', difference, ' | ', Date_, ', ', Close, ' <> ', self.entry_date_of_investment, ', ', self.entry_price_of_investment)        
                    if difference > self.take_profit_at:
                        printd(SIG, '###')
                        printd(SIG, '###')
                        printd(SIG, '### E X I T I N G')
                        self.exit_price_of_investment = Close
                        self.exit_date_of_investment = Date_
                        self.balance += (difference - 100)
                        self.stats.append([
                            self.entry_date_of_investment, self.exit_date_of_investment, self.direction_of_investment, self.balance, self.f_0_description, self.f_0_support_resistance_description
                        ])
                        self.invested = False
                        self.ready_for_investment = False
                        self.direction_of_investment = None
                        self.status_change = True
                        printd(SIG, '###')
                        printd(SIG, '### BALANCE = ', self.balance)
                        printd(SIG, '### duration = ', self.exit_date_of_investment - self.entry_date_of_investment)      
                    elif difference < self.stop_loss_at:
                        printd(SIG, '###')
                        printd(SIG, '###')
                        printd(SIG, '### S T O P   L O S S')
                        self.exit_price_of_investment = Close
                        self.exit_date_of_investment = Date_
                        self.balance += (difference - 100)
                        self.stats.append([
                            self.entry_date_of_investment, self.exit_date_of_investment, self.direction_of_investment, self.balance, self.f_0_description, self.f_0_support_resistance_description
                        ])
                        self.invested = False
                        self.ready_for_investment = False
                        self.direction_of_investment = None
                        self.status_change = True
                        printd(SIG, '###')
                        printd(SIG, '### BALANCE = ', self.balance)
                        printd(SIG, '### duration = ', self.exit_date_of_investment - self.entry_date_of_investment)      
                    if not self.event_listener is None and not self.event_listener.discord is None:
                        self.event_listener.discord.post(f'difference = {difference} // SL @ {self.stop_loss_at}, TP @ {self.take_profit_at}')
                    
                elif self.current_investment_trigger == self.investment_trigger['very-bearish']:
                    difference = round((1 + (1 - (Close / self.entry_price_of_investment))) * 100, 1)
                    #printd(SIG, 'difference = ', difference, ' | ', Date_, ', ', Close, ' <> ', self.entry_date_of_investment, ', ', self.entry_price_of_investment)        
                    if difference > self.take_profit_at:
                        printd(SIG, '###')
                        printd(SIG, '###')
                        printd(SIG, '### E X I T I N G')
                        self.invested = False
                        self.ready_for_investment = False
                        self.exit_price_of_investment = Close
                        self.exit_date_of_investment = Date_
                        self.balance += (difference - 100)
                        self.stats.append([
                            self.entry_date_of_investment, self.exit_date_of_investment, self.direction_of_investment, self.balance, self.f_0_description, self.f_0_support_resistance_description
                        ])
                        self.invested = False
                        self.ready_for_investment = False
                        self.direction_of_investment = None
                        self.status_change = True
                        printd(SIG, '###')
                        printd(SIG, '### BALANCE = ', self.balance)
                        printd(SIG, '### duration = ', self.exit_date_of_investment - self.entry_date_of_investment)      
                    elif difference < self.stop_loss_at:
                        printd(SIG, '###')
                        printd(SIG, '###')
                        printd(SIG, '### S T O P   L O S S')
                        self.exit_price_of_investment = Close
                        self.exit_date_of_investment = Date_
                        self.balance += (difference - 100)
                        self.stats.append([
                            self.entry_date_of_investment, self.exit_date_of_investment, self.direction_of_investment, self.balance, self.f_0_description, self.f_0_support_resistance_description
                        ])
                        self.invested = False
                        self.ready_for_investment = False
                        self.direction_of_investment = None
                        self.status_change = True
                        printd(SIG, '###')
                        printd(SIG, '### BALANCE = ', self.balance)
                        printd(SIG, '### duration = ', self.exit_date_of_investment - self.entry_date_of_investment)      

                    if not self.event_listener is None and not self.event_listener.discord is None:
                        self.event_listener.discord.post(f'difference = {difference} // SL @ {self.stop_loss_at}, TP @ {self.take_profit_at}')


                if not self.event_listener is None and not self.invested:
                    self.event_listener.has_exited_event(self.direction_of_investment, self.entry_price_of_investment, self.entry_date_of_investment, self.exit_price_of_investment, self.exit_date_of_investment, self.balance, difference)

            
        except Exception as E:
            printd(SIG, 'ERROR: ', E)
            traceback.print_exc()

    #-------------                        
 
    def process_4h_forecast(self, f_0):
            global IS_GCP_MODE
            SIG = "BTC_1d_Wonder.process_4h_forecast | "
            last_date = to_datetime(f_0['last_date'])#.replace(tzinfo=pytz.timezone('Europe/Berlin'))
            last_quote = float(f_0['last_quote'])
            f_0_description = describe_future_behavior(f_0)
            sup_res_description = describe_future_resistance_and_support(f_0)
            
            _ = f'f_0 ({last_date}/{last_quote}): f_0_description = {f_0_description}, sup_res_description = {sup_res_description}'
            printd(SIG, _)
            if self.is_discord_available():
                self.event_listener.discord.post(_)
                self.event_listener.discord.post(f'before: is_invested? {self.invested}, is ready for investment? {self.ready_for_investment}')
            
            if not self.invested and not self.ready_for_investment:
                if f_0_description in [FUTURE_WILL_BE_VOLATILE_BULLISH_WITH_PEAK_AT_THE_END, FUTURE_WILL_BE_VOLATILE_BULLISH_WITH_PEAK_IN_THE_MIDDLE] and sup_res_description in [FUTURE_SUPPORT_RESISTANCE_FLOW_POS_X_ING_RESISTANCE, FUTURE_SUPPORT_RESISTANCE_FLOW_POS]:
                    printd(SIG, '***')
                    printd(SIG, '***')
                    printd(SIG, '***')
                    printd(SIG, '*** W A I T I N G   4   I N V E S T I N G   L O N G ***')
                    self.ready_for_investment = True
                    self.direction_of_investment = 'LONG'
                    self.ready_for_investment_maximum_Date_ = last_date + datetime.timedelta(hours=6*4)
                    self.ready_for_investment_entry_Date_ = last_date
                    self.ready_for_investment_entry_price = last_quote * 0.989
                    self.take_profit_at = 101
                    self.stop_loss_at = 98.2
                    self.current_investment_trigger = self.investment_trigger['very-bullish']
                    self.status_change = True
                    printd(SIG, '*** trigger price = ', self.ready_for_investment_entry_price)
                    printd(SIG, '***')
                    printd(SIG, '***')
                    
                elif f_0_description in [FUTURE_IS_NEGATIVE_WITH_POSITIVE_START, FUTURE_IS_VERY_NEGATIVE]: 
                    printd(SIG, '***')
                    printd(SIG, '***')
                    printd(SIG, '***')
                    printd(SIG, '*** W A I T I N G   4   I N V E S T I N G   S H O R T ***')
                    self.ready_for_investment = True
                    self.direction_of_investment = 'SHORT'
                    self.ready_for_investment_maximum_Date_ = last_date + datetime.timedelta(hours=6*4)
                    self.ready_for_investment_entry_Date_ = last_date
                    self.ready_for_investment_entry_price = last_quote * 1.011
                    self.take_profit_at = 101
                    self.stop_loss_at = 98.2
                    self.current_investment_trigger = self.investment_trigger['very-bearish']
                    self.status_change = True
                    printd(SIG, '*** trigger price = ', self.ready_for_investment_entry_price)
                    printd(SIG, '***')
                    printd(SIG, '***')
                
                elif self.is_discord_available():
                    self.event_listener.discord.post('no investment strategy found for this setup...')
                    
                if not self.event_listener is None and self.ready_for_investment:
                    self.event_listener.is_ready_to_invest_event(self.direction_of_investment, self.ready_for_investment_maximum_Date_, self.ready_for_investment_entry_price)
                    if self.is_discord_available():
                        self.event_listener.discord.post(f'I N V E S T   ==>  direction = {self.direction_of_investment}, now = {last_quote} / {last_date}, trigger price = {self.ready_for_investment_entry_price} before {self.ready_for_investment_maximum_Date_}')
                        
                        
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

# ---------------------------------------------


def get_ressource(email, resource):
  import requests
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
  
def get_test_data(email, interval):
    resource = f'test_dataset_BTC-USD_{interval}.csv'
    success, data = get_ressource(email, resource)
    if success:
      import pandas as pd
      from io import StringIO
      csvStringIO = StringIO(data)
      df = pd.read_csv(csvStringIO)
      df.Date_ = pd.to_datetime(df.Date_)
      return df
    else:
      return None

def get_test_forecasts(email):
  resource = 'test_dataset_BTC-USD-4hours_forecasts.json'
  success, data = get_ressource(email, resource)
  if success:
    import json
    return json.loads(data)
  else:
    return None
