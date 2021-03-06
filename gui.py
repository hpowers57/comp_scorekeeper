"""
Comp Scorekeeper by Hannah Powers and Mercedez Young
Last updated: 4/6/2022 at 9:15pm
"""

import os.path
import sys
import traceback

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from time import time
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore, QtGui
from scorecard import *
import json


class multiDancePlacing(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.placements_list = dict()
        self.overall = MultiPlaces()
        self.windows = list()

        layoutRight = QVBoxLayout()
        instr = QLabel()
        instr.setText("Add some placements and an event number!")
        event = QHBoxLayout()
        event_no_label = QLabel()
        event_no_label.setText("Event number:")
        self.event_no = QSpinBox()
        self.event_no.setValue(0)
        self.event_no.setRange(0, 500)
        self.event_no.setFixedWidth(100)
        event.addWidget(event_no_label)
        event.addWidget(self.event_no)
        calculate = QPushButton("Calculate")
        calculate.clicked.connect(self.calculatePlacements)
        cancel = QPushButton("Cancel")
        cancel.setFixedWidth(100)
        cancel.clicked.connect(self.close)
        # save = QPushButton("Save round")
        # save.clicked.connect(self.savePlacements)
        miniLayout1 = QHBoxLayout()
        miniLayout1.addWidget(cancel)
        miniLayout1.addWidget(calculate)
        layoutRight.addWidget(instr)
        layoutRight.addLayout(event)
        layoutRight.addWidget(QLabel())
        layoutRight.addLayout(miniLayout1)

        layoutLeft = QVBoxLayout()
        add = QPushButton("Add placements")
        add.clicked.connect(self.addPlacements)
        clear = QPushButton("Clear")
        clear.clicked.connect(self.clearPlacements)
        delete = QPushButton("Delete")
        delete.clicked.connect(self.deletePlacement)
        miniLayout = QHBoxLayout()
        miniLayout.addWidget(clear)
        miniLayout.addWidget(delete)
        self.placements = QListWidget()
        self.placements.itemDoubleClicked.connect(self.reopenPlacement)
        layoutLeft.addWidget(add)
        layoutLeft.addWidget(self.placements)
        layoutLeft.addLayout(miniLayout)

        layout = QHBoxLayout()
        layout.addLayout(layoutLeft)
        layout.addLayout(layoutRight)
        self.setLayout(layout)
        self.setWindowTitle("Comp Scorekeeper")
        self.setMinimumSize(500, 500)

    def calculatePlacements(self):
        scores = self.overall.return_places()
        if scores is None:
            alert = QMessageBox()
            alert.setText("Not enough placements! You must have at least one.")
            alert.exec_()
        else:
            window = multiResultsWindow(self, scores, str(self.event_no.value()))
            self.windows.append(window)
            window.show()

    def addPlacements(self):
        event_no = str(self.event_no.value())

        if event_no == 0:
            alert = QMessageBox()
            alert.setText("Please add the event number before starting a scoresheet!")
            alert.exec_()
        else:
            window = PlacementWindow(self, event_no)
            self.windows.append(window)
            window.show()

    def clearPlacements(self):
        self.overall.clear()
        self.placements_list.clear()
        self.placements.clear()

    def deletePlacement(self):
        try:
            sel = self.placements.selectedItems()
            for s in sel:
                self.placements_list.pop(s.text())
                self.overall.remove_places(s.text())
                idx = self.placements.indexFromItem(s).row()
                self.placements.takeItem(idx)
        except Exception:
            print(traceback.format_exc())

    def reopenPlacement(self, item: QListWidgetItem):
        window = PlacementWindow(self, self.event_no.value())
        window.addDance(item.text())
        window.addScores(self.placements_list[item.text()][0])
        self.windows.append(window)
        window.show()

    def savePlacement(self, dance, places, event_no, placement):
        def helper():
            ret = self.overall.add_places(dance, places)
            if not ret:
                alert = QMessageBox()
                alert.setText("Looks like you've added a new couple! Check your placements to make sure the numbers are correct.")
                alert.exec_()
            else:
                item = QListWidgetItem(dance)
                match = self.placements.findItems(dance, QtCore.Qt.MatchExactly)
                if len(match) != 0:
                    for m in match:
                        idx = self.placements.indexFromItem(m).row()
                        self.placements.takeItem(idx)
                self.placements.addItem(item)
                self.placements_list[dance] = (places, (dance, event_no))
                placement.close()

        if str(event_no) != str(self.event_no.value()):
            alert = QMessageBox()
            alert.setText("Event number does not match event's. What would you like to do?")
            alert.addButton("Save anyway", QMessageBox.YesRole)
            alert.addButton("Delete placements", QMessageBox.NoRole)
            ret = alert.exec_()
            if ret == 0:
                helper()
                placement.close()
            else:
                placement.close()
        else:
            helper()

    def closeEvent(self, event):
        start = time()
        while len(self.windows) > 0:
            self.windows[0].close()
            if time() - start > 2:
                break

        self.main.windows.remove(self)
        super().closeEvent(event)


class multiResultsWindow(QWidget):
    def __init__(self, main, results, event_no):
        super().__init__()
        self.main = main
        self.event_no = event_no
        self.results, self.dances = results
        title = QLabel("Places for multi-dance event #{}".format(event_no))
        title.setStyleSheet("font-weight: bold")

        n = self.results.shape[0]
        cols = ["Couple"] + self.dances + ["Total", "Result"]
        self.pretty = self.results[cols].sort_values(by="Total")

        self.places = QTableWidget(self.pretty.shape[0], self.pretty.shape[1])
        cols = list(self.pretty.columns)
        self.places.setHorizontalHeaderLabels(cols)
        self.places.setColumnWidth(0, 70)
        self.places.setColumnWidth(self.pretty.shape[1] - 1, 50)
        for i in range(1, len(self.dances) + 1):
            self.places.setColumnWidth(i, 50)
        for i in range(len(self.dances) + 1, self.pretty.shape[1] - 1):
            self.places.setColumnWidth(i, 70)
        for i in range(self.pretty.shape[0]):
            for j in range(self.pretty.shape[1]):
                itm = QTableWidgetItem(str(self.pretty[cols[j]].values[i]))
                itm.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
                itm.setFlags(QtCore.Qt.ItemIsEditable)
                self.places.setItem(i, j, itm)

        blank = QLabel()
        save = QPushButton()
        save.setText("Save")
        save.setFixedWidth(100)
        save.clicked.connect(self.savePlaces)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.places)
        layout2 = QHBoxLayout()
        layout2.addWidget(blank)
        layout2.addWidget(save)
        layout.addLayout(layout2)

        self.setLayout(layout)
        self.setWindowTitle("Comp Scorekeeper")
        self.setMinimumSize(800, 410)

    def savePlaces(self):
        title = "saved/event{}_{}_{}_places.txt".format(self.event_no, "_".join(self.dances), "Final")
        with open(title, "w") as f:
            dfAsString = self.pretty.to_string(header=True, index=False)
            f.write(dfAsString)
        if os.path.isfile(title):
            alert = QMessageBox()
            alert.setText("Placements saved! You can safely close the window now.")
            alert.exec_()

    def closeEvent(self, event):
        self.main.windows.remove(self)
        super().closeEvent(event)


