import random
import matplotlib.pyplot as plt
from source.Strategy_Analyzers import *

class Position:
    #long = True if long position
    def __init__(self, asset, volume, day, long):
        self.asset = asset
        self.volume = volume
        self.open_date = day
        self.close_date = None
        self.long = long
        self.closed = False
        self.value = 0
        self.value_history = []
        self.returns = DailyReturns()

    def __repr__(self):
        if self.long and self.closed:
            return "<Long position of asset {0} and volume {1}, opened on {2}, closed on {3} >".format(self.asset, self.volume, self.open_date, self.close_date)
        elif (not self.long) and self.closed:
            return "<Short position of asset {0} and volume {1}, opened on {2}, closed on {3} >".format(self.asset, self.volume, self.open_date, self.close_date)
        elif self.long and (not self.closed):
            return "<Long position of asset {0} and volume {1}, opened on {2}>".format(self.asset, self.volume, self.open_date)
        if (not self.long) and (not self.closed):
            return "<Short position of asset {0} and volume {1}, opened on {2}>".format(self.asset, self.volume, self.open_date)

    def getReturns(self):
        self.returns.getReturns(self.value_history)
        if not self.long:
            [-rt for rt in self.returns.returns]



class Trade:
    lastId = 0

    def __init__(self, asset, volume, day):
        self.asset = asset
        self.volume = volume
        self.day = day
        self.id = Trade.lastId
        Trade.lastId += 1
        # print(self.__repr__())

    def __repr__(self):
        return "<Trade of asset : {0}  and volume : {1}, the theDay {2}>".format(self.asset.name, self.volume, self.day)


class Prediction:
    lastId = 0

    def __init__(self, asset, evolution, final_term, expert_who_made_it, day_it_was_made):
        self.asset = asset
        self.evolution = evolution  # can be UP, DOWN, or an evolution (ex: -250 pour le cac 40)
        self.expert = expert_who_made_it
        self.day = day_it_was_made
        self.final_term = final_term
        self.isTrue = False

        self.id = Prediction.lastId
        Prediction.lastId += 1
        # print(self.__repr__())

    def __repr__(self):
        return "<Prediction of asset : {0}, the theDay {1}, evolution : {2}>".format(self.asset.name,
                                                                                     self.day, self.evolution)


class Asset:

    def __init__(self, name="Unknown asset", data=[]):
        self.name = name
        self.data = data
        self.length = len(data)
        print(self.__repr__())

    def __repr__(self):
        return "<{0}>".format(self.name)


class Portfolio:

    def __init__(self, name, cash):
        self.name = name
        self.position = {}
        self.todayInQueueTrade = []
        self.valueHistory = []
        self.orderHistoryList = []  # de la forme [ [jour n, liste de Trade du jour n], ...]
        self.presentAssetDict = {}
        self.cash = cash
        self.initialCash = cash
        print(self.__repr__())

    def __repr__(self):
        return "<{0}, cash : {1} $>".format(self.name, self.initialCash)


class Expert:
    def __init__(self, market, name="Unknown Expert"):
        self.name = name
        self.market = market
        self.predictionMadeList = []
        self.market.add_expert(self)
        print(self.__repr__())

    def new_day(self):
        # make a prediction
        pred = ["UP", "DOWN"]
        prediction = Prediction(self.market.assetList[0], pred[random.randint(0, 1)], self.market.theDay + 1, self, self.market.theDay)
        self.market.register_prediction(prediction)

    def prediction_result(self, prediction):
        self.predictionMadeList.append(prediction)

    def description_of_prediction(self):
        number_UP = 0
        number_DOWN = 0
        number_true = 0
        for prediction in self.predictionMadeList:
            if prediction.evolution == "UP":
                number_UP += 1
            if prediction.evolution == "DOWN":
                number_DOWN += 1
            if prediction.isTrue:
                number_true += 1
        length = len(self.predictionMadeList)
        return [length, number_UP, number_DOWN, number_true, number_true / max(1, length)]

    def __repr__(self):
        return "<{0}>".format(self.name)


class Strategy:

    def __init__(self, market, name="Unknown Strategy", cash=10 ** 4):
        self.name = name
        self.market = market
        self.portfolio = Portfolio("Portfolio of " + name, cash)
        self.market.add_portfolio(self.portfolio)
        self.market.add_strategy(self)
        print(self.__repr__())

    def __repr__(self):
        return "<{0}>".format(self.name)

    def new_day(self):
        number_of_asset = len(self.market.assetList)
        i = random.randint(0, 2 * number_of_asset)
        while i < number_of_asset:
            asset = self.market.assetList[random.randint(0, number_of_asset - 1)]
            buy_or_sell = random.randint(0, 1)
            if buy_or_sell:
                self.market.long(self.portfolio, asset, random.randint(1, 10) * 1)
            else:
                self.market.short(self.portfolio, asset, random.randint(1, 10) * 1)
            i += 1


