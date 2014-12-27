from source.Backtest import *
from source.Strategy_Analyzers import *



class JMTestStrat(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_day(self):
        for asset in self.market.assetList:
            data = self.market.get_asset_data(asset)
            if len(data) > 2:
                if data[-1] > data[-2] > data[-3]:
                    self.market.long(self.portfolio, asset, 0.5)
                elif data[-1] < data[-2] < data[-3]:
                    self.market.long(self.portfolio, asset, -0.5)


class GTestStrat(Strategy):

    def __init__(self,market,name = "G Strat Test", cash = 10000):
        Strategy.__init__(self,market,name,cash)
        self.cash = cash
        self.daily_returns = []
        self.sharpe_ratio = SharpeRatio()


    def new_day(self):
        asset1 = self.market.assetList[0]
        asset2 = self.market.assetList[1]
        data1 = self.market.get_asset_data(asset1)
        data2 = self.market.get_asset_data(asset2)
        volume1 = self.cash/data1[0]
        volume2 = 0.5*self.cash/data2[0]
        if self.market.theDay == 0:
            self.market.long(self.portfolio, asset1, volume1)
            self.market.short(self.portfolio, asset2, volume2)



    def getReturns(self):
        for i in range(self.market.maximumDay):
            self.daily_returns += [0]
        for i in range(self.market.maximumDay):
            for position in self.portfolio.position.values():
                if self.market.time[i] == position.open_date:
                    position.getReturns()
                    for j in range(len(position.returns.returns)):
                        self.daily_returns[i+j] += (position.value_history[0]/self.cash)*position.returns.returns[j]


    def getSharpe(self, risk_free):
        self.sharpe_ratio.getSharpe(self.daily_returns,risk_free)
        return self.sharpe_ratio.sharpe



if __name__ == "__main__":
    # # An instance of Backtest is created
    # theBacktest = Backtest()
    #
    # # Assets are added to the Backtest
    # DENTS = theBacktest.add_asset_from_csv("uniformtest.csv", "DENTS")
    # BTCUSD = theBacktest.add_asset_from_csv("BTCUSD_propre.csv", "BTCUSD")
    # IBM = theBacktest.add_asset_from_csv("ibm_propre.csv", "IBM")
    #
    # # Strategies are created
    # randomStrategy = Strategy(theBacktest.market, "Random Srategy", cash=5000)
    # JMstrat = JMTestStrat(theBacktest.market, "StupidDetector", cash=5000)
    #
    # firstDayStrat = FirstDayBuyEverythingStrategy(theBacktest.market, "BuyTheFirstDay", asset=IBM, cash=5000)
    #
    # # Experts are created
    # absurdExpert = Expert(theBacktest.market, "AbsurdExpert")
    #
    # # We plot the assets used
    # # theBacktest.market.plot_market()
    #
    # theBacktest.simule()

    test = Backtest()
    #GS = test.add_asset_from_csv("GS.csv", "GS" ,2)
    IGE = test.add_asset_from_csv("IGE.csv", "IGE", 2)
    SPY = test.add_asset_from_csv("SPY.csv", "SPY", 2)
    test.add_time_from_csv("IGE.csv")
    stratG =GTestStrat(test.market,"Long only",cash=10000)
    test.simule()
    stratG.getReturns()
    print("Annualized Sharpe Ratio : ", stratG.getSharpe(0.05))
    #stratG.getSharpe(0.04)