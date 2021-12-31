import numpy as np
import pandas as panda
from matplotlib import pyplot as plt

path = 'Data_for_analysis.xlsx'


def loadDataFromExcel(pathToExcel, numberRowWhereStart):
    df = panda.read_excel(pathToExcel, header=numberRowWhereStart)
    dataFun = df[['Action', 'Time to failure']].sort_values(by='Time to failure', ignore_index=True)
    return dataFun


def IntervalEndpoint(dataFun):
    dataLength = len(dataFun)
    columnMax = dataFun['Time to failure'].max()
    endPointFun = np.zeros(int(np.round(columnMax / 2000, 0) + 1))
    for i in range(1, dataLength):
        if endPointFun[i - 1] <= columnMax:
            endPointFun[i] = endPointFun[i - 1] + 2000
        else:
            break
    return endPointFun


def countNumberOfUnits(dataFun, endPointFun):
    dataLength = len(dataFun)
    endPointLength = len(endPointFun) - 1
    numberUnitsFun = np.zeros(endPointLength)
    numberUnitsFun[0] = dataLength
    j = 0
    tempValue = numberUnitsFun[0]
    for i in range(1, endPointLength):
        if dataFun['Time to failure'][j] <= endPointFun[i]:
            while dataFun['Time to failure'][j] <= endPointFun[i]:
                numberUnitsFun[i] = tempValue - 1
                tempValue = numberUnitsFun[i]
                j = j + 1
                if j == dataLength:
                    break
        else:
            numberUnitsFun[i] = numberUnitsFun[i - 1]
        tempValue = numberUnitsFun[i]
    return numberUnitsFun


def countNumberOfUnitsF(dataFun, endPointFun):
    dataLength = len(dataFun)
    endPointLength = len(endPointFun) - 1
    numberUnitsFFun = np.zeros(endPointLength)
    j = 0
    for i in range(endPointLength + 1):
        if dataFun['Time to failure'][j] <= endPointFun[i]:
            while dataFun['Time to failure'][j] <= endPointFun[i]:
                if dataFun['Action'][j] == 'F':
                    numberUnitsFFun[i - 1] = numberUnitsFFun[i - 1] + 1
                j = j + 1
                if j == dataLength:
                    break
    return numberUnitsFFun


def countNumberOfUnitsS(dataFun, endPointFun):
    dataLength = len(dataFun)
    endPointLength = len(endPointFun) - 1
    numberUnitsSFun = np.zeros(endPointLength)
    j = 0
    for i in range(endPointLength + 1):
        if dataFun['Time to failure'][j] <= endPointFun[i]:
            while dataFun['Time to failure'][j] <= endPointFun[i]:
                if dataFun['Action'][j] == 'S':
                    numberUnitsSFun[i - 1] = numberUnitsSFun[i - 1] + 1
                j = j + 1
                if j == dataLength:
                    break
    return numberUnitsSFun


# S(t) = S(previous t) * (1-d/(n-w/2)), e.g., S(2000) = S(0) * (1-0/(196-0/2)) = 1
def survival(endPointFun, numberUnitsSFun, numberUnitsFFun, numberUnitsFun):
    endPointFunLength = len(endPointFun)
    SFun = np.zeros(endPointFunLength)
    SFun[0] = 1
    for i in range(1, endPointFunLength):
        SFun[i] = SFun[i - 1] * (1 - numberUnitsFFun[i - 1] / (numberUnitsFun[i - 1] - numberUnitsSFun[i - 1] / 2))
    return SFun


def IntervalMidpoint(endPointFun):
    endPointFunLength = len(endPointFun)
    midPointFun = np.zeros(endPointFunLength - 1)
    for i in range(endPointFunLength - 1):
        midPointFun[i] = (endPointFun[i] + endPointFun[i + 1]) / 2
    return midPointFun


# h( tmid ) = S * d / ((n - 0.5 * w) * width),
def hazard(SFun, numberUnitsSFun, numberUnitsFFun, numberUnitsFun, endPointFun, midPointFun):
    midPointFunLength = len(midPointFun)
    hazardFun = np.zeros(len(endPointFun))
    print("podaj oczekiwany czas: ")
    width = int(input())
    hazardFun[0] = SFun[0] * numberUnitsFFun[0] / ((numberUnitsFun[0] - 0.5 * numberUnitsSFun[0]) * endPointFun[1])
    for i in range(1, midPointFunLength):
        hazardFun[i] = SFun[i + 1] * numberUnitsFFun[i] / (
                (numberUnitsFun[i] - 0.5 * numberUnitsSFun[i]) * width)

    hazardFun[len(endPointFun) - 1] = None
    return hazardFun


def makePlots(hazardFun, SFun, endPointFun):
    plt.figure()
    plt.plot(endPointFun, hazardFun)
    plt.xlabel("Days elapsed")
    plt.ylabel("Hazard Function")
    plt.xlim([0, 20000])
    plt.ylim([0, 4 * pow(10, -5)])

    plt.figure()
    plt.plot(endPointFun, SFun)
    plt.xlabel("Days elapsed")
    plt.ylabel("Survival Distribution Function")
    plt.xlim([0, 20000])
    plt.ylim([0, 1.1])

    plt.show()


if __name__ == '__main__':
    data = loadDataFromExcel(path, 2)
    endPoint = IntervalEndpoint(data)
    numberUnits = countNumberOfUnits(data, endPoint)
    numberUnitsS = countNumberOfUnitsS(data, endPoint)
    numberUnitsF = countNumberOfUnitsF(data, endPoint)
    S = survival(endPoint, numberUnitsS, numberUnitsF, numberUnits)
    midPoint = IntervalMidpoint(endPoint)
    H = hazard(S, numberUnitsS, numberUnitsF, numberUnits, endPoint, midPoint)
    makePlots(H, S, endPoint)
