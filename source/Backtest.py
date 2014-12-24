from source.Market import *
import csv


class Backtest:
    def __init__(self):
        self.market = Market()
        self.strategyDict = {}
        print(self.__repr__())

    def __repr__(self):
        return "<Backtest>"

    def add_strategy(self, strategy: Strategy):
        self.strategyDict[strategy.id] = strategy

    def add_asset_from_csv(self, path_name, asset_name="Unknown asset"):
        the_data_reader = DataReader()
        the_data_reader.open_csv(path_name)
        the_data_reader.clean_data()

        the_asset = Asset(asset_name, the_data_reader.data)
        self.market.add_asset(the_asset)

    def simule(self, max_day=-1):
        while self.market.play_day(max_day):
            pass
        for portfolio in self.market.portfolioList:
            data = portfolio.valueHistory
            print(data)
            print(portfolio.orderHistoryList)
            plt.plot(data)
        plt.show(block=True)


class DataReader:
    def __init__(self):
        self.reader = None
        self.file = None
        self.data = None
        print(self.__repr__())

    def __repr__(self):
        return "<DataReader>"

    def open_csv(self, path_name, delimiter=';'):
        with open(path_name) as self.file:
            self.reader = csv.reader(self.file, delimiter=delimiter)
            self.data = list(self.reader)

    def clean_data(self, sort_type=1):
        if sort_type == 1:
            c = []
            for row in self.data:
                c += [float(row[1])]
            self.data = c


if __name__ == "__main__":
    theBacktest = Backtest()
    randomStrategy = Strategy(theBacktest.market, "Random Srategy")
    theBacktest.add_strategy(randomStrategy)

    theStrategyBis = Strategy(theBacktest.market, "Random Srategy Bis")
    theBacktest.add_strategy(theStrategyBis)

    theBacktest.add_asset_from_csv("BTCUSD_propre.csv", "BTCUSD")
    theBacktest.add_asset_from_csv("ibm_propre.csv", "IBMUSD")

    theBacktest.market.plot_market()

    theBacktest.simule(4)