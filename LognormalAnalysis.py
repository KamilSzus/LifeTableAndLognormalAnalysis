import numpy as np
import pandas as panda
from matplotlib import pyplot as plt
from scipy.stats import norm

path = 'Data_for_analysis.xlsx'


def loadDataFromExcel(pathToExcel, numberRowWhereStart):
    df = panda.read_excel(pathToExcel, header=numberRowWhereStart)
    dataFun = df[['Action', 'Time to failure']].sort_values(by='Time to failure', ignore_index=True)

    return dataFun


def reverseRank(dataFun):
    dataLength = len(dataFun)
    SFun = np.zeros(dataLength)
    SFun[0] = dataLength / (dataLength + 1)
    indexPreviousValue = 0
    for i in range(dataLength):
        if i != 0 and dataFun['Action'][i] == 'F':
            rank = dataLength - i + 1
            SFun[i] = SFun[indexPreviousValue] * rank / (rank + 1)
            indexPreviousValue = i

    return SFun


def InverseNormal(dataFun, SFun):
    dataLength = len(dataFun)
    InvNormalFun = np.zeros(dataLength)
    for i in range(dataLength):
        if dataFun['Action'][i] == 'F':
            InvNormalFun[i] = norm.ppf(1 - SFun[i])

    return InvNormalFun


def logTime(dataFun):
    dataLength = len(dataFun)
    logTimeFun = np.zeros(dataLength)
    for i in range(dataLength):
        if dataFun['Action'][i] == 'F':
            logTimeFun[i] = np.log(dataFun['Time to failure'][i])

    return logTimeFun


def leastSquareMethod(logTimeFun, InvNormalFun, logTimeLengthFun):
    logTimeFunSqr = logTimeFun ** 2
    xy = logTimeFun * InvNormalFun
    sumLogTimeFun = np.sum(logTimeFun)
    sumInvNormalFun = np.sum(InvNormalFun)
    sumLogTimeFunSqr = np.sum(logTimeFunSqr)
    sum_xy = np.sum(xy)

    a = (logTimeLengthFun * sum_xy - sumLogTimeFun * sumInvNormalFun) / (
                logTimeLengthFun * sumLogTimeFunSqr - sumLogTimeFun ** 2)
    b = (sumInvNormalFun - a * sumLogTimeFun) / logTimeLengthFun
    return a, b


def filterData(InvNormalFun, logTimeFun):
    logTimeFun[logTimeFun == 0] = np.nan
    InvNormalFun[InvNormalFun == 0] = np.nan
    logTimeFun = logTimeFun[~np.isnan(logTimeFun)]
    InvNormalFun = InvNormalFun[~np.isnan(InvNormalFun)]
    return InvNormalFun, logTimeFun


def makePlot(logTimeFun, InvNormalFun):
    InvNormalFun, logTimeFun = filterData(InvNormalFun, logTimeFun)
    a, b = leastSquareMethod(logTimeFun, InvNormalFun, len(logTimeFun))
    y = a * logTimeFun + b
    _, plot = plt.subplots()
    plot.set_xlabel("Log time")
    plot.set_ylabel("Probit(1 - Surv)")
    plot.plot(logTimeFun, InvNormalFun, marker='o', mec='black', c='r')
    subPlot = plot.twinx()
    subPlot.plot(logTimeFun, y)
    plt.show()


if __name__ == '__main__':
    data = loadDataFromExcel(path, 2)
    S = reverseRank(data)
    InvNormal = InverseNormal(data, S)
    logTime = logTime(data)
    makePlot(logTime, InvNormal)