class placingResultsWindow(QWidget):
    def __init__(self, main, results, event_no, round, dance):
        super().__init__()
        self.main = main
        self.event_no = event_no
        self.round = round
        self.dance = dance
        self.results, self.judges = results
        round_word = round == "QF" or round == "SF" or round == "Final"
        title = QLabel("Places for event #{}: {} {}".format(event_no, dance,
                                                            round if round_word else round + str(" Round")))
        title.setStyleSheet("font-weight: bold")

        n = self.results.shape[0]
        self.pretty = self.results.sort_values(by="Place")
        self.pretty["Place"] = self.pretty["Place"].astype(str)
        for i in range(1, n + 1):
            self.pretty["1-" + str(i)] = self.pretty["1-" + str(i)].astype(int).astype(str) + "(" + self.pretty["1-" + str(i) + "SUM"].astype(
                int).astype(str) + ")"
            self.pretty.loc[self.pretty["1-" + str(i)] == "0(0)", "1-" + str(i)] = ""
        # for i in range(1, n + 1):
        #     self.pretty.loc[self.pretty["Place"] == str(i), ["1-" + str(j) for j in range(i + 1, n + 1)]] = ""
        drop = [str(i) + "_" for i in range(1, n + 1)] + ["1-" + str(i) + "SUM" for i in range(1, n + 1)]
        self.pretty = self.pretty.drop(drop, axis=1)

        self.places = QTableWidget(self.pretty.shape[0], self.pretty.shape[1])
        cols = list(self.pretty.columns)
        self.places.setHorizontalHeaderLabels(cols)
        self.places.setColumnWidth(0, 70)
        self.places.setColumnWidth(self.pretty.shape[1] - 1, 50)
        for i in range(1, len(self.judges) + 1):
            self.places.setColumnWidth(i, 50)
        for i in range(len(self.judges) + 1, self.pretty.shape[1] - 1):
            self.places.setColumnWidth(i, 70)
        for i in range(self.pretty.shape[0]):
            for j in range(self.pretty.shape[1]):
                itm = QTableWidgetItem(str(self.pretty[cols[j]].values[i]))
                itm.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
                itm.setFlags(QtCore.Qt.ItemIsEditable)
                self.places.setItem(i, j, itm)

        blank = QLabel()
        save = QPushButton()
        save.setText("Save")
        save.setFixedWidth(100)
        save.clicked.connect(self.savePlaces)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.places)
        layout2 = QHBoxLayout()
        layout2.addWidget(blank)
        layout2.addWidget(save)
        layout.addLayout(layout2)

        self.setLayout(layout)
        self.setWindowTitle("Comp Scorekeeper")
        self.setMinimumSize(800, 410)

    def savePlaces(self):
        title = "saved/event{}_{}_{}_places.txt".format(self.event_no, self.dance, self.round)
        with open(title, "w") as f:
            dfAsString = self.pretty.to_string(header=True, index=False)
            f.write(dfAsString)
        if os.path.isfile(title):
            alert = QMessageBox()
            alert.setText("Placements saved! You can safely close the window now.")
            alert.exec_()

    def closeEvent(self, event):
        self.main.windows.remove(self)
        super().closeEvent(event)


