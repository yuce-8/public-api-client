from __future__ import absolute_import, division, print_function, unicode_literals


import pytz
import requests
class CustomUploader:
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        self.buffer = []

    def add_to_upload(self, Date_, Open, High, Low, Close, Volume):
        # ensure CET timezone
        DE_TMZ = pytz.timezone('Europe/Berlin')
        is_tmz_naive = Date_.tzinfo is None or Date_.tzinfo.utcoffset(Date_) is None
        if is_tmz_naive:
            Date_ = DE_TMZ.localize(Date_)
        else:
            Date_ = Date_.astimezone(DE_TMZ)
        self.buffer.append([Date_.strftime("%Y-%m-%d %H:%M:%S"), Open, High, Low, Close, Volume])


    def get_min_max_date_in_db(self):
        _ = { 'symbol': self.symbol, 'action': 'get_last_date' }
        r = requests.post('https://europe-west2-yuce-8-v1.cloudfunctions.net/custom_data_loader', json=_)
        result = r.json()
        if result['success']:
            DE_TMZ = pytz.timezone('Europe/Berlin')
            min_date = DE_TMZ.localize(datetime.datetime.strptime(result['min_date'], '%Y-%m-%d %H:%M:%S')) if not result['min_date'] is None else None
            max_date = DE_TMZ.localize(datetime.datetime.strptime(result['max_date'], '%Y-%m-%d %H:%M:%S')) if not result['max_date'] is None else None
            print('min/max date in db = ', min_date, ', ', max_date)
            return min_date, max_date
        else:
            print('error: ', result)


    def upload(self):
        print(f'upload buffer contains {len(self.buffer)}')
        def divide_chunks(l, n): 
            for i in range(0, len(l), n):
                yield l[i:i + n]
        # upload a maximum of 240 at once
        chunks = list(divide_chunks(self.buffer, 240))
        
        counter = 0
        for chunk in chunks:
            counter += 1
            _ = { 'symbol': self.symbol, 'action': 'upload', 'new_rows' : [] }
            for row in chunk:
                _['new_rows'].append(row)
            print(f'... uploading chunk {counter} of {len(chunks)}')
            r = requests.post('https://europe-west2-yuce-8-v1.cloudfunctions.net/custom_data_loader', json=_)
            print('result = ', r.json())

#----------------------------------------------------------------

#custom_uploader = CustomUploader('abc')
#custom_uploader.get_min_max_date_in_db()
#custom_uploader.add_to_upload(datetime.datetime.strptime('2022-12-29 20:00:00', '%Y-%m-%d %H:%M:%S'), 10, 12, 8, 11, 123)
#custom_uploader.add_to_upload(datetime.datetime.strptime('2022-12-29 20:01:00', '%Y-%m-%d %H:%M:%S'), 10, 12, 8, 11, 123)
#custom_uploader.upload()
