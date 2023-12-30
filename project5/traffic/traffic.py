import cv2
import numpy as np
import os
import sys
import tensorflow as tf
from keras import Input, Model, Sequential
from keras.src.layers import Dense, Conv3D, Conv2D, Dropout, MaxPooling2D, Rescaling, Flatten

from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt

EPOCHS = 10
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
    #plt.plot(list(range(0, len(history.history['loss'])-1)))
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.show()


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
    folder_name = 'gtsrb'
    for i in range(0, NUM_CATEGORIES - 1):
        folder_path = folder_name + os.sep + str(i)
        print("folder_path: ", folder_path)
        all_files_in_dir = [f for f in os.listdir(folder_path)]
        print("files: ", all_files_in_dir)
        for file_name in all_files_in_dir:
            img_path = os.path.join(folder_name, str(i), file_name)
            print("path: ", img_path)
            img = cv2.imread(img_path)
            if img is None:
                print("Bad file path.")
            else:
                dim = (IMG_HEIGHT, IMG_WIDTH)
                image_numpy = cv2.resize(img, dsize=dim)
                images.append(image_numpy)
                labels.append(i)

    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
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
