class Callbacks:
    judges = list()
    heatlist = None
    callbackcards = dict()
    overall = dict()

    def __init__(self, jlist, hlist):
        self.heatlist = hlist
        for j in jlist:
            self.judges.append(j)
            self.callbackcards[j] = CallbackCard(j, self.heatlist)

        for num in self.heatlist:
            self.overall[num] = 0

    def add_callbacks(self, judge, cblist):
        self.callbackcards[judge].add_callbacks(cblist)

    def override_callbacks(self, judge, cblist):
        self.callbackcards[judge].override(cblist)

    def total_callbacks(self):
        for j in self.judges:
            tmp = self.callbackcards[j].callbacks
            for num in tmp.keys():
                if num in self.overall.keys():
                    self.overall[num] += int(tmp[num])
                else:
                    self.overall[num] = int(tmp[num])

    def return_callbacks(self):
        return sorted(self.overall.items(), key=lambda x: (x[1], x[0]), reverse=True)


class CallbackCard:
    judge_no = None
    callbacks = dict()

    def __init__(self, no, heatlist):
        """
        Labels scorecard with judge's id info and heatlist

        :param no: judge number
        :param heatlist: list of competing couples
        """
        self.judge_no = no
        for num in heatlist:
            self.callbacks[num] = False


    def add_callbacks(self, cblist):
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

    def override(self, cblist):
        """
        Adds callbacks by judge even if couples not in heatlist

        :param pdict: list of couple callbacks
        """
        for num in cblist:
            self.callbacks[num] = True


class PlacingCard:
    judge_no = None
    places = dict()

    def __init__(self, no, heatlist):
        """
        Labels scorecard with judge's id info and heatlist

        :param no: judge number
        :param heatlist: list of competing couples
        """
        self.judge_no = no
        for num in heatlist:
            self.places[num] = None

    def add_places(self, pdict):
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

    def override(self, pdict):
        """
        Adds placing by judge even if couples not in heatlist or already placed

        :param pdict: dict of places by couple
        """
        for num in pdict:
            self.places[num] = pdict[num]
