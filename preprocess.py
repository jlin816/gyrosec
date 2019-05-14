import csv
import math
import numpy as np
import sys
from visualize import *

window_size_ms = 200.
samples_per_window = 20

# n = number of windows
# `all_data`: (n, samples_per_window, 6) data (acc_x,acc_y,acc_z, gyro_x, gyro_y, gyro_z)
# `has_touch`: (n,) array of 1/0 (bool for whether touch occured in this window)
# `touch_loc`: (n,2) array of (x,y) touch locations
# All times are adjusted so the first time in the dataset is 0.

def load_dataset(dataset):
    """Loads dataset and returns list of rows.
    Each row is formatted:
        touch_x, touch_y, sensor, t, x, y, z = row
    """
    print("Loading dataset...")
    with open("data/" + dataset + ".csv") as f:
        csvreader = csv.reader(f)
        csvf = list(csvreader)
    print(csvf[0])
    start_time = int(csvf[0][3])
    print("Total time (s): ", (int(csvf[-1][3]) - start_time)/1000)
    return csvf

def normalize(arr):
    """Normalizes data to [0, 1]."""
    arr_min = np.min(arr, axis=0)
    arr_range = np.ptp(arr, axis=0)
    print("Min: ", arr_min)
    print("Range: ", arr_range)
    return (arr - arr_min) / arr_range

def interp_xyz(interp_times, data_times, data):
    """Interpolates sensor data across time.
    Args:
        interp_times: (T,) times to evaluate interpolated data
        data_times: (n,) times we have sampled
        data: (n, 3) (x,y,z) sensor data for each time.
    Returns:
        (T, 3) interpolated (x,y,z) sensor data
    """ 
    assert(len(data_times) == len(data))
    # Remove duplicate readings for the same time (diff = 0)
    dup_times = (np.diff(data_times) == 0).nonzero()
    data_times = np.delete(data_times, dup_times, axis=0)
    data = np.delete(data, dup_times, axis=0)

    # Make sure sampled times are strictly increasing now
    assert(np.all(np.diff(data_times) > 0))
    data_interp = [
        np.interp(interp_times, data_times, data[:,0]),
        np.interp(interp_times, data_times, data[:,1]),
        np.interp(interp_times, data_times, data[:,2]),
    ]
    return data_interp

def preprocess_sensor_data(csvf):
    """Filters into acc/gyro, interpolates data according to `samples_per_window`, and returns data in windows.
    Returns:
        all_data: np array (num_samples, 6). For each sample, (acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z).
    """
    start_time = int(csvf[0][3])

    # Separate acc and gyro data
    acc_data = np.array([[
        int(x[3]) - start_time, float(x[4]), float(x[5]), float(x[6])
    ] for x in csvf if x[2] == "accelerometer"])

    gyro_data = np.array([[
        int(x[3]) - start_time, float(x[4]), float(x[5]), float(x[6])
    ] for x in csvf if x[2] == "gyroscope"])


    end_time = max(acc_data[-1][0], gyro_data[-1][0])
    num_windows = math.ceil((end_time / window_size_ms))
    num_samples = num_windows * samples_per_window
    #print("Total time: ", end_time)
    #print("Num windows:", num_windows)
    #print("Num samples: ", num_samples)

    # Interpolate
    interp_times = np.linspace(0, end_time, num=num_samples)
    acc_data_interp = interp_xyz(interp_times, acc_data[:,0], acc_data[:,1:])
    gyro_data_interp = interp_xyz(interp_times, gyro_data[:,0], gyro_data[:,1:])

    all_data = np.concatenate((acc_data_interp, gyro_data_interp), axis=0).T
    assert(all_data.shape == (num_samples, 6))

    #print("Done.")
    return all_data, num_windows

def preprocess_presses(csvf, num_windows):
    """Constructs labels for dataset. `has_touch`=1 if there is a touch ONSET in a window."""

    start_time = int(csvf[0][3])

    # (# presses, 3) array of (window #, touch_x, touch_y)
    press_locs = np.array([[
        int(math.floor((int(x[3]) - start_time) / window_size_ms)), float(x[0]), float(x[1])
    ] for x in csvf if x[2] == "press"])

    has_touch = np.zeros((num_windows,))
    touch_loc = -2 * np.ones((num_windows, 2))

    has_touch[press_locs[:,0].astype(int)] = 1
    touch_loc[press_locs[:,0].astype(int)] = press_locs[:,1:]

    print("Number touch windows", np.sum(has_touch == 1))
    print("Number no touch windows", np.sum(has_touch == 0))

    return has_touch, touch_loc

