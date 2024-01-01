import itertools

import cv2
import numpy as np
import os
import sys
import tensorflow as tf
from keras import Input, Model, Sequential
from keras.src.layers import Dense, Conv3D, Conv2D, Dropout, MaxPooling2D, Rescaling, Flatten
from keras.src.utils import np_utils
from sklearn.decomposition import PCA

from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt

EPOCHS = 20 # DEFAULT BY HW = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    assert len(images) == len(labels)
    print("Len of images and labels: ", len(images), len(labels))

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    """
    Sometimes it is recommended, however have not provide any benefits...
    x_train = x_train/255.0
    x_test = x_test/255.0
    y_train = y_train/255.0
    y_test = y_test/255.0
    """

    print("train shapes:")
    print(x_train.shape)
    print(y_train.shape)
    print(x_test.shape)
    print(y_test.shape)

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    history = model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    evaluation = model.evaluate(x_test, y_test, verbose=2)
    print("evaluation:\n", evaluation)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")

    plot_history(history)


def plot_history(history):
    print("Availible history metics: ", history.history.keys())
    # summarize history for loss
    print("history loss: ", history.history['loss'])
    plt.plot(history.history['loss'])
    # plt.plot(list(range(0, len(history.history['loss'])-1)))
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()


def reduce_dims(img):
    # RGB split
    blue, green, red = cv2.split(img)
    # scaling
    blue, green, red = blue/255.0, green/255.0, red/255.0
    # PCA apply
    pca_b, pca_g, pca_r = PCA(n_components=20), PCA(n_components=20), PCA(n_components=20)
    transformed_pca_b = pca_b.fit_transform(blue)
    transformed_pca_g = pca_g.fit_transform(green)
    transform_pca_r = pca_r.fit_transform(red)
    # Reconstruction of the image
    b_arr = pca_b.inverse_transform(transformed_pca_b)
    g_arr = pca_g.inverse_transform(transformed_pca_g)
    r_arr = pca_r.inverse_transform(transform_pca_r)
    # Merging the channels
    img_reduced = cv2.merge((b_arr, g_arr, r_arr))

    return img_reduced


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images = []
    labels = []
    rgb_values = {}
    folder_name = 'gtsrb'
    print("Processing files...")
    for i in range(0, NUM_CATEGORIES - 1):
        folder_path = folder_name + os.sep + str(i)
        all_files_in_dir = [f for f in os.listdir(folder_path)]
        for file_name in all_files_in_dir:
            img_path = os.path.join(folder_name, str(i), file_name)
            img = cv2.imread(img_path)
            # reduced_dims = reduce_dims(img)
            # TODO: Create dict of frequencies
            actual_image_values = list(itertools.chain.from_iterable(itertools.chain.from_iterable(img.tolist())))
            for rgb_value in actual_image_values:
                if rgb_value in rgb_values:
                    rgb_values[rgb_value] += 1
                else:
                    rgb_values[rgb_value] = 0
            if img is None:
                print("Bad file path.")
            else:
                dim = (IMG_HEIGHT, IMG_WIDTH)
                image_numpy = cv2.resize(img, dsize=dim)
                images.append(image_numpy)
                labels.append(i)

    rgb_values_sorted = dict(sorted(rgb_values.items()))

    plt.xlabel('RGB value')
    plt.ylabel('Frequency of the RGB value')
    rgb_values = list(rgb_values_sorted.keys())
    rgb_values_freqs = list(rgb_values_sorted.values())
    print("rgb_values: ", rgb_values)
    print("rgb_values: ", len(rgb_values))
    print("rgb_values_freqs: ", rgb_values_freqs)
    plt.bar(rgb_values, rgb_values_freqs)
    plt.legend('RGB values of all loaded images: ')
    plt.show()

    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """

    # Basic version:
    """
    nn_model = Sequential([
        # Rescaling(1. / 255, input_shape=(IMG_HEIGHT, IMG_HEIGHT, 3)),
        Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_HEIGHT, 3)),
        MaxPooling2D(pool_size=(2, 2)),
        Flatten(),
        Dense(20, activation='relu'),
        Dropout(0.5),
        # NOTICE: Must be set to NUM_CATEGORIES - 1 to match the num. of training instances
        Dense(NUM_CATEGORIES - 1, activation='softmax'),
    ])
    """
    nn_model = Sequential([
        # Rescaling(1. / 255, input_shape=(IMG_HEIGHT, IMG_HEIGHT, 3)),
        Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_HEIGHT, 3)),
        MaxPooling2D(pool_size=(2, 2)),
        Flatten(),
        Dense(20, activation='relu'),
        Dropout(0.5),
        # NOTICE: Must be set to NUM_CATEGORIES - 1 to match the num. of training instances
        Dense(NUM_CATEGORIES - 1, activation='softmax'),
    ])

    for layer in nn_model.layers:
        print("input shape: ", layer.input_shape)

    nn_model.compile(optimizer='adam',
                     loss='categorical_crossentropy',
                     metrics=['accuracy'])
    return nn_model


if __name__ == "__main__":
    main()
