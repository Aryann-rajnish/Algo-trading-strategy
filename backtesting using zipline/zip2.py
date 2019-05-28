
import pytz
from datetime import datetime
from zipline.api import order, symbol, record, order_target
from zipline.algorithm import TradingAlgorithm
from zipline.data.loader import load_bars_from_yahoo
import pyexcel

# Load data manually from Yahoo! finance
start = datetime(2011, 1, 1, 0, 0, 0, 0, pytz.utc).date()
end = datetime(2012,1,1,0,0,0,0, pytz.utc).date()

data = load_bars_from_yahoo(stocks=['SPY'], start=start,end=end)



#code
def initialize(context):
    context.security = symbol('SPY')


#code
def handle_data(context, data):
    MA1 = data[context.security].mavg(50)
    MA2 = data[context.security].mavg(100)
    date = str(data[context.security].datetime)[:10]
    current_price = data[context.security].price
    current_positions = context.portfolio.positions[symbol('SPY')].amount
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




