#import libraries
import pytz
from datetime import datetime
from zipline.api import order, symbol, record, order_target
from zipline.algorithm import TradingAlgorithm
from zipline.utils.factory import load_bars_from_yahoo
import pyexcel
import pandas.io.data as web
import zipline
from collections import OrderedDict
import pandas as pd
                       
#extracting data from csv
datas = OrderedDict()
datas['SPY'] = pd.read_csv('/home/priyanka.s/work/algorithms/mac/AAPL_web.csv', index_col=0, parse_dates=['Date'])
#datas['SPY'] = pd.read_csv('/home/priyanka.s/work/algorithms/mac/CHRIS-CME_GC1.csv', index_col=0, parse_dates=['Date'])
#datas['SPY'] = datas['SPY'][::-1]

#converting dataframe data into panel
panel = pd.Panel(datas)
panel.minor_axis = ['open', 'high', 'low', 'close', 'volume', 'price']
panel.major_axis = panel.major_axis.tz_localize(pytz.utc)
                   
csv_data = []
def initialize(context):
    context.security = symbol('SPY')
    csv_data.append(["date","MA1","MA2","Current Price","Buy/Sell","Shares","PnL","Cash","Value"])

def handle_data(context, panel):
    #calculating moving average
    MA1 = panel[context.security].mavg(50)
    MA2 = panel[context.security].mavg(100)
    date = str(panel[context.security].datetime)[:10]
    #calculating price, pnl, portfolio value
    current_price = panel[context.security].price
    current_positions = context.portfolio.positions[symbol('SPY')].amount
    cash = context.portfolio.cash
    value = context.portfolio.portfolio_value
    current_pnl = context.portfolio.pnl
    #to buy stock
    if (MA1 > MA2) and current_positions == 0:
        number_of_shares = int(cash/current_price)
        order(context.security, number_of_shares)
        #recording the data
        record(date=date,MA1 = MA1, MA2 = MA2, Price= current_price,status="buy",shares=number_of_shares,\
        PnL=current_pnl,cash=cash,value=value)
        csv_data.append([date,format(MA1, '.2f'),format(MA2, '.2f'),format(current_price, '.2f'),\
        "buy",number_of_shares,format(current_pnl, '.2f'),format(cash, '.2f'),format(value, '.2f')])
    #to sell stocks
    elif (MA1 < MA2) and current_positions != 0:
        order_target(context.security, 0)
        record(date=date,MA1 = MA1, MA2 = MA2, Price= current_price,status="sell",shares="--",\
        PnL=current_pnl,cash=cash,value=value)
        csv_data.append([date,format(MA1, '.2f'),format(MA2, '.2f'),format(current_price, '.2f'),\
        "sell","--",format(current_pnl, '.2f'),format(cash, '.2f'),format(value, '.2f')])
    #do nothing just record the data
    else:
        record(date=date,MA1 = MA1, MA2 = MA2, Price= current_price,status="--",shares="--",\
        PnL=current_pnl,cash=cash,value=value)
        csv_data.append([date,format(MA1, '.2f'),format(MA2, '.2f'),format(current_price, '.2f'),\
        "--","--",format(current_pnl, '.2f'),format(cash, '.2f'),format(value, '.2f')])

#initializing trading enviroment
algo_obj = TradingAlgorithm(initialize=initialize, handle_data=handle_data, capital_base = 100000.0)

#run algo
perf_manual = algo_obj.run(panel)
#plotting graph
print perf_manual[["MA1","MA2","Price","status","PnL"]][50:]
perf_manual[["MA1","MA2","Price"]].plot()
#saving csv
pyexcel.save_as(array = csv_data, dest_file_name = 'mac_zipline.csv')
#calculation 
print "\n\n\ntotal pnl : " + str(float(perf_manual[["PnL"]].iloc[-1]))
buy_trade = perf_manual[["status"]].loc[perf_manual["status"] == "buy"].count()
sell_trade = perf_manual[["status"]].loc[perf_manual["status"] == "sell"].count()
total_trade = buy_trade + sell_trade
print "buy trade : " + str(int(buy_trade)) + " sell trade : " + str(int(sell_trade)) + " total trade : " + str(int(total_trade))
