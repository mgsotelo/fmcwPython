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
        self.stream = sd.InputStream(samplerate=self.fs, channels=2, device=0)
        # print(self.stream)

    def run(self):
        with self.stream:
            while True:
                data, overflow = self.stream.read(1)
                if data.any():
                    datos = data[0]
                    self.dataChanged.emit(np.float(datos[0]))
        
        
class FMCWoperations:
    def __init__(self):
        self.contador = 0
        self.contador2 = 0
        self.contador3 = 0
        # contadortime = 0
        # cambiar a arduino si se quiere usar un arduino
        self.thread1 = AudioThread()
        self.thread2 = AudioThread()
        self.thread3 = AudioThread()
        # self.thread = ArduinoThread()
        self.numMuestras = 882
        self.y1 = np.zeros(self.numMuestras, dtype=float)
        self.xd = np.zeros(1)

        #################################################################
        # parametros para modificar :D
        self.BW = 490e6  # ancho de banda
        self.T = self.numMuestras / self.thread2.fs  # periodo de muestreo
        self.Vg = 3e8  # velocidad de la luz aprox
        #################################################################

    def frequencyPlot(self):
        self.thread1.start()
        self.thread1.dataChanged.connect(self.updateFrequencyPlot)
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle('Frecuencia(LIVE) - TEL236')
        self.p1 = self.win.addPlot()
        self.p1.setYRange(0, 1e-5, padding=0)
        self.curva1 = self.p1.plot()
        self.p_max1 = self.win.addPlot()
        self.p_max1.setYRange(0, 1e-5, padding=0)
        self.puntito1 = self.p_max1.plot()
        # print(self.win.setAntialiasing(True))

    def updateFrequencyPlot(self, data):
        fs = self.thread1.fs
        if self.contador > self.numMuestras - 1:
            self.contador = 0
            self.y1 = np.zeros(self.numMuestras, dtype=float)
        elif self.contador == self.numMuestras - 1:
            data = signal.welch(self.y1, fs, scaling='spectrum')
            f, Pwelch_spec = data
            self.max_index = np.argmax(Pwelch_spec)
            # max_amp = Pwelch_spec[max_index]
            self.Puntito_spec = np.zeros(len(data[0]), dtype=float)
            # Puntito_spec[max_index] = max_amp
            # Maxima amplitud para que solo varía dependiendo de la frecuencia
            self.Puntito_spec[self.max_index] = 6e-6
            self.puntito1.setData(f, self.Puntito_spec, pen=None, symbol='o')
            self.curva1.setData(f, Pwelch_spec, pen='y')
            self.contador += 1
        else:
            self.y1[self.contador] = data
            self.contador += 1
        
    def frequencyDist(self):
        self.thread2.start()
        self.thread2.dataChanged.connect(self.updateFrequencyDist)
        self.win3 = pg.GraphicsWindow()
        self.win3.setWindowTitle('Distancia (LIVE) - TEL236')
        self.p3 = self.win3.addPlot()
        self.p_dis = self.p3.plot(pen=None, symbol='o')
        self.p3.setYRange(0, 15, padding=0)
        self.p3.showGrid(True, True, 0.7)
        self.R1 = 0  # la distancia que queremos hallar

    def updateFrequencyDist(self, data):
        fs = self.thread2.fs
        if self.contador2 > self.numMuestras - 1:
            self.contador2 = 0
            self.y1 = np.zeros(self.numMuestras, dtype=float)
        elif self.contador2 == self.numMuestras - 1:
            f, Pwelch_spec = signal.welch(self.y1, fs, scaling='spectrum')
            self.max_index = np.argmax(Pwelch_spec)
            # print(self.T + " " + self.Vg)
            # print(f[self.max_index])
            self.R1 = (self.T * self.Vg * f[self.max_index]) / (2 * self.BW)
            print("frecuencia = ", f[self.max_index], " distancia = ",
                  self.R1, " amplitud = ", Pwelch_spec[self.max_index])
            self.xd[0] = self.R1
            # print(self.xd)
            self.p_dis.setData(self.xd)
            self.contador2 += 1
        else:
            self.y1[self.contador2] = data
            self.contador2 += 1
        
    def timePlot(self):        
        self.thread3.start()
        self.thread3.dataChanged.connect(self.updateTimePlot)
        self.win2 = pg.GraphicsWindow()
        self.win2.setWindowTitle('Tiempo(LIVE) - TEL236')
        self.p2 = self.win2.addPlot()
        self.curva2 = self.p2.plot()
        self.y2 = np.zeros(self.numMuestras, dtype=float)
        
    def updateTimePlot(self, data):
        if self.contador3 > self.numMuestras - 1:
            self.y2 = np.zeros(self.numMuestras, dtype=float)
            self.contador3 = 0
            # self.curva2.setData(self.y2)
            # TO DO time plotting :(
        else:
            self.y2[self.contador3] = data
            self.contador3 += 1
