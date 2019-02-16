import numpy as np
import pandas as pd
import random as rd

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
    tempdata = np.zeros((numgames, 16, 9), object)
    templabels = np.zeros(numgames, int)
    outerindex = 0
    for i in range(startdate, enddate):
        print(i)
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
                    tempdata[outerindex][innerindex] = np.append(players.loc[players["Name"] == player].squeeze().iloc[1:9].to_numpy(), minutes)
                    innerindex += 1
                for player, minutes in zip(game[13:21], game[29:37]):
                    tempdata[outerindex][innerindex] = np.append(players.loc[players["Name"] == player].squeeze().iloc[1:9].to_numpy(), minutes)
                    innerindex += 1

            else:
                templabels[outerindex] = scoretoclassification(game[4] - game[3])
                for player, minutes in zip(game[13:21], game[29:37]):
                    tempdata[outerindex][innerindex] = np.append(players.loc[players["Name"] == player].squeeze().iloc[1:9].to_numpy(), minutes)
                    innerindex += 1
                for player, minutes in zip(game[5:13], game[21:29]):
                    tempdata[outerindex][innerindex] = np.append(players.loc[players["Name"] == player].squeeze().iloc[1:9].to_numpy(), minutes)
                    innerindex += 1

            outerindex += 1
        print(tempdata.shape)
    return np.array(tempdata), np.array(templabels)

print(makedata(2005,2018))