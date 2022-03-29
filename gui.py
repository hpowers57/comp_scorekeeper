import traceback

from PyQt5.QtWidgets import *
from time import time
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from scorecard import *


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
        for i in range(max(places.keys())):
            self.places.setItem(i, 0, QTableWidgetItem(places[i + 1]))

    def onSave(self):
        judge = self.judge.text()
        places = dict()
        j = 1
        for i in range(10):
            tmp = self.places.item(i, 0).text()
            if tmp != '' and tmp.isnumeric():
                places[j] = tmp
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


class RoundWindow(QWidget):
    windows = list()
    scoresheets_list = dict()

    def __init__(self, main):
        super().__init__()
        self.main = main

        layoutLeft = QVBoxLayout()
        instr = QLabel("State the event number, round, and dance, then add some scoresheets!")
        event_no_label = QLabel("Event Number")
        event_no_label.setStyleSheet("font-weight: bold")
        self.event_no = QLineEdit()
        self.event_no.setPlaceholderText("0")
        self.event_no.setFixedWidth(100)
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
        save = QPushButton("Save round")
        self.scoresheets = QListWidget()
        self.scoresheets.itemDoubleClicked.connect(self.reopenScoresheet)
        layoutRight.addWidget(add)
        layoutRight.addWidget(self.scoresheets)
        layoutRight.addLayout(miniLayout)
        layoutRight.addWidget(save)

        layout = QHBoxLayout()
        layout.addLayout(layoutLeft)
        layout.addLayout(layoutRight)

        self.setLayout(layout)
        self.setWindowTitle("Comp Scorekeeper")
        self.setMinimumSize(500, 500)

    def saveScoresheet(self, judge, scores, event_info, scoresheet):
        def helper():
            # TODO: add in saving using classes from scorecard module
            item = QListWidgetItem("Judge {}".format(judge))
            match = self.scoresheets.findItems("Judge {}".format(judge), QtCore.Qt.MatchExactly)
            if len(match) != 0:
                for m in match:
                    idx = self.scoresheets.indexFromItem(m).row()
                    self.scoresheets.takeItem(idx)
            self.scoresheets.addItem(item)
            self.scoresheets_list[judge] = (scores, event_info)

        if (event_info[1] == "Final" and self.round.currentText() != "Final") or (event_info[1] != "Final" and self.round.currentText() == "Final"):
            alert = QMessageBox()
            alert.setText("Scoresheet's round type does not match event's round type! Could not save scoresheet.")
            alert.exec_()
            scoresheet.close()
        elif event_info[0] != self.event_no.text() or event_info[2] != self.dance.currentText() or event_info[1] != self.round.currentText():
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
            scoresheet.close()

    def reopenScoresheet(self, item: QListWidgetItem):
        judge = item.text().split()[1]
        scores, event_info = self.scoresheets_list[judge]
        if self.round.currentText() == "Final":
            window = PlacingWindow(self, event_info[0], event_info[1], event_info[2])
        else:
            window = CallbacksWindow(self, event_info[0], event_info[1], event_info[2])
        print("Here!")
        window.addScores(scores)
        print("Here!!")
        window.addJudge(judge)
        print("Here!!!")
        self.windows.append(window)
        window.show()

    def addScoresheet(self):
        event_no = self.event_no.text()
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
            idx = self.scoresheets.indexFromItem(s).row()
            self.scoresheets.takeItem(idx)

    def clearScoresheets(self):
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
        button = QPushButton("Create new round.")
        button.clicked.connect(self.on_new_round_clicked)

        layout.addWidget(logo)
        layout.addWidget(label)
        layout.addWidget(button)
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.setWindowTitle("Comp Scorekeeper")
        self.setMinimumSize(500, 500)

    def on_new_round_clicked(self):
        round = RoundWindow(self)
        self.windows.append(round)
        round.show()

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
                      "QComboBox{font-size: 12pt;} QLineEdit{font-size: 12pt;}")

    window = MainWindow()
    window.show()

    # window2 = RoundWindow(window)
    # window2.show()

    # window3 = PlacingWindow(window2, "1", "1st", "Waltz")
    # window3.show()

    app.exec_()
