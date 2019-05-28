# This code is part of free course - Python For Algo Trading. Enroll at https://algoji.com/pro
# Copyright AlgoJi.com, all rights reserved

# Import Packages
import pyalgotrade.strategy as strategy
import pyalgotrade.technical.stats as stats
import pyalgotrade.technical.roc as roc
import pyalgotrade.technical.ma as ma
import pyalgotrade.plotter as plotter
import pyalgotrade.barfeed.csvfeed as csvfeed
import pyalgotrade.bar as bar
# Create Strategy Class
class ZScoreStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, nper, lowerThreshold, upperThreshold):
        super(ZScoreStrategy, self).__init__(feed)
        self.position = None
        self.instrument = instrument
        self.sma = ma.SMA(feed[instrument].getPriceDataSeries(), nper)
        self.roc = roc.RateOfChange(feed[instrument].getPriceDataSeries(), 1)
        self.zscore = stats.ZScore(self.roc, nper)
        self.lowerThreshold = lowerThreshold
        self.upperThreshold = upperThreshold

    # Define Technical Indicators Functions
    def getSMA(self):
        return self.sma
    def getZScore(self):
        return self.zscore
    # Define mandatory onBars Functions
    def onBars(self, bars):
        if self.sma[-1] is None:
            return
        if self.position is None:
            if  bars[self.instrument].getPrice() > self.sma[-1] > 0 and self.zscore[-1] < self.lowerThreshold:
                self.position = self.enterLong(self.instrument, 1, True)
        elif self.zscore[-1] > self.upperThreshold:
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
def ZScorePlot(nper, lowerThreshold, upperThreshold):
    # Create Instruments object with stock tickers
    instruments = ["NIFTY"]
    # create feed object, add bars to the data feed
    feed = csvfeed.GenericBarFeed(bar.Frequency.DAY)
    feed.addBarsFromCSV(instruments[0], "Data//NIFTY.csv")
    # create object to run strategy
    zscore_plot = ZScoreStrategy(feed, instruments[0], nper, lowerThreshold, upperThreshold)
    # Attach Strategy Plotter
    plt = plotter.StrategyPlotter(zscore_plot,  plotAllInstruments=True, plotBuySell=True, plotPortfolio=False)
    plt.getOrCreateSubplot("ZScore").addDataSeries("ZScore", zscore_plot.getZScore())
    # plt.getOrCreateSubplot("RSI").addLine("Center Line", 40)
    # Run Strategy
    zscore_plot.run()
    # Plot Strategy
    plt.plot()

# Hurray!
ZScorePlot(20, -1.5, 1.5)
