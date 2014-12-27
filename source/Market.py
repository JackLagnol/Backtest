import random
import matplotlib.pyplot as plt

"""
NOTE : volume *MUST* be >0 when a trade is open or close (PUT not yet implemented)
"""


class Trade:
    """ Represent a Trade made by a Strategy.

    Constructor : Trade(the asset traded,
                       the volume bought (<0 if sold),
                       the day it was mad)

    id: (int) unique id generated using the 'static' variable lastId
    """
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
    """ Represent a Predication made by an Expert.

    Constructor : Prediction(the asset traded,
                             the evolution predicted (may be 'UP' and 'DOWN' for the moment -> subject to change),
                             the day the prediction should be verified,
                             the expert who made it,
                             the day it was made)

    id: (int) unique id generated using the 'static' variable lastId
    isTrue: (boolean) initially False and turn to True (if true) by the market when the Prediction is checked
    """
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
    """ Represent a Asset in the market.

    Constructor : Asset(the name of the asset (optional),
                        the list of the value (one for each day) (optional))

    length: (int) the number of day that can be simulated (from day=0 to length-1 because the first simulated day is 0)
    """
    def __init__(self, name="Unknown asset", data=[]):
        self.name = name
        self.data = data
        self.length = len(data)
        print(self.__repr__())

    def __repr__(self):
        return "<{0}>".format(self.name)


class Portfolio:
    """ Represent a Portfolio in the market usually own by a Strategy.

    Constructor : Portfolio(the name of the asset,
                            the initial cash owned)

    valueHistory: (list of int) updated at the end of each day within the function market.update_portfolio,
        that store the value of the portfolio day after day, converting the value of every asset owned in cash
    orderHistoryList: (list of list) [ [0, list of trade made the day 0], ..., [n, list of trade made the day n] ]
        updated each day within the function market.update_portfolio
    presentAssetDict: (dict) that store the asset actually owned, update directly when a trade is register
        (with the function market.register_trade)
    todayInQueueTrade: (list of Trade) temporary store Trade during the day, emptied at the end of the day when
        the Trade are registered in orderHistoryList
    cash: (float) used to buy (and sell) assets
    initialCash: (float) the cash available when instantiated
    """
    def __init__(self, name, cash):
        self.name = name
        self.todayInQueueTrade = []
        self.valueHistory = []
        self.orderHistoryList = []  # [ ..., [day n, list of Trade made the day n], ...]
        self.presentAssetDict = {}
        self.cash = cash
        self.initialCash = cash
        print(self.__repr__())

    def __repr__(self):
        return "<{0}, cash : {1} $>".format(self.name, self.initialCash)


class Expert:
    """ Represent a Expert that makes prediction, but doesn't buy assets.

    Is made to be a super class.

    Constructor : Expert(the market where it operates,
                         the name (optional))

    predictionMadeList: (list of Prediction) register that prediction *after they have been verified*
    """
    def __init__(self, market, name="Unknown Expert"):
        self.name = name
        self.market = market
        self.predictionMadeList = []
        # we register the expert in the market
        self.market.add_expert(self)
        print(self.__repr__())

    def new_day(self):
        """ Called each day by the market to ask the expert to make its predictions

        Currently a random prediction (50%)
        """
        pred = ["UP", "DOWN"]
        prediction = Prediction(self.market.assetList[0], pred[random.randint(0, 1)], self.market.theDay + 1, self, self.market.theDay)
        self.market.register_prediction(prediction)

    def prediction_result(self, prediction):
        """" Called by the market to inform the result of a passed prediction """
        self.predictionMadeList.append(prediction)

    def description_of_prediction(self):
        """" Called by anyone that wants to get the results of the expert """
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
    """ Represent a Strategy that buys assets.

    Is made to be a super class.

    Constructor : Strategy(the market where it operates,
                           the name (optional),
                           the initialCash (optional, value = 10 000) )

    portfolio: (Portfolio) portfolio owned by the strategy
    """
    def __init__(self, market, name="Unknown Strategy", cash=10 ** 4):
        self.name = name
        self.market = market
        self.portfolio = Portfolio("Portfolio of " + name, cash)
        # we register the strategy and its portfolio in the market
        self.market.add_portfolio(self.portfolio)
        self.market.add_strategy(self)
        print(self.__repr__())

    def __repr__(self):
        return "<{0}>".format(self.name)

    def new_day(self):
        """ Called each day by the market to ask the strategy to buy assets

        Currently a random strategy
        """
        number_of_asset = len(self.market.assetList)
        i = random.randint(0, 2 * number_of_asset)
        while i < number_of_asset:
            asset = self.market.assetList[random.randint(0, number_of_asset - 1)]
            buy_or_sell = random.randint(0, 1)
            if buy_or_sell:
                self.market.open(self.portfolio, asset, random.randint(1, 10) * 1)
            else:
                self.market.close(self.portfolio, asset, random.randint(1, 10) * 1)
            i += 1


