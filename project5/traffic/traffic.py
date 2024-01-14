import itertools

import cv2
import numpy as np
import os
import sys
import tensorflow as tf
import pickle
from keras import Input, Model, Sequential
from keras.src.layers import Dense, Conv3D, Conv2D, Dropout, MaxPooling2D, Rescaling, Flatten
from keras.src.utils import np_utils
from sklearn.decomposition import PCA

from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt

EPOCHS = 10 # DEFAULT BY HW = 10
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

    x_train, x_val, y_train, y_val = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Values needs to be normalized, otherwise very poor results
    print("Before norm: ", x_train[:5])
    x_train = x_train / 255.
    print("After norm: ", x_train[:5])
    x_test = x_test / 255.

    print("train shapes:")
    print(x_train.shape)
    print(y_train.shape)
    print(x_test.shape)
    print(y_test.shape)

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    history = model.fit(x_train, y_train, epochs=EPOCHS, batch_size=50,
                        validation_split=0.2)

    # Evaluate neural network performance
    evaluation = model.evaluate(x_test, y_test, verbose=2)
    print("evaluation:\n", evaluation)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")

    plot_history(history)
    plot_accuracy(history)


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


def plot_accuracy(history, miny=None):
    accuracy = history.history['accuracy'] # NOTE: Needs to correspond with the values specified in the metrics=[]
    test_accuracy = history.history['val_accuracy']
    print("accuracy: ", accuracy)
    print("val_accuracy: ", test_accuracy)
    epochs = range(len(accuracy))
    plt.title('model accuracy')
    plt.plot(epochs, accuracy)
    plt.plot(epochs, test_accuracy)
    if miny:
        plt.ylim(miny, 1.0)
    plt.figure()
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

    saved_images_list = 'images.pkl'
    saved_labels_list = 'labels.pkl'

    if not os.path.exists(saved_images_list) or not os.path.exists(saved_labels_list):
        print("Lists not presaved, computing anew and saving...")
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

        print("Saving...")
        with open(saved_images_list, 'wb') as pickle_f:
            pickle.dump(images, pickle_f)
        with open(saved_labels_list, 'wb') as pickle_f:
            pickle.dump(labels, pickle_f)
    else:
        print("Loading lists from saved pickle...")
        with open(saved_images_list, 'rb') as f:
            images = pickle.load(f)
        with open(saved_labels_list, 'rb') as f:
            labels = pickle.load(f)

    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    # TODO: Try to make the Dense higher and lower. What happened?
    # TODO:
    # 1. Try to make the Dense higher and lower. What happened?
    # 2. Try to use another Conv2D after MaxPooling
    # 3. What about smaller kernel_size with best performing model so far?
    # 3. Try any more sophisticated method of normalization
    # 4. Experiment inspired by: https://thedatafrog.com/en/articles/deep-learning-keras/
    # 5. Does batches influence the results?
    # 6. Increase epochs.

    # What about just one dimension for kernel site????
    # Rescaling(1. / 255, input_shape=(IMG_HEIGHT, IMG_HEIGHT, 3)),
    # NOTICE: When is just 1 number specified in kernel_size=12 => (12,12)
    # NOTICE: We need to lower the kernel size, otherwise we loose the dimansions during the training since first,
    # there is a small reduction with the convolution and later, there is / pool_size after max_pooling, so for the
    # Conv2D /w kernel_size=12 and default image size => 30 - 12 + 1 = 19
    # after max pooling: 19/2 = 9, etc.
    # See the model summary
    nn_model = Sequential([
        Conv2D(NUM_CATEGORIES - 1, 3, activation='relu', input_shape=(IMG_HEIGHT, IMG_HEIGHT, 3)),
        # OUT Shapes: IMG_HEIGHT - kernel_size + 1
        MaxPooling2D(pool_size=2),
        Conv2D((NUM_CATEGORIES - 1)*2, 3, activation='relu'),
        MaxPooling2D(pool_size=2),
        Flatten(),
        Dense(300, activation='relu'),
        Dropout(0.45),
        # NOTICE: Must be set to NUM_CATEGORIES - 1 to match the num. of training instances
        Dense(NUM_CATEGORIES - 1, activation='softmax'),
    ])

    print(nn_model.summary())

    # Current best results. Use accuracy as the leading metric
    # loss: 0.0623 - accuracy: 0.9812 - val_loss: 0.0517 - val_accuracy: 0.9880
    """
    nn_model = Sequential([
        Conv2D(NUM_CATEGORIES - 1, 3, activation='relu', input_shape=(IMG_HEIGHT, IMG_HEIGHT, 3)),
        # OUT Shapes: IMG_HEIGHT - kernel_size + 1
        MaxPooling2D(pool_size=2),
        Conv2D((NUM_CATEGORIES - 1)*2, 3, activation='relu'),
        MaxPooling2D(pool_size=2),
        Flatten(),
        Dense(300, activation='relu'),
        Dropout(0.45),
        # NOTICE: Must be set to NUM_CATEGORIES - 1 to match the num. of training instances
        Dense(NUM_CATEGORIES - 1, activation='softmax'),
    ])
    """

    for layer in nn_model.layers:
        print("input shape: ", layer.input_shape)

    nn_model.compile(optimizer='adam',
                     loss='categorical_crossentropy',
                     metrics=['accuracy'])
    return nn_model


if __name__ == "__main__":
    main()
