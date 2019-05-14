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

window_width = 500
has_touch_model = load_model("has_touch_model.h5")
loc_model = load_model("touch_loc_model.h5")
sensor_stats = np.load("processed/spacedout1-2_min_range.npy")
sensor_mins = sensor_stats[0]
sensor_ranges = sensor_stats[1]
#print("Normalizing...")
#print("Min: ", sensor_mins)
#print("Range: ", sensor_ranges)

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
    acc_data = deque(maxlen=window_width)
    press_data = deque()
    app = QtGui.QApplication([])
    win = pg.GraphicsWindow()

    acc_plot = win.addPlot(title="Accelerometer Data")
    # Create an empty plot
    acc_curve = acc_plot.plot()

    phone_win = pg.GraphicsWindow()
    phone_win.resize(375, 812)
    phone_plot = phone_win.addPlot(title="Press Location", viewBox=pg.ViewBox(invertY=True, lockAspect=375/812))
    phone_plot.disableAutoRange()
    phone_plot.setRange(xRange=(0,375), yRange=(0,812), padding=0)
    scatter = pg.ScatterPlotItem(pen=pg.mkPen(width=5, color="r"), brush=pg.mkBrush(color="r"), symbol="o")
    phone_plot.addItem(scatter)

    # Draw rectangle for phone
    rect = pg.QtGui.QGraphicsRectItem(0, 0, 375, 812)
    rect.setPen(pg.mkPen("r", width=3))
    rect.setBrush(pg.mkBrush(None))
    phone_plot.addItem(rect)

    while True:
        data = await websocket.recv()
        data = json.loads(data)
        if data["event"] == "accelerometer":
            data = data["data"]
            acc_data.append(float(data["x"]))
            ptr += 1
            acc_curve.setData(acc_data)
            acc_curve.setPos(ptr, 0)
            QtGui.QApplication.processEvents()
        elif data["event"] == "press":
#            acc_plot.addLine(x=ptr, y=None)
            pos = [{"pos": [float(data["locationX"]), float(data["locationY"])]}]
            scatter.setData(pos)
            QtGui.QApplication.processEvents()

def json_evts_to_arr(json_evts):
    """Given list of json events sent directly from device, flatten into an array, filter sensor events, and remove ground-truth locations."""
    return [[
            "-2", "-2", # dummy location, will be filtered in preprocessing
            d["event"],
            d["time"],
            d["data"]["x"],
            d["data"]["y"],
            d["data"]["z"]
        ] for d in json_evts if d["event"] in ["accelerometer", "gyroscope"]]

async def predict(websocket, path):
    """Given datastream, first predict when there's a touch onset, then predict touch location from that window.
    Predict on overlapping windows every 100ms (time 0-200, 100-300, 200-400,...).
    """
    last_100ms = []
    last_window_end_t = -1
    next_100ms = []
    print("Connected to a client.")

    app = QtGui.QApplication([])
    win = pg.GraphicsWindow()

    acc_plot_data = deque(maxlen=window_width)
    ptr = 0
    acc_plot = win.addPlot(title="Accelerometer Data")
    # Create an empty plot
    acc_curve = acc_plot.plot()
    got_info = False

    while True:
        data = await websocket.recv()
        data_obj = json.loads(data)

        if data_obj["event"] == "info":
            print("Got info")
            device_w = data_obj["width"]
            device_h = data_obj["height"]

            # Set up phone visualization with dimensions
            phone_win = pg.GraphicsWindow()
            phone_win.resize(device_w, device_h)
            phone_plot = phone_win.addPlot(title="Press Location", viewBox=pg.ViewBox(invertY=True, lockAspect=device_w / device_h))
            phone_plot.disableAutoRange()
            touch_scatter = pg.ScatterPlotItem(pen=pg.mkPen(width=5, color="r"), brush=pg.mkBrush(color=(255, 0, 0, 0.75)), symbol="o")
            pred_scatter = pg.ScatterPlotItem(pen=pg.mkPen(width=5, color="b"), brush=pg.mkBrush(color=(0, 0, 255, 0.75)), symbol="o")

            phone_plot.addItem(touch_scatter)
            phone_plot.addItem(pred_scatter)

            # Draw rectangle for phone
            phone_plot.setRange(xRange=(0, device_w), yRange=(0, device_h), padding=0)
            rect = pg.QtGui.QGraphicsRectItem(0, 0, device_w, device_h)
            rect.setPen(pg.mkPen("r", width=7))
            rect.setBrush(pg.mkBrush(None))
            phone_plot.addItem(rect)
            got_info = True
            continue

        # Wait for initial info
        elif not got_info:
            continue

        # Update plots
        if data_obj["event"] == "accelerometer":
            acc_plot_data.append(float(data_obj["data"]["x"]))
            ptr += 1
            acc_curve.setData(acc_plot_data)
            acc_curve.setPos(ptr, 0)
            QtGui.QApplication.processEvents()
        if data_obj["event"] == "press":
            print("Press detected at time %d, loc (%.2f, %.2f)" % (data_obj["time"], data_obj["locationX"], data_obj["locationY"]))
            pos = [{"pos": [float(data_obj["locationX"]), float(data_obj["locationY"])]}]
            touch_scatter.setData(pos)
            QtGui.QApplication.processEvents()

        # Collect samples for the next prediction window
        if data_obj["time"] < last_window_end_t + 100:
            next_100ms.append(data_obj)
            continue

        # Otherwise, predict on window
        # Edge case: beginning of stream, no "last window"
        if len(last_100ms) == 0:
            last_100ms = next_100ms
            next_100ms = [data_obj]
            last_window_end_t = last_100ms[-1]["time"] if len(last_100ms) > 0 else data_obj["time"]
            continue
        
        # Predict
        has_touch, pred_loc_normalized = predict_loc_if_has_touch(last_100ms + next_100ms)
        if has_touch != -1:
            print("PREDICTION: prob %.2f press between %d-%d" % (has_touch, last_100ms[0]["time"], next_100ms[-1]["time"]))

            pred_loc = [pred_loc_normalized[0] * device_w, pred_loc_normalized[1] * device_h]
            pos = [{"pos": pred_loc}]
            pred_scatter.setData(pos)
            print("Predicted loc: ", pred_loc)

        if len(next_100ms) == 0:
            print(next_100ms)
            import pdb; pdb.set_trace()

        last_window_end_t = next_100ms[-1]["time"]
        last_100ms = list(filter(lambda d: d["time"] > last_window_end_t - 100, next_100ms))
        next_100ms = []

