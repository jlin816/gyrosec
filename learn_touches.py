#from keras.models import Sequential
#from keras.layers import Dense
#from sklearn.model_selection import StratifiedKFold
#from keras.optimizers import Adam
import numpy as np

from preprocess import visualize_windows

def build_model():
    model = Sequential()
    model.add(Dense(80, activation="relu", input_dim=(samples_per_window * 6)))
    model.add(Dense(40, activation="relu"))
    model.add(Dense(20, activation="relu"))
    model.add(Dense(1, activation="tanh"))
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics = ["accuracy"])
    model.summary()

    return model

def balance_classes(X, has_touch_y):
    X_with_touch = X[has_touch_y == 1]
    print(X_with_touch.shape)
    print(has_touch_y == -1)
    X_no_touch = X[has_touch_y == -1][:len(X_with_touch)]

    has_touch_y_with_touch = has_touch_y[has_touch_y == 1]
    has_touch_y_no_touch = has_touch_y[has_touch_y == -1][:len(X_with_touch)]

    X_balanced = np.concatenate([X_with_touch, X_no_touch])
    has_touch_y_balanced = np.concatenate([has_touch_y_with_touch, has_touch_y_no_touch])

    print("Number touch:", np.sum(has_touch_y_balanced == 1))
    print("Number no touch:", np.sum(has_touch_y_balanced == -1))

    visualize_windows("balanced_combined", X_balanced, has_touch_y_balanced, "touch")
    visualize_windows("balanced_combined", X_balanced, has_touch_y_balanced, "no_touch")
    return X_balanced, has_touch_y_balanced

if __name__ == "__main__":
    all_datasets = ["dataPixelRHandStandingRandomShortPressesSpacedOut2",
            "dataPixelRHandStandingRandomShortPressesSpacedOut"]
#    skf = StratifiedKFold(n_splits = 5)

    X = []
    has_touch_y = []
    touch_loc_y = []
    for dataset in all_datasets:
        X.append(np.load("processed/{}_x.npy".format(dataset)))
        has_touch_y.append(np.load("processed/{}_has_touch_y.npy".format(dataset)))
        touch_loc_y.append(np.load("processed/{}_touch_loc_y.npy".format(dataset)))

    print(X[0].shape)

    X = np.concatenate(X, axis=0)
    has_touch_y = np.concatenate(has_touch_y, axis=0)
    touch_loc_y = np.concatenate(touch_loc_y, axis=0)
    print(X.shape)
    print(has_touch_y.shape)
    print(touch_loc_y.shape)

    print("Number touch:", np.sum(has_touch_y == 1))
    print("Number no touch:", np.sum(has_touch_y == -1))

    visualize_windows("combined", X, has_touch_y, "touch")
    visualize_windows("combined", X, has_touch_y, "no_touch")

    X_balanced, y_balanced = balance_classes(X, has_touch_y)

    np.save("processed/balanced_combined_X", X_balanced)
    np.save("processed/balanced_combined_has_touch_y", y_balanced)
