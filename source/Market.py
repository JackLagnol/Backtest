import random
import matplotlib.pyplot as plt
from source.commonTools import *

# TODO SHORT (opening and closing)
# TODO PREDICTION (other than UP or DOWN)

# TODO Check SharpRatio and convert it to a function

# TODO Strategy
# - Lead lag : un detecteur de tendence
# - Moyenne mobile avec une strategie (inclu le managment du portfolio)
# - Moyenne mobile avec un expert (indicateur)


class Trade:
    """ Represent a Trade registered in a Position

    No registration needed : position are registered

    Constructor : Trade(the asset traded,
                       the volume bought (<0 if sold) by the strategy,
                       the day it was made)

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
        return "<Trade of {0}, volume: {1}, the day: {2}>".format(self.asset.name, self.volume, self.day)


class Position:
    """ Represent a Position opened by a Strategy, may be SHORT or LONG.

    Is registered into the portfolio when created: Portfolio.register_position()

    Must be updated by the market (to keep updated value_history, and be closed properly)

    Constructor : Position(the asset traded,
                           the volume bought (long) or sold (short),
                           the day it was opened,
                           the type of position (True for LONG, False for SHORT),
                           the portfolio where it will be registered and where the cash will be send when closed)

    openTrade: (Trade) the opening trade
    closeTrade: (Trade) the closing trade (None initially)

    long: (boolean) True for long, False for short
    closed: (boolean) True if closed (False initially)

    gain: (float) the gain realized by the position (>0 for a SHORT if final_price < first_price)
    value_history: (list) the historical values of the position (volume*price stored each day)
    portfolio: (Portfolio) the portfolio where it is registered and where the cash will be send when closed
    """

    def __init__(self, asset, volume, day, long, portfolio):
        self.openTrade = Trade(asset, volume, day)
        self.closeTrade = None

        self.long = long
        self.closed = False

        self.gain = None
        self.valueHistory = []
        self.portfolio = portfolio

        # the position is registered in the portfolio
        portfolio.register_position(self)

        # print(self.__repr__())

    def __repr__(self):
        if not self.closed:
            current_price = self.openTrade.asset.data[self.portfolio.market.theDay]
            opening_price = self.openTrade.asset.data[self.openTrade.day]
            gain = (current_price - opening_price) * self.openTrade.volume
            return "<Long: {0}, sill open, asset {1}, volume {2}, " \
                   "opened the {3}, actual gain: {4}$>".format(self.long, self.openTrade.asset.name,
                                                               self.openTrade.volume, self.openTrade.day, gain)
        else:
            return "<Long: {0}, closed, asset {1}, volume {2}, " \
                   "opened the {3}, closed the {4}, gain: {5}$>".format(self.long, self.openTrade.asset.name,
                                                                        self.openTrade.volume, self.openTrade.day,
                                                                        self.closeTrade.day, self.gain)

    def get_returns(self):
        returns = get_returns(self.valueHistory)

        # ***** POINT TO CHECK ***** (Guillaume)
        # seems ok to me (JM) because for a short, value_history should be normally decreasing and cause
        # returns = (S_t - S_(t-1)) / S_(t-1) to increase

        # multiply by -1 if is short
        if not self.long:
            returns = [-item for item in returns]

        return returns


class Prediction:
    """ Represent a Prediction made by an Expert.

    Is registered into the market when created : Market.register_prediction()

    Constructor : Prediction(the asset traded,
                             the evolution predicted (may be 'UP' and 'DOWN' for the moment -> subject to change),
                             the day the prediction should be verified (usually tomorrow),
                             the expert who made it,
                             the day it was made,
                             the market where it will be registered (market not stored))

    id: (int) unique id generated using the 'static' variable lastId
    isTrue: (boolean) initially False and turn to True (if is true) by the market when the Prediction is checked
    final_term: (int) the day ID when the prediction will be verified (and isTrue finally set) NB: not the shift of day!
    result: (float) yield: asset(final_term)/asset(day_it_was_made)
    """
    lastId = 0

    def __init__(self, asset, evolution, final_term, expert_who_made_it, day_it_was_made, market):
        self.asset = asset
        self.evolution = evolution  # can be UP, DOWN for the moment (soon : an evolution (ex: -250 for the cac 40))
        self.expert = expert_who_made_it
        self.day = day_it_was_made
        self.final_term = final_term
        self.isTrue = False
        self.result = -1

        self.id = Prediction.lastId
        Prediction.lastId += 1
        # the prediction is registered in the market
        market.register_prediction(self)
        # print(self.__repr__())

    def __repr__(self):
        return "<Prediction of asset : {0}, the theDay {1}, evolution : {2}>".format(self.asset.name,
                                                                                     self.day, self.evolution)


class Asset:
    """ Represent a Asset in the market.

    Must be registered into the market: market.

    Constructor : Asset(the name of the asset,
                        the list of the value (one for each day))

    length: (int) the number of day that can be simulated (from day=0 to length-1 because the first simulated day is 0)
    """

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.length = len(data)
        # print(self.__repr__())

    def __repr__(self):
        return "<Asset: {0}>".format(self.name)


class Portfolio:
    """ Represent a Portfolio in the market usually own by a Strategy.

    Must be update by the market.
    Is registered in the market.

    Constructor : Portfolio(the name of the asset,
                            the initial cash owned,
                            the market where it is operating)

    valueHistory: (list of int) updated at the end of each day within the function market.update_portfolio,
        that store the value of the portfolio day after day, converting the value of every asset owned in cash
    presentAssetDict: (dict) that store the asset actually owned, update directly when a position is register
    presentPositionList: (list of Position) position (still open) hold by the portfolio
    pastPositionList: (list of Position) position closed (opened or closed), *ORDERED BY THE CLOSING DAY*

    cash: (float) used to buy (and sell) assets
    initialCash: (float) the cash available when created
    market: (Market) the market where it is operating
    """

    def __init__(self, name, cash, market):
        self.name = name
        self.valueHistory = []
        self.presentAssetDict = {}
        self.openPositionList = []
        self.closePositionList = []

        self.cash = cash
        self.initialCash = cash

        self.market = market
        # the portfolio is registered in the market
        market.register_portfolio(self)

        # print(self.__repr__())

    def __repr__(self):
        return "<{0}, cash : {1}$>".format(self.name, self.initialCash)

    def register_position(self, position):
        # print("Position registered: {}".format(position))
        self.openPositionList.append(position)

    def results_description(self, string_mode=False):
        total_number_of_positions = len(self.openPositionList) + len(self.closePositionList)
        number_of_open_positions = len(self.openPositionList)
        number_of_good_positions = len([pos for pos in self.closePositionList if pos.gain >= 0])
        ratio = number_of_good_positions / max(total_number_of_positions, 1)
        the_list = [total_number_of_positions, number_of_open_positions,
                    number_of_good_positions, ratio]
        if not string_mode:
            return the_list
        else:
            return "{0} positions ({1} still open), in the closed ones: {2} good, ratio: {3:.3f}".format(*the_list)


class Expert:
    """ Represent a Expert that makes prediction, but doesn't buy assets.

    Is registered in the market when created.
    Is made to be a super class.
    Register the *expired* (ie checked) predictions, market must call Expert.prediction_result

    Constructor : Expert(the market where it operates,
                         the name (optional))

    predictionMadeList: (list of Prediction) register the predictions *after they have been verified*
    """

    def __init__(self, market, name="Unknown Expert"):
        self.name = name
        self.market = market
        self.predictionMadeList = []
        # the expert is registered in the market
        self.market.register_expert(self)
        # print(self.__repr__())

    def new_day(self):
        """ Called each day by the market to ask the expert to make its predictions

        Currently a random prediction (50%)
        """
        pred = ["UP", "DOWN"]
        Prediction(self.market.assetList[0],
                   pred[random.randint(0, 1)],
                   self.market.theDay + 1,
                   self,
                   self.market.theDay,
                   self.market)

    def prediction_result(self, prediction):
        """" Called by the market to inform the result of a passed prediction """
        self.predictionMadeList.append(prediction)

    def results_description(self, string_mode=False):
        length = len(self.predictionMadeList)
        number_up = 0
        number_down = 0
        number_true = 0
        for prediction in self.predictionMadeList:
            if prediction.evolution == "UP":
                number_up += 1
            if prediction.evolution == "DOWN":
                number_down += 1
            if prediction.isTrue:
                number_true += 1
        the_list = [length, number_up, number_down, number_true, number_true / max(1, length)]
        if not string_mode:
            return the_list
        else:
            return "Prediction of {0} : number of prediction {1} ({2} UP,{3} DOWN), {4} good, " \
                   "Ratio : {5:.3f}".format(self.name, *the_list)

    def __repr__(self):
        return "<{0}>".format(self.name)


