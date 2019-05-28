# This code is part of free course - Python For Algo Trading. Enroll at https://algoji.com/pro
# Copyright AlgoJi.com, all rights reserved

# Import Packages
import pyalgotrade.strategy as strategy
import pyalgotrade.technical.bollinger as bollinger
import pyalgotrade.plotter as plotter
import pyalgotrade.barfeed.csvfeed as csvfeed
import pyalgotrade.bar as bar
import pyalgotrade.stratanalyzer.returns as ret
import pyalgotrade.stratanalyzer.sharpe as sharpe
import pyalgotrade.stratanalyzer.drawdown as drawdown
import pyalgotrade.stratanalyzer.trades as trades
import pyalgotrade.broker as broker

# Create Strategy Class
class BBStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, nper, nstdev):
        super(BBStrategy, self).__init__(feed,100000)
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
        elif bars[self.instrument].getPrice() < self.getBBands().getLowerBand()[-1]  and self.position.getShares()>0:
            self.position.exitMarket()
            # Update Strategy Position to None when a Buy-Sell cycle is complete
            self.position = None
        if self.position is None:
            if bars[self.instrument].getPrice() < self.getBBands().getLowerBand()[-1]:
                self.position = self.enterShort(self.instrument, 1, True)
        elif bars[self.instrument].getPrice() > self.getBBands().getUpperBand()[-1]  and self.position.getShares()<0:
            self.position.exitMarket()
            self.position = None
        # onEnterOk: Tells us when order to Enter a position is filled
    def onEnterOk(self, position):
            # getting info for execution price and execution order type
        tradeInfo = position.getEntryOrder().getExecutionInfo()
        self.info("Buy shares at $%.2f" % (tradeInfo.getPrice()))
        # onEnterCanceled: Get notified when order submitted to enter a position was canceled and update position
        def onEnterCanceled(self, position):
            self.position = None

        # onExitOk: Tells us when order to Exit a position is filled
    def onExitOk(self, position):
        tradeInfo = position.getExitOrder().getExecutionInfo()
        self.info("Sell shares at $%.2f" % (tradeInfo.getPrice()))
        # onExitCanceled: Get notified when order submitted to exit a position was canceled.
        # Re-submit order when canceled
        def onExitCanceled(self, position):
            self.position.exitMarket()

# Define Function to Plot MAs
def BbandBacktest(nper, nstdev):
    # Create Instruments object with stock tickers
    instruments = ["BANKNIFTY"]
    # create feed object, add bars to the data feed
    feed = csvfeed.GenericBarFeed(bar.Frequency.DAY)
    feed.addBarsFromCSV(instruments[0], "Data//bnf.csv")
    # create object to run strategy
    bb_strat = BBStrategy(feed, instruments[0], nper, nstdev)
    # add trading costs using TradePercentage()
    bb_strat.getBroker().setCommission(broker.backtesting.TradePercentage(0.01))
    # Attach Strategy Plotter
    plt = plotter.StrategyPlotter(bb_strat,  plotAllInstruments=True, plotBuySell=True, plotPortfolio=False)
    plt.getInstrumentSubplot("BANKNIFTY").addDataSeries("Lower band", bb_strat.getBBands().getLowerBand())
#    plt.getInstrumentSubplot("NIFTY").addDataSeries("Middle band", bb_strat.getBBands().getMiddleBand())
    plt.getInstrumentSubplot("BANKNIFTY").addDataSeries("Upper band", bb_strat.getBBands().getUpperBand())
    retAnalyzer = ret.Returns()
    bb_strat.attachAnalyzer(retAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    bb_strat.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    bb_strat.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    bb_strat.attachAnalyzer(tradesAnalyzer)
    # Run Strategy
    bb_strat.run()
    # Print Strategy Trading Statistics
    print
    print "------------------------------"
    print "1. Portfolio statistics"
    print
    print "Portfolio initial equity: $100000.00"
    print "Portfolio final equity: $%.2f" % bb_strat.getBroker().getEquity()
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
BbandBacktest(20, 2)
