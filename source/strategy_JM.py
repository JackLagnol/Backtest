from source.Backtest import *
from mpl_toolkits.mplot3d import Axes3D
from scipy import interpolate
import numpy as np
from matplotlib.widgets import Slider, RadioButtons


class JMTendanceStrat(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_day(self):
        for the_asset in self.market.assetList:
            data = self.market.get_asset_data(the_asset)
            if len(data) > 2:
                if data[-1] > data[-2] > data[-3]:
                    self.market.open(self.portfolio, the_asset, 5, "LONG")
                elif data[-1] < data[-2] < data[-3]:
                    for position in self.portfolio.openPositionList:
                        self.market.close(position)


class JMTestStrat(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_day(self):
        the_asset = self.market.assetList[0]
        if self.market.theDay == 0:
            self.market.open(self.portfolio, the_asset, 1, "LONG")
        if self.market.theDay == 1:
            self.market.close(self.portfolio.openPositionList[0])
            self.market.open(self.portfolio, the_asset, 1, "LONG")
        if self.market.theDay == 5:
            self.market.close(self.portfolio.openPositionList[0])


class JMTendanceExpert(Expert):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_day(self):
        """ Called each day by the market to ask the expert to make its predictions """
        pred = ["UP", "DOWN"]
        for the_asset in self.market.assetList:
            data = self.market.get_asset_data(the_asset)
            if len(data) > 2:
                if data[-1] > data[-2] > data[-3]:
                    Prediction(the_asset, pred[1], self.market.theDay + 1,
                               self, self.market.theDay, self.market)
                elif data[-1] < data[-2] < data[-3]:
                    Prediction(the_asset, pred[0], self.market.theDay + 1,
                               self, self.market.theDay, self.market)


class JMMobileExpert(Expert):
    def __init__(self, *args, **kwargs):

        temp_kwargs = kwargs.copy()
        del kwargs["longMedian"]
        del kwargs["shortMedian"]
        if "asset" in kwargs:
            del kwargs["asset"]
        super().__init__(*args, **kwargs)

        self.longMedian = temp_kwargs["longMedian"]
        self.shortMedian = temp_kwargs["shortMedian"]
        self.pastShortSum = []
        self.pastLongSum = []
        self.initialised = False

        if "asset" in temp_kwargs:
            self.asset = temp_kwargs["asset"]
        else:
            self.asset = self.market.assetList[0]

    def new_day(self):
        """ Called each day by the market to ask the expert to make its predictions """
        pred = ["UP", "DOWN"]
        if self.initialised:
            data = self.market.get_asset_data(self.asset)
            short_sum = 0
            long_sum = 0
            for i in range(self.longMedian):
                long_sum += data[-i-1]  # -1 because i start at 0
            long_sum /= self.longMedian
            for i in range(self.shortMedian):
                short_sum += data[-i-1]  # -1 because i start at 0
            short_sum /= self.shortMedian

            if short_sum > long_sum and self.pastLongSum[-1] > self.pastShortSum[-1]:
                Prediction(self.asset, pred[0], self.market.theDay + self.shortMedian,
                           self, self.market.theDay, self.market)
            elif short_sum < long_sum and self.pastLongSum[-1] < self.pastShortSum[-1]:
                Prediction(self.asset, pred[1], self.market.theDay + self.shortMedian,
                           self, self.market.theDay, self.market)

            self.pastLongSum.append(long_sum)
            self.pastShortSum.append(short_sum)

        # if it is the first time self.market.theDay > self.longMedian, the median value are initialised
        elif self.market.theDay >= self.longMedian - 1:
            self.initialised = True
            data = self.market.get_asset_data(self.asset)
            # print("data sent", data, self.market.theDay)
            short_sum = 0
            long_sum = 0
            for i in range(self.longMedian):
                # print(-i-1)
                long_sum += data[-i-1]  # -1 because i start at 0
            long_sum /= self.longMedian
            for i in range(self.shortMedian):
                short_sum += data[-i-1]  # -1 because i start at 0
            short_sum /= self.shortMedian
            self.pastLongSum.append(long_sum)
            self.pastShortSum.append(short_sum)

    def plot_medians(self):
        size = min(len(self.pastShortSum) + self.longMedian - 1, len(self.asset.data) - 1)
        x = list(range(size))
        translation_list = [None] * (self.longMedian - 1)
        translated_short = translation_list + self.pastShortSum
        translated_long = translation_list + self.pastLongSum

        plt.plot(x, translated_short, label="Short Median")
        plt.plot(x, translated_long, label="Long Median")
        plt.plot(x, self.asset.data[:size], label=self.asset.name)
        plt.legend(loc=2)
        plt.show(block=True)

    def __repr__(self):
        return "<{0}, long: {1}, short: {2}>".format(self.name, self.longMedian, self.shortMedian)


def test_the_mobile_expert(number_of_line, number_of_column, first_day, last_day, print_time=True):
    beginning_time = clock()  # for time execution measurement
    matrix_of_results = np.zeros((number_of_line, number_of_column))
    for i in range(number_of_line):
        # print(i, (clock() - beginning_time), "s")
        for j in range(number_of_column):
            if j > i:
                JMMobile = JMMobileExpert(theBacktest.market, "MobileExpert", longMedian=j+1, shortMedian=i+1)
                theBacktest.simule(first_day=first_day, last_day=last_day, string_mode=False)
                matrix_of_results[i, j] = JMMobile.results_description()[4]
            else:
                matrix_of_results[i, j] = 0.5
    if print_time:
        print((clock() - beginning_time), "s")
    return matrix_of_results


def super_test_the_mobile_expert(number_of_line, number_of_column, windows_duration, length_of_the_asset, print_time=True, **kwargs):

    if "windows_offset" in kwargs:
        windows_offset = kwargs["windows_offset"]
    else:
        windows_offset = windows_duration

    list_of_results = []

    number_of_windows = int((length_of_the_asset - windows_duration) / windows_offset)

    first_day = 0
    last_day = windows_duration

    beginning_time = clock()  # for time execution measurement
    for i in range(number_of_windows+1):
        list_of_results.append(test_the_mobile_expert(number_of_line, number_of_column, first_day, last_day, print_time=False))
        print(first_day, last_day, (clock() - beginning_time), "s")
        first_day += windows_offset
        last_day += windows_offset


    return list_of_results


def plot_the_mobile_expert(number_of_line, number_of_column, matrix_of_results, plot_type="3D"):
    if plot_type == "3D":
        X = np.arange(0, number_of_line)
        Y = np.arange(0, number_of_column)

        # X, Y = np.meshgrid(X, Y)  # old command, does not work if number_of_column != number_of_line
        X, Y = np.mgrid[0:number_of_line, 0:number_of_column]
        # print(X, Y, "\n", matrix_of_results)
        fig = plt.figure()

        ax = fig.add_subplot(111, projection='3d')  # fig.gca(projection='3d')
        surf = ax.plot_surface(X, Y, matrix_of_results, rstride=1, cstride=1, cmap=plt.cm.RdYlGn, linewidth=0, antialiased=True)

        # # to add a new part in the graph NB localisation problem needs to be solved
        # ax2 = fig.add_subplot(211, projection='3d')
        # surf2 = ax2.plot_surface(Y, X, matrix_of_results, rstride=1, cstride=1, cmap=plt.cm.RdYlGn, linewidth=0, antialiased=True)

        # this is the cloud of points
        # ax.scatter(X, Y, Z)

        ax.set_zlim(0, 1)
        fig.colorbar(surf, shrink=0.7, aspect=10)

        alpha_axis  = plt.axes([0.25, 0.15, 0.65, 0.03])
        alpha_slider = Slider(alpha_axis, 'Amp', 0, 1, valinit=.5)
        alpha_slider.on_changed(lambda val: update(ax, val))

        def update(ax, val):
            alpha = alpha_slider.val
            ax.cla()
            plt.draw()

        plt.show()

    if plot_type == "2D":
        # # supersimple method
        # plt.matshow(matrix_of_results)
        # plt.show(block=True)

        # fig = plt.figure()  # seems useless here
        # ax = fig.add_subplot()  # seems useless here
        plt.imshow(matrix_of_results, cmap=plt.cm.RdYlGn, interpolation="nearest")
        plt.colorbar()
        # plt.plot()  # seems useless here
        plt.show(block=True)


def plot_several_matrix(number_of_line, number_of_column, list_of_results, plot_type="3D", interpolation="nearest"):

    # the min and max of the list of matrix are searched to set the scale
    list_of_max = []
    list_of_min = []
    for matrix in list_of_results:
        list_of_max.append(matrix.max())
        list_of_min.append(matrix.min())
    max_of_results = max(list_of_max)
    min_of_results = min(list_of_min)

    # use for the slider
    val_max = 1/len(list_of_results)

    if plot_type == "2D":

        def update(ax, val):
            index = min(int(val/val_max), len(list_of_results)-1)
            # print(val, index)
            ax.cla()
            image = ax.imshow(list_of_results[index], cmap=plt.cm.RdYlGn, interpolation=interpolation)
            image.set_clim([min_of_results, max_of_results])
            # plt.draw()

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        fig.subplots_adjust(left=0.25, bottom=0.25)
        image = ax1.imshow(list_of_results[0], cmap=plt.cm.RdYlGn, interpolation=interpolation)
        image.set_clim([min_of_results, max_of_results])
        plt.colorbar(image)
        alpha_axis = plt.axes([0.25, 0.15, 0.65, 0.03])
        alpha_slider = Slider(alpha_axis, 'First day', 0, 1, valinit=0)
        alpha_slider.on_changed((lambda val: update(ax1, val)))

        plt.show(block=True)

    if plot_type == "2D+":

        def update(ax, val):
            index = min(int(val/val_max), len(list_of_results)-1)
            # print(val, index)
            ax.cla()
            image1 = ax.imshow(list_of_results[index], cmap=plt.cm.RdYlGn, interpolation=interpolation)
            image1.set_clim([min_of_results, max_of_results])
            # plt.draw()

        def radiofunc(label):
            if label == "variance":
                image = ax2.imshow(variance, cmap=plt.cm.YlGn, interpolation=interpolation)
                image.set_clim([0, variance.max()])
                colorbar2.update_bruteforce(image)
                # colorbar2 = fig.colorbar(image, ax=ax2)
            if label == "expectation":
                image = ax2.imshow(esperance, cmap=plt.cm.RdYlGn, interpolation=interpolation)
                # image.set_clim([min_of_results, max_of_results])
                colorbar2.update_bruteforce(image)
            if label == "EV  - VAR":
                image = ax2.imshow(esperance-variance, cmap=plt.cm.YlGn, interpolation=interpolation)
                # image.set_clim([min_of_results, max_of_results])
                colorbar2.update_bruteforce(image)
            if label == "EV + VAR":
                image = ax2.imshow(esperance+variance, cmap=plt.cm.YlGn, interpolation=interpolation)
                # image.set_clim([min_of_results, max_of_results])
                colorbar2.update_bruteforce(image)
            plt.draw()


        esperance = sum(list_of_results)/len(list_of_results)

        variance = np.zeros((number_of_line, number_of_column))
        for i in range(number_of_line):
            for j in range(number_of_column):
                if j > i:
                    list_of_elem = []
                    for matrix in list_of_results:
                        list_of_elem.append(matrix[i, j])
                    print(list_of_elem)
                    variance[i, j] = statistics.stdev(list_of_elem)
        print(variance*100)

        fig = plt.figure()
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        fig.subplots_adjust(left=0.25, bottom=0.25)
        image1 = ax1.imshow(list_of_results[0], cmap=plt.cm.RdYlGn, interpolation=interpolation)
        image1.set_clim([min_of_results, max_of_results])

        image = ax2.imshow(esperance, cmap=plt.cm.RdYlGn, interpolation=interpolation)
        ax2.set_xlabel("Long Median")
        ax2.set_ylabel("Short Median")
        colorbar1 = fig.colorbar(image1, ax=ax1)
        colorbar2 = fig.colorbar(image, ax=ax2)

        alpha_axis = plt.axes([0.15, 0.12, 0.5, 0.05])
        alpha_slider = Slider(alpha_axis, 'First day', 0, 1, valinit=0)
        alpha_slider.on_changed((lambda val: update(ax1, val)))

        rax = plt.axes([0.75, 0.1, 0.2, 0.1])  # rect = [left, bottom, width, height]
        radio = RadioButtons(rax, ("variance", "expectation", "EV  - VAR", "EV + VAR"), active=1)
        radio.on_clicked(radiofunc)

        fig.subplots_adjust(left=0.1, bottom=0.25)
        plt.show(block=True)
        plt.show(block=True)

    if plot_type == "3D":

        def update(ax, val):
            index = min(int(val/val_max), len(list_of_results)-1)
            print(val, index)
            ax.cla()
            surf = ax.plot_surface(X, Y, list_of_results[index], rstride=1, cstride=1,
                                   cmap=plt.cm.RdYlGn, linewidth=0, antialiased=True)
            ax.set_zlim(min_of_results, max_of_results)
            surf.set_clim([min_of_results, max_of_results])
            # plt.draw()


        X = np.arange(0, number_of_line)
        Y = np.arange(0, number_of_column)
        X, Y = np.mgrid[0:number_of_line, 0:number_of_column]

        fig = plt.figure()
        ax1 = fig.add_subplot(111, projection='3d')
        fig.subplots_adjust(left=0.25, bottom=0.25)


        surf = ax1.plot_surface(X, Y, list_of_results[0], rstride=1, cstride=1,
                               cmap=plt.cm.RdYlGn, linewidth=0, antialiased=True)
        ax1.set_zlim(min_of_results, max_of_results)
        fig.colorbar(surf, shrink=0.7, aspect=10)

        surf.set_clim([min_of_results, max_of_results])
        alpha_axis = plt.axes([0.25, 0.15, 0.65, 0.03])
        alpha_slider = Slider(alpha_axis, 'First day', 0, 1, valinit=0)
        alpha_slider.on_changed((lambda val: update(ax1, val)))

        plt.show(block=True)

    if plot_type == "3D+":

        def update(ax, val):
            index = min(int(val/val_max), len(list_of_results)-1)
            # print(val, index)
            ax.cla()
            surf = ax.plot_surface(X, Y, list_of_results[index], rstride=1, cstride=1,
                                   cmap=plt.cm.RdYlGn, linewidth=0.2, antialiased=True)
            ax.set_zlim(min_of_results, max_of_results)
            surf.set_clim([min_of_results, max_of_results])
            # plt.draw()

        def radiofunc(label):
            if label == "variance":
                image = ax2.imshow(variance, cmap=plt.cm.YlGn, interpolation=interpolation)
                image.set_clim([0, variance.max()])
                colorbar2.update_bruteforce(image)
                # colorbar2 = fig.colorbar(image, ax=ax2)
            if label == "expectation":
                image = ax2.imshow(esperance, cmap=plt.cm.RdYlGn, interpolation=interpolation)
                # image.set_clim([min_of_results, max_of_results])
                colorbar2.update_bruteforce(image)
            if label == "EV  - VAR":
                image = ax2.imshow(esperance-variance, cmap=plt.cm.YlGn, interpolation=interpolation)
                # image.set_clim([min_of_results, max_of_results])
                colorbar2.update_bruteforce(image)
            if label == "EV + VAR":
                image = ax2.imshow(esperance+variance, cmap=plt.cm.YlGn, interpolation=interpolation)
                # image.set_clim([min_of_results, max_of_results])
                colorbar2.update_bruteforce(image)
            plt.draw()

        X = np.arange(0, number_of_line)
        Y = np.arange(0, number_of_column)
        X, Y = np.mgrid[0:number_of_line, 0:number_of_column]

        fig = plt.figure()
        ax1 = fig.add_subplot(121, projection='3d')
        ax2 = fig.add_subplot(122)

        esperance = sum(list_of_results)/len(list_of_results)

        variance = np.zeros((number_of_line, number_of_column))
        for i in range(number_of_line):
            for j in range(number_of_column):
                if j > i:
                    list_of_elem = []
                    for matrix in list_of_results:
                        list_of_elem.append(matrix[i, j])
                    print(list_of_elem)
                    variance[i, j] = statistics.stdev(list_of_elem)
        print(variance*100)



        surf = ax1.plot_surface(X, Y, list_of_results[0], rstride=1, cstride=1,
                                cmap=plt.cm.RdYlGn, linewidth=0.2, antialiased=True)
        surf.set_clim([min_of_results, max_of_results])
        ax1.set_zlim(min_of_results, max_of_results)

        image = ax2.imshow(esperance, cmap=plt.cm.RdYlGn, interpolation=interpolation)
        ax2.set_xlabel("Long Median")
        ax2.set_ylabel("Short Median")
        colorbar1 = fig.colorbar(surf, ax=ax1)
        colorbar2 = fig.colorbar(image, ax=ax2)

        alpha_axis = plt.axes([0.15, 0.12, 0.5, 0.05])
        alpha_slider = Slider(alpha_axis, 'First day', 0, 1, valinit=0)
        alpha_slider.on_changed((lambda val: update(ax1, val)))

        rax = plt.axes([0.75, 0.1, 0.2, 0.1])  # rect = [left, bottom, width, height]
        radio = RadioButtons(rax, ("variance", "expectation", "EV  - VAR", "EV + VAR"), active=1)
        radio.on_clicked(radiofunc)

        fig.subplots_adjust(left=0.1, bottom=0.25)
        plt.show(block=True)


if __name__ == "__main__":
    # An instance of Backtest is created
    theBacktest = Backtest()

    # Assets are added to the Backtest
    # DENTS = theBacktest.add_asset_from_csv("Data/uniformtest.csv", "propre", ";", "DENTS")
    # STUP = theBacktest.add_asset_from_csv("Data/stupidtest.csv", "propre", ";", "STUP")
    # BTCUSD = theBacktest.add_asset_from_csv("Data/BTCUSD_propre.csv", "propre", ";", "BTCUSD")
    # IBM = theBacktest.add_asset_from_csv("Data/ibm_propre.csv", "propre", ";", "IBM")
    # GS = theBacktest.add_asset_from_csv("Data/GS_yahoo.csv", "yahoo", ",", "GS")
    # IGE = theBacktest.add_asset_from_csv("Data/IGE_yahoo.csv", "yahoo", ",", "IGE")
    # SPY = theBacktest.add_asset_from_csv("Data/SPY_yahoo.csv", "yahoo", ",", "SPY")
    IBMyahoo = theBacktest.add_asset_from_csv("Data/IBM_1970_2010_yahoo.csv", "yahoo", ",", "IBM")

    # Strategies are created
    # randomStrategy = Strategy(theBacktest.market, "Random Srategy", cash=5000)
    # JMstrat = JMTendanceStrat(theBacktest.market, "StupidDetector", cash=15000)
    # firstDayStrat = FirstDayBuyEverythingStrategy(theBacktest.market, "BuyTheFirstDay", asset=IGE, cash=15000)
    # JMstratTest = JMTestStrat(theBacktest.market, "TestStrat", cash=5000)

    # Experts are created
    # absurdExpert = Expert(theBacktest.market, "AbsurdExpert")
    # TendanceExpert = JMTendanceExpert(theBacktest.market, "TendanceExpert")
    # MobileExpert = JMMobileExpert(theBacktest.market, "MobileExpert", longMedian=20, shortMedian=10)

    beginning_time = clock()  # for time execution measurement
    number_of_line = 5  # short median
    number_of_column = 5  # long median

    # matrix_of_results = test_the_mobile_expert(number_of_line, number_of_column, 0, 1000)

    windows_duration = 1000
    length_of_the_asset = 5000
    list_of_results = super_test_the_mobile_expert(number_of_line, number_of_column,
                                                   windows_duration, length_of_the_asset,
                                                   windows_offset=1000, print_time=True)

    # for i in range(len(list_of_results)):
    #     plot_the_mobile_expert(number_of_line, number_of_column, list_of_results[i], plot_type="3D")
    print("len list", len(list_of_results))
    plot_several_matrix(number_of_line, number_of_column, list_of_results, plot_type="2D+", interpolation="nearest")



    # We plot the assets used
    # theBacktest.market.plot_market()

    # theBacktest.simule(first_day=50, last_day=100, string_mode=True)
    # MobileExpert.plot_medians()

    # print("open:", JMstratTest.portfolio.openPositionList)
    # print(JMstratTest.portfolio.valueHistory)
    # print(JMstratTest.portfolio.closePositionList[0].valueHistory)
    # print("close", JMstratTest.portfolio.closePositionList)

    # # Useful syntax
    # l = [0, 1, 2, -3]
    # print(l)
    # print([-rt for rt in l])
    # print(l*(-1)) # do not work


    ############################################
    # beginning_time = clock()  # for time execution measurement
    # liste_of_line = []
    # empty_column = [0]*number_of_column
    # for i in range(number_of_line):
    #     liste_of_line.append([0]*number_of_column)
    # # liste_of_line = [empty_column]*number_of_line
    # matrice = np.zeros((number_of_line, number_of_column))
    # for i in range(number_of_line):
    #     for j in range(number_of_column):
    #         if j > i:
    #             # print(i, j)
    #             liste_of_line[i][j] = JMMobileExpert(theBacktest.market,
    #                                                  "MobileExpert", longMedian=j+1, shortMedian=i+1)
    #
    # # for liste in liste_of_line:
    # #     print(liste)
    # theBacktest.simule(500, string_mode=False)
    # for i in range(number_of_line):
    #     for j in range(number_of_column):
    #         if j > i:
    #             matrice[i, j] = liste_of_line[i][j].results_description()[4]  # line i, column j
    #         else:
    #             matrice[i, j] = 0
    # # # print(matrice)
    #
    # print((clock() - beginning_time), "s")
    # plt.imshow(matrice, cmap=plt.cm.RdYlGn, interpolation="nearest")
    # plt.colorbar()
    # plt.show()