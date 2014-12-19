import random
import matplotlib.pyplot as plt


class Trade:
    lastId = 0

    def __init__(self, asset_id, volume, day):
        self.asset_id = asset_id
        self.volume = volume
        self.day = day
        self.id = Trade.lastId
        Trade.lastId += 1
        print(self.__repr__())

    def __repr__(self):
        return "<Trade of asset : {0}  and volume : {1}, the day {2}>".format(self.asset_id, self.volume, self.day)


class Asset:
    lastId = 0

    def __init__(self, name="Unknown asset", data=[]):
        self.name = name
        self.id = Asset.lastId
        Asset.lastId += 1
        self.data = data
        self.length = len(data)
        print(self.__repr__())

    def __repr__(self):
        return "<{0}, id : {1}>".format(self.name, self.id)


class Portfolio:
    lastId = 0

    def __init__(self, name="Unknown portfolio"):
        self.name = name
        self.id = Portfolio.lastId
        Portfolio.lastId += 1
        self.todayInQueueTrade = []
        self.valueHistory = []
        self.orderHistoryList = []  # de la forme [ [jour n, liste de Trade du jour n], ...]
        self.presentAssetDict = {}
        print(self.__repr__())

    def __repr__(self):
        return "<{0}, id : {1}>".format(self.name, self.id)


class Strategy:
    lastId = 0

    def __init__(self, market, name="Unknown Strategy"):
        self.name = name

        self.id = Strategy.lastId
        Strategy.lastId += 1

        self.market = market

        portfolio = Portfolio("Portfolio of " + name)
        self.portfolio_id = portfolio.id
        self.market.add_portfolio(portfolio)

        self.market.add_strategy(self)
        print(self.__repr__())

    def __repr__(self):
        return "<{0}, id : {1}>".format(self.name, self.id)

    def new_day(self):
        number_of_asset = len(self.market.assetDict.keys())
        i = random.randint(0, 2*number_of_asset)
        while i < number_of_asset:
            asset = random.randint(0, number_of_asset-1)
            self.market.buy(self.id, asset, random.randint(-10, 10)*0.1)
            i += 1


class Market:
    def __init__(self):
        self.assetDict = {}
        self.portfolioDict = {}
        self.strategyDict = {}
        self.theDay = 0
        self.maximumDay = 0
        print(self.__repr__())

    def __repr__(self):
        return "<Market, theDay : {0}>".format(self.theDay)

    def add_asset(self, the_asset: Asset):
        self.assetDict[the_asset.id] = the_asset
        if self.maximumDay < the_asset.length - 1:  # -1 car le premier jour est le jour 0
            self.maximumDay = the_asset.length - 1

    def add_portfolio(self, the_portfolio: Portfolio):
        self.portfolioDict[the_portfolio.id] = the_portfolio

    def add_strategy(self, the_strategy: Strategy):
        self.strategyDict[the_strategy.id] = the_strategy

    def plot_market(self):
        for asset_id in self.assetDict:
            plt.plot(self.assetDict[asset_id].data)
        plt.show()

    def play_day(self, max_day=-1):
        if max_day == -1:
            max_day = self.maximumDay

        if self.theDay <= min(self.maximumDay, max_day):
            for strategy_id in self.strategyDict:
                self.strategyDict[strategy_id].new_day()

            for portfolio_id in self.portfolioDict:
                self.update_portfolio(portfolio_id)
                # print(self.portfolioDict[portfolio_id].presentAssetDict)

            self.theDay += 1
            return True
        else:
            return False

    def update_portfolio(self, portfolio_id):
        portfolio = self.portfolioDict[portfolio_id]

        actual_value = 0
        for asset_id, volume in portfolio.presentAssetDict.items():
            actual_value += self.assetDict[asset_id].data[self.theDay]*volume
        portfolio.valueHistory += [actual_value]

        portfolio.orderHistoryList += [[self.theDay, portfolio.todayInQueueTrade]]
        portfolio.todayInQueueTrade = []

    def buy(self, portfolio_id, asset_id, volume):
        new_trade = Trade(asset_id, volume, self.theDay)
        portfolio = self.portfolioDict[portfolio_id]

        portfolio.todayInQueueTrade += [new_trade]

        if asset_id in portfolio.presentAssetDict:
            portfolio.presentAssetDict[asset_id] += volume
        else:
            portfolio.presentAssetDict[asset_id] = volume

    def sell(self, portfolio_id, asset_id, volume):
        self.buy(portfolio_id, asset_id, -volume)

    def get_asset_data(self, asset_id, start=0):
        return self.assetDict[asset_id].data[start:self.theDay+1]

    def get_portfolio_order_history_list(self, portfolio_id):
        return self.portfolioDict[portfolio_id].orderHistoryList