import pandas as pd
from collections import OrderedDict
import pytz
from zipline.api import order, record, symbol
from zipline.algorithm import TradingAlgorithm
def initialize(context):
	context.security = symbol('HDFC')
   
def strategy(context, data):
    MA1 = data[context.security].mavg(10)
    MA2 = data[context.security].mavg(20)
    date = str(data[context.security].datetime)[:10]
    current_price = data[context.security].price
    current_positions = context.portfolio.positions[symbol('HDFC')].amount
    cash = context.portfolio.cash
    value = context.portfolio.portfolio_value
    current_pnl = context.portfolio.pnl
    
    
    
    if (MA1 > MA2) and current_positions == 0:
        number_of_shares = int(cash/current_price)
        order(context.security, number_of_shares)
        record(date=date,MA1 = MA1, MA2 = MA2, Price= 
        current_price,status="buy",shares=number_of_shares,PnL=current_pnl,cash=cash,value=value)
    
    elif (MA1 < MA2) and current_positions != 0:
        order_target(context.security, 0)
        record(date=date,MA1 = MA1, MA2 = MA2, Price= current_price,status="sell",shares="--",PnL=current_pnl,cash=cash,value=value)
    
    else:
        record(date=date,MA1 = MA1, MA2 = MA2, Price= current_price,status="--",shares="--",PnL=current_pnl,cash=cash,value=value)

	


algo_obj = TradingAlgorithm(initialize=initialize, handle_data=strategy)
#run algo
perf_manual = algo_obj.run(panel)