class callbacksResultsWindow(QWidget):
    def __init__(self, main, results, event_no, round, dance):
        super().__init__()
        self.main = main
        self.event_no = event_no
        self.round = round
        self.dance = dance
        self.results, self.judges = results
        self.n = len(self.results)
        m = 1 + len(self.judges)
        round_word = round == "QF" or round == "SF" or round == "Final"
        title = QLabel("Callbacks for event #{}: {} {}".format(event_no, dance,
                                                            round if round_word else round + str(" Round")))
        title.setStyleSheet("font-weight: bold")

        num_label = QLabel("Please select a number of callbacks needed:")
        self.num = QSpinBox()
        self.num.setRange(0, len(self.judges))
        self.num.setValue(np.ceil(len(self.judges) / 2))
        self.num.valueChanged.connect(self.changeCallbacks)

        self.num_callbacks = dict()
        for i in range(len(self.judges) + 1):
            self.num_callbacks[i] = sum([1 if len(y) >= i else 0 for _, y in self.results])
        num_called_label = QLabel("Number of couples called:")
        self.num_called = QLineEdit()
        self.num_called.setText(str(self.num_callbacks[self.num.value()]))
        self.num_called.setReadOnly(True)

        self.callbacks = QTableWidget(self.n, m)
        for i in range(1, m):
            self.callbacks.setColumnWidth(i, 50)
        cols = ["Couple"] + self.judges
        self.callbacks.setHorizontalHeaderLabels(cols)
        for i in range(self.n):
            call = len(self.results[i][1]) >= self.num.value()
            itm = QTableWidgetItem(self.results[i][0])
            itm.setFlags(QtCore.Qt.ItemIsEditable)
            itm.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
            if call:
                itm.setBackground(QtGui.QColor(200, 200, 200))
            self.callbacks.setItem(i, 0, itm)
            for j in range(1, m):
                if cols[j] in self.results[i][1]:
                    itm = QTableWidgetItem("X")
                    itm.setFlags(QtCore.Qt.ItemIsEditable)
                    itm.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
                    if call:
                        itm.setBackground(QtGui.QColor(200, 200, 200))
                    self.callbacks.setItem(i, j, itm)
                else:
                    itm = QTableWidgetItem("")
                    itm.setFlags(QtCore.Qt.ItemIsEditable)
                    itm.setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
                    if call:
                        itm.setBackground(QtGui.QColor(200, 200, 200))
                    self.callbacks.setItem(i, j, itm)

        blank = QLabel()
        save = QPushButton()
        save.setText("Save")
        save.setFixedWidth(100)
        save.clicked.connect(self.saveCallbacks)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout2 = QHBoxLayout()
        layout2.addWidget(num_label)
        layout2.addWidget(self.num)
        layout.addLayout(layout2)
        layout3 = QHBoxLayout()
        layout3.addWidget(num_called_label)
        layout3.addWidget(self.num_called)
        layout.addLayout(layout3)
        layout.addWidget(self.callbacks)
        layout4 = QHBoxLayout()
        layout4.addWidget(blank)
        layout4.addWidget(save)
        layout.addLayout(layout4)

        self.setLayout(layout)
        self.setWindowTitle("Comp Scorekeeper")
        self.setMinimumSize(200, 500)

    def changeCallbacks(self):
        self.num_called.setText(str(self.num_callbacks[self.num.value()]))
        for i in range(self.n):
            call = len(self.results[i][1]) >= self.num.value()
            for j in range(len(self.judges) + 1):
                if call:
                    self.callbacks.item(i, j).setBackground(QtGui.QColor(200, 200, 200))
                else:
                    self.callbacks.item(i, j).setBackground(QtGui.QColor(255, 255, 255))

    def saveCallbacks(self):
        cols = ["Couple"] + self.judges + ["Total", "Recall"]
        callbacks = pd.DataFrame(columns=cols, index=range(self.n))
        callbacks["Couple"] = [couple for couple, _ in self.results]
        callbacks["Total"] = [len(a) for _, a in self.results]
        callbacks["Recall"] = ["R" if len(a) >= self.num.value() else "" for _, a in self.results]
        for i in range(len(self.judges)):
            callbacks[self.judges[i]] = ["X" if self.judges[i] in a else "" for _, a in self.results]
        title = "saved/event{}_{}_{}_callbacks.txt".format(self.event_no, self.dance, self.round)
        with open(title, "w") as f:
            dfAsString = callbacks.to_string(header=True, index=False)
            f.write(dfAsString)
        if os.path.isfile(title):
            alert = QMessageBox()
            alert.setText("Callbacks saved! You can safely close the window now.")
            alert.exec_()

    def closeEvent(self, event):
        self.main.windows.remove(self)
        super().closeEvent(event)


