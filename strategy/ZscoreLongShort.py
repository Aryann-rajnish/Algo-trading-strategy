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
import pyalgotrade.stratanalyzer.returns as ret
import pyalgotrade.stratanalyzer.sharpe as sharpe
import pyalgotrade.stratanalyzer.drawdown as drawdown
import pyalgotrade.stratanalyzer.trades as trades

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
            if  bars[self.instrument].getPrice() > self.sma[-1] and self.zscore[-1] < self.lowerThreshold:
                self.position = self.enterLong(self.instrument, 1, True)
        elif self.zscore[-1] > self.upperThreshold and self.position.getShares()>0:
            self.position.exitMarket()
            # Update Strategy Position to None when a Buy-Sell cycle is complete
            self.position = None
        if self.position is None:
            if  bars[self.instrument].getPrice() < self.sma[-1] and self.zscore[-1] > self.upperThreshold:
                self.position = self.enterShort(self.instrument, 1, True)
        elif self.zscore[-1] < self.lowerThreshold and self.position.getShares()<0:
            self.position.exitMarket()
            # Update Strategy Position to None when a Buy-Sell cycle is complete
            self.position = None
    def onEnterOk(self, position):
        # getting info for execution price and execution order type
        tradeInfo = position.getEntryOrder().getExecutionInfo()
        self.info("Buy shares at $%.2f" % (tradeInfo.getPrice()))
    # onExitOk: Tells us when order to Exit a position is filled
    def onExitOk(self, position):
        tradeInfo = position.getExitOrder().getExecutionInfo()
        self.info("Sell shares at $%.2f" % (tradeInfo.getPrice()))

# Define Function to Plot MAs
def ZScoreBacktest(nper, lowerThreshold, upperThreshold):
    # Create Instruments object with stock tickers
    instruments = ["BANKNIFTY"]
    # create feed object, add bars to the data feed
    feed = csvfeed.GenericBarFeed(bar.Frequency.DAY)
    feed.addBarsFromCSV(instruments[0], "Data//bnf.csv")
    # create object to run strategy
    zscore_strategy = ZScoreStrategy(feed, instruments[0], nper, lowerThreshold, upperThreshold)
    # Attach Strategy Plotter
    plt = plotter.StrategyPlotter(zscore_strategy,  plotAllInstruments=True, plotBuySell=True, plotPortfolio=False)
    plt.getOrCreateSubplot("ZScore").addDataSeries("ZScore", zscore_strategy.getZScore())
    retAnalyzer = ret.Returns()
    zscore_strategy.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    zscore_strategy.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    zscore_strategy.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    zscore_strategy.attachAnalyzer(tradesAnalyzer)
    # Run Strategy
    zscore_strategy.run()
    print
    print "------------------------------"
    print "1. Portfolio statistics"
    print
    print "Portfolio initial equity: $100000.00"
    print "Portfolio final equity: $%.2f" % zscore_strategy.getBroker().getEquity()
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
ZScoreBacktest(20, -1.5, 1.5)
