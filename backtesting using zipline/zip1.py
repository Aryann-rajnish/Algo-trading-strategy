from zipline.api import order, record, symbol
from zipline.algorithm import TradingAlgorithm

def initialize(context):
   pass


def handle_data(context, data):
  order(symbol('AAPL'), 10)
  record(AAPL=data.current(symbol('AAPL'), 'price'))


algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