class CallbacksWindow(QWidget):
    def __init__(self, main, event_no, round, dance):
        super().__init__()
        self.main = main
        self.event_no = event_no
        self.round = round
        self.dance = dance

        layout = QVBoxLayout()
        round_word = round == "QF" or round == "SF" or round == "Final"
        title = QLabel("Places for event #{}: {} {}".format(event_no, dance,
                                                            round if round_word else round + str(" Round")))
        title.setStyleSheet("font-weight: bold")
        layout2 = QHBoxLayout()
        judge_label = QLabel("Judge:")
        judge_label.setStyleSheet("font-weight: bold")
        self.judge = QLineEdit()
        self.judge.setPlaceholderText("0")
        layout2.addWidget(judge_label)
        layout2.addWidget(self.judge)
        callbacks_label = QLabel("Callbacks:")
        callbacks_label.setStyleSheet("font-weight: bold")
        self.callbacks = QTableWidget(50, 1)
        for i in range(50):
            self.callbacks.setItem(i, 0, QTableWidgetItem(''))
        self.callbacks.setHorizontalHeaderLabels(["Couple"])
        layout3 = QHBoxLayout()
        cancel = QPushButton("Cancel.")
        cancel.clicked.connect(self.close)
        save = QPushButton("Save.")
        save.clicked.connect(self.onSave)
        layout3.addWidget(cancel)
        layout3.addWidget(save)
        layout.addWidget(title)
        layout.addLayout(layout2)
        layout.addWidget(callbacks_label)
        layout.addWidget(self.callbacks)
        layout.addLayout(layout3)

        self.setLayout(layout)
        self.setWindowTitle("Comp Scorekeeper")
        self.setMinimumSize(200, 500)

    def addJudge(self, judge):
        self.judge.setText(judge)

    def addScores(self, callbacks):
        for i in range(len(callbacks)):
            self.callbacks.setItem(i, 0, QTableWidgetItem(callbacks[i]))

    def onSave(self):
        judge = self.judge.text()
        callbacks = list()
        for i in range(50):
            tmp = self.callbacks.item(i, 0).text()
            if tmp != '' and tmp.isnumeric():
                callbacks.append(tmp)
        if judge != "" and judge.isnumeric() and len(callbacks) > 0:
            self.main.saveScoresheet(judge, callbacks, (self.event_no, self.round, self.dance), self)
        else:
            alert = QMessageBox()
            alert.setText("Please add valid judge number and some callbacks!")
            alert.exec_()

    def closeEvent(self, event):
        self.main.windows.remove(self)
        super().closeEvent(event)


