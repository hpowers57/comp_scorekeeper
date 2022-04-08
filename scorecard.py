"""
Comp Scorekeeper by Hannah Powers and Mercedez Young
Last updated: 4/6/2022 at 9:15pm
"""

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
        if jlist:
            for j in jlist:
                self.judges.append(j)
                self.callbackcards[j] = CallbackCard(j)

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
        self.overall = None

    def remove_callbacks(self, judge):
        if judge in self.judges:
            self.judges.remove(judge)
            self.callbackcards.pop(judge)
            self.overall = None
        print(self.judges)
        print(self.callbackcards)
        print(self.overall)

    def total_callbacks(self):
        """
        Updates callbacks per couple from judges callbacks cards
        """
        if len(self.judges) > 0:
            self.overall = dict()
            for j in self.judges:
                tmp = self.callbackcards[j].callbacks
                for num in tmp:
                    if num in self.overall.keys():
                        self.overall[num].append(j)
                    else:
                        self.overall[num] = [j]

    def return_callbacks(self):
        if self.overall is None:
            self.total_callbacks()
        if self.overall is None:
            return None
        return sorted(self.overall.items(), key=lambda x: (len(x[1]), x[0]), reverse=True), self.judges

    def clear(self):
        self.judges.clear()
        self.callbackcards.clear()
        self.overall = None


class CallbackCard:
    def __init__(self, no):
        """
        Labels scorecard with judge's id info and heatlist

        :param no: judge number
        :param heatlist: list of competing couples
        """
        self.judge_no = no
        self.callbacks = None

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
        self.callbacks = set(cblist)


