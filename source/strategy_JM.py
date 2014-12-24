from source.Backtest import *


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
    # An instance of Backtest is created
    theBacktest = Backtest()

    # Assets are added to the Backtest
    DENTS = theBacktest.add_asset_from_csv("uniformtest.csv", "DENTS")
    BTCUSD = theBacktest.add_asset_from_csv("BTCUSD_propre.csv", "BTCUSD")
    IBM = theBacktest.add_asset_from_csv("ibm_propre.csv", "IBM")

    # Strategies are created
    randomStrategy = Strategy(theBacktest.market, "Random Srategy", cash=5000)
    JMstrat = JMTestStrat(theBacktest.market, "StupidDetector", cash=5000)
    firstDayStrat = FirstDayBuyEverythingStrategy(theBacktest.market, "BuyTheFirstDay", asset=IBM, cash=5000)

    # Experts are created
    absurdExpert = Expert(theBacktest.market, "AbsurdExpert")

    # We plot the assets used
    # theBacktest.market.plot_market()

    theBacktest.simule()