class PlacingWindow(QWidget):
    def __init__(self, main, event_no, round, dance):
        super().__init__()
        self.main = main
        self.event_no = event_no
        self.round = round
        self.dance = dance

        layout = QVBoxLayout()
        round_word = round == "QF" or round == "SF" or round == "Final"
        title = QLabel("Places for event #{}: {} {}".format(event_no, dance,
                                                            round if round_word else round + str(" round")))
        title.setStyleSheet("font-weight: bold")
        layout2 = QHBoxLayout()
        judge_label = QLabel("Judge:")
        judge_label.setStyleSheet("font-weight: bold")
        self.judge = QLineEdit()
        self.judge.setPlaceholderText("0")
        layout2.addWidget(judge_label)
        layout2.addWidget(self.judge)
        placing_label = QLabel("Places:")
        placing_label.setStyleSheet("font-weight: bold")
        self.places = QTableWidget(10, 1)
        for i in range(10):
            self.places.setItem(i, 0, QTableWidgetItem(''))
        self.places.setHorizontalHeaderLabels(["Couple"])
        layout3 = QHBoxLayout()
        cancel = QPushButton("Cancel.")
        cancel.clicked.connect(self.close)
        save = QPushButton("Save.")
        save.clicked.connect(self.onSave)
        layout3.addWidget(cancel)
        layout3.addWidget(save)
        layout.addWidget(title)
        layout.addLayout(layout2)
        layout.addWidget(placing_label)
        layout.addWidget(self.places)
        layout.addLayout(layout3)

        self.setLayout(layout)
        self.setWindowTitle("Comp Scorekeeper")
        self.setMinimumSize(350, 500)

    def addJudge(self, judge):
        self.judge.setText(judge)

    def addScores(self, places):
        for k in places.keys():
            self.places.setItem(places[k] - 1, 0, QTableWidgetItem(k))

    def onSave(self):
        judge = self.judge.text()
        places = dict()
        j = 1
        for i in range(10):
            tmp = self.places.item(i, 0).text()
            if tmp != '' and tmp.isnumeric():
                places[tmp] = j
                j += 1
        if judge != "" and judge.isnumeric() and len(places.keys()) > 0:
            self.main.saveScoresheet(judge, places, (self.event_no, self.round, self.dance), self)
        else:
            alert = QMessageBox()
            alert.setText("Please add valid judge number and some callbacks!")
            alert.exec_()

    def closeEvent(self, event=None):
        self.main.windows.remove(self)
        super().closeEvent(event)


class PlacementWindow(QWidget):
    def __init__(self, main, event_no):
        super().__init__()
        self.main = main
        self.event_no = event_no

        layout = QVBoxLayout()
        title = QLabel("Places for event #{}".format(event_no))
        title.setStyleSheet("font-weight: bold")
        layout2 = QHBoxLayout()
        dance_label = QLabel("Dance")
        dance_label.setStyleSheet("font-weight: bold")
        self.dance = QComboBox()
        self.dance.addItem("")
        self.dance.addItem("Waltz")
        self.dance.addItem("Tango")
        self.dance.addItem("Foxtrot")
        self.dance.addItem("V Waltz")
        self.dance.addItem("Quickstep")
        self.dance.addItem("Peabody")
        self.dance.addItem("Cha Cha")
        self.dance.addItem("Rumba")
        self.dance.addItem("Swing")
        self.dance.addItem("Mambo")
        self.dance.addItem("Bolero")
        self.dance.addItem("Samba")
        self.dance.addItem("Jive")
        self.dance.addItem("Paso Doble")
        self.dance.setFixedWidth(100)
        layout2.addWidget(dance_label)
        layout2.addWidget(self.dance)
        placing_label = QLabel("Places:")
        placing_label.setStyleSheet("font-weight: bold")
        self.places = QTableWidget(8, 1)
        for i in range(8):
            self.places.setItem(i, 0, QTableWidgetItem(''))
        self.places.setHorizontalHeaderLabels(["Couple"])
        layout3 = QHBoxLayout()
        cancel = QPushButton("Cancel.")
        cancel.clicked.connect(self.close)
        save = QPushButton("Save.")
        save.clicked.connect(self.onSave)
        layout3.addWidget(cancel)
        layout3.addWidget(save)
        layout.addWidget(title)
        layout.addLayout(layout2)
        layout.addWidget(placing_label)
        layout.addWidget(self.places)
        layout.addLayout(layout3)

        self.setLayout(layout)
        self.setWindowTitle("Comp Scorekeeper")
        self.setMinimumSize(350, 500)

    def addDance(self, dance):
        self.dance.setCurrentText(dance)

    def addScores(self, places):
        for k in places.keys():
            self.places.setItem(places[k] - 1, 0, QTableWidgetItem(k))

    def onSave(self):
        try:
            dance = self.dance.currentText()
            places = dict()
            j = 1
            for i in range(10):
                tmp = self.places.item(i, 0)
                if tmp is not None and tmp.text() != '' and tmp.text().isnumeric():
                    places[tmp.text()] = j
                    j += 1
            if dance != "" and len(places.keys()) > 0:
                self.main.savePlacement(dance, places, self.event_no, self)
            else:
                alert = QMessageBox()
                alert.setText("Please add valid dance and some places!")
                alert.exec_()
        except Exception:
            print(traceback.format_exc())

    def closeEvent(self, event=None):
        self.main.windows.remove(self)
        super().closeEvent(event)


