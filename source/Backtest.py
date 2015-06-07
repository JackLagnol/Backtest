from source.Market import *
from source.commonStratgy import *
from time import clock
import csv


class Backtest:
    def __init__(self):
        self.market = Market()
        print(self.__repr__())

    def __repr__(self):
        return "<Backtest>"

    def add_asset_from_csv(self, path_name, sort_type, delimiter=";", asset_name="Unknown asset"):
        the_data_reader = DataReader()
        the_data_reader.open_csv(path_name, delimiter)
        the_data_reader.clean_data(sort_type)

        the_asset = Asset(asset_name, the_data_reader.data)
        self.market.register_asset(the_asset)
        return the_asset

    def simule(self, string_mode=True, plot_mode=True, **kwargs):
        """ Called to simulate a market from the day 0 (or first_day included if given in the parameters)
        to the last day (or the last_day included given in the parameters) """

        beginning_time = clock()  # for time execution measurement

        if "last_day" in kwargs and kwargs["last_day"] is not None:
            last_day = min(self.market.maximumDay, kwargs["last_day"])
            if self.market.maximumDay < kwargs["last_day"]:
                print("-!- PARAM last_day TOO BIG: {} in simule -!-".format(last_day))
        else:
            last_day = self.market.maximumDay

        if "first_day" in kwargs and kwargs["first_day"] is not None:
            first_day = min(last_day, kwargs["first_day"])
        else:
            first_day = 0

        self.market._theDay = first_day
        # print("first day :", first_day, "and last day :", last_day)
        while self.market.play_day(last_day):
            pass
        elapsed_time = clock() - beginning_time
        if string_mode:
            print("")
            print("######                RESULTS OF THE SIMULATION                ######")
            print("Duration : {0} days were simulated, in {1:.0f} ms".format(last_day + 1 - first_day,
                                                                             elapsed_time*1000))
            print("---------------------------------------------------------------------")
            for portfolio in self.market.portfolioList:
                data = portfolio.valueHistory
                result = 100*(portfolio.valueHistory[-1]-portfolio.initialCash)/portfolio.initialCash
                print("{0} result : {1:.2f} %, cash : {2:.2f} $, "
                      "assets : {3}".format(portfolio.name, result, portfolio.cash, portfolio.presentAssetDict))
                print("\t", portfolio.results_description(string_mode=True))
                plt.plot(data, label=portfolio.name)

            # a line is printed if both expertList and portfolioList are not empty
            if len(self.market.portfolioList)*len(self.market.expertList) > 0:
                print("---------------------------------------------------------------------")
            for expert in self.market.expertList:
                print(expert.results_description(string_mode=True))
            print("---------------------------------------------------------------------")
            print("######                   ENDS OF THE RESULTS                   ######")
            if len(self.market.portfolioList) > 0:
                plt.legend(loc=2)
            if plot_mode:
                plt.show(block=True)

    def soft_reset(self):
        """Reset the market for an other new simulation, keep the assets loaded
        WARNING : the max day is still the lowest ! """
        self.market.strategyList.clear()
        self.market.portfolioList.clear()
        self.market.predictionList.clear()
        self.market.expertList.clear()
        self.market._theDay = 0

    def hard_reset(self):
        """Reset the market for an other new simulation, delete the assset and reset max day """
        self.market = Market()


class DataReader:
    def __init__(self):
        self.reader = None
        self.file = None
        self.data = None
        # print(self.__repr__())

    def __repr__(self):
        return "<DataReader>"

    def open_csv(self, path_name, delimiter):
        with open(path_name) as self.file:
            self.reader = csv.reader(self.file, delimiter=delimiter)
            self.data = list(self.reader)

    def clean_data(self, sort_type):
        if sort_type == "propre":
            temp_data = []
            for row in self.data:
                temp_data += [float(row[1])]
            self.data = temp_data

        elif sort_type == "yahoo":  # G : get adjusted close data from csv (date, open, high, low, close, adjclose)
            temp_data = []
            self.data = self.data[1:]  # delete the first line
            # reverse the order of the data (the oldest become the last ones)
            for i in range(len(self.data)):
                temp_data += [self.data[-i-1]]

            self.data = temp_data
            temp_data = []
            for row in self.data:
                temp_data += [float(row[6])]
            self.data = temp_data

        elif sort_type == "ltc":  # G : get adjusted close data from csv (date, open, high, low, close, adjclose)
            temp_data = []
            self.data = self.data[1:]  # delete the first line
            # reverse the order of the data (the oldest become the last ones)
            for i in range(len(self.data)):
                temp_data += [self.data[-i-1]]

            self.data = temp_data
            temp_data = []
            for row in self.data:
                temp_data += [float(row[4])]
            self.data = temp_data




def data_writer(file_name, data, overwrite=True, first_line=None):
    # 'w' : overwrite the file, 'a' add to the file
    if overwrite:
        open_mode = 'w'
    else:
        open_mode = 'a'

    # print(file_name, data)
    with open(file_name, open_mode, newline='') as csvfile:
        writer = csv.writer(csvfile)
        if first_line is not None:
            writer.writerow([first_line])
        writer.writerows(data)
