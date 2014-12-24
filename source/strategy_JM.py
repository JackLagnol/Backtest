from source.Backtest import *


class FirstDayBuyEverythingStrategy(Strategy):
    def __init__(self, *args, **kwargs):
        self.asset = kwargs["asset"]
        del kwargs["asset"]
        super().__init__(*args, **kwargs)

    def new_day(self):
        if self.market.theDay == 0:
            price = self.market.get_asset_data(self.asset)[0]
            self.market.open(self.portfolio, self.asset, self.portfolio.cash/price)


class JMTestStrat(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_day(self):
        for asset in self.market.assetList:
            data = self.market.get_asset_data(asset)
            if len(data) > 2:
                if data[-1] > data[-2] > data[-3]:
                    self.market.open(self.portfolio, asset, 0.5)
                elif data[-1] < data[-2] < data[-3]:
                    self.market.open(self.portfolio, asset, -0.5)

if __name__ == "__main__":
    theBacktest = Backtest()

    # theBacktest.add_asset_from_csv("BTCUSD_propre.csv", "BTCUSD")
    theBacktest.add_asset_from_csv("uniformtest.csv", "UNIF")
    theBacktest.add_asset_from_csv("ibm_propre.csv", "IBMUSD")

    # randomStrategy = Strategy(theBacktest.market, "Random Srategy")
    # theBacktest.add_strategy(randomStrategy)
    FirstDayBuyEverythingStrategy(theBacktest.market, asset=theBacktest.market.assetList[0], cash=5000)
    stratWithC = Strategy(theBacktest.market, cash=5000)
    JMstrat = JMTestStrat(theBacktest.market, cash=5000)
    theBacktest.add_strategy(stratWithC)
    theBacktest.add_strategy(JMstrat)


    absurdExpert = Expert(theBacktest.market)

    # theBacktest.market.plot_market()

    theBacktest.simule()
    print(absurdExpert.description_of_prediction())