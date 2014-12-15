from source.Market import *
import csv


class Backtest:
    def __init__(self):
        self.market = Market()
        self.strategyDict = {}
        print("Backtest instantiated")

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
        for strategy_id in self.strategyDict:
            plt.plot(self.market.portfolio_value(self.strategyDict[strategy_id].portfolio))
        print(self.market.portfolio_value(self.market.portfolioDict[0])[:50])
        print(self.market.portfolio_value(self.strategyDict[0].portfolio)[:50])
        plt.show(block=True)


class DataReader:
    def __init__(self):
        self.reader = None
        self.csvFile = None
        self.data = None
        print("DataReader instantiated")

    def open_csv(self, path_name, delimiter=';'):
        with open(path_name) as self.csvFile:
            self.reader = csv.reader(self.csvFile, delimiter=delimiter)
            self.data = list(self.reader)

    def clean_data(self, sort_type=1):
        if sort_type == 1:
            c = []
            for row in self.data:
                c += [float(row[1])]
            self.data = c


if __name__ == "__main__":
    theBacktest = Backtest()
    theStrategy = Strategy(theBacktest.market, "Random Srategy")
    theStrategyBis = Strategy(theBacktest.market, "Random Srategy Bis")
    theBacktest.add_strategy(theStrategy)
    theBacktest.add_strategy(theStrategyBis)

    theBacktest.add_asset_from_csv("source_propre.csv", "BTCUSD")
    theBacktest.market.plot_market()
    theBacktest.simule(10)