class RoundWindow(QWidget):
    def __init__(self, main):
        super().__init__()
        self.windows = list()
        self.scoresheets_list = dict()
        self.callbacks = Callbacks()
        self.places = Places()
        self.main = main

        layoutLeft = QVBoxLayout()
        instr = QLabel("State the event number, round, and dance, then add some scoresheets!")
        event_no_label = QLabel("Event Number")
        event_no_label.setStyleSheet("font-weight: bold")
        self.event_no = QSpinBox()
        self.event_no.setValue(0)
        self.event_no.setRange(0, 500)
        self.event_no.setFixedWidth(100)
        self.event_no.valueChanged.connect(self.eventNoChanged)
        round_label = QLabel("Round")
        round_label.setStyleSheet("font-weight: bold")
        self.round = QComboBox()
        self.round.addItem("")
        self.round.addItem("1st")
        self.round.addItem("2nd")
        self.round.addItem("3rd")
        self.round.addItem("QF")
        self.round.addItem("SF")
        self.round.addItem("Final")
        self.round.setFixedWidth(100)
        self.round.currentTextChanged.connect(self.roundChanged)
        dance_label = QLabel("Dance")
        dance_label.setStyleSheet("font-weight: bold")
        self.dance = QComboBox()
        self.dance.addItem("")
        self.dance.addItem("Waltz")
        self.dance.addItem("Tango")
        self.dance.addItem("Foxtrot")
        self.dance.addItem("V Waltz")
        self.dance.addItem("Quickstep")
        self.dance.addItem("Peabody")
        self.dance.addItem("Cha Cha")
        self.dance.addItem("Rumba")
        self.dance.addItem("Swing")
        self.dance.addItem("Mambo")
        self.dance.addItem("Bolero")
        self.dance.addItem("Samba")
        self.dance.addItem("Jive")
        self.dance.addItem("Paso Doble")
        self.dance.setFixedWidth(100)
        self.dance.currentTextChanged.connect(self.danceChanged)
        blank = QLabel("")
        cancel = QPushButton("Cancel")
        cancel.setFixedWidth(100)
        cancel.clicked.connect(self.close)
        layoutLeft.addWidget(instr)
        layoutLeft.addWidget(event_no_label)
        layoutLeft.addWidget(self.event_no)
        layoutLeft.addWidget(round_label)
        layoutLeft.addWidget(self.round)
        layoutLeft.addWidget(dance_label)
        layoutLeft.addWidget(self.dance)
        layoutLeft.addWidget(blank)
        layoutLeft.addWidget(cancel)

        layoutRight = QVBoxLayout()
        add = QPushButton("Add scoresheet")
        add.clicked.connect(self.addScoresheet)
        clear = QPushButton("Clear")
        clear.clicked.connect(self.clearScoresheets)
        delete = QPushButton("Delete")
        delete.clicked.connect(self.deleteScoresheet)
        miniLayout = QHBoxLayout()
        miniLayout.addWidget(clear)
        miniLayout.addWidget(delete)
        calculate = QPushButton("Calculate")
        calculate.clicked.connect(self.calculateRound)
        save = QPushButton("Save round")
        save.clicked.connect(self.saveRound)
        self.scoresheets = QListWidget()
        self.scoresheets.itemDoubleClicked.connect(self.reopenScoresheet)
        layoutRight.addWidget(add)
        layoutRight.addWidget(self.scoresheets)
        layoutRight.addLayout(miniLayout)
        layoutRight.addWidget(calculate)
        layoutRight.addWidget(save)

        layout = QHBoxLayout()
        layout.addLayout(layoutLeft)
        layout.addLayout(layoutRight)

        self.setLayout(layout)
        self.setWindowTitle("Comp Scorekeeper")
        self.setMinimumSize(500, 500)

    def eventNoChanged(self):
        judges = list(self.scoresheets_list.keys())
        for j in judges:
            scores, event_info = self.scoresheets_list[j]
            self.scoresheets_list[j] = (scores, (str(self.event_no.value()), event_info[1], event_info[2]))

    def danceChanged(self):
        judges = list(self.scoresheets_list.keys())
        for j in judges:
            scores, event_info = self.scoresheets_list[j]
            self.scoresheets_list[j] = (scores, (event_info[0], event_info[1], self.dance.currentText()))

    def roundChanged(self):
        if len(self.scoresheets_list.keys()) > 0:
            judges = list(self.scoresheets_list.keys())
            scores, event_info = self.scoresheets_list[judges[0]]
            if (event_info[1] == "Final" and self.round.currentText() != "Final") or (event_info[1] != "Final" and self.round.currentText() == "Final"):
                alert = QMessageBox()
                alert.setText("You changed this round to or from a final and your scoresheets don't match! Changing will remove all scoresheets. What would you like to do?")
                alert.addButton("Change anyway", QMessageBox.YesRole)
                alert.addButton("Cancel", QMessageBox.NoRole)
                ret = alert.exec_()
                if ret == 0:
                    self.clearScoresheets()
                else:
                    self.round.setCurrentText(event_info[1])
            else:
                for j in judges:
                    scores, event_info = self.scoresheets_list[j]
                    self.scoresheets_list[j] = (scores, (event_info[0], self.round.currentText(), event_info[2]))

    def saveRound(self):
        event_no = self.event_no.value()
        round = self.round.currentText()
        dance = self.dance.currentText()
        if event_no == 0 or round == "" or dance == "":
            alert = QMessageBox()
            alert.setText("Try adding in an event number, round, and dance before saving!")
            alert.exec_()
        else:
            title = "saved/event{}_{}_{}_round_data.json".format(event_no, dance, round)
            tmp = {"event_no": event_no, "round": round, "dance": dance, "scoresheets": self.scoresheets_list}
            with open(title, "w", encoding="utf-8") as f:
                json.dump(tmp, f, ensure_ascii=False, indent=4)

            if os.path.isfile(title):
                alert = QMessageBox()
                alert.setText("Round saved! Would you like to keep working on it or close it?")
                alert.addButton("Keep working", QMessageBox.YesRole)
                alert.addButton("Close", QMessageBox.NoRole)
                ret = alert.exec_()
                if ret != 0:
                    self.close()
            else:
                alert = QMessageBox()
                alert.setText("Failed to save round!")
                alert.exec_()

    def calculateRound(self):
        try:
            if self.round.currentText() == "Final":
                scores = self.places.return_places()
                func = placingResultsWindow
            else:
                scores = self.callbacks.return_callbacks()
                func = callbacksResultsWindow
            if scores is None:
                alert = QMessageBox()
                alert.setText("Not enough scoresheets! Callbacks must have at least one and placing must have an odd number.")
                alert.exec_()
            else:
                window = func(self, scores, str(self.event_no.value()), self.round.currentText(), self.dance.currentText())
                self.windows.append(window)
                window.show()
        except Exception:
            print(traceback.format_exc())

    def saveScoresheet(self, judge, scores, event_info, scoresheet):
        def helper():
            if self.round.currentText() == "Final":
                try:
                    ret = self.places.add_places(judge, scores)
                except Exception:
                    print(traceback.format_exc())
            else:
                self.callbacks.add_callbacks(judge, scores)
                ret = True
            if not ret:
                alert = QMessageBox()
                alert.setText("You're trying to place too many couples! Check your scoresheets to make sure the numbers are correct.")
                alert.exec_()
            else:
                item = QListWidgetItem("Judge {}".format(judge))
                match = self.scoresheets.findItems("Judge {}".format(judge), QtCore.Qt.MatchExactly)
                if len(match) != 0:
                    for m in match:
                        idx = self.scoresheets.indexFromItem(m).row()
                        self.scoresheets.takeItem(idx)
                self.scoresheets.addItem(item)
                self.scoresheets_list[judge] = (scores, event_info)
                scoresheet.close()

        if (event_info[1] == "Final" and self.round.currentText() != "Final") or (event_info[1] != "Final" and self.round.currentText() == "Final"):
            alert = QMessageBox()
            alert.setText("Scoresheet's round type does not match event's round type! Could not save scoresheet.")
            alert.exec_()
            scoresheet.close()
        elif event_info[0] != str(self.event_no.value()) or event_info[2] != self.dance.currentText() or event_info[1] != self.round.currentText():
            alert = QMessageBox()
            alert.setText("Event number, dance, or round does not match event's. What would you like to do?")
            alert.addButton("Save anyway", QMessageBox.YesRole)
            alert.addButton("Delete scoresheet", QMessageBox.NoRole)
            ret = alert.exec_()
            if ret == 0:
                helper()
                scoresheet.close()
            else:
                scoresheet.close()
        else:
            helper()

    def reopenScoresheet(self, item: QListWidgetItem):
        try:
            judge = item.text().split()[1]
            scores, event_info = self.scoresheets_list[judge]
            if self.round.currentText() == "Final":
                window = PlacingWindow(self, event_info[0], event_info[1], event_info[2])
            else:
                window = CallbacksWindow(self, event_info[0], event_info[1], event_info[2])
            window.addScores(scores)
            window.addJudge(judge)
            self.windows.append(window)
            window.show()
        except Exception:
            print(traceback.format_exc())

    def addScoresheet(self):
        event_no = str(self.event_no.value())
        round_no = self.round.currentText()
        dance = self.dance.currentText()

        if event_no == "" or round_no == "" or dance == "":
            alert = QMessageBox()
            alert.setText("Please add the event number, round, and dance before starting a scoresheet!")
            alert.exec_()
        else:
            if round_no == "Final":
                window = PlacingWindow(self, event_no, round_no, dance)
            else:
                window = CallbacksWindow(self, event_no, round_no, dance)

            self.windows.append(window)
            window.show()

    def deleteScoresheet(self):
        sel = self.scoresheets.selectedItems()
        for s in sel:
            self.scoresheets_list.pop(s.text().split()[1])
            self.callbacks.remove_callbacks(s.text().split()[1])
            self.places.remove_places(s.text().split()[1])
            idx = self.scoresheets.indexFromItem(s).row()
            self.scoresheets.takeItem(idx)

    def clearScoresheets(self):
        self.places.clear()
        self.callbacks.clear()
        self.scoresheets_list.clear()
        self.scoresheets.clear()

    def closeEvent(self, event):
        start = time()
        while len(self.windows) > 0:
            self.windows[0].close()
            if time() - start > 2:
                break

        self.main.windows.remove(self)
        super().closeEvent(event)