class Strategy:
    """ Represent a Strategy that buys assets.

    Is registered in the market when created.
    Is made to be a super class.

    Constructor : Strategy(the market where it operates,
                           the name (optional),
                           the initialCash (optional, value = 10 000) )

    portfolio: (Portfolio) portfolio owned by the strategy
    """

    def __init__(self, market, name="Unknown Strategy", cash=10 ** 4):
        self.name = name
        self.market = market
        self.portfolio = Portfolio("Portfolio of " + name, cash, self.market)
        # the strategy is registered in the market
        self.market.register_strategy(self)
        # print(self.__repr__())

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
            should_i_buy = random.randint(0, 1)
            if should_i_buy:
                self.market.open(self.portfolio, asset, random.randint(1, 10), "LONG")
            else:
                length = len(self.portfolio.openPositionList)
                if length > 0:
                    self.market.close(self.portfolio.openPositionList[random.randint(0, length - 1)])
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

    predictionList: (list of Prediction) list of predictions not yet expired made by the experts
    expertList: (list of Expert) list of expert simulated
    """

    def __init__(self):
        self._theDay = 0
        self.maximumDay = 0

        self.assetList = []

        self.portfolioList = []
        self.strategyList = []

        self.predictionList = []
        self.expertList = []

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

    def play_day(self, last_day):
        """ Manage the simulation of a day

        if theDay <= min(maximumDay, max day set in backtest), add 1 to theDay and return True, else False
        the property mechanism calls the useful functions used to manage the simulation
        """

        if self.theDay <= last_day:
            self.theDay += 1
            return True
        else:
            return False

    def play_prediction(self):
        """ Call new_day() of expert and check their pasted predictions and remove them from self.predictionList """
        # print("play prediction")
        for expert in self.expertList:
            expert.new_day()

        for prediction in self.predictionList:
            if prediction.final_term == self.theDay:
                asset_before = prediction.asset.data[prediction.day]
                asset_today = prediction.asset.data[self.theDay]

                # prediction.result is calculated and set
                prediction.result = asset_today/asset_before

                # prediction.isTrue is calculated and set
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

    def update_portfolio(self, portfolio):
        """ Update the attributes of portfolios (valueHistory) and their Positions (valueHistory) """
        actual_value = portfolio.cash
        for asset, volume in portfolio.presentAssetDict.items():
            actual_value += asset.data[self.theDay] * volume
        portfolio.valueHistory.append(actual_value)

        # update position history value of the positions held by the portfolio
        for position in portfolio.openPositionList:
            position.valueHistory.append(position.openTrade.asset.data[self.theDay] * position.openTrade.volume)
        for position in portfolio.closePositionList:
            if position.closeTrade.day == self.theDay:
                position.valueHistory.append(position.openTrade.asset.data[self.theDay] * position.openTrade.volume)

    def open(self, portfolio, asset, volume, type_of_position):
        """ Called by Strategy to create a buy Trade, VOLUME MUST BE >0
        type: (String) "LONG" or "SHORT"

        Create the position if Portfolio has enough cash, and manage the cash
        """
        asset_price = asset.data[self.theDay]

        owned_volume = 0
        if type_of_position == "LONG":
            type_of_position = True
            owned_volume = volume
        elif type_of_position == "SHORT":
            print("!!! SHORT NOT YET IMPLEMENTED !!!")
            # TODO SHORT opening
            # !! the next line is a problematic one !! what do we pay when opening a short ?
            owned_volume = -volume
            # type_of_position = False
        else:
            print("!!! WRONG FORMAT FOR POSITION !!!")

        if portfolio.cash >= asset_price * volume:
            portfolio.cash -= asset_price * volume
            # print("bought :", asset_price * volume, "$ of", asset.name)
            Position(asset, volume, self.theDay, type_of_position, portfolio)

            # update the value of the portfolio.presentAssetDict
            # owned_volume is <0 for SHORT, >0 for LONG
            if asset in portfolio.presentAssetDict:
                portfolio.presentAssetDict[asset] += owned_volume
            else:
                portfolio.presentAssetDict[asset] = owned_volume
        else:
            print("!!! Not enough money to open {0} of {1} "
                  "for {2}, {3} has only {4:.2f} $ in cash !!!".format(volume, asset.name, asset_price * volume,
                                                                       portfolio.name, portfolio.cash))

    def close(self, position: Position):
        """ Called by Strategy to close a position, and manage the cash """
        # NB valueHistory is not yet updated !
        # If the position is already closed, the order is canceled
        if position.closed:
            print("!!! POSITION ALREADY CLOSED !!!")
            return False

        # Else we execute the order
        # Useful variables
        open_trade = position.openTrade
        current_price = position.openTrade.asset.data[self.theDay]
        opening_price = open_trade.asset.data[open_trade.day]

        # gain for a LONG (difference between opening price and closing price X volume)
        gain = (current_price - opening_price) * open_trade.volume
        # to update the value of the portfolio.presentAssetDict: sold_volume is >0 for LONG, <0 for SHORT
        sold_volume = open_trade.volume

        if position.long:
            # print("Long sold : {0}$ of {1} by {2}".format(position.portfolio.cash, open_trade.asset.name,
            #                                               position.portfolio.name))
            # update the cash of the portfolio for a LONG
            position.portfolio.cash += gain + opening_price*open_trade.volume
        else:
            sold_volume = -sold_volume
            gain = -gain
            # TODO SHORT closing
            # !! the next line is a problematic one !! what do we gain when closing a short ?
            # update the cash of the portfolio for a SHORT
            position.portfolio.cash += gain + opening_price*open_trade.volume
            print("Short sold : {0}$ of {1} by {2}".format(position.portfolio.cash, open_trade.asset.name,
                                                           position.portfolio.name))

        # update the variables of the position
        position.closeTrade = Trade(open_trade.asset, open_trade.volume, self.theDay)
        position.closed = True
        position.gain = gain
        # update the value of the portfolio: presentAssetDict, openPositionList and closePositionList
        position.portfolio.presentAssetDict[open_trade.asset] -= sold_volume
        position.portfolio.closePositionList.append(position)
        position.portfolio.openPositionList.remove(position)

    def register_asset(self, asset: Asset):
        """ Register a asset in self.assetList and update the value of self.maximumDay """
        self.assetList.append(asset)
        print("+ Asset added : {0}, number of days : {1}".format(asset.name, asset.length))
        if self.maximumDay > asset.length - 1 or self.maximumDay < 1:  # -1; the first day is 0 day, not 1
            self.maximumDay = asset.length - 1

    def register_portfolio(self, portfolio: Portfolio):
        """ Register a portfolio in self.portfolioList """
        self.portfolioList.append(portfolio)

    def register_strategy(self, strategy: Strategy):
        """ Register a strategy in self.strategyList """
        self.strategyList.append(strategy)

    def register_expert(self, expert):
        """ Register an expert in self.expertList """
        self.expertList.append(expert)

    def register_prediction(self, prediction):
        """ Register a prediction made by a Expert into self.predictionList """
        self.predictionList.append(prediction)
        # print("prediction registered")

    def plot_market(self):
        """ Plot all assets imported """
        for asset in self.assetList:
            plt.plot(asset.data)
        plt.show()

    def get_asset_data(self, asset, start=0):
        return asset.data[start:self.theDay + 1]