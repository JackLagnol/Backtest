from source.Backtest import *


class FirstDayBuyEverythingStrategy(Strategy):

    """Strategy that buys all that it can the first day on the asset
    given in the parameter 'asset' in the generator, and then keep everything
    example of use:"""

    def __init__(self, *args, **kwargs):
        self.asset = kwargs["asset"]
        del kwargs["asset"]
        super().__init__(*args, **kwargs)

    def new_day(self):
        if self.market.theDay == 0:
            price = self.market.get_asset_data(self.asset)[0]
            self.market.open(self.portfolio, self.asset, self.portfolio.cash/price)


if __name__ == "__main__":
    # An instance of Backtest is created
    theBacktest = Backtest()

    # Assets are added to the Backtest
    DENTS = theBacktest.add_asset_from_csv("uniformtest.csv", "DENTS")
    BTCUSD = theBacktest.add_asset_from_csv("BTCUSD_propre.csv", "BTCUSD")
    IBM = theBacktest.add_asset_from_csv("ibm_propre.csv", "IBM")

    # Strategies are created
    randomStrategy = Strategy(theBacktest.market, "Random Srategy", cash=5000)
    firstDayStrat = FirstDayBuyEverythingStrategy(theBacktest.market, "BuyTheFirstDay", asset=IBM, cash=5000)

    # Experts are created
    absurdExpert = Expert(theBacktest.market, "AbsurdExpert")

    # We plot the assets used
    # theBacktest.market.plot_market()

    theBacktest.simule()