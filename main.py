from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import gui

class MyApp(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyApp, self).__init__(parent)
        self.setupUi(self)

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = MyApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()