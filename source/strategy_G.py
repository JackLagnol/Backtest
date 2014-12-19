from source.Backtest import *


class GTestStrat(Strategy):
    def __init__(self, market, name="GTest Strategy"):
        super().__init__(market, name)

    def new_day(self):
        for i in range(len(self.market.assetDict.keys())):
            data = self.market.get_asset_data(i)
            if len(data) > 2:
                if data[-1] > data[-2] > data[-3]:
                    self.market.buy(self.portfolio_id, i, 0.1)
                elif data[-1] < data[-2] < data[-3]:
                    self.market.buy(self.portfolio_id, i, -0.1)

if __name__ == "__main__":
    theBacktest = Backtest()
    randomStrategy = Strategy(theBacktest.market, "Random Srategy")
    theBacktest.add_strategy(randomStrategy)

    Gstrat = GTestStrat(theBacktest.market)
    theBacktest.add_strategy(Gstrat)

    theBacktest.add_asset_from_csv("BTCUSD_propre.csv", "BTCUSD")
    # theBacktest.add_asset_from_csv("ibm_propre.csv", "IBMUSD")

    theBacktest.market.plot_market()

    theBacktest.simule()