import os

from udger import Udger

data_dir = os.path.join(os.path.dirname(__file__), '../udger-data')

udger = Udger(data_dir)
ua = udger.parse_ua('Mozilla/5.0 (compatible; MJ12bot/v1.4.7; http://mj12bot.com/)')

print(ua)