class Places:
    def __init__(self, jlist=None, hlist=None):
        """
        Creates Places class instance

        :param jlist: list of judges
        :param hlist: list of couples
        """
        self.judges = list()
        self.placingcards = dict()
        self.overall = None
        self.heatlist = set()
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
        if len(self.heatlist.union(pdict.keys())) > 8:
            return False
        if judge not in self.judges:
            self.judges.append(judge)
            self.placingcards[judge] = PlacingCard(judge)
        self.placingcards[judge].add_places(pdict)
        self.overall = None
        self.heatlist = self.heatlist.union(pdict.keys())
        return True

    def remove_places(self, judge):
        if judge in self.judges:
            self.judges.remove(judge)
            self.placingcards.pop(judge)
            self.overall = None

        self.heatlist = set()
        for judge in self.judges:
            self.heatlist = self.heatlist.union(self.placingcards[judge].places.keys())

    # def OLD_calculate_places(self):
    #     """
    #     Updates dataframe of calculation table and couple's placement by judge and overall
    #     Satisfies Skating System rules
    #
    #     :return: True if dataframe could be updated, False otherwise
    #     """
    #     n = len(self.placingcards.keys())
    #     self.overall = None
    #     if n % 2 == 1 and n > 1:
    #         # Build dataframe
    #         place_cols = [[str(i) + "_", "1-" + str(i), "1-" + str(i) + "SUM"] for i in range(1, 11)]
    #         place_cols = [elmt for sublst in place_cols for elmt in sublst]
    #         columns = ["Couple"] + self.judges + place_cols + ["Place"]
    #         self.overall = pd.DataFrame(columns=columns, index=list(range(10)))
    #
    #         # Fill couples and judge placements
    #         heatlist = set()
    #         for j in self.judges:
    #             heatlist = heatlist.union(self.placingcards[j].places.keys())
    #         print(heatlist)
    #         self.overall["Couple"] = list(heatlist) + [np.NaN] * (10 - len(heatlist))
    #         for j in self.judges:
    #             idx = [couple in self.placingcards[j].places.keys() for couple in self.overall["Couple"]]
    #             self.overall.loc[idx, j] = [self.placingcards[j].places[couple] for couple in self.overall.loc[idx, "Couple"]]
    #
    #         # Fill calculation table
    #         tmp = self.overall[self.judges].apply(pd.Series.value_counts, axis=1)
    #         self.overall[[str(i) + "_" for i in range(1, tmp.shape[1] + 1)]] = tmp
    #         self.overall[place_cols] = self.overall[place_cols].fillna(0)
    #         self.overall["1-1"] = self.overall["1_"]
    #         self.overall["1-1SUM"] = self.overall["1_"]
    #         for i in range(2, 11):
    #             self.overall["1-" + str(i)] = self.overall["1-" + str(i - 1)] + self.overall[str(i) + "_"]
    #             self.overall["1-" + str(i) + "SUM"] = self.overall["1-" + str(i - 1) + "SUM"] + (self.overall[str(i) + "_"] * i)
    #
    #         # Decide placements
    #         # TODO: ask Matt if we should break ties after first attempt or just award
    #         i = 1
    #         while i < 11:
    #             idxna = pd.isna(self.overall["Place"])
    #             couples = self.overall.loc[idxna, "Couple"]
    #             idxp = (self.overall.loc[idxna, "1-" + str(i)] == max(self.overall.loc[idxna, "1-" + str(i)]))
    #             couples = couples.loc[idxp]
    #             if couples.shape[0] > 1:
    #                 idxs = self.overall.loc[idxna].loc[idxp, "1-" + str(i) + "SUM"] == min(
    #                     self.overall.loc[idxna].loc[idxp, "1-" + str(i) + "SUM"])
    #                 couples = couples.loc[idxs]
    #                 # for j in range(i + 1, 11):
    #                 #     idxtp = self.overall.loc[idxna].loc[idxp, "1-" + str(j)] == max(
    #                 #         self.overall.loc[idxna].loc[idxp, "1-" + str(j)])
    #                 #     tmp_couples = couples.loc[idxtp]
    #                 #     if tmp_couples.shape[0] <= 1:
    #                 #         couples = tmp_couples
    #                 #         break
    #                 #     idxts = self.overall.loc[idxna].loc[idxp, "1-" + str(j) + "SUM"] == min(
    #                 #         self.overall.loc[idxna].loc[idxp, "1-" + str(j) + "SUM"])
    #                 #     tmp_couples = couples.loc[idxts]
    #                 #     if tmp_couples.shape[0] <= 1:
    #                 #         couples = tmp_couples
    #                 #         break
    #             idxf = [couple in couples.values for couple in self.overall["Couple"]]
    #             n = np.count_nonzero(idxf)
    #             tmp = [i for _ in range(n)]
    #             self.overall.loc[idxf, "Place"] = tmp
    #             i += n if n > 0 else 1

    def calculate_places(self):
        """
        Updates dataframe of calculation table and couple's placement by judge and overall
        Satisfies Skating System rules

        :return: True if dataframe could be updated, False otherwise
        """
        n = len(self.placingcards.keys())
        majority = n // 2 + n % 2
        self.overall = None
        if n % 2 == 1 and n > 1:
            heatlist = set()
            for j in self.judges:
                heatlist = heatlist.union(self.placingcards[j].places.keys())

            # Build dataframe
            place_cols = [[str(i) + "_", "1-" + str(i), "1-" + str(i) + "SUM"] for i in range(1, len(heatlist) + 1)]
            place_cols = [elmt for sublst in place_cols for elmt in sublst]
            columns = ["Couple"] + self.judges + place_cols + ["Place"]
            self.overall = pd.DataFrame(columns=columns, index=list(range(len(heatlist))))

            # Fill couples and judge placements
            self.overall["Couple"] = list(heatlist)
            for j in self.judges:
                idx = [couple in self.placingcards[j].places.keys() for couple in self.overall["Couple"]]
                self.overall.loc[idx, j] = [self.placingcards[j].places[couple] for couple in self.overall.loc[idx, "Couple"]]

            # Fill calculation table
            tmp = self.overall[self.judges].apply(pd.Series.value_counts, axis=1)
            self.overall[[str(i) + "_" for i in range(1, tmp.shape[1] + 1)]] = tmp
            self.overall[place_cols] = self.overall[place_cols].fillna(0)
            self.overall["1-1"] = self.overall["1_"]
            self.overall["1-1SUM"] = self.overall["1_"]
            for i in range(2, len(heatlist) + 1):
                self.overall["1-" + str(i)] = self.overall["1-" + str(i - 1)] + self.overall[str(i) + "_"]
                self.overall["1-" + str(i) + "SUM"] = self.overall["1-" + str(i - 1) + "SUM"] + (self.overall[str(i) + "_"] * i)

            place = 1
            max_place = len(heatlist)
            col = 1
            while np.count_nonzero(pd.isna(self.overall["Place"])) > 0:
                # print(place, col, "\n", self.overall.loc[pd.isna(self.overall["Place"]) == True])
                couples = self.overall.loc[pd.isna(self.overall["Place"]) == True]
                couples = couples.loc[couples["1-" + str(col)] >= majority]
                if couples.shape[0] == 0:
                    # print("No majority for", col, "\n", self.overall["1-" + str(col)])
                    col += 1
                    continue
                sort_order = [["1-" + str(i), "1-" + str(i) + "SUM"] for i in range(col, max_place + 1)]
                sort_order = [elmt for sublst in sort_order for elmt in sublst]
                asc_order = ["SUM" in name for name in sort_order]
                couples = couples.sort_values(by=sort_order, ascending=asc_order)
                for c in couples["Couple"].values:
                    self.overall.loc[self.overall["Couple"] == c, "Place"] = str(place)
                    place += 1
                col = place


    def return_places(self):
        """
        Returns overall places for the judges' placements so far

        :return: dataframe with couples, calculation table, and placement by judge and overall
        """
        if self.overall is None:
            self.calculate_places()
        if self.overall is None:
            return None
        return self.overall.copy(), self.judges

    def clear(self):
        self.judges.clear()
        self.placingcards.clear()
        self.overall = None
        self.heatlist = set()


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

