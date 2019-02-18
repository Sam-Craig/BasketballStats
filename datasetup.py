import numpy as np
import pandas as pd
import random as rd
from matplotlib import pyplot as plt


csvloc = "/Users/samcraig/PycharmProjects/BasketballRefScraper/bbstats/"

# 5 is blowout win for team 0, 0 is blowout win for team 1, and so on. For use in classification


def scoretoclassification(delta):
    if delta > 20:
        return 5
    elif delta > 10:
        return 4
    elif delta > 0:
        return 3
    elif delta > -10:
        return 2
    elif delta > -20:
        return 1
    else:
        return 0

def getnumgames(startdate, enddate):
    count = 0
    for i in range(startdate, enddate):
        games = pd.read_csv(csvloc + "games/{}-{}_games.csv".format(i, i+1))
        count += len(games.index)
    return count


def makedata(startdate, enddate):
    numgames = getnumgames(startdate, enddate)
    tempdata = np.zeros((numgames, 16, 9), dtype=np.float)
    templabels = np.zeros(numgames, dtype=np.uint)
    outerindex = 0
    for i in range(startdate, enddate):
        players = pd.read_csv(csvloc + "players/{}-{}_players.csv".format(i, i+1))
        games = pd.read_csv(csvloc + "games/{}-{}_games.csv".format(i, i+1))
        for game in games.itertuples(index=False, name=None):
            # the team with higher record is always listed first in bbref boxes scores, so we need to switch them at
            # random to account for that
            switched = rd.randrange(0,2)
            innerindex = 0
            if switched:

                templabels[outerindex] = scoretoclassification(game[3] - game[4])
                for player, minutes in zip(game[5:13], game[21:29]):
                    for i, stat in enumerate(players.loc[players["Name"] == player].squeeze().iloc[1:9]):
                        try:
                            tempdata[outerindex][innerindex][i] = stat
                        except ValueError:
                            print(game)
                            break
                    tempdata[outerindex][innerindex][8] = minutes
                    innerindex += 1
                for player, minutes in zip(game[13:21], game[29:37]):
                    for i, stat in enumerate(players.loc[players["Name"] == player].squeeze().iloc[1:9]):
                        try:
                            tempdata[outerindex][innerindex][i] = stat
                        except ValueError:
                            print(game)
                            break
                    tempdata[outerindex][innerindex][8] = minutes
                    innerindex += 1

            else:
                templabels[outerindex] = scoretoclassification(game[4] - game[3])
                for player, minutes in zip(game[13:21], game[29:37]):
                    for i, stat in enumerate(players.loc[players["Name"] == player].squeeze().iloc[1:9]):
                        try:
                            tempdata[outerindex][innerindex][i] = stat
                        except ValueError:
                            print(game)
                            break
                    tempdata[outerindex][innerindex][8] = minutes
                    innerindex += 1
                for player, minutes in zip(game[5:13], game[21:29]):
                    for i, stat in enumerate(players.loc[players["Name"] == player].squeeze().iloc[1:9]):
                        try:
                            tempdata[outerindex][innerindex][i] = stat
                        except ValueError:
                            print(game)
                            break
                    tempdata[outerindex][innerindex][8] = minutes
                    innerindex += 1

            outerindex += 1
    return np.array(tempdata), np.array(templabels)

#data is a numpy array of shape (x, 16, 9)
def scaledata(data, labels):
    max = np.zeros(9)
    cont = True
    i = 0
    for datum in data:
        for player in datum:
            for j in range(9):
                if player[j] > max[j]:
                    max[j] = player[j]

    for datum in data:
        for player in datum:
            for i in range(9):
                player[i]/=max[0]
    return data, labels


# takes a subset of data to be used for testing our neural network
def gettestdata(data, labels, percent):
    testdata = np.empty((0, 16,9))
    testlabels = np.array([])
    i = 0
    while True:
        try:
            if rd.random() < percent:
                testdata = np.append(testdata, np.array([data[i]]), axis = 0)
                data = np.delete(data, i, axis = 0)
                testlabels = np.append(testlabels, np.array([labels[i]]), axis = 0)
                labels = np.delete(labels, i, axis = 0)



            i+=1
        except IndexError:
            return data, labels, testdata, testlabels

data, labels = makedata(2007,2009)

data, labels = scaledata(data, labels)

data, labels, testdata, testlabels = gettestdata(data, labels, .05)

data.shape, labels.shape, testdata.shape, testlabels.shape