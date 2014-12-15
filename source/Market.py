import random
import matplotlib.pyplot as plt


class Asset:
    lastId = 0

    def __init__(self, name="Unknown asset", data=[]):
        self.name = name
        self.id = Asset.lastId
        Asset.lastId += 1
        self.data = data
        self.lenth = len(data)
        print("Asset instantiated")


class Portfolio:
    lastId = 0

    def __init__(self, name="Unknown portfolio"):
        self.name = name
        self.id = Portfolio.lastId
        Portfolio.lastId += 1
        self.history = [0]
        self.assetList = []  # contient des couples idAsset et volume (carnet d'ordres)
        print("Portfolio instantiated")


class Strategy:
    lastId = 0

    def __init__(self, market, name="Unknown Strategy"):
        self.name = name
        self.id = Strategy.lastId
        Strategy.lastId += 1
        self.market = market
        self.portfolio = Portfolio(name + "'s Portfolio")
        self.market.add_strategy(self)
        self.market.add_portfolio(self.portfolio)
        print("Strategy instantiated")

    def new_day(self):
        self.market.buy(self.portfolio,
                        self.market.assetDict[0],
                        random.randint(-10, 10)*0.01)


class Market:
    def __init__(self):
        self.assetDict = {}
        self.portfolioDict = {}
        self.strategyDict = {}
        self.theDay = 0
        self.maximumDay = 0
        print("Market instantiated")

    def add_asset(self, the_asset: Asset):
        self.assetDict[the_asset.id] = the_asset
        if self.maximumDay < the_asset.lenth - 1:  # -1 car le premier jour est le jour 0
            self.maximumDay = the_asset.lenth - 1

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

        if self.theDay <= min(self.maximumDay, max_day): #peut être -1
            for strategy_id in self.strategyDict:
                self.strategyDict[strategy_id].new_day()
            self.theDay += 1
            return True
        else:
            return False

    def portfolio_value(self, portfolio: Portfolio):
        value = 0
        history = []
        for asset in portfolio.assetList:
            # asset[0] est l'id de l'asset, asset[1] est le volume
            for i in range(self.maximumDay):
                value += self.assetDict[asset[0]].data[i]*asset[1]
                history += [value]
        return history

    def buy(self, portfolio: Portfolio, asset: Asset, volume):
        portfolio.assetList += [[asset.id, volume]]

    def sell(self, portfolio: Portfolio, asset: Asset, volume):
        portfolio.assetList += [asset.id, -volume]




