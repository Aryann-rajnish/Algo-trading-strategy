# This code is part of free course - Python For Algo Trading. Enroll at https://algoji.com/pro
# Copyright AlgoJi.com, all rights reserved

# Import Packages
import pyalgotrade.strategy as strategy
import pyalgotrade.technical.macd as macd
import pyalgotrade.plotter as plotter
import pyalgotrade.barfeed.csvfeed as csvfeed
import pyalgotrade.bar as bar

# Create Strategy Class
class MACDStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, nfastEMA, nslowEMA, nsignalEMA):
        super(MACDStrategy, self).__init__(feed)
        self.position = None
        self.instrument = instrument
        self.macd = macd.MACD(feed[instrument].getPriceDataSeries(), nfastEMA, nslowEMA, nsignalEMA)

    # Define Technical Indicators Functions
    def getMACD(self):
        return self.macd
    # onBars used to define Buy, Sell rules. Enter Long Order = Buy when MACD>0 AND MACD>SIGNAL, Exit Order = Sell when MACD < 0
    def onBars(self, bars):
        if self.macd[-1] is None:
            return
        if self.position is None:
            if self.macd[-1] > 0 and self.macd[-1] > self.macd.getSignal()[-1]:
                self.position = self.enterLong(self.instrument, 1, True)
        elif self.macd[-1] < 0:
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


# Define Function to Plot MACD
def MACDPlot(nfastEMA, nslowEMA, nsignalEMA):
    # Create Instruments object with stock tickers
    instruments = ["NIFTY"]
    # create feed object, add bars to the data feed
    feed = csvfeed.GenericBarFeed(bar.Frequency.DAY)
    feed.addBarsFromCSV(instruments[0], "Data//NIFTY.csv")
    # create object to run strategy
    macd_plot = MACDStrategy(feed, instruments[0], nfastEMA, nslowEMA, nsignalEMA)
    # Attach Strategy Plotter
    plt = plotter.StrategyPlotter(macd_plot,  plotAllInstruments=True, plotBuySell=True, plotPortfolio=False)
    plt.getOrCreateSubplot("MACD").addDataSeries("MACD", macd_plot.getMACD())
    plt.getOrCreateSubplot("MACD").addDataSeries("Signal", macd_plot.getMACD().getSignal())
    plt.getOrCreateSubplot("MACD").addLine("CenterLine", 0)
    # Run Strategy
    macd_plot.run()
    # Plot Strategy
    plt.plot()

# Hurray!
MACDPlot(12, 26, 9)
