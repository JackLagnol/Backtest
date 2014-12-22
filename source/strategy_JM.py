from source.Backtest import *


class FirstDayBuyEverythingStrategy(Strategy):
    def __init__(self, *args, **kwargs):
        self.asset_id = kwargs["asset_id"]
        del kwargs["asset_id"]
        super().__init__(*args, **kwargs)

    def new_day(self):
        if self.market.theDay == 0:
            price = self.market.get_asset_data(self.asset_id)[0]
            self.market.open(self.portfolio_id, self.asset_id, self.market.portfolioDict[self.portfolio_id].cash/price)


class JMTestStrat(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_day(self):
        for i in range(len(self.market.assetDict.keys())):
            data = self.market.get_asset_data(i)
            if len(data) > 2:
                if data[-1] > data[-2] > data[-3]:
                    self.market.open(self.portfolio_id, i, 0.5)
                elif data[-1] < data[-2] < data[-3]:
                    self.market.open(self.portfolio_id, i, -0.5)

if __name__ == "__main__":
    theBacktest = Backtest()
    # randomStrategy = Strategy(theBacktest.market, "Random Srategy")
    # theBacktest.add_strategy(randomStrategy)
    '''FirstDayBuyEverythingStrategy(theBacktest.market, asset_id=0, cash=5000)
    stratWithC = Strategy(theBacktest.market, cash=5000)
    JMstrat = JMTestStrat(theBacktest.market, cash=5000)
    theBacktest.add_strategy(stratWithC)
    theBacktest.add_strategy(JMstrat)'''

    # theBacktest.add_asset_from_csv("BTCUSD_propre.csv", "BTCUSD")
    theBacktest.add_asset_from_csv("uniformtest.csv", "UNIF")
    # theBacktest.add_asset_from_csv("ibm_propre.csv", "IBMUSD")

    absurdExpert = Expert(theBacktest.market)

    # theBacktest.market.plot_market()

    theBacktest.simule()
    ratio = 0
    print(absurdExpert.description_of_prediction())