from PyQt5 import QtCore
import numpy as np
import scipy.signal as signal
import serial as ps
import pyqtgraph as pg


class ArduinoThread(QtCore.QThread):
    dataChanged = QtCore.pyqtSignal(str)
    
    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self, *args, **kwargs)
        self.raw = ps.Serial('COM3', 9600)
        self.raw.close()
        self.raw.open()

    def run(self):
        while True:
            datos_array = self.raw.readline().decode().split(',')
            if datos_array:
                datos = datos_array[0]
            self.dataChanged.emit(datos)
            QtCore.QThread.msleep(1)


class FMCWoperations:
    def __init__(self):
        self.contador = 0
        self.contadortime = 0
        self.thread = ArduinoThread()
        self.thread.start()
    
    def frequencyPlot(self):
        
        self.thread.dataChanged.connect(self.updateFrequencyPlot)
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle('Frecuencia(LIVE) - TEL236')
        self.p1 = self.win.addPlot()
        self.p1.setYRange(0, 1024, padding=0)
        self.curva1 = self.p1.plot()
        self.y1 = np.zeros(1024, dtype=float)

    def updateFrequencyPlot(self, data):
        fs = 2e3
        if self.contador > 1023:
            self.contador = 0
            self.y1 = np.zeros(1024, dtype=float)
        elif self.contador == 1023:
            f, Pwelch_spec = signal.welch(self.y1, fs, scaling='spectrum')
            self.curva1.setData(f, Pwelch_spec, pen='r')
        else:
            self.y1[self.contador] = data
            self.contador += 1
        
    def frequencyDist(self):
        pass

    def timePlot(self):
        self.thread.dataChanged.connect(self.updateTimePlot)
        self.win2 = pg.GraphicsWindow()
        self.win2.setWindowTitle('Tiempo(LIVE) - TEL236')
        self.p2 = self.win2.addPlot()
        self.p2.setYRange(0, 1024, padding=0)
        self.curva2 = self.p2.plot()
        self.y2 = np.zeros(100, dtype=float)

    def updateTimePlot(self, data):
        if self.contadortime > 99:
            self.y2 = np.zeros(100, dtype=float)
            self.contadortime = 0
        else:
            self.y2[self.contadortime] = data
            self.contadortime += 1
        self.curva2.setData(self.y2)
