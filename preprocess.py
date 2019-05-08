import csv
import math
import numpy as np
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import sys

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
    # Check sampled times are increasing
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
        all_data: np array (n, samples_per_window * 6). For each sample, (acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z).
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
    print("Total time: ", end_time)
    print("Num windows:", num_windows)
    print("Num samples: ", num_samples)

    # Interpolate
    interp_times = np.linspace(0, end_time, num=num_samples)
    acc_data_interp = interp_xyz(interp_times, acc_data[:,0], acc_data[:,1:])
    gyro_data_interp = interp_xyz(interp_times, gyro_data[:,0], gyro_data[:,1:])

    all_data = np.concatenate((acc_data_interp, gyro_data_interp), axis=0).T
    assert(all_data.shape == (num_samples, 6))

    print("Done.")
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

def visualize_with_presses(csvf, xyz_data, num_samples_to_view = 1500):
    """Visualizes sensor data with presses highlighted.
    Args:
        csvf: csvf file to filter `press` events from
        xyz_data: (# samples, 4) sensor data. First column is time (ms since start).
    """

    plt.figure(figsize=(20,5))

    plot_end_time = xyz_data[num_samples_to_view - 1][0]
    t_ms = xyz_data[:num_samples_to_view, 0]
    plt.plot(t_ms, xyz_data[:num_samples_to_view, 1], marker="o")
    plt.plot(t_ms, xyz_data[:num_samples_to_view, 2])
    plt.plot(t_ms, xyz_data[:num_samples_to_view, 3])

    presses = [int(x[3]) - start_time for x in csvf if x[2] == "press" if int(x[3]) - start_time < plot_end_time]
    releases = [int(x[3]) - start_time for x in csvf if x[2] == "release" if int(x[3]) - start_time < plot_end_time]

    presses = presses[:min(len(presses), len(releases))]

    for i in range(len(presses)):
        plt.axvspan(presses[i], releases[i], alpha=0.3, color="r")
        
    plt.xticks(np.arange(0, plot_end_time, step=window_size_ms))
    plt.show()

def visualize_windows(dataset, sensor_data_x, has_touch_y, window_type, nrows=5, ncols=5):
    """Visualize touch / no touch windows separately.
    Args:
        sensor_data_x: (# windows, samples_per_window * 6) np array of sensor data
        has_touch_y: (# windows,) np array of 1 (touch) or 0 (no touch) for each window
        window_type: "touch" or "no_touch" which windows to visualize
    """
    sensor_data_x = sensor_data_x.reshape((-1, samples_per_window, 6))

    fig, axes = plt.subplots(nrows, ncols, figsize=(15, 15))
    axes = axes.reshape(-1)
    window_type_val = 1 if window_type == "touch" else 0

    count = 0
    for i in range(50, len(has_touch_y)):
        if has_touch_y[i] == window_type_val:
            if count == nrows * ncols: break
            axes[count].plot(np.linspace(0, window_size_ms, num=samples_per_window), sensor_data_x[i,:,0])
            axes[count].plot(np.linspace(0, window_size_ms, num=samples_per_window), sensor_data_x[i,:,1])
            axes[count].plot(np.linspace(0, window_size_ms, num=samples_per_window), sensor_data_x[i,:,2])
            axes[count].set_ylim(0, 1)
            count += 1
            
    fig.suptitle(dataset + ": " + window_type)
    fname = "figs/{}_{}.png".format(window_type, dataset) 
    print("Saving figure to ", fname)
    plt.savefig(fname) 

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
    dsname = "spacedout1-2"
    all_datasets = ["dataPixelRHandStandingRandomShortPressesSpacedOut2",
            "dataPixelRHandStandingRandomShortPressesSpacedOut"]

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
