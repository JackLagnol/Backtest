def get_returns(data):
    """ Compute daily returns of an asset"""

    returns = []
    for i in range(1, len(data)):
        returns += [(data[i] - data[i - 1]) / data[i - 1]]
    return returns