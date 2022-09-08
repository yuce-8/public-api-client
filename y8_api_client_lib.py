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
        
    
    def __init__(self, CLIENT_ID, EVENT_LISTENER, PARALLEL_EXECUTOR) -> None:
        self.CLIENT_ID = CLIENT_ID
        self.EVENT_LISTENER = EVENT_LISTENER
        self.stop = False
        self.PARALLEL_EXECUTOR = PARALLEL_EXECUTOR
        pass


    def start_listening(self, symbol='BTCUSD'):
        self.stop = False
        URL = 'https://storage.googleapis.com/y8-poc/trades/' + ('test' if self.CLIENT_ID is None else self.CLIENT_ID) + '-' + symbol + '.json'
           
        # wait until the next 5-minute tick
        tz_Berlin = pytz.timezone('Europe/Berlin')
        
        # now we got the next 5-minute tick, start quering the client file
        while not self.stop:
            print('waiting for next 5:20 minute tick... ', datetime.datetime.now(tz_Berlin))
            while not (datetime.datetime.now(tz_Berlin).minute % 5 == 0 and datetime.datetime.now(tz_Berlin).second == 20):
                time.sleep(1)
        
            try:
                print(URL)
                json_content = json.loads(requests.get(URL).text)
                print(json_content)
                id = json_content['ID']
                direction = json_content['DIRECTION']
                price_of_investment = json_content['PRICE_OF_INVESTMENT'] if 'PRICE_OF_INVESTMENT' in json_content else None
                timestamp = json_content['TIMESTAMP']
                if direction == 'CLOSED' and not self.EVENT_LISTENER is None and not self.PARALLEL_EXECUTOR is None:
                    # position was closed
                    self.PARALLEL_EXECUTOR.submit(self.EVENT_LISTENER.position_got_closed, id, price_of_investment, timestamp)
                elif direction in ['LONG', 'SHORT'] and not self.EVENT_LISTENER is None and not self.PARALLEL_EXECUTOR is None:
                    # position was opened
                    self.PARALLEL_EXECUTOR.submit(self.EVENT_LISTENER.position_got_opened, id, direction, price_of_investment, timestamp)
            except:
                print('no file for ', self.CLIENT_ID, ' available yet')
                time.sleep(2)



    def stop_listening(self):
        self.stop = True


#----------------------------------------------------------------------------------------

class SAMPLE_EVENT_LISTENER:

    def __init__(self):
        self.last_known_closed_id = -1
        self.last_known_opened_id = -1

    def position_got_closed(self, id, price_of_investment, timestamp):
        if id != self.last_known_closed_id:
            # this one is new:
            print('the BTC position got closed at ', price_of_investment, '$ / ', timestamp)
            self.last_known_closed_id = id
    
    def position_got_opened(self, id, direction, price_of_investment, timestamp):
        if id != self.last_known_opened_id:
            # this one is new:
            print('a new BTC position was opened: ', direction, ', ', price_of_investment, '$, ', timestamp)
            self.last_known_opened_id = id