def predict_loc_if_has_touch(window):
    """Predict if there's a touch in a window, and if there is, predict location.
    Args:
        window: array of json events
    """
    window_data = json_evts_to_arr(window)
    sensor_data, num_windows = preprocess_sensor_data(window_data)
    assert(num_windows == 1)
    sensor_data = sensor_data.reshape(-1, 120)
    has_touch = has_touch_model.predict(sensor_data)[0]
    if has_touch < 0.5:
        return -1, -1

    # Normalize data according to each sensor
    sensor_data = sensor_data.reshape(-1, 20, 6)
    sensor_data = (sensor_data - sensor_mins) / sensor_ranges
    sensor_data = sensor_data.reshape(-1, 120)

    predicted_loc_normalized = loc_model.predict(sensor_data)[0]
    return has_touch, predicted_loc_normalized

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
            press_data = list(last_100ms) 
        if collecting_press_data:
            if dataObj["time"] > press_start_time + 100:
                predict_touch_loc(press_data, press_start_time, press_true_loc)
                collecting_press_data = False
                press_start_time = -1
                press_data = []
                press_true_loc = []
            else:
                press_data.append(dataObj)

def predict_touch_loc(press_window_data, press_start_time, true_loc):
    """Given a 200ms window centered on a press event, predict the location."""

    press_window_data = json_evts_to_arr(press_window_data)
    sensor_data, num_windows = preprocess_sensor_data(press_window_data) 
    assert(num_windows == 1)

    sensor_stats = np.load("processed/spacedout1-2_min_range.npy")
    sensor_mins = sensor_stats[0]
    sensor_ranges = sensor_stats[1]
    #print("Normalizing...")
    #print("Min: ", sensor_mins)
    #print("Range: ", sensor_ranges)

    # Normalize data according to each sensor
    sensor_data = (sensor_data - sensor_mins) / sensor_ranges
    sensor_data = sensor_data.reshape(-1, 120)

    predicted_loc = model.predict(sensor_data)[0]
    print("Prediction (according to Jason's screen dims): ", [predicted_loc[0] * 411.43, predicted_loc[1] * 774.857])
    print(true_loc)

    
if __name__ == "__main__":
    mode = sys.argv[1] # "visualize", "collect_data", "predict_given_touch", "predict"
    print("Starting server...")
    if mode == "visualize":
        start_server = websockets.serve(plot_live, "localhost", 8765)
    elif mode == "collect_data":
        save_to = sys.argv[2]
        with open(save_to, mode='w') as data_file:
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
    elif mode == "predict":
        start_server = websockets.serve(predict, "localhost", 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
