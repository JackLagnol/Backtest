from source.Backtest import *


class GTestStrat(Strategy):
    def __init__(self, market, name="G Strat Test", cash=10000):
        Strategy.__init__(self, market, name, cash)
        self.cash = cash
        self.daily_returns = []
        self.sharpe_ratio = SharpeRatio()

    def new_day(self):
        asset1 = self.market.assetList[0]
        asset2 = self.market.assetList[1]
        data1 = self.market.get_asset_data(asset1)
        data2 = self.market.get_asset_data(asset2)
        volume1 = self.cash / data1[0]
        volume2 = 0.5 * self.cash / data2[0]
        if self.market.theDay == 0:
            self.market.open(self.portfolio, asset1, volume1, "LONG")
            self.market.open(self.portfolio, asset2, volume2, "SHORT")

    def get_returns(self):
        for i in range(self.market.maximumDay):
            self.daily_returns += [0]
        for i in range(self.market.maximumDay):
            for position in self.portfolio.presentPositionList:
                # # if self.market.time[i] == position.openTrade.day:
                #     position.get_returns()
                #     for j in range(len(position.returns.returns)):
                #         self.daily_returns[i + j] += (position.value_history[0] / self.cash) * position.returns.returns[
                #             j]
                pass

    def get_sharpe(self, risk_free):
        self.get_returns()
        self.sharpe_ratio.getSharpe(self.daily_returns, risk_free)
        return self.sharpe_ratio.sharpe


class GTestStrat1(Strategy):
    def __init__(self, market, name="G Strat Test", cash=10000):
        Strategy.__init__(self, market, name, cash)
        self.cash = cash
        self.daily_returns = []
        self.sharpe_ratio = SharpeRatio()


if __name__ == "__main__":
    # An instance of Backtest is created
    theBacktest = Backtest()

    # Assets are added to the Backtest
    # DENTS = theBacktest.add_asset_from_csv("Data/uniformtest.csv", "DENTS")
    # BTCUSD = theBacktest.add_asset_from_csv("Data/BTCUSD_propre.csv", "BTCUSD")
    # IBM = theBacktest.add_asset_from_csv("Data/ibm_propre.csv", "IBM")

    # GS = theBacktest.add_asset_from_csv("Data/GS_yahoo.csv", "yahoo", ",", "GS")
    IGE = theBacktest.add_asset_from_csv("Data/IGE_yahoo.csv", "yahoo", ",", "IGE")
    SPY = theBacktest.add_asset_from_csv("Data/SPY_yahoo.csv", "yahoo", ",", "SPY")

    # Strategies are created
    # randomStrategy = Strategy(theBacktest.market, "Random Srategy", cash=5000)
    # firstDayStrat = FirstDayBuyEverythingStrategy(theBacktest.market, "BuyTheFirstDay", asset=IBM, cash=5000)
    stratG = GTestStrat(theBacktest.market, "Long only", cash=10000)

    # We plot the assets used
    # theBacktest.market.plot_market()

    theBacktest.simule()

    print("Annualized Sharpe Ratio : ", stratG.get_sharpe(0.05))
    # stratG.get_sharpe(0.04)