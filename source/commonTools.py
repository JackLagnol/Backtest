import statistics
import math
import numpy as np

def get_returns(data):
    """ Compute daily returns of an asset"""

    returns = []
    for i in range(1, len(data)):
        returns += [(data[i] - data[i - 1]) / data[i - 1]]
    return returns


###############################
# copy past of G's version    #
###############################


def compute_returns(data):
    """ Compute daily returns of an asset"""

    returns = []
    for i in range(1, len(data)):
        returns += [(data[i] - data[i - 1]) / data[i - 1]]
    return returns

def compute_sharpe(returns, risk_free):
    """ Compute annualized Sharpe Ratio based on daily returns (252 trading days / year)"""

    adj_returns = []
    for i in range(len(returns)):
        adj_returns += [returns[i] - (risk_free / 252)]
    if statistics.stdev(adj_returns) == 0:
        return 0
    sharpe = math.sqrt(252) * statistics.mean(adj_returns) / statistics.stdev(adj_returns)
    return sharpe

def correlation(data1, data2, start, time_frame, time_shift):
    """ Compute  correlation coefficient between 2 sets of data
        data1 (list): first set of data
        data2 (list): second set of data
        start (int): start date data1
        time_frame (int): time frame considered
        time_shift (int): shift between data1 and data2
    """
    return np.corrcoef(data1[start:start+time_frame],data2[(start+time_shift):(start+time_frame+time_shift)])[0][1]

def moving_average(data, time_frame):
    """ Compute moving average of a set of data
    data (list): set of data
    time_frame (int) : time frame of moving average
    """

    data_adj  = data[(len(data)-time_frame):len(data)]
    return statistics.mean(data_adj)

def SMA(data,l,p1,p2):
        Data = data

        MA=[]

        MA[p1]=[]

        for j in range(1,p1+1):
            a+=Data[j]

        MA[p1][p1]=a/p1

        for i in range(1,l-p1-1):
            a=MA[p1][p1+i]*p1+Data[p1+i+1]-Data[i-1]
            MA[p1][p1+i]=a/p1

        for p in range(p1,p2):
            for i in range(1,l-p-1):
                MA[p+1][p+i]=(MA[p][p+i]*p+Data[p+i+1])/(p+1)