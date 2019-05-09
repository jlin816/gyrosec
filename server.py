import asyncio
import websockets
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import json
import csv
from collections import deque
from keras.models import load_model

import signal
import sys

from preprocess import preprocess_sensor_data

windowWidth = 500

async def hello(websocket, path):
    pressed = False
    locationX = -2
    locationY = -2
    while True:
        data = await websocket.recv()
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
        if data["event"] == "accelerometer":
            data = data["data"]
            acc_data[:-1] = acc_data[1:]
            acc_data[-1] = float(data["x"])
            ptr += 1
            acc_curve.setData(acc_data)
            acc_curve.setPos(ptr, 0)
            QtGui.QApplication.processEvents()

async def predict_given_touch(websocket, path):
    """Easier version of prediction task: given the ground-truth touch events, predict location"""
    last_100ms = deque() 
    collecting_press_data = False
    press_start_time = -1
    press_data = []
    press_true_loc = []
    
    while True:
        data = await websocket.recv()
        dataObj = json.loads(data)
        # Remove old samples before the last 100ms
        while len(last_100ms) > 0 and last_100ms[0]["time"] < dataObj["time"] - 100:
            last_100ms.popleft()
        # Add new samples
        last_100ms.append(dataObj)

        if dataObj["event"] == "press":
            # Make sure we're not pressing too quickly / not done collecting previous press data
            assert(not collecting_press_data)
            collecting_press_data = True
            press_start_time = dataObj["time"]
            press_true_loc = [dataObj["locationX"], dataObj["locationY"]]
            print("Detected a press at time ", press_start_time)
            press_data = list(last_100ms) 
        if collecting_press_data:
            if dataObj["time"] > press_start_time + 100:
                print("Stopping press window at time ", dataObj["time"])
                predict_touch_loc(press_data, press_start_time, press_true_loc)
                collecting_press_data = False
                press_start_time = -1
                press_data = []
                press_true_loc = []
            else:
                press_data.append(dataObj)

def predict_touch_loc(press_window_data, press_start_time, true_loc):
    """Given a 200ms window centered on a press event, predict the location."""
    print("Predicting location...")

    press_window_data = [[
            "-2", "-2", # dummy location, will be filtered in preprocessing
            d["event"],
            d["time"],
            d["data"]["x"],
            d["data"]["y"],
            d["data"]["z"]
        ] for d in press_window_data if d["event"] in ["accelerometer", "gyroscope"]]

    sensor_data, num_windows = preprocess_sensor_data(press_window_data) 
    assert(num_windows == 1)

    sensor_stats = np.load("processed/spacedout1-2_min_range.npy")
    sensor_mins = sensor_stats[0]
    sensor_ranges = sensor_stats[1]
    print("Normalizing...")
    print("Min: ", sensor_mins)
    print("Range: ", sensor_ranges)

    # Normalize data according to each sensor
    sensor_data = (sensor_data - sensor_mins) / sensor_ranges
    sensor_data = sensor_data.reshape(-1, 120)

    print("Loading model...")
    model = load_model("touch_loc_model.h5")
    print("Predicting...")
    predicted_loc = model.predict(sensor_data)
    print(predicted_loc)
    print(true_loc)

    
if __name__ == "__main__":
    mode = sys.argv[1] # "visualize", "collect_data", "predict_given_touch"
    print("starting server")
    if mode == "collect_data":
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
    elif mode == "predict_given_touch":
        start_server = websockets.serve(predict_given_touch, "localhost", 8765)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
