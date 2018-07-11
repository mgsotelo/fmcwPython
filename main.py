from PyQt5 import QtWidgets
import sys
import gui
import myMicrowaves


class MyApp(QtWidgets.QMainWindow, gui.Ui_MainWindow,
            myMicrowaves.FMCWoperations):
    def __init__(self, parent=None):
        super(MyApp, self).__init__(parent)
        self.setupUi(self)
        self.fmcw = myMicrowaves.FMCWoperations()
        self.pushButton.clicked.connect(lambda: self.fmcw.frequencyPlot())
        self.pushButton_2.clicked.connect(lambda: self.fmcw.frequencyDist())
        self.pushButton_3.clicked.connect(lambda: self.fmcw.timePlot())
        self.pushButton_4.clicked.connect(self.exitGui)

    def exitGui(self):
        self.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = MyApp()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