class MultiPlaces:
    def __init__(self):
        self.indiv_places = dict()
        self.dances = list()
        self.overall = None
        self.heatlist = set()

    def add_places(self, dance, places):
        if len(self.heatlist) > 0 and len(set(places.keys()).symmetric_difference(self.heatlist)) > 0:
            return False
        self.dances.append(dance)
        self.indiv_places[dance] = places
        if len(self.heatlist) == 0:
            self.heatlist = set(places.keys())
        self.overall = None
        return True

    def remove_places(self, dance):
        if dance in self.dances:
            self.dances.remove(dance)
            self.indiv_places.pop(dance)
            if len(self.indiv_places.keys()) == 0:
                self.heatlist = set()
            self.overall = None

    def clear(self):
        self.indiv_places.clear()
        self.dances.clear()
        self.heatlist = set()
        self.overall = None

    def calculate_places(self):
        if len(self.dances) > 0:
            n = len(self.heatlist)
            place_cols = [[str(i) + "_", "1-" + str(i) + "SUM", "1-" + str(i)] for i in range(1, n + 1)]
            place_cols = [elmt for sublst in place_cols for elmt in sublst]
            cols = ["Couple"] + self.dances + place_cols + ["Total", "Result"]
            self.overall = pd.DataFrame(index=range(n), columns=cols)
            self.overall["Couple"] = list(self.heatlist)
            for dance in self.dances:
                self.overall[dance] = [self.indiv_places[dance][couple] for couple in self.overall["Couple"].values]
            self.overall[[str(i) + "_" for i in range(1, n + 1)]] = self.overall[self.dances].apply(pd.Series.value_counts, axis=1)
            self.overall[place_cols] = self.overall[place_cols].fillna(0)
            self.overall["1-1"] = self.overall["1_"]
            self.overall["1-1SUM"] = self.overall["1_"] * 1
            for i in range(2, n + 1):
                self.overall["1-" + str(i)] = self.overall["1-" + str(i - 1)] + self.overall[str(i) + "_"]
                self.overall["1-" + str(i) + "SUM"] = self.overall["1-" + str(i - 1) + "SUM"] + self.overall[str(i) + "_"] * i
            self.overall["Total"] = self.overall[self.dances].sum(axis=1)

            self.overall = self.overall.sort_values(by="Total")
            place = 1
            while np.count_nonzero(pd.isna(self.overall["Result"])):
                couples = self.overall.loc[pd.isna(self.overall["Result"]) == True]
                couples = couples.loc[couples["Total"] == min(couples["Total"])]
                couples = couples.sort_values(by=["1-" + str(place), "1-" + str(place) + "SUM"], ascending=[False, True])
                match = couples.duplicated(subset=["1-" + str(place), "1-" + str(place) + "SUM"], keep=False)
                if match.iloc[0]:
                    for i in match.index:
                        if not match.loc[i]:
                            break
                        self.overall.loc[i, "Result"] = "R11"
                        place += 1
                else:
                    for c in couples["Couple"].values:
                        self.overall.loc[self.overall["Couple"] == c, "Result"] = str(place)
                        place += 1
                        break

    def return_places(self):
        """
        Returns overall places for the judges' placements so far

        :return: dataframe with couples, calculation table, and placement by judge and overall
        """
        if self.overall is None:
            self.calculate_places()
        if self.overall is None:
            return None
        return self.overall.copy(), self.dances


