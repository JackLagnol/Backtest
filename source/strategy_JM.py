from source.Backtest import *


class JMTendanceStrat(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_day(self):
        for the_asset in self.market.assetList:
            data = self.market.get_asset_data(the_asset)
            if len(data) > 2:
                if data[-1] > data[-2] > data[-3]:
                    self.market.open(self.portfolio, the_asset, 5, "LONG")
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


class JMTendanceExpert(Expert):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_day(self):
        """ Called each day by the market to ask the expert to make its predictions """
        pred = ["UP", "DOWN"]
        for the_asset in self.market.assetList:
            data = self.market.get_asset_data(the_asset)
            if len(data) > 2:
                if data[-1] > data[-2] > data[-3]:
                    Prediction(the_asset, pred[1], self.market.theDay + 1,
                               self, self.market.theDay, self.market)
                elif data[-1] < data[-2] < data[-3]:
                    Prediction(the_asset, pred[0], self.market.theDay + 1,
                               self, self.market.theDay, self.market)


class JMMobileExpert(Expert):
    def __init__(self, *args, **kwargs):

        temp_kwargs = kwargs.copy()
        del kwargs["longMedian"]
        del kwargs["shortMedian"]
        if "asset" in kwargs:
            del kwargs["asset"]
        super().__init__(*args, **kwargs)

        self.longMedian = temp_kwargs["longMedian"]
        self.shortMedian = temp_kwargs["shortMedian"]
        self.pastShortSum = []
        self.pastLongSum = []
        self.initialised = False

        if "asset" in temp_kwargs:
            self.asset = temp_kwargs["asset"]
        else:
            self.asset = self.market.assetList[0]

    def new_day(self):
        """ Called each day by the market to ask the expert to make its predictions """
        pred = ["UP", "DOWN"]
        if self.initialised:
            data = self.market.get_asset_data(self.asset)
            short_sum = 0
            long_sum = 0
            for i in range(self.longMedian):
                long_sum += data[-i-1]  # -1 because i start at 0
            long_sum /= self.longMedian
            for i in range(self.shortMedian):
                short_sum += data[-i-1]  # -1 because i start at 0
            short_sum /= self.shortMedian

            if short_sum > long_sum and self.pastLongSum[-1] > self.pastShortSum[-1]:
                Prediction(self.asset, pred[0], self.market.theDay + self.shortMedian,
                           self, self.market.theDay, self.market)
            elif short_sum < long_sum and self.pastLongSum[-1] < self.pastShortSum[-1]:
                Prediction(self.asset, pred[1], self.market.theDay + self.shortMedian,
                           self, self.market.theDay, self.market)

            self.pastLongSum.append(long_sum)
            self.pastShortSum.append(short_sum)

        # if it is the first time self.market.theDay > self.longMedian, the median value are initialised
        elif self.market.theDay >= self.longMedian - 1:
            self.initialised = True
            data = self.market.get_asset_data(self.asset)
            print("data sent", data, self.market.theDay)
            short_sum = 0
            long_sum = 0
            for i in range(self.longMedian):
                # print(-i-1)
                long_sum += data[-i-1]  # -1 because i start at 0
            long_sum /= self.longMedian
            for i in range(self.shortMedian):
                short_sum += data[-i-1]  # -1 because i start at 0
            short_sum /= self.shortMedian
            self.pastLongSum.append(long_sum)
            self.pastShortSum.append(short_sum)

    def plot_medians(self):
        size = min(len(self.pastShortSum) + self.longMedian - 1, len(self.asset.data) - 1)
        x = list(range(size))
        translation_list = [None] * (self.longMedian - 1)
        translated_short = translation_list + self.pastShortSum
        translated_long = translation_list + self.pastLongSum

        plt.plot(x, translated_short, label="Short Median")
        plt.plot(x, translated_long, label="Long Median")
        plt.plot(x, self.asset.data[:size], label=self.asset.name)
        plt.legend(loc=2)
        plt.show(block=True)


if __name__ == "__main__":
    # An instance of Backtest is created
    theBacktest = Backtest()

    # Assets are added to the Backtest
    # DENTS = theBacktest.add_asset_from_csv("Data/uniformtest.csv", "propre", ";", "DENTS")
    # STUP = theBacktest.add_asset_from_csv("Data/stupidtest.csv", "propre", ";", "STUP")
    # BTCUSD = theBacktest.add_asset_from_csv("Data/BTCUSD_propre.csv", "propre", ";", "BTCUSD")
    # IBM = theBacktest.add_asset_from_csv("Data/ibm_propre.csv", "propre", ";", "IBM")

    # GS = theBacktest.add_asset_from_csv("Data/GS_yahoo.csv", "yahoo", ",", "GS")
    IGE = theBacktest.add_asset_from_csv("Data/IGE_yahoo.csv", "yahoo", ",", "IGE")
    # SPY = theBacktest.add_asset_from_csv("Data/SPY_yahoo.csv", "yahoo", ",", "SPY")

    # Strategies are created
    # randomStrategy = Strategy(theBacktest.market, "Random Srategy", cash=5000)
    # JMstrat = JMTendanceStrat(theBacktest.market, "StupidDetector", cash=15000)
    # firstDayStrat = FirstDayBuyEverythingStrategy(theBacktest.market, "BuyTheFirstDay", asset=IGE, cash=15000)
    # JMstratTest = JMTestStrat(theBacktest.market, "TestStrat", cash=5000)

    # Experts are created
    # absurdExpert = Expert(theBacktest.market, "AbsurdExpert")
    # TendanceExpert = JMTendanceExpert(theBacktest.market, "TendanceExpert")
    MobileExpert = JMMobileExpert(theBacktest.market, "MobileExpert", longMedian=20, shortMedian=10)

    # We plot the assets used
    # theBacktest.market.plot_market()

    theBacktest.simule(200)

    MobileExpert.plot_medians()

    # print("open:", JMstratTest.portfolio.openPositionList)
    # print(JMstratTest.portfolio.valueHistory)
    # print(JMstratTest.portfolio.closePositionList[0].valueHistory)
    # print("close", JMstratTest.portfolio.closePositionList)

    # # Useful syntax
    # l = [0, 1, 2, -3]
    # print(l)
    # print([-rt for rt in l])
    # print(l*(-1)) # do not work
