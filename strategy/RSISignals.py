# This code is part of free course - Python For Algo Trading. Enroll at https://algoji.com/pro
# Copyright AlgoJi.com, all rights reserved

# Import Packages
import pyalgotrade.strategy as strategy
import pyalgotrade.technical.rsi as rsi
import pyalgotrade.plotter as plotter
import pyalgotrade.barfeed.csvfeed as csvfeed
import pyalgotrade.bar as bar
# Create Strategy Class
class RSIStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, nper):
        super(RSIStrategy, self).__init__(feed)
        self.position = None
        self.instrument = instrument
        self.rsi = rsi.RSI(feed[instrument].getPriceDataSeries(), nper)

    # Define Technical Indicators Functions
    def getRSI(self):
        return self.rsi
    # Define mandatory onBars Functions
    def onBars(self, bars):
        if self.getRSI()[-1] is None:
            return
        if self.position is None:
            if self.getRSI()[-1] > 70:
                self.position = self.enterLong(self.instrument, 1, True)
        elif self.getRSI()[-1] < 40:
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
def RSIPlot(nper):
    # Create Instruments object with stock tickers
    instruments = ["NIFTY"]
    # create feed object, add bars to the data feed
    feed = csvfeed.GenericBarFeed(bar.Frequency.DAY)
    feed.addBarsFromCSV(instruments[0], "Data//NIFTY.csv")
    # create object to run strategy
    rsi_plot = RSIStrategy(feed, instruments[0], nper)
    # Attach Strategy Plotter
    plt = plotter.StrategyPlotter(rsi_plot,  plotAllInstruments=True, plotBuySell=True, plotPortfolio=False)
    plt.getOrCreateSubplot("RSI").addDataSeries("RSI", rsi_plot.getRSI())
    plt.getOrCreateSubplot("RSI").addLine("Upper Threshold", 70)
    plt.getOrCreateSubplot("RSI").addLine("Lower Threshold", 40)
#    plt.getOrCreateSubplot("RSI").addLine("Center Line", 40)
    # Run Strategy
    rsi_plot.run()
    # Plot Strategy
    plt.plot()

# Hurray!
RSIPlot(14)
