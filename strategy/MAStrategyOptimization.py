# This code is part of free course - Python For Algo Trading. Enroll at https://algoji.com/pro
# Copyright AlgoJi.com, all rights reserved

# Import Packages
import itertools
import pyalgotrade.optimizer.local as local
import pyalgotrade.strategy as strategy
import pyalgotrade.technical.ma as ma
import pyalgotrade.barfeed.csvfeed as csvfeed
import pyalgotrade.bar as bar

# Create Strategy Class
class MAStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, nfast, nslow):
        super(MAStrategy, self).__init__(feed, 100000)
        self.position = None
        self.instrument = "NIFTY"
        self.setUseAdjustedValues(True)
        self.fastsma = ma.SMA(feed["NIFTY"].getPriceDataSeries(), nfast)
        self.slowsma = ma.SMA(feed["NIFTY"].getPriceDataSeries(), nslow)

    def getfastSMA(self):
        return self.fastsma
    def getslowSMA(self):
        return self.slowsma

    def onEnterOk(self, position):
        tradeInfo = position.getEntryOrder().getExecutionInfo()
        self.info("Buy shares at $%.2f" % (tradeInfo.getPrice()))
    def onExitOk(self, position):
        tradeInfo = position.getExitOrder().getExecutionInfo()
        self.info("Sell shares at $%.2f" % (tradeInfo.getPrice()))
        self.position = None

    def onBars(self, bars):
        if self.slowsma[-1] is None:
            return
        if self.position is None:
            if self.fastsma[-1] > self.slowsma[-1]:
                self.position = self.enterLong(self.instrument, 10, True)
        elif self.fastsma[-1] < self.slowsma[-1] and not self.position.exitActive():
            self.position.exitMarket()

# Create Parameter Combinations using itertools
def parameters():
    nfast = (5, 10, 15, 20, 25, 30)
    nslow = (20, 25, 30, 40, 50, 100)
    return itertools.product(nfast, nslow)

# Use optimizer from pyalgotrade
# If__name__ == '__main__': only needed for Windows
if __name__ == '__main__':
    instruments = ["NIFTY"]
    # Data Reading
    feed = csvfeed.GenericBarFeed(bar.Frequency.DAY)
    feed.addBarsFromCSV(instruments[0], "Data//NIFTY.csv")
    # Strategy Optimization
    local.run(MAStrategy, feed, parameters())
