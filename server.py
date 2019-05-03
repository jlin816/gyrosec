import asyncio
import websockets
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import json
import csv

import signal
import sys


windowWidth = 500

async def hello(websocket, path):
    pressed = False
    locationX = -2
    locationY = -2
    while True:
        data = await websocket.recv()
        # print(data)
        # if "press" in data:
        #     # print("oh boiiiiiiiiiiii")
        #     print(f"< {data}")
        # print(f"< {data}")
        # print(type(data))
        def pressedX():
            if not pressed:
                return -2.0
            else:
                return locationX
        def pressedY():
            if not pressed:
                return -2.0
            else:
                return locationY

        dataObj = json.loads(data)
        if dataObj["event"] == "accelerometer":
            #write
            data_writer.writerow([pressedX(), pressedY(), dataObj["event"], dataObj["time"], dataObj["data"]["x"], dataObj["data"]["y"], dataObj["data"]["z"]])
        elif dataObj["event"] == "press":
            #writee
            pressed=True
            locationY=dataObj["locationY"]
            locationX=dataObj["locationX"]
            data_writer.writerow([pressedX(), pressedY(), dataObj["event"], dataObj["time"], -2, -2, -2])
        elif dataObj["event"] == "gyroscope":
            #writee
            data_writer.writerow([pressedX(), pressedY(), dataObj["event"], dataObj["time"], dataObj["data"]["x"], dataObj["data"]["y"], dataObj["data"]["z"]])
        elif dataObj["event"] == "release":
            #writee
            pressed=False
            locationY=-2
            locationX=-2
            data_writer.writerow([pressedX(), pressedY(), dataObj["event"], dataObj["time"], -2, -2, -2])
        # data_writer.writerow([])
        print("data boiiiis")

async def plot_live(websocket, path):
    ptr = 0
    acc_data = np.zeros((windowWidth,))
    gyro_data = np.zeros((windowWidth,4))
    plot = QtGui.QApplication([])
    win = pg.GraphicsWindow()

    acc_plot = win.addPlot(title="Accelerometer Data")
    # Create an empty plot
    acc_curve = acc_plot.plot()


    while True:
        data = await websocket.recv()
        print(f"< {data}")
        data = json.loads(data)
        acc_data[:-1] = acc_data[1:]
        acc_data[-1] = float(data["x"])
        ptr += 1
        acc_curve.setData(acc_data)
        acc_curve.setPos(ptr, 0)
        QtGui.QApplication.processEvents()

print("starting server")
with open('dataPixelRHandStandingRandomShortPressesFourCornerOnly.csv', mode='w') as data_file:
    def signal_handler(sig, frame):
            print('You pressed Ctrl+C!, saving csv!')
            data_file.close()
            sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    start_server = websockets.serve(hello, "localhost", 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
