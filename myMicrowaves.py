from PyQt5 import QtCore
import numpy as np
import scipy.signal as signal
import serial as ps
import pyqtgraph as pg
import sounddevice as sd


class ArduinoThread(QtCore.QThread):
    dataChanged = QtCore.pyqtSignal(str)
    
    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self, *args, **kwargs)
        self.fs = 20000
        self.raw = ps.Serial('COM3', 9600)
        self.raw.close()
        self.raw.open()

    def run(self):
        while True:
            datos_array = self.raw.readline().decode().split(',')
            if datos_array:
                datos = datos_array[0]
                self.dataChanged.emit(datos)
            # QtCore.QThread.msleep(1)


class AudioThread(QtCore.QThread):
    dataChanged = QtCore.pyqtSignal(np.float)

    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self, *args, **kwargs)
        self.fs = 44100
        self.stream = sd.InputStream(samplerate=self.fs, channels=1, device=0)
        # print(self.stream)

    def run(self):
        with self.stream:
            while True:
                data, overflow = self.stream.read(1)
                if data:
                    datos = data[0]
                    self.dataChanged.emit(np.float(datos[0]))
        
        
class FMCWoperations:
    def __init__(self):
        self.contador = 0
        self.contadortime = 0
        # cambiar a arduino si se quiere usar un arduino
        self.thread = AudioThread()
        # self.thread = ArduinoThread()
        self.thread.start()
    
    def frequencyPlot(self):
        
        self.thread.dataChanged.connect(self.updateFrequencyPlot)
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle('Frecuencia(LIVE) - TEL236')
        # print(sd.query_devices())
        self.p1 = self.win.addPlot()
        # self.p1.setYRange(0, 1024, padding=0)
        self.curva1 = self.p1.plot()
        self.y1 = np.zeros(1024, dtype=float)
        print(self.win.setAntialiasing(True))

    def updateFrequencyPlot(self, data):

        fs = self.thread.fs
        if self.contador > 1023:
            self.contador = 0
            self.y1 = np.zeros(1024, dtype=float)
        elif self.contador == 1023:
            f, Pwelch_spec = signal.welch(self.y1, fs, scaling='spectrum')
            self.curva1.setData(f, Pwelch_spec, pen='r')
            self.contador += 1
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
        self.curva2 = self.p2.plot()
        self.y2 = np.zeros(1024, dtype=float)

    def updateTimePlot(self, data):
        if self.contadortime > 1023:
            self.y2 = np.zeros(1024, dtype=float)
            self.contadortime = 0
        else:
            self.y2[self.contadortime] = data
            self.contadortime += 1
        self.curva2.setData(self.y2)
