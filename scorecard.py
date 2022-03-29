import numpy as np
import pandas as pd

class Callbacks:
    def __init__(self, jlist=None, hlist=None):
        """
        Creates instance of Callbacks class

        :param jlist: list of judges
        :param hlist: list of couples
        """
        self.judges = list()
        self.heatlist = set(hlist) if hlist else set()
        self.callbackcards = dict()
        self.overall = None
        self.current = True
        if jlist:
            for j in jlist:
                self.judges.append(j)
                self.callbackcards[j] = CallbackCard(j, hlist)

    def add_callbacks(self, judge, cblist):
        """
        Adds judge to list of judges and creates CallbackCard for them and adds callbacks to it

        :param judge: string of judge number
        :param pdict: list of couples with callbacks
        """
        if judge not in self.judges:
            self.judges.append(judge)
            self.callbackcards[judge] = CallbackCard(judge)
        self.heatlist = self.heatlist.union(cblist)
        self.callbackcards[judge].add_callbacks(cblist)
        self.current = False

    def total_callbacks(self):
        """
        Updates callbacks per couple from judges callbacks cards
        """
        self.overall = dict()
        for j in self.judges:
            tmp = self.callbackcards[j].callbacks
            for num in tmp.keys():
                if num in self.overall.keys():
                    self.overall[num] += int(tmp[num])
                else:
                    self.overall[num] = int(tmp[num])
        self.current = True

    def return_callbacks(self):
        if not self.current or not self.overall:
            self.total_callbacks()
        return sorted(self.overall.items(), key=lambda x: (x[1], x[0]), reverse=True)


class CallbackCard:
    def __init__(self, no, heatlist=None):
        """
        Labels scorecard with judge's id info and heatlist

        :param no: judge number
        :param heatlist: list of competing couples
        """
        self.judge_no = no
        self.callbacks = dict()
        for num in heatlist:
            self.callbacks[num] = False


    def OLD_add_callbacks(self, cblist):
        """
        Adds callbacks by judge to predefined heatlist

        :param pdict: list of couple callbacks
        :return: list of couples that weren't in heatlist
        """
        dne = list()
        for num in cblist:
            if num in self.callbacks.keys():
                self.callbacks[num] = True
            else:
                dne.append(num)

        return dne

    def add_callbacks(self, cblist):
        """
        Adds callbacks by judge even if couples not in heatlist

        :param pdict: list of couple callbacks
        """
        for num in cblist:
            self.callbacks[num] = True


