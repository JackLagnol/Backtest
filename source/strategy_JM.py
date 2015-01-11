from source.Backtest import *


class JMTendanceStrat(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_day(self):
        for the_asset in self.market.assetList:
            data = self.market.get_asset_data(the_asset)
            if len(data) > 2:
                if data[-1] > data[-2] > data[-3]:
                    self.market.open(self.portfolio, the_asset, 50, "LONG")
                elif data[-1] < data[-2] < data[-3]:
                    for position in self.portfolio.openPositionList:
                        self.market.close(position)


class JMTestStrat(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_day(self):
        the_asset = self.market.assetList[0]
        if self.market.theDay == 0:
            self.market.open(self.portfolio, the_asset, 1, "LONG")
        if self.market.theDay == 2:
            self.market.close(self.portfolio.openPositionList[0])
            self.market.open(self.portfolio, the_asset, 3, "LONG")
        if self.market.theDay == 4:
            self.market.close(self.portfolio.openPositionList[0])


if __name__ == "__main__":
    # An instance of Backtest is created
    theBacktest = Backtest()

    # Assets are added to the Backtest
    # DENTS = theBacktest.add_asset_from_csv("Data/uniformtest.csv", "propre", ";", "DENTS")
    # STUP = theBacktest.add_asset_from_csv("Data/stupidtest.csv", "propre", ";", "STUP")
    # BTCUSD = theBacktest.add_asset_from_csv("Data/BTCUSD_propre.csv", "propre", ";", "BTCUSD")
    # IBM = theBacktest.add_asset_from_csv("Data/ibm_propre.csv", "propre", ";", "IBM")

    GS = theBacktest.add_asset_from_csv("Data/GS_yahoo.csv", "yahoo", ",", "GS")
    IGE = theBacktest.add_asset_from_csv("Data/IGE_yahoo.csv", "yahoo", ",", "IGE")
    SPY = theBacktest.add_asset_from_csv("Data/SPY_yahoo.csv", "yahoo", ",", "SPY")

    # Strategies are created
    randomStrategy = Strategy(theBacktest.market, "Random Srategy", cash=5000)
    JMstrat = JMTendanceStrat(theBacktest.market, "StupidDetector", cash=15000)
    firstDayStrat = FirstDayBuyEverythingStrategy(theBacktest.market, "BuyTheFirstDay", asset=GS, cash=15000)
    # JMstratTest = JMTestStrat(theBacktest.market, "TestStrat", cash=5000)

    # Experts are created
    absurdExpert = Expert(theBacktest.market, "AbsurdExpert")

    # We plot the assets used
    # theBacktest.market.plot_market()

    theBacktest.simule()

    # print("open:", JMstratTest.portfolio.openPositionList)
    # print(JMstratTest.portfolio.valueHistory)
    # print(JMstratTest.portfolio.closePositionList[0].valueHistory)
    # print("close", JMstratTest.portfolio.closePositionList)

    # # Useful syntax
    # l = [0, 1, 2, -3]
    # print(l)
    # print([-rt for rt in l])
    # print(l*(-1)) # do not work