class Market:
    """ Represent a Market that simulates assets and portfolios.

    Is used to link Expert, Strategy and their prediction or portfolio.

    Constructor : Market()

    _theDay: (int) PRIVATE *do not set it* used stored the current day
        used theDay instead to get the current day
    theDay: (int) *do not set it* property used to manage the simulation,
        used in market.play_day()
    maximumDay: (int) day limit after which at least one asset has no value
    assetList: (list of Asset) list of asset simulated
    portfolioList: (list of Portfolio) list of portfolio simulated
    strategyList: (list of Strategy) list of strategy simulated
    expertList: (list of Expert) list of expert simulated
    """
    def __init__(self):
        self.assetList = []
        self.portfolioList = []
        self.strategyList = []
        self.predictionList = []
        self.expertList = []
        self._theDay = 0
        self.maximumDay = 0
        print(self.__repr__())

    @property
    def theDay(self):
        """ Property used to manage the simulation

        When set, calls new_day() of Strategy, update_portfolio() and self.play_prediction()
        """
        return self._theDay

    @theDay.setter
    def theDay(self, value):
        # print("Simulation theDay", self._theDay)
        for strategy in self.strategyList:
            strategy.new_day()

        for portfolio in self.portfolioList:
            self.update_portfolio(portfolio)
            # print(portfolio.presentAssetDict)

        self.play_prediction()
        self._theDay = value

    @theDay.deleter
    def theDay(self):
        del self._theDay

    def __repr__(self):
        return "<Market, theDay : {0}>".format(self.theDay)

    def register_prediction(self, prediction):
        """ Register a prediction made by a Expert into self.predictionList, called by the expert """
        self.predictionList.append(prediction)
        # print("prediction registered")

    def play_prediction(self):
        """ Call new_day() of expert and check their pasted predictions and remove them from self.predictionList """
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
                    print("!!! WRONG FORMAT FOR PREDICTION !!!")
                prediction.expert.prediction_result(prediction)
                self.predictionList.remove(prediction)

    def plot_market(self):
        """ Plot all assets imported """
        for asset in self.assetList:
            plt.plot(asset.data)
        plt.show()

    def play_day(self, max_day=-1):
        """ Manage the simulation of a day

        if theDay <= min(maximumDay, max day set in backtest), add 1 to theDay and return True, else False
        the property mechanism calls the useful functions used to manage the simulation
        """
        if max_day == -1:
            max_day = self.maximumDay

        if self.theDay <= min(self.maximumDay, max_day):
            self.theDay += 1
            return True
        else:
            return False

    def update_portfolio(self, portfolio):
        """ Update the attributes of portfolios (valueHistory, todayInQueueTrade, orderHistoryList) """
        actual_value = portfolio.cash
        for asset, volume in portfolio.presentAssetDict.items():
            actual_value += asset.data[self.theDay] * volume
        portfolio.valueHistory.append(actual_value)

        portfolio.orderHistoryList.append([self.theDay, portfolio.todayInQueueTrade])
        portfolio.todayInQueueTrade = []

    def open(self, portfolio, asset, volume):
        """ Called by Strategy to create a buy Trade, VOLUME MUST BE >0 FOR THE MOMENT
        PUT not yet implemented

        Register the Trade if Portfolio has enough cash and manage the cash
        """
        asset_price = asset.data[self.theDay]
        if portfolio.cash >= asset_price * volume:
            portfolio.cash -= asset_price * volume
            # print("bought :", asset_price * volume, "$ of", asset.name)
            self.register_trade(portfolio, asset, volume)
        else:
            print(
                "!!! Not enough money to open {0} for {1}, only {2:.2f} $ in cash !!!".format(asset.name, asset_price, portfolio.cash))

    def close(self, portfolio, asset, volume):
        """ Called by Strategy to create a sell Trade, VOLUME MUST BE >0 FOR THE MOMENT

        Register the Trade if Portfolio has enough volume and manage the cash
        """
        asset_price = asset.data[self.theDay]

        if asset in portfolio.presentAssetDict.keys():
            actual_owned_volume = portfolio.presentAssetDict[asset]
        else:
            actual_owned_volume = 0

        if actual_owned_volume >= volume:
            portfolio.cash += asset_price * volume
            # print("Sold :", portfolio.cash, "$ of", asset.name)
            self.register_trade(portfolio, asset, -volume)
        else:
            print("!!! Not enough volume of {0} to close {1}, only {2} owned !!!".format(asset.name, volume, actual_owned_volume))

    def register_trade(self, portfolio, asset, volume):
        """ Called by self.open() and self.close() to register a Trade

        Add the Trade to portfolio.todayInQueueTrade
        Update portfolio.presentAssetDict
        """
        new_trade = Trade(asset, volume, self.theDay)
        portfolio.todayInQueueTrade += [new_trade]

        if asset in portfolio.presentAssetDict:
            portfolio.presentAssetDict[asset] += volume
        else:
            portfolio.presentAssetDict[asset] = volume

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