class Market:
    def __init__(self):
        self.assetList = []
        self.portfolioList = []
        self.strategyList = []
        self.predictionList = []
        self.expertList = []
        self._theDay = 0
        self.maximumDay = 0
        self.time = [] #G
        print(self.__repr__())

    @property
    def theDay(self):
        """I'm the 'theday' property."""
        return self._theDay

    @theDay.setter
    def theDay(self, value):
        # print("Simulation theDay", self._theDay)
        for strategy in self.strategyList:
            strategy.new_day()

        for portfolio in self.portfolioList:
            self.update_portfolio(portfolio)
            self.update_position(portfolio)
            # print(portfolio.presentAssetDict)

        self.play_prediction()
        self._theDay = value

    @theDay.deleter
    def theDay(self):
        del self._theDay

    def __repr__(self):
        return "<Market, theDay : {0}>".format(self.theDay)

    def register_prediction(self, prediction):
        self.predictionList.append(prediction)
        # print("prediction registered")

    def play_prediction(self):
        # print("play prediction")
        for expert in self.expertList:
            expert.new_day()

        for prediction in self.predictionList:
            if prediction.final_term == self.theDay:
                asset_before = prediction.asset.data[prediction.day]
                asset_today = prediction.asset.data[self.theDay]
                if prediction.evolution == "UP":
                    if asset_before < asset_today:
                        prediction.isTrue = True
                elif prediction.evolution == "DOWN":
                    if asset_before > asset_today:
                        prediction.isTrue = True
                elif type(prediction.evolution) is (int or float):
                    print("!!! NOT YET IMPLEMENTED !!!")
                else:
                    print("!!! WRONG PREDICTION !!!")
                prediction.expert.prediction_result(prediction)
                self.predictionList.remove(prediction)

    def plot_market(self):
        for asset in self.assetList:
            plt.plot(asset.data)
        plt.show()

    def play_day(self, max_day=-1):
        if max_day == -1:
            max_day = self.maximumDay

        if self.theDay <= min(self.maximumDay, max_day):
            self.theDay += 1
            return True
        else:
            return False

    def update_portfolio(self, portfolio):

        actual_value = portfolio.cash
        for asset, volume in portfolio.presentAssetDict.items():
            actual_value += asset.data[self.theDay] * volume
        portfolio.valueHistory.append(actual_value)

        portfolio.orderHistoryList.append([self.theDay, portfolio.todayInQueueTrade])
        portfolio.todayInQueueTrade = []

    def update_position(self, portfolio):
        for asset, position in portfolio.position.items():
            position.value = asset.data[self.theDay]*position.volume
            position.value_history += [position.value]


    def long(self, portfolio, asset, volume):
        asset_price = asset.data[self.theDay]

        if portfolio.cash >= asset_price * volume:
            portfolio.cash -= asset_price * volume
            print(self.time[self.theDay],": Bought ",volume, "at $",asset_price, " of ", asset.name) #G
            self.register_trade(portfolio, asset, volume)
            self.add_position(portfolio,asset,volume, True)
        else:
            print(
                "!!! Not enough money to open {0} for {1}, only {2:.2f} $ in cash !!!".format(asset.name, asset_price, portfolio.cash))

    def short(self, portfolio, asset, volume):
        asset_price = asset.data[self.theDay]

        # if asset in portfolio.presentAssetDict.keys():
        #     actual_owned_volume = portfolio.presentAssetDict[asset]
        # else:
        #     actual_owned_volume = 0

        #if actual_owned_volume >= volume:
        portfolio.cash += asset_price * volume
        print(self.time[self.theDay],": Sold ", volume, "at $",asset_price, " of ", asset.name) #G
        self.register_trade(portfolio, asset, -volume)
        self.add_position(portfolio,asset,volume, False)
        # else:
        #     print("!!! Not enough volume of {0} to close {1}, only {2} owned !!!".format(asset.name, volume, actual_owned_volume))

    def close(self,portfolio, position): #close a position of a portfolio
        position.closed = True
        position.close_date = self.time[self.theDay]
        if position.long:
            asset_price = position.asset.data[self.theDay]
            portfolio.cash += asset_price * position.volume
            print(self.time[self.theDay],": Sold ", position.volume, "at $",asset_price, " of ", position.asset.name) #G
            self.register_trade(portfolio, position.asset, -position.volume)
        else:
            asset_price = position.asset.data[self.theDay]
            portfolio.cash -= asset_price * position.volume
            print(self.time[self.theDay],": Bought ",position.volume, "at $",asset_price, " of ", position.asset.name) #G
            self.register_trade(portfolio, position.asset, position.volume)



    def register_trade(self, portfolio, asset, volume):
        new_trade = Trade(asset, volume, self.theDay)
        portfolio.todayInQueueTrade += [new_trade]

        if asset in portfolio.presentAssetDict:
            portfolio.presentAssetDict[asset] += volume
        else:
            portfolio.presentAssetDict[asset] = volume

    def add_position(self, portfolio, asset, volume, long):
        new_pos = Position(asset,volume,self.time[self.theDay],long)
        portfolio.position[asset] = new_pos


    def get_asset_data(self, asset, start=0):
        return asset.data[start:self.theDay + 1]

    def get_portfolio_order_history_list(self, portfolio):
        return portfolio.orderHistoryList

    def get_portfolio_value_history(self, portfolio):
        return portfolio.valueHistory

    def get_portfolio_cash(self, portfolio):
        return portfolio.cash

    def add_asset(self, asset: Asset):
        self.assetList.append(asset)
        print("+ Asset added : {0}, number of days : {1}".format(asset.name, asset.length))
        if self.maximumDay > asset.length - 1 or self.maximumDay < 1:  # -1 car le premier jour est le jour 0
            self.maximumDay = asset.length - 1

    def add_portfolio(self, portfolio: Portfolio):
        self.portfolioList.append(portfolio)

    def add_strategy(self, strategy: Strategy):
        self.strategyList.append(strategy)

    def add_expert(self, expert):
        self.expertList.append(expert)

    def add_time(self, time):
        self.time = time