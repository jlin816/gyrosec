import asyncio
import websockets
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import json

windowWidth = 500

async def hello(websocket, path):
    while True:
        data = await websocket.recv()
        print(f"< {data}")

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
        if data["event"] == "accelerometer":
            data = data["data"]
            acc_data[:-1] = acc_data[1:]
            acc_data[-1] = float(data["x"])
            ptr += 1
            acc_curve.setData(acc_data)
            acc_curve.setPos(ptr, 0)
            QtGui.QApplication.processEvents()

print("starting server")
start_server = websockets.serve(plot_live, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
