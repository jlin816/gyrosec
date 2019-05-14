import numpy as np
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

window_size_ms = 200.
samples_per_window = 20

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
