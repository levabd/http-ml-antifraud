import os

from lib import Udger

data_dir = os.path.join(os.path.dirname(__file__), 'data')

udger = Udger(data_dir)
ua = udger.parse_ua('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9')

print(ua)