from bs4 import BeautifulSoup
import requests
from datetime import date, timedelta
import csv

baseurl = "https://www.basketball-reference.com"
csvlocplayers = "/Users/samcraig/PycharmProjects/BasketballRefScraper/bbstats/players/"
csvlocgames = "/Users/samcraig/PycharmProjects/BasketballRefScraper/bbstats/games/"


def loadplayerstocsv(startdate, enddate):
    url = baseurl + "/leagues/NBA_{}_per_minute.html".format(enddate.year)
    with open(csvlocplayers + "{}-{}_players.csv".format(startdate.year, enddate.year), "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(["Name", "mp", "pp36", "ap36", "rp36", "2pmp36", "2pap36", "3pmp36", "3pap36"])
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')
        allplayers = soup.find("table", {"id": "per_minute_stats"}).find("tbody").find_all("tr")
        prevplayer = ""
        # Array of floats
        row = []
        # indexdict[i] is the location of the (i)th statistic in the header inside the
        indexdict = {1: 6, 2: 27, 3: 22, 4: 21, 5: 13, 6: 14, 7: 10, 8: 11}
        for player in allplayers:
            if player["class"] == ["italic_text", "partial_table"] or player["class"] == ["full_table"]:
                name = player.find_all("td")[0]["data-append-csv"]
                if name == prevplayer:
                    minutes = float(player.find_all("td")[indexdict[1]].getText())
                    for i in range(2, 9):
                        # For players who have played with mutliple teams, we find the weighted average of their stats with each team
                        try:
                            row[i] = (row[1] * row[i] + float(
                                player.find_all("td")[indexdict[i]].getText()) * minutes) / (row[1] + minutes)
                        except ValueError:
                            print(name, enddate)

                    row[1] += minutes
                else:
                    if not (row == [] or row[1] < 50):
                        csvwriter.writerow(row)
                    row = [name]
                    for i in range(1,9):
                        try:
                            row.append(float(player.find_all("td")[indexdict[i]].getText()))
                        except ValueError:
                            print(name, enddate)
                prevplayer = name
        csvwriter.writerow(row)

        soup.decompose()


def loadgamestocsv(startdate, enddate):
    with open(csvlocgames + "{}-{}_games.csv".format(startdate.year, enddate.year), "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # T0P0 is the 0th player on Team0, T0M0 is the minutes played by the 0th player on Team0
        csvwriter.writerow(
            ["Date", "Team0", "Team1", "Score0", "Score1", "T0P0", "T0P1", "T0P2", "T0P3", "T0P4", "T0P5", "T0P6"
                , "T0P7", "T1P0", "T1P1", "T1P2", "T1P3", "T1P4", "T1P5", "T1P6", "T1P7", "T0M0", "T0M1"
                , "T0M2", "T0M3", "T0M4", "T0M5", "T0M6", "T0M7", "T1M0", "T1M1", "T1M2", "T1M3", "T1M4", "T1M5",
             "T1M6", "T1M7"])
        basedate = baseurl + "/boxscores/?month={0}&day={1}&year={2}"
        curday = startdate
        nextday = timedelta(1)
        while enddate >= curday:
            print(curday)
            finddailyboxes(basedate.format(curday.month, curday.day, curday.year), curday, csvwriter)
            curday = curday + nextday

    print("CSV loaded")


def finddailyboxes(url, date, csvwriter):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    gameslist = soup.find(class_="game_summaries")
    if gameslist is None:
        return
    gameslist = gameslist.find_all(class_='game_summary expanded nohover')

    boxes = []

    for games in gameslist:
        boxes.append(baseurl + games.find(class_="links").find_all("a")[0]["href"])

    soup.decompose()

    for box in boxes:
        row = [date.strftime('%Y/%m/%d')]
        soup = BeautifulSoup(requests.get(box).text, 'html.parser')
        teams = soup.find(class_="scorebox").find_all('strong')
        # finds the teams names
        row.append(teams[0].find("a")["href"][7:10].lower())
        row.append(teams[1].find("a")["href"][7:10].lower())
        # finds the scores
        row.append(soup.find("table", {"id": "box_{}_basic".format(row[1])}).find("tfoot").find_all("td", {
            "data-stat": "pts"})[0].getText())
        row.append(soup.find("table", {"id": "box_{}_basic".format(row[2])}).find("tfoot").find_all("td", {
            "data-stat": "pts"})[0].getText())
        # finds the players and minutes
        t0 = soup.find("table", {"id": "box_{}_basic".format(row[1])}).find("tbody").find_all("th", {"class": "left"})
        t1 = soup.find("table", {"id": "box_{}_basic".format(row[2])}).find("tbody").find_all("th", {"class": "left"})
        m0 = soup.find("table", {"id": "box_{}_basic".format(row[1])}).find("tbody").find_all("td", {"data-stat": "mp"})
        m1 = soup.find("table", {"id": "box_{}_basic".format(row[2])}).find("tbody").find_all("td", {"data-stat": "mp"})
        # sorts players by minutes played
        temp0 = [(t["data-append-csv"], m["csk"]) for t, m, e in zip(t0, m0, range(8))]
        temp1 = [(t["data-append-csv"], m["csk"]) for t, m, e in zip(t1, m1, range(8))]
        temp0.sort(key=lambda x: int(x[1]), reverse=True)
        temp1.sort(key=lambda x: int(x[1]), reverse=True)
        row += [t[0] for t in temp0] + [t[0] for t in temp1] + [t[1] for t in temp0] + [t[1] for t in temp1]
        csvwriter.writerow(row)
        soup.decompose()


dates = [
        (date(2004, 11, 2 ), date(2005, 4, 20)),
        (date(2003, 10, 28), date(2004, 4, 14)),
        (date(2002, 10, 29), date(2003, 4, 16)),
        (date(2001, 10, 30), date(2002, 4, 17)),
        (date(2000, 10, 31), date(2001, 4, 18))
         ]


loadplayerstocsv(date(2017, 10, 17), date(2018, 4, 11))


# 2017-2018 dates: 17-10-2017 11-4-2018
# 2016-2017 dates: 25-10-2016 12-4-2017
# 2015-2016 dates: 27-10-2015 13-4-2016
# 2014-2015 dates: 28-10-2014 15-4-2015
'''(date(2016, 10, 25), date(2017, 4, 12)),
         (date(2015, 10, 27), date(2016, 4, 13)),
         (date(2014, 10, 28), date(2015, 4, 15)),
         (date(2013, 10, 29), date(2014, 4, 16)),
         (date(2012, 10, 30), date(2013, 4, 17)),
         (date(2011, 12, 25), date(2012, 4, 26)), # lockout season
         (date(2010, 10, 26), date(2011, 4, 13)),
         (date(2009, 10, 27), date(2010, 4, 14)),
         (date(2008, 10, 25), date(2009, 4, 16)),
         (date(2007, 10, 30), date(2008, 4, 16)),'''