# This code is part of free course - Python For Algo Trading. Enroll at https://algoji.com/pro
# Copyright AlgoJi.com, all rights reserved

# Import Packages
import pyalgotrade.strategy as strategy
import pyalgotrade.technical.bollinger as bollinger
import pyalgotrade.plotter as plotter
import pyalgotrade.barfeed.csvfeed as csvfeed
import pyalgotrade.bar as bar
# Create Strategy Class
class BBStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, nper, nstdev):
        super(BBStrategy, self).__init__(feed)
        self.position = None
        self.instrument = instrument
        self.bbands = bollinger.BollingerBands(feed[instrument].getPriceDataSeries(), nper, nstdev)

    # Define Technical Indicators Functions
    def getBBands(self):
        return self.bbands
    # Define mandatory onBars Functions
    def onBars(self, bars):
        if self.getBBands().getUpperBand()[-1] is None:
            return
        if self.position is None:
            if bars[self.instrument].getPrice() > self.getBBands().getUpperBand()[-1]:
                self.position = self.enterLong(self.instrument, 1, True)
        elif bars[self.instrument].getPrice() < self.getBBands().getLowerBand()[-1]:
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
def BbandPlot(nper, nstdev):
    # Create Instruments object with stock tickers
    instruments = ["NIFTY"]
    # create feed object, add bars to the data feed
    feed = csvfeed.GenericBarFeed(bar.Frequency.DAY)
    feed.addBarsFromCSV(instruments[0], "Data//NIFTY.csv")
    # create object to run strategy
    bb_plot = BBStrategy(feed, instruments[0], nper, nstdev)
    # Attach Strategy Plotter
    plt = plotter.StrategyPlotter(bb_plot,  plotAllInstruments=True, plotBuySell=True, plotPortfolio=False)
    plt.getInstrumentSubplot("NIFTY").addDataSeries("Lower band", bb_plot.getBBands().getLowerBand())
#    plt.getInstrumentSubplot("NIFTY").addDataSeries("Middle band", bb_plot.getBBands().getMiddleBand())
    plt.getInstrumentSubplot("NIFTY").addDataSeries("Upper band", bb_plot.getBBands().getUpperBand())
    # Run Strategy
    bb_plot.run()
    # Plot Strategy
    plt.plot()

# Hurray!
BbandPlot(20, 2)
