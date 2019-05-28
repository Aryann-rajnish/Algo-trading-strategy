# This code is part of free course - Python For Algo Trading. Enroll at https://algoji.com/pro
# Copyright AlgoJi.com, all rights reserved

# Import Packages
import pyalgotrade.strategy as strategy
import pyalgotrade.technical.rsi as rsi
import pyalgotrade.plotter as plotter
import pyalgotrade.barfeed.csvfeed as csvfeed
import pyalgotrade.bar as bar
import pyalgotrade.stratanalyzer.returns as ret
import pyalgotrade.stratanalyzer.sharpe as sharpe
import pyalgotrade.stratanalyzer.drawdown as drawdown
import pyalgotrade.stratanalyzer.trades as trades
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
        elif self.getRSI()[-1] < 40 and self.position.getShares()>0:
            self.position.exitMarket()
            self.position = None
        if self.position is None:
            if self.getRSI()[-1] < 30:
                self.position = self.enterShort(self.instrument, 1, True)
        elif self.getRSI()[-1] > 60 and self.position.getShares() < 0:
                self.position.exitMarket()
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
def RSIBacktest(nper):
    # Create Instruments object with stock tickers
    instruments = ["BANKNIFTY"]
    # create feed object, add bars to the data feed
    feed = csvfeed.GenericBarFeed(bar.Frequency.DAY)
    feed.addBarsFromCSV(instruments[0], "Data//bnf.csv")
    # create object to run strategy
    rsi_strat = RSIStrategy(feed, instruments[0], nper)
    # Attach Strategy Plotter
    plt = plotter.StrategyPlotter(rsi_strat,  plotAllInstruments=True, plotBuySell=True, plotPortfolio=False)
    plt.getOrCreateSubplot("RSI").addDataSeries("RSI", rsi_strat.getRSI())
    plt.getOrCreateSubplot("RSI").addLine("Upper Threshold", 70)
    plt.getOrCreateSubplot("RSI").addLine("Lower Threshold", 40)
#    plt.getOrCreateSubplot("RSI").addLine("Center Line", 40)
    retAnalyzer = ret.Returns()
    rsi_strat.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    rsi_strat.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    rsi_strat.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    rsi_strat.attachAnalyzer(tradesAnalyzer)
    # Run Strategy
    rsi_strat.run()
    # Print Strategy Trading Statistics
    print
    print "------------------------------"
    print "1. Portfolio statistics"
    print
    print "Portfolio initial equity: $100000.00"
    print "Portfolio final equity: $%.2f" % rsi_strat.getBroker().getEquity()
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
RSIBacktest(14)
