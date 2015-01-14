import statistics
import math
from source.Backtest import *


class FirstDayBuyEverythingStrategy(Strategy):
    """ Strategy that buys all that it can the first day on the asset given
    in the parameter 'asset' in the generator, and then keep everything
    """

    def __init__(self, *args, **kwargs):
        self.asset = kwargs["asset"]
        del kwargs["asset"]
        self.alreadyBought = False
        super().__init__(*args, **kwargs)

    def new_day(self):
        if not self.alreadyBought:
            self.alreadyBought = True
            price = self.market.get_asset_data(self.asset)[self.market.theDay]
            self.market.open(self.portfolio, self.asset, self.portfolio.cash / price, "LONG")


class SharpeRatio:
    """ Compute annualized Sharpe Ratio based on daily returns (252 trading days / year)"""

    def __init__(self):
        self.sharpe = 0

    def getSharpe(self, returns, risk_free):
        adj_returns = []
        for i in range(len(returns)):
            adj_returns += [returns[i] - (risk_free / 252)]
        self.sharpe = math.sqrt(252) * statistics.mean(adj_returns) / statistics.stdev(adj_returns)


if __name__ == "__main__":
    # An instance of Backtest is created
    theBacktest = Backtest()

    # Assets are added to the Backtest
    # DENTS = theBacktest.add_asset_from_csv("Data/uniformtest.csv", "propre", ";", "DENTS")
    # BTCUSD = theBacktest.add_asset_from_csv("Data/BTCUSD_propre.csv", "propre", ";", "BTCUSD")
    # IBM = theBacktest.add_asset_from_csv("Data/ibm_propre.csv", "propre", ";", "IBM")

    # GS = theBacktest.add_asset_from_csv("Data/GS_yahoo.csv", "yahoo", ",", "GS")
    IGE = theBacktest.add_asset_from_csv("Data/IGE_yahoo.csv", "yahoo", ",", "IGE")
    # SPY = theBacktest.add_asset_from_csv("Data/SPY_yahoo.csv", "yahoo", ",", "SPY")

    # Strategies are created
    randomStrategy = Strategy(theBacktest.market, "Random Srategy", cash=5000)
    firstDayStrat = FirstDayBuyEverythingStrategy(theBacktest.market, "BuyTheFirstDay", asset=GS, cash=5000)

    # Experts are created
    absurdExpert = Expert(theBacktest.market, "AbsurdExpert")

    # We plot the assets used
    # theBacktest.market.plot_market()

    theBacktest.simule()

    # # Useful syntax: [-rt for rt in l]
    # l = [0, 1, 2, -3]
    # print(l)
    # print([-rt for rt in l])
    # print(l*(-1)) # do not work