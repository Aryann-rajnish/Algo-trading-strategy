# This code is part of free course - Python For Algo Trading. Enroll at https://algoji.com/pro
# Copyright AlgoJi.com, all rights reserved

# Import Packages
import pyalgotrade.strategy as strategy
import pyalgotrade.technical.ma as ma
import pyalgotrade.plotter as plotter
import pyalgotrade.barfeed.csvfeed as csvfeed
import pyalgotrade.bar as bar

# Create Strategy Class
class MAStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, nfast, nslow):
        super(MAStrategy, self).__init__(feed, 100000)
        self.position = None
        self.instrument = instrument
        self.fastsma = ma.SMA(feed[instrument].getPriceDataSeries(), nfast)
        self.slowsma = ma.SMA(feed[instrument].getPriceDataSeries(), nslow)
    # Define Technical Indicators Functions
    def getfastSMA(self):
        return self.fastsma
    def getslowSMA(self):
        return self.slowsma
    # onBars used to define Buy, Sell rules. Enter Long Order = Buy when Fast SMA > Slow SMA,
    # Exit Order = Sell when Fast SMA < Slow SMA
    def onBars(self, bars):
        if self.slowsma[-1] is None:
            return
        if self.position is None:
            if self.fastsma[-1] > self.slowsma[-1]:
                self.position = self.enterLong(self.instrument, 1, True)
        elif self.fastsma[-1] < self.slowsma[-1]:
            self.position.exitMarket()
            # Update Strategy Position to None when a Buy-Sell cycle is complete
            self.position = None
    # onEnterOk: Tells us when order to Enter a position is filled
    def onEnterOk(self, position):
        # getting info for execution price and execution order type
        tradeInfo = position.getEntryOrder().getExecutionInfo()
        self.info("Buy shares at $%.2f" % (tradeInfo.getPrice()))
    # onExitOk: Tells us when order to Exit a position is filled
    def onExitOk(self, position):
        tradeInfo = position.getExitOrder().getExecutionInfo()
        self.info("Sell shares at $%.2f" % (tradeInfo.getPrice()))


# Define Function to Plot MAs
def MACrossSignals(nfast, nslow):
    # Create Instruments object with stock tickers
    instruments = ["NIFTY"]
    # create feed object, add bars to the data feed
    feed = csvfeed.GenericBarFeed(bar.Frequency.DAY)
    feed.addBarsFromCSV(instruments[0], "Data//NIFTY.csv")
    # create object to run strategy
    ma_signals = MAStrategy(feed, instruments[0], nfast, nslow)
    # Attach Strategy Plotter
    plt = plotter.StrategyPlotter(ma_signals,  plotAllInstruments=True, plotBuySell=True, plotPortfolio=False)
    plt.getInstrumentSubplot("NIFTY").addDataSeries("Fast SMA", ma_signals.getfastSMA())
    plt.getInstrumentSubplot("NIFTY").addDataSeries("Slow SMA", ma_signals.getslowSMA())
    # Run Strategy
    ma_signals.run()
    # Plot Strategy
    plt.plot()

# Hurray!
MACrossSignals(5, 20)