if __name__ == "__main__":
    # round = Callbacks()
    # j1 = ["100", "101", "112", "113", "114", "117"]
    # j2 = ["112", "113", "114", "117", "120", "135"]
    # j3 = ["100", "112", "117", "135", "141", "171"]
    # round.add_callbacks("10", j1)
    # round.add_callbacks("11", j2)
    # round.add_callbacks("12", j3)
    # print(round.return_callbacks())

    # places = {"100": 1, "101": 2, "112": 3, "113": 4, "114": 5, "117": 6, "120": 7, "135": 8}
    # places1 = {"100": 3, "101": 1, "112": 2, "113": 4, "114": 8, "117": 5, "120": 7, "135": 6}
    # places2 = {"100": 1, "101": 4, "112": 2, "113": 5, "114": 3, "117": 6, "120": 8, "135": 7}
    # p = {"10": places, "11": places1, "12": places2}
    # round = Places()
    # round.add_places("10", places)
    # round.add_places("11", places1)
    # round.add_places("12", places2)
    # tmp, judges = round.return_places()

    # round = Places()
    # round.add_places("10", {"10": 1, "20": 2, "30": 3, "40": 4, "50": 5, "60": 6})
    # round.add_places("11", {"20": 1, "10": 2, "40": 3, "30": 4, "60": 5, "50": 6})
    # round.add_places("12", {"30": 1, "20": 2, "10": 3, "60": 4, "50": 5, "40": 6})
    # round.add_places("13", {"60": 1, "50": 2, "40": 3, "30": 4, "20": 5, "10": 6})
    # round.add_places("14", {"30": 1, "10": 2, "20": 3, "60": 4, "40": 5, "50": 6})
    # print(round.return_places()[0].sort_values(by="Place"))

    round = MultiPlaces()
    # round.add_places("W", {"171": 1, "193": 2, "103": 3, "173": 4, "176": 6, "145": 5, "111": 7})
    # round.add_places("T", {"171": 2, "193": 1, "103": 3, "173": 4, "176": 5, "145": 6, "111": 7})
    # round.add_places("F", {"113": 1, "181": 2, "176": 5, "103": 4, "193": 3, "171": 6})
    # round.add_places("T", {"113": 1, "181": 3, "176": 2, "103": 4, "193": 5, "171": 6})
    round.add_places("W", {"171": 1, "193": 2, "176": 3, "103": 5, "145": 4, "173": 7, "178": 6})
    round.add_places("F", {"171": 1, "193": 2, "176": 4, "103": 3, "145": 6, "173": 5, "178": 7})
    round.calculate_places()
    print(round.overall)