class MainWindow(QMainWindow):
    windows = list()

    def __init__(self):
        super().__init__()

        widget = QWidget()

        layout = QVBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap("ballroom_logo_thumb.png"))
        logo.setAlignment(QtCore.Qt.AlignCenter)
        label = QLabel("Welcome to Comp Scorekeeper! Create a new round to get started.")
        button = QPushButton("Create new round")
        button.clicked.connect(self.on_new_round_clicked)
        button2 = QPushButton("Total placements for multi-dance")
        button2.clicked.connect(self.on_total_placements)

        layout.addWidget(logo)
        layout.addWidget(label)
        layout.addWidget(button)
        layout.addWidget(button2)
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.setWindowTitle("Comp Scorekeeper")
        self.setMinimumSize(500, 500)

    def on_new_round_clicked(self):
        round = RoundWindow(self)
        self.windows.append(round)
        round.show()

    def on_total_placements(self):
        try:
            multi = multiDancePlacing(self)
            self.windows.append(multi)
            multi.show()
        except Exception:
            print(traceback.format_exc())

    def closeEvent(self, event):
        start = time()
        while len(self.windows) > 0:
            self.windows[0].closeEvent(event)
            if time() - start > 2:
                break

        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet("QLabel{font-size: 12pt;} QPushButton{font-size: 12pt;} " +
                      "QComboBox{font-size: 12pt;} QLineEdit{font-size: 12pt;} " +
                      "QSpinBox{font-size: 12pt;} QTableWidget{font-size: 12pt;} " +
                      "QListWidget{font-size: 12pt;}")

    window = MainWindow()
    window.show()

    # window2 = RoundWindow(window)
    # window2.show()

    # window3 = PlacingWindow(window2, "1", "1st", "Waltz")
    # window3.show()

    app.exec_()
