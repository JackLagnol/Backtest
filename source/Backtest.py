from source.Market import *
from source.commonStratgy import  *
import csv


class Backtest:
    def __init__(self):
        self.market = Market()
        print(self.__repr__())

    def __repr__(self):
        return "<Backtest>"

    def add_asset_from_csv(self, path_name, asset_name="Unknown asset",sort_type = 1):
        the_data_reader = DataReader()
        the_data_reader.open_csv(path_name)
        the_data_reader.clean_data(sort_type)

        asset = Asset(asset_name, the_data_reader.data)
        self.market.add_asset(asset)
        return asset

    def add_time_from_csv(self, path_name, sort_type = 0): #G ; get actual time
        data_reader = DataReader()
        data_reader.open_csv(path_name)
        data_reader.clean_data(sort_type)

        self.market.add_time(data_reader.data)

    def simule(self, max_day=-1):
        while self.market.play_day(max_day):
            if self.market.theDay == self.market.maximumDay:
                for portfolio in self.market.portfolioList: #G
                    for position in portfolio.position.values():
                        self.market.close(portfolio,position)


        print("")
        print("######        RESULTS OF THE SIMULATION        ######")
        print("Duration : {0} days were simulated".format(self.market.theDay))
        print("-----------------------------------------------------")
        for portfolio in self.market.portfolioList:
            data = portfolio.valueHistory
            result = 100*(portfolio.valueHistory[-1]-portfolio.initialCash)/portfolio.initialCash
            print("{0} result : {1:.2f} %, cash : {2:.2f} $, assets : {3}".format(portfolio.name, result, portfolio.cash, portfolio.presentAssetDict))
            plt.plot(portfolio.valueHistory)
            print(portfolio.position)

        print("-----------------------------------------------------")
        # for expert in self.market.expertList:
        #     print("Prediction of {0} : number of prediction {1}, UP : {2}, DOWN : {3}, Good : {4}, Ratio : {5:.3f}".format(expert.name, *expert.description_of_prediction()))
        # print("-----------------------------------------------------")
        print("######           END OF THE RESULTS           ######")
        #plt.show(block=True)


class DataReader:
    def __init__(self):
        self.reader = None
        self.file = None
        self.data = None #used to store prices
        print(self.__repr__())

    def __repr__(self):
        return "<DataReader>"

    def open_csv(self, path_name, delimiter=','):
        with open(path_name) as self.file:
            self.reader = csv.reader(self.file, delimiter=delimiter)
            self.data = list(self.reader)

    def clean_data(self, sort_type=1):
        if sort_type == 1:
            c = []
            for row in self.data:
                c += [float(row[1])]
            self.data = c

        elif sort_type == 2: #G : get adj close data from csv (date, open, high, low, close, adjclose) (yahoo finance data)
            c = []
            self.data = self.data[1:]
            for i in range(len(self.data)):
                c += [self.data[-i-1]]
            self.data = c
            c = []
            for row in self.data:
                c += [float(row[6])]
            self.data = c

        elif sort_type == 0: #time for yahoo finance
            c = []
            self.data = self.data[1:]
            for i in range(len(self.data)):
                c += [self.data[-i-1]]
            self.data = c
            c = []
            for row in self.data:
                c += [row[0]]
            self.data = c


