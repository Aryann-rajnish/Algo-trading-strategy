# This code is part of free course - Python For Algo Trading. Enroll at https://algoji.com/pro
# Copyright AlgoJi.com, all rights reserved

# Import Packages
import pyalgotrade.strategy as strategy
import pyalgotrade.technical.ma as ma
import pyalgotrade.plotter as plotter
import pyalgotrade.barfeed.csvfeed as csvfeed
import pyalgotrade.bar as bar
import pyalgotrade.stratanalyzer.returns as ret
import pyalgotrade.stratanalyzer.sharpe as sharpe
import pyalgotrade.stratanalyzer.drawdown as drawdown
import pyalgotrade.stratanalyzer.trades as trades

# Create Strategy Class
class MAStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, nfast, nslow):
        super(MAStrategy, self).__init__(feed, 100000)
        self.position = None
        self.instrument = instrument
        self.setUseAdjustedValues(True)
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
def MACrossTrade(nfast, nslow):
    # Create Instruments object with stock tickers
    instruments = ["NIFTY"]
    # create feed object, add bars to the data feed
    feed = csvfeed.GenericBarFeed(bar.Frequency.DAY)
    feed.addBarsFromCSV(instruments[0], "Data//NIFTY.csv")
    # create object to run strategy
    ma_trade = MAStrategy(feed, instruments[0], nfast, nslow)
    # Attach Strategy Plotter
    plt = plotter.StrategyPlotter(ma_trade,  plotAllInstruments=True, plotBuySell=True, plotPortfolio=True)
    plt.getInstrumentSubplot("NIFTY").addDataSeries("Fast SMA", ma_trade.getfastSMA())
    plt.getInstrumentSubplot("NIFTY").addDataSeries("Slow SMA", ma_trade.getslowSMA())
    # analyse results
    # Returns class calculates time weighted returns for the whole portfolio
    retAnalyzer = ret.Returns()
    ma_trade.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    ma_trade.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    ma_trade.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    ma_trade.attachAnalyzer(tradesAnalyzer)
    # Run Strategy
    ma_trade.run()
    # print statistics
    # Print Strategy Trading Statistics
    print
    print "------------------------------"
    print "1. Portfolio statistics"
    print
    print "Portfolio initial equity: $100000.00"
    print "Portfolio final equity: $%.2f" % ma_trade.getBroker().getEquity()
    print "Portfolio net trading p&l: $%.2f" % tradesAnalyzer.getAll().sum()
    print "Portfolio maximum drawdown: %.2f %%" % (drawDownAnalyzer.getMaxDrawDown() * 100)
    print "Portfolio annualized return: %.2f %%" % (retAnalyzer.getCumulativeReturns()[-1] * 100)
    print "Portfolio annualized Sharpe ratio (Rf = 0%%): %.2f" % (sharpeRatioAnalyzer.getSharpeRatio(0.0))
    print "------------------------------"
    print "2. Total trades statistics"
    print "Total trades: %d" % (tradesAnalyzer.getCount())
    if tradesAnalyzer.getCount() > 0:
        tradesProfits = tradesAnalyzer.getAll()
        print "Total trades average p&l: $%2.f" % (tradesProfits.mean())
        print "Largest Winning Trade: $%2.f" % (tradesProfits.max())
        print "Largest Losing Trade: $%2.f" % (tradesProfits.min())
        tradesReturns = tradesAnalyzer.getAllReturns()
        print "Average return: %2.f %%" % (tradesReturns.mean() * 100)
        print "Largest Winning Trade Return: %2.f %%" % (tradesReturns.max() * 100)
        print "Largest Losing Trade Return: %2.f %%" % (tradesReturns.min() * 100)
    print "------------------------------"

    # Plot Strategy
    plt.plot()

# Hurray!
MACrossTrade(30, 40)