def save(sensor_data, has_touch, touch_loc, dataset):
    print("Saving...")
    sensor_data = sensor_data.reshape(-1, samples_per_window * 6)

    print("sensor_data: ", sensor_data.shape)
    print("has_touch: ", has_touch.shape)
    print("touch_loc: ", touch_loc.shape)
    np.save("processed/{}_x.npy".format(dataset), sensor_data)
    np.save("processed/{}_has_touch_y.npy".format(dataset), has_touch)
    np.save("processed/{}_touch_loc_y.npy".format(dataset), touch_loc)

def preprocess_single_dataset(dataset):
    csvf = load_dataset(dataset)
    sensor_data, num_windows = preprocess_sensor_data(csvf) 
    has_touch, touch_loc = preprocess_presses(csvf, num_windows)

    assert(has_touch.shape == (num_windows,))
    assert(touch_loc.shape == (num_windows, 2))

    visualize_windows(dataset, sensor_data, has_touch, "touch")
    visualize_windows(dataset, sensor_data, has_touch, "no_touch")

    save(sensor_data, has_touch, touch_loc, dataset)

def normalize_sensor_data_over_windows(X):
    X = X.reshape(-1, 6)
    X_min = np.min(X, axis=0)
    X_range = np.ptp(X, axis=0)
    assert(X_min.shape == (6,))
    assert(X_range.shape == (6,))
    print("Min: ", X_min)
    print("Range: ", X_range)
    X = (X - X_min) / X_range
    
    # Split into windows
    X = X.reshape((-1, samples_per_window, 6)), X_min, X_range
    return X

def balance_classes(X, has_touch_y):
    X_with_touch = X[has_touch_y == 1]
    print(X_with_touch.shape)
    print(has_touch_y == 0)

    X_no_touch = X[has_touch_y == 0][:len(X_with_touch)]

    has_touch_y_with_touch = has_touch_y[has_touch_y == 1]
    has_touch_y_no_touch = has_touch_y[has_touch_y == 0][:len(X_with_touch)]

    X_balanced = np.concatenate([X_with_touch, X_no_touch])
    has_touch_y_balanced = np.concatenate([has_touch_y_with_touch, has_touch_y_no_touch])

    print("Number touch:", np.sum(has_touch_y_balanced == 1))
    print("Number no touch:", np.sum(has_touch_y_balanced == 0))

    return X_balanced, has_touch_y_balanced

def main():
    dsname = "jessyiPhone"
    all_datasets = ["jessyiPhone"]
#            "dataPixelRHandStandingRandomShortPressesSpacedOut"]

    X = []
    has_touch_y = []
    touch_loc_y = []
    for dataset in all_datasets:
        preprocess_single_dataset(dataset)
        X.append(np.load("processed/{}_x.npy".format(dataset)))
        has_touch_y.append(np.load("processed/{}_has_touch_y.npy".format(dataset)))
        touch_loc_y.append(np.load("processed/{}_touch_loc_y.npy".format(dataset)))

    X = np.concatenate(X, axis=0)
    has_touch_y = np.concatenate(has_touch_y, axis=0)
    touch_loc_y = np.concatenate(touch_loc_y, axis=0)
    assert(X.shape[1] == 120)

    X, X_min, X_range = normalize_sensor_data_over_windows(X)
    # Save stats so we can normalize inputs at test time
    np.save("processed/%s_min_range" % dsname, [X_min, X_range])

    print("Number touch:", np.sum(has_touch_y == 1))
    print("Number no touch:", np.sum(has_touch_y == 0))

    visualize_windows(dsname, X, has_touch_y, "touch")
    visualize_windows(dsname, X, has_touch_y, "no_touch")
    np.save("processed/%s_X" % dsname, X)
    np.save("processed/%s_has_touch_y" % dsname, has_touch_y)
    np.save("processed/%s_touch_loc_y" % dsname, touch_loc_y)

    # Balance classes
    X_balanced, has_touch_y_balanced = balance_classes(X, has_touch_y)

    visualize_windows("balanced_%s" % dsname, X_balanced, has_touch_y_balanced, "touch")
    visualize_windows("balanced_%s" % dsname, X_balanced, has_touch_y_balanced, "no_touch")
    np.save("processed/balanced_%s_X" % dsname, X_balanced)
    np.save("processed/balanced_%s_has_touch_y" % dsname, has_touch_y_balanced)

if __name__ == "__main__":
    main()
