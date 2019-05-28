import quandl
df = quandl.get("NSE/NIFTY_BANK",trim_start = "2007-01-01", trim_end = "2017-12-01")

#write to csv
df.to_csv("Data//BankNifty.csv", date_format= '%Y-%m-%d %H:%M:%S')

# Yahoo Finance
#instruments = ["^NSEI"]
#import pyalgotrade.tools.yahoofinance as yahooweb
#feed = yahooweb.build_feed(instruments, fromYear=2007, toYear=2016, storage="Data")