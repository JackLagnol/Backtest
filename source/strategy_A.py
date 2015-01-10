from source.Backtest import *


class JMTestStrat(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_day(self):
        for the_asset in self.market.assetList:
            data = self.market.get_asset_data(the_asset)
            if len(data) > 2:
                if data[-1] > data[-2] > data[-3]:
                    self.market.open(self.portfolio, the_asset, 0.5)
                elif data[-1] < data[-2] < data[-3]:
                    self.market.open(self.portfolio, the_asset, -0.5)

if __name__ == "__main__":
    pass