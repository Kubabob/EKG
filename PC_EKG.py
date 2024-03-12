import pyqtgraph as pg
from PyQt6 import QtCore, QtWidgets

import socket
from time import time
from os import system
from sys import stdout

def reScale(value, min, max, nMin, nMax):
    return int(((value - min)/(max - min)) * (nMax-nMin) + nMin)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.server = socket.socket()
        #podaj ip
        #cmd > ipconfig > WLAN > IPv4
        self.server.bind(('ip', 80))
        print(f'Server is ready to go')
        self.server.listen(1)
        self.clientSocket = self.server.accept()[0]
        print(f'{self.clientSocket} connected!')

        # EKG signal vs time dynamic plot
        self.plot_graph = pg.PlotWidget()
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground("w")
        pen = pg.mkPen(color=(255, 0, 0))
        self.plot_graph.setTitle("EKG vs Time", color="b", size="20pt")
        styles = {"color": "red", "font-size": "18px"}
        self.plot_graph.setLabel("left", "EKG signal", **styles)
        self.plot_graph.setLabel("bottom", "Time (s)", **styles)
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.setYRange(-10, 120)
        self.time_space = list(range(100))
        self.EKG = [0 for _ in range(100)]

        # Get a line reference
        self.line = self.plot_graph.plot(
            self.time_space,
            self.EKG,
            name="EKG Sensor",
            pen=pen,
            symbol="+",
            symbolSize=0,
            symbolBrush="b",
        )
        # Add a timer to simulate new temperature measurements
        self.timer = QtCore.QTimer()
        self.timer.setInterval(5)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        self.startTime = time.time()
        self.beats = []
        self.oldBPM = 0
        self.newBPM = 0


    def update_plot(self):
        actualTime = time() - self.startTime
        self.time_space = self.time_space[-100:]
        self.time_space.append(self.time_space[-1] + 1)
        self.EKG = self.EKG[-100:]
        val = reScale(int(self.clientSocket.recv(4).decode('utf-8')), 1000, 9999, 0, 100)
        self.EKG.append(
            val
        )
        self.line.setData(self.time_space, self.EKG)
        

        #saving time of beat
        if 95<=val<=100:
            self.beats.append(round(actualTime,2))

        #checking if first beat in the list happened more than 60 seconds ago
        #if so, delete it
        for beat in self.beats:
            if abs(self.beats[-1] - beat) > 60:
                self.beats = self.beats[1:]
            else:
                break

        #if signal is going for less than 60 seconds we need to extrapolate the value
        if actualTime < 60:
            self.newBPM = int(len(self.beats)/(actualTime/60))
        else:
            self.newBPM = int(len(self.beats))

        #just displaying BPM, but faster
        if self.oldBPM != self.newBPM:
            system('cls')
            stdout.write(f'BPM: {self.newBPM}')
            stdout.flush()
            self.oldBPM = self.newBPM

app = QtWidgets.QApplication([])
main = MainWindow()
main.show()
app.exec()