class Places:
    def __init__(self, jlist=None, hlist=None):
        """
        Creates Places class instance

        :param jlist: list of judges
        :param hlist: list of couples
        """
        self.judges = list()
        self.heatlist = set(hlist) if hlist else set()
        self.placingcards = dict()
        self.overall = None
        self.current = True
        if jlist:
            for j in jlist:
                self.judges.append(j)
                self.placingcards[j] = PlacingCard(j, hlist)

    def add_places(self, judge, pdict):
        """
        Adds judge to list of judges and creates PlacingCard for them and adds places to it

        :param judge: string of judge number
        :param pdict: dict of placement by couple
        """
        if judge not in self.judges:
            self.judges.append(judge)
            self.placingcards[judge] = PlacingCard(judge)
        self.heatlist = self.heatlist.union(pdict.keys())
        self.placingcards[judge].add_places(pdict)
        self.current = False

    def calculate_places(self):
        """
        Updates dataframe of calculation table and couple's placement by judge and overall
        Satisfies Skating System rules

        :return: True if dataframe could be updated, False otherwise
        """
        n = len(self.placingcards.keys())
        if n % 2 == 1 and n > 1:
            # Build dataframe
            place_cols = [[str(i) + "_", "1-" + str(i), "1-" + str(i) + "SUM"] for i in range(1, 11)]
            place_cols = [elmt for sublst in place_cols for elmt in sublst]
            columns = ["Couple"] + self.judges + place_cols + ["Place"]
            self.overall = pd.DataFrame(columns=columns, index=list(range(10)))

            # Fill couples and judge placements
            self.overall["Couple"] = list(self.heatlist) + [np.NaN] * (10 - len(self.heatlist))
            for j in self.judges:
                idx = [couple in self.placingcards[j].places.keys() for couple in self.overall["Couple"]]
                self.overall.loc[idx, j] = [self.placingcards[j].places[couple] for couple in self.overall.loc[idx, "Couple"]]

            # Fill calculation table
            tmp = self.overall[self.judges].apply(pd.Series.value_counts, axis=1)
            self.overall[[str(i) + "_" for i in range(1, tmp.shape[1] + 1)]] = tmp
            self.overall[place_cols] = self.overall[place_cols].fillna(0)
            self.overall["1-1"] = self.overall["1_"]
            self.overall["1-1SUM"] = self.overall["1_"]
            for i in range(2, 11):
                self.overall["1-" + str(i)] = self.overall["1-" + str(i - 1)] + self.overall[str(i) + "_"]
                self.overall["1-" + str(i) + "SUM"] = self.overall["1-" + str(i - 1) + "SUM"] + (self.overall[str(i) + "_"] * i)

            # Decide placements
            for i in range(1, 11):
                idxna = pd.isna(self.overall["Place"])
                couples = self.overall.loc[idxna, "Couple"]
                idxp = (self.overall.loc[idxna, "1-" + str(i)] == max(self.overall.loc[idxna, "1-" + str(i)]))
                couples = couples.loc[idxp]
                if couples.shape[0] > 1:
                    idxs = self.overall.loc[idxna].loc[idxp, "1-" + str(i) + "SUM"] == min(
                        self.overall.loc[idxna].loc[idxp, "1-" + str(i) + "SUM"])
                    couples = couples.loc[idxs]
                idxf = [couple in couples.values for couple in self.overall["Couple"]]
                tmp = [i for j in range(np.count_nonzero(couples.shape[0]))]
                self.overall.loc[idxf, "Place"] = tmp
        else:
            return False

        self.current = True
        return True

    def return_places(self):
        """
        Returns overall places for the judges' placements so far

        :return: dataframe with couples, calculation table, and placement by judge and overall
        """
        if not self.current or not self.overall:
            self.calculate_places()
        return self.overall.copy()


class PlacingCard:
    def __init__(self, no, heatlist=None):
        """
        Labels scorecard with judge's id info and heatlist

        :param no: judge number
        :param heatlist: list of competing couples
        """
        self.judge_no = no
        self.places = dict()
        if heatlist:
            for num in heatlist:
                self.places[num] = None

    def OLD_add_places(self, pdict):
        """
        Adds placing by judge to predefined heatlist

        :param pdict: dict of places by couple
        :return: list of couples that weren't in heatlist and list of couples who were already given another place
        """
        dne = list()
        replaced = list()
        for num in pdict:
            if num in self.places.keys():
                if self.places[num] is not None and self.places[num] != pdict[num]:
                    replaced.append((num, self.places[num], pdict[num]))
                else:
                    self.places[num] = pdict[num]
            else:
                dne.append((num, pdict[num]))

        return dne, replaced

    def add_places(self, pdict):
        """
        Adds placing by judge even if couples not in heatlist or already placed

        :param pdict: dict of places by couple
        """
        for num in pdict.keys():
            self.places[num] = pdict[num]


if __name__ == "__main__":
    places = {"100": 1, "101": 2, "112": 3, "113": 4, "114": 5, "117": 6, "120": 7, "135": 8}
    places1 = {"100": 3, "101": 1, "112": 2, "113": 4, "114": 8, "117": 5, "120": 7, "135": 6}
    places2 = {"100": 1, "101": 4, "112": 2, "113": 5, "114": 3, "117": 6, "120": 8, "135": 7}
    p = {"10": places, "11": places1, "12": places2}
    round = Places()
    round.add_places("10", places)
    round.add_places("11", places1)
    round.add_places("12", places2)
    print(round.return_places().sort_values(by="10"))
