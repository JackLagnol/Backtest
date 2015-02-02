from source.Backtest import *
from mpl_toolkits.mplot3d import Axes3D
from scipy import interpolate
import numpy as np
from matplotlib.widgets import Slider, RadioButtons

class GTestStrat2(Strategy):

    def __init__(self, market, short_frame, long_frame, length_data, start_date, name="G Strat Test", cash=10000):
        Strategy.__init__(self, market, name, cash)
        self.daily_returns = []
        self.short_frame = short_frame
        self.long_frame = long_frame
        self.length_data = length_data
        self.start_date = start_date

    def new_day(self):
        asset = self.market.assetList[0]
        data = self.market.get_asset_data(asset)

        if self.market.theDay >= self.start_date + self.long_frame and self.market.theDay <= self.start_date+self.length_data:
            short = moving_average(data, self.short_frame)
            long = moving_average(data, self.long_frame)
            if short > long and self.portfolio.cash > 0:
                volume = self.portfolio.cash / data[self.market.theDay] - 1
                self.market.open(self.portfolio, asset, volume, "LONG")
            elif short < long:
                for position in self.portfolio.openPositionList:
                    if not position.closed:
                        self.market.close(position)


    def get_returns(self):
        for i in range(self.market.maximumDay):
            self.daily_returns += [0]
        for i in range(self.market.maximumDay):
            for position in self.portfolio.openPositionList:
                if i == position.openTrade.day:
                    current_position_return = position.get_returns()
                    for j in range(len(current_position_return)):
                        self.daily_returns[i + j] += (position.valueHistory[0] / self.portfolio.initialCash) * current_position_return[j]
        self.daily_returns = self.daily_returns[self.start_date:self.start_date+self.length_data+1]


    def get_sharpe(self, risk_free):
        return compute_sharpe(self.daily_returns, risk_free)


if __name__ == "__main__":
    # An instance of Backtest is created
    theBacktest = Backtest()

    BTC = theBacktest.add_asset_from_csv("Data/BTC_daily.csv", "propre", ",", "BTC")
    LTC = theBacktest.add_asset_from_csv("Data/LTC_daily.csv", "ltc", ",", "LTC")

    # Strategies are created
    # randomStrategy = Strategy(theBacktest.market, "Random Srategy", cash=5000)

    sharpe_max = -1000
    long_opt = []
    short_opt = []

    # theBacktest.market.plot_market()
    l = 0
    beginning_time = clock()  # for time execution measurement
    for k in range(100, 600, 10):
        sharpe_max = -1000
        long_opt += [0]
        short_opt += [0]

        for i in range(5, 20):
            print(k, i, (clock() - beginning_time), "s")
            for j in range(20, 30):
                stratG = GTestStrat2(theBacktest.market, i, j, 300, k, "TEST")
                theBacktest.simule(first_day=0, string_mode=False)
                stratG.get_returns()
                sharpe = stratG.get_sharpe(0.04)
                if sharpe > sharpe_max:
                    sharpe_max = sharpe
                    short_opt[l] = i
                    long_opt[l] = j
        l += 1

    plt.plot(long_opt)
    plt.plot(short_opt)
    plt.ylim([0,50])

    plt.show(block=True)

    # We plot the assets used
    # theBacktest.market.plot_market()



    # stratG.get_returns()
    # print("Annualized Sharpe Ratio : ", stratG.get_sharpe(0.04))
    # stratG.get_sharpe(0.04)
    #
    # theBacktest = Backtest()
    # BTC = theBacktest.add_asset_from_csv("Data/BTC_daily.csv", "propre", ",", "BTC")
    # LTC = theBacktest.add_asset_from_csv("Data/LTC_daily.csv", "ltc", ",", "LTC")
    # stratG = GTestStrat3(theBacktest.market, 300,500, "TEST", cash = 0)
    #
    # theBacktest.simule()